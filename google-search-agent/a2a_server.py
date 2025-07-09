#!/usr/bin/env python3
"""Google Search Agent A2A Server."""

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from search_agent_executor import GoogleSearchAgentExecutor


def create_a2a_server():
    """Create and configure the A2A server for Google Search Agent."""
    
    # Define the search skill
    search_skill = AgentSkill(
        id='google_search',
        name='Google Search',
        description='Performs Google web searches and returns current information from the internet',
        tags=['search', 'web', 'google', 'current', 'internet'],
        examples=[
            'Search for artificial intelligence',
            'Find information about Python programming',
            'What is the latest news about climate change?',
            'Search for restaurant reviews in San Francisco'
        ],
    )
    
    # Define the agent card
    agent_card = AgentCard(
        name='Google Search Agent',
        description='Specialized agent for performing Google web searches and retrieving current information',
        url='http://localhost:8001/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[search_skill],
    )
    
    # Create the request handler
    request_handler = DefaultRequestHandler(
        agent_executor=GoogleSearchAgentExecutor(),
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
    print("🔍 Starting Google Search Agent A2A Server...")
    print("📋 Agent card will be available at: http://localhost:8001/.well-known/agent.json")
    
    server = create_a2a_server()
    uvicorn.run(server.build(), host='127.0.0.1', port=8001)


if __name__ == '__main__':
    main()
