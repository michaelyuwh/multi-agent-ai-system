"""Common utilities for AI agents."""

import os
import time
import logging
import uuid
from typing import Dict, Any, Optional, List
from pathlib import Path


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Set up logging configuration."""
    level = getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("ai_agents.log")],
    )

    return logging.getLogger(__name__)


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return str(uuid.uuid4())


def get_timestamp() -> float:
    """Get current timestamp."""
    return time.time()


def format_timestamp(timestamp: float) -> str:
    """Format timestamp for display."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input."""
    if not text:
        return ""

    # Remove potentially harmful characters
    sanitized = text.strip()

    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."

    return sanitized


def create_response_metadata(
    model_used: str,
    response_time: float,
    token_count: Optional[int] = None,
    memory_context_used: bool = False,
) -> Dict[str, Any]:
    """Create metadata for agent responses."""
    return {
        "model_used": model_used,
        "response_time_seconds": response_time,
        "token_count": token_count,
        "memory_context_used": memory_context_used,
        "timestamp": get_timestamp(),
    }


def validate_environment() -> Dict[str, Any]:
    """Validate environment configuration."""
    required_vars = ["OLLAMA_API_BASE", "DEFAULT_MODEL"]
    optional_vars = ["GOOGLE_API_KEY", "LOG_LEVEL"]

    validation_result: Dict[str, Any] = {
        "valid": True,
        "missing_required": [],
        "missing_optional": [],
        "environment_info": {},
    }

    # Check required variables
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            validation_result["missing_required"].append(var)
            validation_result["valid"] = False
        else:
            validation_result["environment_info"][var] = value

    # Check optional variables
    for var in optional_vars:
        value = os.getenv(var)
        if not value:
            validation_result["missing_optional"].append(var)
        else:
            validation_result["environment_info"][var] = (
                value[:10] + "..." if len(value) > 10 else value
            )

    return validation_result


def create_agent_instructions(base_instruction: str, memory_context: str = "") -> str:
    """Create enhanced agent instructions with memory context."""
    enhanced_instruction = base_instruction

    if memory_context:
        enhanced_instruction = f"""
{base_instruction}

CONVERSATION CONTEXT:
{memory_context}

Please use the above context to provide more personalized and informed responses. 
Reference previous conversations when relevant, and maintain consistency with past interactions.
"""

    return enhanced_instruction


def extract_model_name(full_model_name: str) -> str:
    """Extract the base model name from full model specification."""
    if "/" in full_model_name:
        return full_model_name.split("/")[-1]
    return full_model_name


def estimate_token_count(text: str) -> int:
    """Rough estimation of token count (approximately 4 characters per token)."""
    return len(text) // 4


def check_system_resources() -> Dict[str, Any]:
    """Check system resources and provide recommendations."""
    import psutil

    # Get system information
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)

    # Convert bytes to GB
    total_memory_gb = memory.total / (1024**3)
    available_memory_gb = memory.available / (1024**3)
    used_memory_percent = memory.percent

    # Create recommendations
    recommendations = []

    if used_memory_percent > 80:
        recommendations.append(
            "High memory usage detected. Consider using a smaller model."
        )

    if cpu_percent > 80:
        recommendations.append(
            "High CPU usage detected. Consider reducing concurrent requests."
        )

    if available_memory_gb < 2:
        recommendations.append(
            "Low available memory. Close other applications or use a lighter model."
        )

    return {
        "total_memory_gb": round(total_memory_gb, 2),
        "available_memory_gb": round(available_memory_gb, 2),
        "memory_usage_percent": used_memory_percent,
        "cpu_usage_percent": cpu_percent,
        "recommendations": recommendations,
        "suitable_for_ai": available_memory_gb > 4 and cpu_percent < 70,
    }


def create_startup_banner() -> str:
    """Create a startup banner for the AI agents."""
    return """
    ╭─────────────────────────────────────────────────────────────╮
    │                    🤖 AI Agents System                      │
    │                Powered by Google ADK & Ollama              │
    ╰─────────────────────────────────────────────────────────────╯
    
    🚀 Base AI Agent: http://localhost:8000
    🔍 Google Search Agent: http://localhost:8001
    📝 Memory System: Enabled
    🧠 Local LLM: Ollama Integration
    
    """


def create_health_check_endpoint_data() -> Dict[str, Any]:
    """Create health check data for the agents."""
    from .ollama_config import check_ollama_status
    from .memory_manager import get_memory_manager

    # Check Ollama status
    ollama_status = check_ollama_status()

    # Check memory manager
    memory_manager = get_memory_manager()
    memory_stats = memory_manager.get_memory_stats()

    # Check environment
    env_validation = validate_environment()

    # Check system resources
    system_resources = check_system_resources()

    return {
        "status": (
            "healthy"
            if ollama_status["service_running"] and env_validation["valid"]
            else "unhealthy"
        ),
        "timestamp": format_timestamp(get_timestamp()),
        "ollama": ollama_status,
        "memory": memory_stats,
        "environment": env_validation,
        "system": system_resources,
        "version": "1.0.0",
    }


class Timer:
    """Simple timer context manager for measuring execution time."""

    def __init__(self) -> None:
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.elapsed: Optional[float] = None

    def __enter__(self) -> "Timer":
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.end_time = time.time()
        if self.start_time is not None:
            self.elapsed = self.end_time - self.start_time


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely load JSON string with default fallback."""
    try:
        import json

        return json.loads(json_str)
    except Exception:
        return default


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def create_error_response(
    error_message: str, error_code: str = "GENERAL_ERROR"
) -> Dict[str, Any]:
    """Create standardized error response."""
    return {
        "error": True,
        "error_code": error_code,
        "error_message": error_message,
        "timestamp": format_timestamp(get_timestamp()),
        "suggestion": "Please check the logs for more details or contact support.",
    }
