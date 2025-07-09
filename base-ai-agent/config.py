"""Configuration for the Base AI Agent."""

import os
from typing import Dict, Any
from pathlib import Path

# Get the root directory
ROOT_DIR = Path(__file__).parent.parent

# Agent Configuration
AGENT_CONFIG = {
    "name": "base_ai_agent",
    "description": "A conversational AI agent with memory capabilities and local Ollama integration",
    "version": "1.0.0",
    "model_provider": "ollama",
    "enable_memory": True,
    "enable_web_interface": True,
    "enable_a2a_communication": True,
}

# Model Configuration
MODEL_CONFIG = {
    "default_model": os.getenv("DEFAULT_MODEL", "ollama_chat/mistral-small:7b"),
    "temperature": float(os.getenv("MODEL_TEMPERATURE", "0.7")),
    "max_tokens": int(os.getenv("MODEL_MAX_TOKENS", "2048")),
    "context_window": int(os.getenv("MODEL_CONTEXT_WINDOW", "8192")),
    "timeout": 30,  # seconds
}

# Memory Configuration
MEMORY_CONFIG = {
    "max_history": int(os.getenv("MEMORY_MAX_HISTORY", "100")),
    "search_threshold": float(os.getenv("MEMORY_SEARCH_THRESHOLD", "0.7")),
    "session_timeout": int(os.getenv("SESSION_TIMEOUT", "3600")),
    "enable_cross_session": os.getenv("ENABLE_CROSS_SESSION_MEMORY", "true").lower()
    == "true",
    "memory_dir": str(ROOT_DIR / "memory_data"),
}

# Web Interface Configuration
WEB_CONFIG = {
    "host": "127.0.0.1",
    "port": int(os.getenv("ADK_WEB_PORT", "8000")),
    "auto_reload": os.getenv("AUTO_RELOAD", "true").lower() == "true",
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
}

# A2A Configuration (for communication with Google Search Agent)
A2A_CONFIG = {
    "google_search_agent_url": f"http://localhost:{os.getenv('ADK_A2A_PORT', '8001')}/a2a/google_search_agent/.well-known/agent.json",
    "enable_delegation": True,
    "timeout": 30,  # seconds
}

# Ollama Configuration
OLLAMA_CONFIG = {
    "api_base": os.getenv("OLLAMA_API_BASE", "http://localhost:11434"),
    "health_check_interval": 30,  # seconds
    "retry_attempts": 3,
    "retry_delay": 1,  # seconds
}

# Security Configuration
SECURITY_CONFIG = {
    "max_input_length": 1000,
    "rate_limit_requests_per_minute": 60,
    "enable_input_sanitization": True,
    "allowed_origins": ["http://localhost:8000", "http://127.0.0.1:8000"],
}

# Feature Flags
FEATURES = {
    "enable_streaming": True,
    "enable_tool_calling": True,
    "enable_context_memory": True,
    "enable_user_preferences": True,
    "enable_conversation_summarization": False,  # Can be enabled for longer conversations
    "enable_debug_logging": os.getenv("DEVELOPMENT_MODE", "false").lower() == "true",
    "enable_mcp_integration": os.getenv("ENABLE_MCP", "false").lower()
    == "true",  # Future feature
}

# MCP Configuration (Future)
MCP_CONFIG = {
    "enabled": os.getenv("ENABLE_MCP", "false").lower() == "true",
    "filesystem_access": {
        "enabled": False,  # Will be configurable in future
        "allowed_paths": [],  # Safe paths for filesystem access
        "read_only": True,  # Start with read-only access
    },
    "custom_servers": [],  # Custom MCP servers configuration
    "tool_timeout": 10,  # Timeout for MCP tool calls
}

