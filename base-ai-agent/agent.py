"""Base AI Agent with A2A communication to Google Search Agent."""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.function_tool import FunctionTool
from a2a.client import A2AClient
import httpx
import asyncio
import os

# Base instruction with A2A delegation capability
BASE_INSTRUCTION = """You are a helpful AI assistant running locally with Ollama.

You can:
1. Answer questions and have conversations using your knowledge - for greetings, general questions, coding help, explanations, etc.
2. ONLY when users explicitly ask for current information, recent news, web searches, or real-time data, use the search_google function

Important guidelines:
- For simple greetings like "hello", "hi", "how are you" - respond directly without using any tools
- For general knowledge questions - use your existing knowledge 
- For coding questions, explanations, creative tasks - respond directly
- ONLY use search_google when users specifically ask to "search for", "find current info about", "what's the latest news on", or similar search requests

Be friendly, helpful, and informative in your responses."""

async def search_google(query: str) -> str:
    """Search Google using the Google Search Agent via A2A protocol."""
    try:
        # Get the Google Search Agent URL from environment
        search_agent_base_url = os.getenv('GOOGLE_SEARCH_AGENT_URL', 'http://localhost:8001')
        
        async with httpx.AsyncClient(timeout=30.0) as httpx_client:
            # Create A2A client from agent card
            a2a_client = await A2AClient.get_client_from_agent_card_url(
                httpx_client=httpx_client,
                base_url=search_agent_base_url,
                agent_card_path='/.well-known/agent.json'
            )
            
            # Send search request to the Google Search Agent
            response = await a2a_client.send_message(query)
            
            return f"🔍 {response}"
        
    except Exception as e:
        return f"❌ Search failed: {str(e)}. Make sure the Google Search Agent is running on port 8001 and properly configured as an A2A server."

def create_base_agent() -> Agent:
    """Create a base agent with Ollama and search capability."""
    
    # Configure LiteLLM for Ollama
    litellm_model = LiteLlm(
        model="ollama_chat/llama3.1:8b",
        api_base="http://localhost:11434",
        temperature=0.7,
        max_tokens=2048,
    )
    
    # Create search tool
    search_tool = FunctionTool(search_google)
    
    # Create the main agent with search tool
    agent = Agent(
        model=litellm_model,
        name="base_ai_agent",
        description="A conversational AI assistant with search capabilities",
        instruction=BASE_INSTRUCTION,
        tools=[search_tool],
    )
    
    return agent

# Create the root agent for ADK
root_agent = create_base_agent()
