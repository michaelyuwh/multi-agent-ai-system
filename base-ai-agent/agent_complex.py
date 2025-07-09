"""Base AI Agent - Main conversational agent with memory and Ollama integration."""

import sys
import os
import time
import asyncio
from typing import Optional, Dict, Any, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from pydantic import BaseModel

# Import our shared utilities
from shared.memory_manager import (
    get_memory_manager,
    create_memory_context_instruction,
    extract_user_info_from_memory,
)
from shared.ollama_config import get_ollama_config, check_ollama_status
from shared.utils import (
    setup_logging,
    generate_session_id,
    sanitize_input,
    create_response_metadata,
    Timer,
    format_timestamp,
)
from config import (
    get_agent_config,
    get_instruction_template,
    BASE_INSTRUCTION,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES,
    validate_config,
)

# Set up logging
logger = setup_logging()

# Initialize configurations
config = get_agent_config()
ollama_config = get_ollama_config()
memory_manager = get_memory_manager()

# Setup Ollama environment
ollama_config.setup_environment()


# Custom tools for the base agent
def get_agent_status(tool_context: ToolContext) -> Dict[str, Any]:
    """Get comprehensive status of the AI agent system."""

    # Check Ollama status
    ollama_status = check_ollama_status()

    # Get memory statistics
    memory_stats = memory_manager.get_memory_stats()

    # Get configuration validation
    config_validation = validate_config()

    # System information
    system_info = {
        "agent_name": config["agent"]["name"],
        "version": config["agent"]["version"],
        "model": config["model"]["default_model"],
        "memory_enabled": config["memory"]["enable_cross_session"],
        "uptime": "Available since session start",
    }

    status = {
        "system": system_info,
        "ollama": ollama_status,
        "memory": memory_stats,
        "configuration": config_validation,
        "timestamp": format_timestamp(time.time()),
        "healthy": ollama_status["service_running"] and config_validation["valid"],
    }

    return status


def remember_information(information: str, tool_context: ToolContext) -> str:
    """Manually save important information to memory."""
    try:
        session_id = getattr(tool_context, "session_id", "default_session")

        # Save to memory
        memory_manager.add_interaction(
            user_message=f"User wants to remember: {information}",
            assistant_response=f"I've saved this information: {information}",
            session_id=session_id,
            metadata={"type": "manual_memory", "importance": "high"},
        )

        return f"I've successfully saved this information to my memory: {information}"

    except Exception as e:
        logger.error(f"Error saving information to memory: {e}")
        return "I had trouble saving that information, but I'll try to remember it for this conversation."


def search_my_memory(query: str, tool_context: ToolContext) -> str:
    """Search through conversation memory for relevant information."""
    try:
        relevant_memories = memory_manager.search_memory(query, limit=5)

        if not relevant_memories:
            return f"I don't have any relevant memories about '{query}'. This might be the first time we've discussed this topic."

        memory_results = []
        for memory in relevant_memories:
            memory_results.append(
                f"From our conversation on {format_timestamp(memory.timestamp)}:"
            )
            memory_results.append(f"User: {memory.user_message}")
            memory_results.append(f"Me: {memory.assistant_response}")
            memory_results.append("---")

        return f"Here's what I found in my memory about '{query}':\n\n" + "\n".join(
            memory_results
        )

    except Exception as e:
        logger.error(f"Error searching memory: {e}")
        return f"I had trouble searching my memory for '{query}', but I'm still here to help."


def get_user_profile(tool_context: ToolContext) -> str:
    """Get information about the user from conversation history."""
    try:
        session_id = getattr(tool_context, "session_id", "default_session")
        user_info = extract_user_info_from_memory(memory_manager, session_id)

        profile_parts = []

        if user_info["name"]:
            profile_parts.append(f"Name: {user_info['name']}")

        if user_info["preferences"]:
            profile_parts.append(
                f"Preferences: {', '.join(user_info['preferences'][:3])}"
            )

        if user_info["interests"]:
            profile_parts.append(f"Interests: {', '.join(user_info['interests'][:3])}")

        if not profile_parts:
            return "I don't have specific profile information yet. Feel free to share more about yourself!"

        return (
            "Based on our conversations, here's what I know about you:\n"
            + "\n".join(profile_parts)
        )

    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        return "I'm still learning about you as we chat!"


def clear_my_memory(tool_context: ToolContext) -> str:
    """Clear the current session memory (not persistent memory)."""
    try:
        session_id = getattr(tool_context, "session_id", "default_session")
        memory_manager.clear_session_memory(session_id)
        return "I've cleared my memory for this session. My persistent memory across sessions remains intact."

    except Exception as e:
        logger.error(f"Error clearing memory: {e}")
        return "I had trouble clearing my memory, but I'm still here to help."


# Callback functions for enhanced memory integration
# TODO: Re-implement when CallbackContext is available in the ADK version
# async def before_agent_callback(callback_context: Any) -> None:
#     """Called before the agent processes a request."""
#     pass

