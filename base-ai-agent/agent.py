"""Base AI Agent with A2A communication to Google Search Agent and Web Scraper Agent."""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.function_tool import FunctionTool
from a2a.client import A2AClient
import httpx
import asyncio
import os
import re

# Base instruction with enhanced A2A delegation capability
BASE_INSTRUCTION = """You are a helpful AI assistant running locally with Ollama.

You can:
1. Answer questions and have conversations using your knowledge - for greetings, general questions, coding help, explanations, etc.
2. When users explicitly ask for current information, recent news, web searches, or real-time data, use the search_and_scrape function for comprehensive results
3. Use search_google for simple search results without content scraping

Important guidelines:
- For simple greetings like "hello", "hi", "how are you" - respond directly without using any tools
- For general knowledge questions - use your existing knowledge 
- For coding questions, explanations, creative tasks - respond directly
- For current information that needs web content: use search_and_scrape
- For simple searches: use search_google
- ONLY use search functions when users specifically ask to "search for", "find current info about", "what's the latest news on", or similar search requests

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

async def search_and_scrape(query: str) -> str:
    """Search Google and then scrape the top results for comprehensive information."""
    try:
        # Step 1: Perform Google search
        search_result = await search_google(query)
        
        # Step 2: Extract URLs from search results
        urls = _extract_urls_from_search_result(search_result)
        
        if not urls:
            return search_result + "\\n\\n⚠️ No URLs found for scraping. Search results only."
        
        # Step 3: Scrape the URLs using Web Scraper Agent
        scrape_result = await _scrape_urls(urls)
        
        # Step 4: Combine search and scrape results
        combined_result = f"{search_result}\\n\\n🌐 **Detailed Content Analysis:**\\n\\n{scrape_result}"
        
        return combined_result
        
    except Exception as e:
        return f"❌ Search and scrape failed: {str(e)}. Make sure both Google Search Agent (port 8001) and Web Scraper Agent (port 8002) are running."

def _extract_urls_from_search_result(search_result: str) -> list:
    """Extract URLs from search result text."""
    urls = []
    
    # Look for URLs in the search result
    url_pattern = r'https?://[^\\s<>"{}|\\\\^`\\[\\]]+'
    found_urls = re.findall(url_pattern, search_result)
    
    # Also look for SCRAPABLE_URLS section
    if "SCRAPABLE_URLS:" in search_result:
        lines = search_result.split("SCRAPABLE_URLS:")[1].strip().split('\\n')
        for line in lines:
            line = line.strip()
            if line and line.startswith('http'):
                urls.append(line)
    
    # Remove duplicates and limit to top 3
    unique_urls = list(dict.fromkeys(found_urls + urls))[:3]
    
    return unique_urls

async def _scrape_urls(urls: list) -> str:
    """Scrape URLs using the Web Scraper Agent via A2A protocol."""
    try:
        # Get the Web Scraper Agent URL from environment
        scraper_agent_base_url = os.getenv('WEB_SCRAPER_AGENT_URL', 'http://localhost:8002')
        
        async with httpx.AsyncClient(timeout=60.0) as httpx_client:  # Longer timeout for scraping
            # Create A2A client from agent card
            a2a_client = await A2AClient.get_client_from_agent_card_url(
                httpx_client=httpx_client,
                base_url=scraper_agent_base_url,
                agent_card_path='/.well-known/agent.json'
            )
            
            # Send scraping request with URLs
            urls_text = "Scrape these URLs:\\n" + "\\n".join(urls)
            response = await a2a_client.send_message(urls_text)
            
            return response
        
    except Exception as e:
        return f"❌ Web scraping failed: {str(e)}. Make sure the Web Scraper Agent is running on port 8002."

def create_base_agent() -> Agent:
    """Create a base agent with Ollama, search, and scraping capabilities."""
    
    # Configure LiteLLM for Ollama
    litellm_model = LiteLlm(
        model="ollama_chat/llama3.1:8b",
        api_base="http://localhost:11434",
        temperature=0.7,
        max_tokens=2048,
    )
    
    # Create tools
    search_tool = FunctionTool(search_google)
    search_and_scrape_tool = FunctionTool(search_and_scrape)
    
    # Create the main agent with both search and scraping tools
    agent = Agent(
        model=litellm_model,
        name="base_ai_agent",
        description="A conversational AI assistant with search and web scraping capabilities",
        instruction=BASE_INSTRUCTION,
        tools=[search_tool, search_and_scrape_tool],
    )
    
    return agent

# Create the root agent for ADK
root_agent = create_base_agent()
