"""Ollama configuration and utilities."""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class OllamaConfig:
    """Configuration class for Ollama integration."""

    def __init__(self):
        self.api_base = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
        self.default_model = os.getenv("DEFAULT_MODEL", "ollama_chat/mistral-small:7b")
        self.temperature = float(os.getenv("MODEL_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("MODEL_MAX_TOKENS", "2048"))
        self.context_window = int(os.getenv("MODEL_CONTEXT_WINDOW", "8192"))

    def get_litellm_config(self) -> Dict[str, Any]:
        """Get configuration for LiteLLM integration."""
        return {
            "model": self.default_model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "api_base": self.api_base,
        }

    def validate_model_availability(self) -> bool:
        """Check if the configured model is available in Ollama."""
        try:
            import requests

            response = requests.get(f"{self.api_base}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_name = self.default_model.replace("ollama_chat/", "")
                return any(
                    model.get("name", "").startswith(model_name) for model in models
                )
            return False
        except Exception:
            return False

    def get_recommended_models(self) -> list[str]:
        """Get list of recommended models for MacBook Air M3 16GB."""
        return [
            "mistral-small:7b",  # Primary recommendation
            "llama3.1:8b",  # Alternative general purpose
            "llama3.1:7b",  # Faster responses
            "codellama:7b",  # For code-related tasks
            "gemma2:7b",  # Google's model
        ]

    def setup_environment(self) -> None:
        """Set up environment variables for Ollama integration."""
        os.environ["OLLAMA_API_BASE"] = self.api_base
        # Set OpenAI API base for LiteLLM compatibility
        if self.default_model.startswith("ollama_chat/"):
            os.environ["OPENAI_API_BASE"] = f"{self.api_base}/v1"
            os.environ["OPENAI_API_KEY"] = "anything"  # Placeholder for Ollama


def get_ollama_config() -> OllamaConfig:
    """Factory function to get Ollama configuration."""
    return OllamaConfig()


def check_ollama_status() -> Dict[str, Any]:
    """Check Ollama service status and available models."""
    import requests

    config = get_ollama_config()
    status = {
        "service_running": False,
        "api_accessible": False,
        "model_available": False,
        "available_models": [],
        "error": None,
    }

    try:
        # Check if Ollama service is running
        response = requests.get(f"{config.api_base}/api/version", timeout=5)
        if response.status_code == 200:
            status["service_running"] = True
            status["api_accessible"] = True

            # Get available models
            models_response = requests.get(f"{config.api_base}/api/tags")
            if models_response.status_code == 200:
                models_data = models_response.json()
                status["available_models"] = [
                    model.get("name", "") for model in models_data.get("models", [])
                ]

                # Check if configured model is available
                model_name = config.default_model.replace("ollama_chat/", "")
                status["model_available"] = any(
                    model.startswith(model_name) for model in status["available_models"]
                )

    except requests.RequestException as e:
        status["error"] = str(e)
    except Exception as e:
        status["error"] = f"Unexpected error: {str(e)}"

    return status


def get_model_suggestions(current_model: Optional[str] = None) -> Dict[str, str]:
    """Get model suggestions based on use case."""
    suggestions = {
        "fastest": "llama3.1:7b - Fastest responses, good for quick interactions",
        "balanced": "mistral-small:7b - Best balance of speed and quality (recommended)",
        "quality": "llama3.1:8b - Higher quality responses, slightly slower",
        "coding": "codellama:7b - Optimized for code generation and programming tasks",
        "lightweight": "gemma2:7b - Efficient Google model, good for basic tasks",
    }

    if current_model:
        suggestions["current"] = f"Currently using: {current_model}"

    return suggestions
