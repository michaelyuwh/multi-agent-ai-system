"""Base AI Agent with A2A communication to Google Search Agent and Web Scraper Agent."""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.function_tool import FunctionTool
from a2a.client import A2AClient
import httpx
import asyncio
import os
import re

# Base instruction with intelligent search capability
BASE_INSTRUCTION = """You are a helpful AI assistant with access to current web information.

IMPORTANT: Always respond directly to users in natural, conversational language. Never expose function calls, tool names, or technical details to users.

Your capabilities:
1. Answer general questions using your knowledge for topics like coding, explanations, mathematics, etc.
2. Automatically search the web when you need current information, recent news, or specific data
3. Provide comprehensive answers by combining your knowledge with current web information

Guidelines:
- For simple greetings like "hello", "hi", "how are you" - respond directly in a friendly, conversational manner without using any tools
- For general knowledge questions that don't require current information - use your existing knowledge and respond naturally
- For questions about current events, recent developments, stock prices, weather, news, or when you're unsure about recent information - use the web_search function but present the results naturally to the user
- Always provide helpful, informative responses in plain, conversational text
- Never show function calls, JSON responses, or technical details to users
- When you search the web, integrate the information smoothly into your response

Response Format Rules:
- Respond directly to users with natural language
- Never output function call syntax like {"type":"function","function":{"name":"..."}}
- Never mention tool names like "web_search" or "base_ai_agent_response" in your responses
- For greetings, respond immediately with something like "Hello! How can I help you today?\""""

async def web_search(query: str) -> str:
    """Search the web for current information and scrape relevant content automatically."""
    try:
        # Step 1: Perform Google search
        search_result = await _search_google_internal(query)
        
        # Step 2: Extract URLs from search results
        urls = _extract_urls_from_search_result(search_result)
        
        if not urls:
            return search_result
        
        # Step 3: Scrape the URLs using Web Scraper Agent
        scrape_result = await _scrape_urls_internal(urls)
        
        # Step 4: Combine and format results
        combined_result = f"{search_result}\n\n🌐 **Detailed Content Analysis:**\n\n{scrape_result}"
        
        return combined_result
        
    except Exception as e:
        return f"❌ Search failed: {str(e)}. Unable to retrieve current information from the web."

async def _search_google_internal(query: str) -> str:
    """Internal function to search Google using the Google Search Agent via A2A protocol."""
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
            
            # Extract content from A2A response - handle different response formats
            if hasattr(response, 'content') and response.content:
                return response.content
            elif hasattr(response, 'text') and response.text:
                return response.text
            elif isinstance(response, str):
                return response
            elif hasattr(response, 'choices') and response.choices:
                # Handle OpenAI-style response
                return response.choices[0].message.content
            elif hasattr(response, 'messages') and response.messages:
                # Handle messages list
                content = ""
                for msg in response.messages:
                    if hasattr(msg, 'content'):
                        content += msg.content
                    elif hasattr(msg, 'text'):
                        content += msg.text
                return content
            else:
                # Last resort - convert to string
                return str(response)
        
    except Exception as e:
        return f"❌ Search failed: {str(e)}. Make sure the Google Search Agent is running on port 8001."

async def _scrape_urls_internal(urls: list) -> str:
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
            urls_text = "Scrape these URLs:\n" + "\n".join(urls)
            response = await a2a_client.send_message(urls_text)
            
            # Extract content from A2A response - handle different response formats
            if hasattr(response, 'content') and response.content:
                return response.content
            elif hasattr(response, 'text') and response.text:
                return response.text
            elif isinstance(response, str):
                return response
            elif hasattr(response, 'choices') and response.choices:
                # Handle OpenAI-style response
                return response.choices[0].message.content
            elif hasattr(response, 'messages') and response.messages:
                # Handle messages list
                content = ""
                for msg in response.messages:
                    if hasattr(msg, 'content'):
                        content += msg.content
                    elif hasattr(msg, 'text'):
                        content += msg.text
                return content
            else:
                # Last resort - convert to string
                return str(response)
        
    except Exception as e:
        return f"❌ Web scraping failed: {str(e)}. Make sure the Web Scraper Agent is running on port 8002."

def _extract_urls_from_search_result(search_result: str) -> list:
    """Extract URLs from search result text."""
    urls = []
    
    # Look for URLs in the search result
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    found_urls = re.findall(url_pattern, search_result)
    
    # Also look for SCRAPABLE_URLS section
    if "SCRAPABLE_URLS:" in search_result:
        lines = search_result.split("SCRAPABLE_URLS:")[1].strip().split('\n')
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
            urls_text = "Scrape these URLs:\n" + "\n".join(urls)
            response = await a2a_client.send_message(urls_text)
            
            # Extract content from A2A response - handle different response formats
            if hasattr(response, 'content') and response.content:
                return response.content
            elif hasattr(response, 'text') and response.text:
                return response.text
            elif isinstance(response, str):
                return response
            elif hasattr(response, 'choices') and response.choices:
                # Handle OpenAI-style response
                return response.choices[0].message.content
            elif hasattr(response, 'messages') and response.messages:
                # Handle messages list
                content = ""
                for msg in response.messages:
                    if hasattr(msg, 'content'):
                        content += msg.content
                    elif hasattr(msg, 'text'):
                        content += msg.text
                return content
            else:
                # Last resort - convert to string
                return str(response)
        
    except Exception as e:
        return f"❌ Web scraping failed: {str(e)}. Make sure the Web Scraper Agent is running on port 8002."

def create_base_agent() -> Agent:
    """Create a base agent with intelligent web search capabilities."""
    
    # Configure LiteLLM for Ollama
    litellm_model = LiteLlm(
        model="ollama_chat/llama3.1:8b",
        api_base="http://localhost:11434",
        temperature=0.7,
        max_tokens=2048,
    )
    
    # Create tool for web search
    web_search_tool = FunctionTool(web_search)
    
    # Create the main agent with web search capability
    agent = Agent(
        model=litellm_model,
        name="base_ai_agent",
        description="A conversational AI assistant with intelligent web search capabilities",
        instruction=BASE_INSTRUCTION,
        tools=[web_search_tool],
    )
    
    return agent

# Create the root agent for ADK
root_agent = create_base_agent()
