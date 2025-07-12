"""Web Scraper Agent definition."""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

def create_web_scraper_agent() -> Agent:
    """Create a web scraper agent for local testing."""
    
    # Configure LiteLLM for Gemini
    litellm_model = LiteLlm(
        model="gemini-1.5-flash",
        temperature=0.3,
        max_tokens=2048,
    )
    
    instruction = """You are a web scraper agent that extracts and summarizes content from web pages.
    
    You can:
    1. Extract meaningful content from HTML pages
    2. Clean and process text content
    3. Provide intelligent summaries of scraped content
    4. Handle multiple URLs efficiently
    
    When provided with URLs, you will scrape the content and provide comprehensive summaries."""
    
    # Create the web scraper agent
    agent = Agent(
        model=litellm_model,
        name="web_scraper_agent",
        description="Web content scraper and summarizer",
        instruction=instruction,
    )
    
    return agent

# Create the root agent for ADK
root_agent = create_web_scraper_agent()
