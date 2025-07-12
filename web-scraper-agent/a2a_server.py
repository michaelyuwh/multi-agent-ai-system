#!/usr/bin/env python3
"""Web Scraper Agent A2A Server."""

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from scraper_agent_executor import WebScraperAgentExecutor

def create_web_scraper_server():
    """Create and configure the A2A server for Web Scraper Agent."""
    
    # Define the scraping skill
    scraper_skill = AgentSkill(
        id='web_scraper',
        name='Web Content Scraper',
        description='Scrapes web content from URLs and provides intelligent summaries and analysis',
        tags=['scraping', 'web', 'content', 'summarization', 'analysis'],
        examples=[
            'Scrape https://example.com and summarize the content',
            'Extract and analyze content from these URLs: https://site1.com https://site2.com',
            'Get detailed content from https://news.com/article',
            'Scrape and summarize multiple web pages'
        ],
    )
    
    # Define the agent card
    agent_card = AgentCard(
        name='Web Scraper Agent',
        description='Specialized agent for scraping web content and providing intelligent summaries',
        url='http://localhost:8002/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=False),
        skills=[scraper_skill],
    )
    
    # Create the request handler
    request_handler = DefaultRequestHandler(
        agent_executor=WebScraperAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    
    # Create the A2A server
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    
    return server

def main():
    """Start the A2A server."""
    print("🌐 Starting Web Scraper Agent A2A Server...")
    print("📋 Agent card will be available at: http://localhost:8002/.well-known/agent.json")
    
    server = create_web_scraper_server()
    uvicorn.run(server.build(), host='127.0.0.1', port=8002)

if __name__ == "__main__":
    main()
