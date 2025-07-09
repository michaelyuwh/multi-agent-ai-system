"""Memory management utilities for AI agents."""

import os
import json
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class MemoryEntry:
    """A single memory entry containing conversation context."""

    timestamp: float
    user_message: str
    assistant_response: str
    session_id: str
    context_hash: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MemoryManager:
    """Manages persistent memory and chat history for AI agents."""

    def __init__(self, memory_dir: str = "memory_data"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)

        # Configuration from environment
        self.max_history = int(os.getenv("MEMORY_MAX_HISTORY", "100"))
        self.search_threshold = float(os.getenv("MEMORY_SEARCH_THRESHOLD", "0.7"))
        self.session_timeout = int(os.getenv("SESSION_TIMEOUT", "3600"))
        self.enable_cross_session = (
            os.getenv("ENABLE_CROSS_SESSION_MEMORY", "true").lower() == "true"
        )

        # Memory storage
        self.current_session_memory: List[MemoryEntry] = []
        self.persistent_memory: List[MemoryEntry] = []

        # Load existing memory
        self._load_persistent_memory()

    def _generate_context_hash(self, text: str) -> str:
        """Generate a hash for context similarity comparison."""
        return hashlib.md5(text.lower().encode()).hexdigest()[:8]

    def _load_persistent_memory(self) -> None:
        """Load persistent memory from disk."""
        memory_file = self.memory_dir / "persistent_memory.json"
        if memory_file.exists():
            try:
                with open(memory_file, "r") as f:
                    data = json.load(f)
                    self.persistent_memory = [MemoryEntry(**entry) for entry in data]
                    # Clean old entries
                    self._cleanup_old_memories()
            except Exception as e:
                print(f"Warning: Could not load persistent memory: {e}")
                self.persistent_memory = []

    def _save_persistent_memory(self) -> None:
        """Save persistent memory to disk."""
        memory_file = self.memory_dir / "persistent_memory.json"
        try:
            data = [asdict(entry) for entry in self.persistent_memory]
            with open(memory_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save persistent memory: {e}")

    def _cleanup_old_memories(self) -> None:
        """Remove old memories beyond the maximum limit."""
        if len(self.persistent_memory) > self.max_history:
            # Sort by timestamp and keep the most recent
            self.persistent_memory.sort(key=lambda x: x.timestamp, reverse=True)
            self.persistent_memory = self.persistent_memory[: self.max_history]

    def add_interaction(
        self,
        user_message: str,
        assistant_response: str,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a new interaction to memory."""
        entry = MemoryEntry(
            timestamp=time.time(),
            user_message=user_message,
            assistant_response=assistant_response,
            session_id=session_id,
            context_hash=self._generate_context_hash(user_message + assistant_response),
            metadata=metadata or {},
        )

        # Add to current session
        self.current_session_memory.append(entry)

        # Add to persistent memory if cross-session memory is enabled
        if self.enable_cross_session:
            self.persistent_memory.append(entry)
            self._cleanup_old_memories()
            self._save_persistent_memory()

    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[MemoryEntry]:
        """Get conversation history for a specific session."""
        session_memories = [
            entry
            for entry in self.current_session_memory
            if entry.session_id == session_id
        ]

        if limit:
            session_memories = session_memories[-limit:]

        return session_memories

    def search_memory(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """Search memory for relevant past interactions."""
        query_lower = query.lower()
        relevant_memories = []

        # Combine current session and persistent memory
        all_memories = self.current_session_memory + self.persistent_memory

        # Simple keyword-based search (can be enhanced with semantic search)
        for entry in all_memories:
            score = 0

            # Check user message
            if query_lower in entry.user_message.lower():
                score += 1

            # Check assistant response
            if query_lower in entry.assistant_response.lower():
                score += 0.5

            # Check for word overlap
            query_words = set(query_lower.split())
            message_words = set(entry.user_message.lower().split())
            response_words = set(entry.assistant_response.lower().split())

            word_overlap = len(
                query_words.intersection(message_words.union(response_words))
            )
            score += word_overlap * 0.1

            if score > 0:
                relevant_memories.append((score, entry))

        # Sort by relevance and return top results
        relevant_memories.sort(key=lambda x: x[0], reverse=True)
        return [entry for score, entry in relevant_memories[:limit] if score >= 0.1]

    def get_context_for_query(self, query: str, session_id: str) -> str:
        """Get relevant context for a query from memory."""
        context_parts = []

        # Get recent session history (last 5 interactions)
        recent_history = self.get_session_history(session_id, limit=5)
        if recent_history:
            context_parts.append("Recent conversation:")
            for entry in recent_history[-3:]:  # Last 3 interactions
                context_parts.append(f"User: {entry.user_message}")
                context_parts.append(f"Assistant: {entry.assistant_response}")

        # Search for relevant past interactions
        if self.enable_cross_session:
            relevant_memories = self.search_memory(query, limit=3)
            if relevant_memories:
                context_parts.append("\nRelevant past conversations:")
                for memory in relevant_memories:
                    if memory.session_id != session_id:  # Don't repeat current session
                        context_parts.append(f"Previous context: {memory.user_message}")
                        context_parts.append(
                            f"Previous response: {memory.assistant_response}"
                        )

        return "\n".join(context_parts) if context_parts else ""

    def clear_session_memory(self, session_id: str) -> None:
        """Clear memory for a specific session."""
        self.current_session_memory = [
            entry
            for entry in self.current_session_memory
            if entry.session_id != session_id
        ]

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory usage."""
        current_time = time.time()

        # Count recent interactions (last hour)
        recent_count = sum(
            1
            for entry in self.current_session_memory
            if current_time - entry.timestamp < 3600
        )

        # Count unique sessions
        unique_sessions = len(
            set(entry.session_id for entry in self.current_session_memory)
        )

        return {
            "total_current_session_memories": len(self.current_session_memory),
            "total_persistent_memories": len(self.persistent_memory),
            "recent_interactions_last_hour": recent_count,
            "unique_sessions": unique_sessions,
            "memory_enabled": self.enable_cross_session,
            "max_history_limit": self.max_history,
        }

    def export_memory(self, filepath: str) -> None:
        """Export memory to a JSON file."""
        all_memories = self.current_session_memory + self.persistent_memory
        data = [asdict(entry) for entry in all_memories]

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def import_memory(self, filepath: str) -> None:
        """Import memory from a JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)
            imported_memories = [MemoryEntry(**entry) for entry in data]

            # Add to persistent memory
            self.persistent_memory.extend(imported_memories)
            self._cleanup_old_memories()
            self._save_persistent_memory()


def get_memory_manager() -> MemoryManager:
    """Factory function to get memory manager instance."""
    return MemoryManager()


# Utility functions for memory integration with ADK agents


def create_memory_context_instruction(
    memory_manager: MemoryManager, query: str, session_id: str
) -> str:
    """Create a context instruction for the agent based on memory."""
    context = memory_manager.get_context_for_query(query, session_id)

    if context:
        return f"""Previous conversation context:
{context}

Current user query: {query}

Please use the above context to provide a more informed and personalized response. Reference previous conversations when relevant, and maintain consistency with past interactions."""

    return f"Current user query: {query}"


def extract_user_info_from_memory(
    memory_manager: MemoryManager, session_id: str
) -> Dict[str, Any]:
    """Extract user information and preferences from memory."""
    user_info = {
        "name": None,
        "preferences": [],
        "interests": [],
        "previous_topics": [],
    }

    # Get all memories for analysis
    all_memories = (
        memory_manager.get_session_history(session_id)
        + memory_manager.persistent_memory
    )

    # Simple extraction logic (can be enhanced with NLP)
    for memory in all_memories:
        user_msg = memory.user_message.lower()

        # Extract name
        if "my name is" in user_msg:
            name_part = user_msg.split("my name is")[-1].strip().split()[0]
            user_info["name"] = name_part.capitalize()

        # Extract preferences
        if "i like" in user_msg or "i prefer" in user_msg:
            preference = user_msg.split(
                "i like" if "i like" in user_msg else "i prefer"
            )[-1].strip()
            user_info["preferences"].append(preference)

        # Extract interests
        if "interested in" in user_msg or "working on" in user_msg:
            interest = user_msg.split(
                "interested in" if "interested in" in user_msg else "working on"
            )[-1].strip()
            user_info["interests"].append(interest)

    return user_info