# Agent Instructions
BASE_INSTRUCTION = """You are a helpful and knowledgeable AI assistant. Your name is BaseAI, and you are designed to:

1. **Be Conversational**: Engage in natural, friendly conversations with users
2. **Use Memory**: Remember previous interactions and context from our conversation history
3. **Delegate When Needed**: Use the Google Search Agent for web searches and current information
4. **Be Helpful**: Provide accurate, relevant, and useful information
5. **Stay Focused**: Keep responses concise but comprehensive

Key capabilities:
- I can remember our conversation history and reference previous topics
- I can search the web through my Google Search Agent when you need current information
- I work locally using Ollama, ensuring privacy and fast responses
- I can help with various tasks: answering questions, creative writing, problem-solving, coding, analysis

If you need information that requires web searching (like current events, latest news, real-time data), I'll delegate that to my Google Search Agent to get you the most up-to-date information.

How can I help you today?"""

MEMORY_ENHANCED_INSTRUCTION = """You are BaseAI, a conversational AI assistant with advanced memory capabilities.

CONVERSATION CONTEXT:
{memory_context}

Based on our conversation history above, please:
1. Acknowledge relevant previous context when appropriate
2. Maintain consistency with past interactions
3. Reference user preferences and information shared earlier
4. Build upon previous topics naturally

Current user message: {user_message}

Provide a helpful, contextually-aware response that takes into account our conversation history."""

# Error Messages
ERROR_MESSAGES = {
    "ollama_connection": "I'm having trouble connecting to my language model. Please make sure Ollama is running.",
    "memory_error": "I encountered an issue with my memory system, but I can still help you.",
    "search_agent_error": "I couldn't reach my Google Search Agent right now, but I'll try to help with my existing knowledge.",
    "rate_limit": "You're sending messages too quickly. Please wait a moment before trying again.",
    "input_too_long": "Your message is too long. Please try breaking it into smaller parts.",
    "general_error": "I encountered an unexpected error. Please try again or rephrase your request.",
}

# Success Messages
SUCCESS_MESSAGES = {
    "memory_saved": "I've saved our conversation to memory.",
    "search_delegated": "Let me search for that information...",
    "context_loaded": "I've loaded our previous conversation context.",
    "agent_ready": "BaseAI is ready to chat! How can I help you today?",
}


def get_agent_config() -> Dict[str, Any]:
    """Get complete agent configuration."""
    return {
        "agent": AGENT_CONFIG,
        "model": MODEL_CONFIG,
        "memory": MEMORY_CONFIG,
        "web": WEB_CONFIG,
        "a2a": A2A_CONFIG,
        "ollama": OLLAMA_CONFIG,
        "security": SECURITY_CONFIG,
        "features": FEATURES,
    }


def get_instruction_template(use_memory: bool = False) -> str:
    """Get the appropriate instruction template."""
    if use_memory:
        return MEMORY_ENHANCED_INSTRUCTION
    return BASE_INSTRUCTION


def validate_config() -> Dict[str, Any]:
    """Validate agent configuration."""
    validation_result = {"valid": True, "errors": [], "warnings": []}

    # Check required environment variables
    required_vars = ["OLLAMA_API_BASE", "DEFAULT_MODEL"]
    for var in required_vars:
        if not os.getenv(var):
            validation_result["errors"].append(
                f"Missing required environment variable: {var}"
            )
            validation_result["valid"] = False

    # Check model configuration
    if MODEL_CONFIG["temperature"] < 0 or MODEL_CONFIG["temperature"] > 1:
        validation_result["warnings"].append("Temperature should be between 0 and 1")

    if MODEL_CONFIG["max_tokens"] < 100:
        validation_result["warnings"].append(
            "Max tokens seems low, responses might be truncated"
        )

    # Check memory configuration
    if MEMORY_CONFIG["max_history"] < 10:
        validation_result["warnings"].append(
            "Max history is very low, context might be limited"
        )

    # Check ports
    if WEB_CONFIG["port"] == int(os.getenv("ADK_A2A_PORT", "8001")):
        validation_result["errors"].append("Web and A2A ports cannot be the same")
        validation_result["valid"] = False

    return validation_result