# async def after_agent_callback(callback_context: Any) -> None:
#     """Called after the agent generates a response.""" 
#     pass
    """Called after the agent generates a response."""
    try:
        session_id = callback_context._invocation_context.session.id

        # Get the latest user message and agent response
        events = callback_context._invocation_context.session.events

        user_message = ""
        agent_response = ""

        # Find the latest user message and agent response
        for event in reversed(events):
            if event.content:
                if event.content.role == "user" and not user_message:
                    user_message = (
                        event.content.parts[0].text if event.content.parts else ""
                    )
                elif event.content.role == "model" and not agent_response:
                    agent_response = (
                        event.content.parts[0].text if event.content.parts else ""
                    )

                if user_message and agent_response:
                    break

        # Save to memory if we have both messages
        if user_message and agent_response:
            memory_enhanced = callback_context.state.get("memory_enhanced", False)

            memory_manager.add_interaction(
                user_message=sanitize_input(user_message),
                assistant_response=sanitize_input(agent_response),
                session_id=session_id,
                metadata={
                    "memory_enhanced": memory_enhanced,
                    "timestamp": time.time(),
                    "agent_version": config["agent"]["version"],
                },
            )

            logger.debug(f"Saved interaction to memory for session {session_id}")

    except Exception as e:
        logger.error(f"Error in after_agent_callback: {e}")


# Initialize Google Search Agent (A2A communication)
# TODO: Re-enable A2A communication when RemoteA2aAgent is available
google_search_agent = None
logger.info("A2A communication temporarily disabled")


# Create the main Base AI Agent
def create_base_ai_agent() -> Agent:
    """Create and configure the base AI agent."""

    # Validate configuration
    validation = validate_config()
    if not validation["valid"]:
        raise ValueError(f"Configuration validation failed: {validation['errors']}")

    # Check Ollama status
    ollama_status = check_ollama_status()
    if not ollama_status["service_running"]:
        raise RuntimeError(
            "Ollama service is not running. Please start Ollama before running the agent."
        )

    if not ollama_status["model_available"]:
        model_name = config["model"]["default_model"].replace("ollama_chat/", "")
        logger.warning(
            f"Model {model_name} not found. Available models: {ollama_status['available_models']}"
        )

    # Create LiteLLM model for Ollama
    litellm_model = LiteLlm(
        model=config["model"]["default_model"], **ollama_config.get_litellm_config()
    )

    # Create tools
    tools = [
        FunctionTool(get_agent_status),
        FunctionTool(remember_information),
        FunctionTool(search_my_memory),
        FunctionTool(get_user_profile),
        FunctionTool(clear_my_memory),
    ]

    # Add Google Search Agent if available
    sub_agents = []
    if google_search_agent:
        sub_agents.append(google_search_agent)
        logger.info("Added Google Search Agent as sub-agent")

    # Create the agent
    agent = Agent(
        model=litellm_model,
        name=config["agent"]["name"],
        description=config["agent"]["description"],
        instruction=BASE_INSTRUCTION,
        tools=tools,
        sub_agents=sub_agents,
        # TODO: Re-enable callbacks when available
        # before_agent_callback=before_agent_callback,
        # after_agent_callback=after_agent_callback,
        generate_content_config=types.GenerateContentConfig(
            temperature=config["model"]["temperature"],
            max_output_tokens=config["model"]["max_tokens"],
            safety_settings=[
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.OFF,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                    threshold=types.HarmBlockThreshold.OFF,
                ),
            ],
        ),
    )

    logger.info(f"Base AI Agent '{config['agent']['name']}' created successfully")
    logger.info(f"Using model: {config['model']['default_model']}")
    logger.info(f"Memory enabled: {config['memory']['enable_cross_session']}")
    logger.info(
        f"Google Search Agent: {'Available' if google_search_agent else 'Not available'}"
    )

    return agent


# Create the agent instance
try:
    root_agent = create_base_ai_agent()

    # Log startup information
    logger.info("=" * 60)
    logger.info("🤖 Base AI Agent Started Successfully!")
    logger.info(f"Agent Name: {config['agent']['name']}")
    logger.info(f"Version: {config['agent']['version']}")
    logger.info(f"Model: {config['model']['default_model']}")
    logger.info(f"Web Interface: http://localhost:{config['web']['port']}")
    logger.info(
        f"Memory System: {'Enabled' if config['memory']['enable_cross_session'] else 'Disabled'}"
    )
    logger.info(
        f"A2A Communication: {'Enabled' if google_search_agent else 'Disabled'}"
    )
    logger.info("=" * 60)

    # Print startup banner
    from shared.utils import create_startup_banner

    print(create_startup_banner())

except Exception as e:
    logger.error(f"Failed to create Base AI Agent: {e}")
    print(f"\n❌ Error: {e}")
    print("\nPlease check:")
    print("1. Ollama is running: `ollama list`")
    print("2. Required model is installed: `ollama pull mistral-small:7b`")
    print("3. Environment variables are set correctly")
    print("4. No port conflicts exist")
    sys.exit(1)
