"""Simplified Base AI Agent for testing."""

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm

# Simple instruction
SIMPLE_INSTRUCTION = """You are a helpful AI assistant. 
You can answer questions and have conversations.
Be friendly, helpful, and informative in your responses."""

def create_simple_agent() -> Agent:
    """Create a simple working agent."""
    
    # Configure LiteLLM for Ollama
    litellm_model = LiteLlm(
        model_name="ollama_chat/llama3.1:8b",
        api_base="http://localhost:11434",
        temperature=0.7,
        max_tokens=2048,
    )
    
    # Create the agent
    agent = Agent(
        model=litellm_model,
        name="simple_base_agent",
        description="A simple conversational AI assistant",
        instruction=SIMPLE_INSTRUCTION,
    )
    
    return agent

# Create the root agent for ADK
root_agent = create_simple_agent()
