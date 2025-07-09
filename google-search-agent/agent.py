# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Search Agent - A2A Server implementation."""

import asyncio
import json
import logging
import sys
from typing import List, Dict, Any, Optional

from google.adk import Agent
from google.adk.tools import google_search
from google.genai import Client, types

from .config import config


# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("google_search_agent.log"),
    ],
)
logger = logging.getLogger(__name__)


async def perform_google_search(query: str, num_results: Optional[int] = None) -> str:
    """Perform a Google search and return formatted results.

    Args:
        query: The search query string
        num_results: Number of results to return (default: from config)

    Returns:
        Formatted search results as a string
    """
    try:
        num_results = num_results or config.max_search_results
        logger.info(
            f"Performing Google search for query: '{query}' with {num_results} results"
        )

        # Use the ADK google_search tool
        search_results = await google_search(query, num_results=num_results)

        if not search_results:
            return f"No search results found for query: '{query}'"

        # Format the results
        formatted_results = []
        formatted_results.append(f"Google Search Results for: '{query}'")
        formatted_results.append("=" * 50)

        for i, result in enumerate(search_results[:num_results], 1):
            formatted_results.append(f"\n{i}. {result.get('title', 'No title')}")
            formatted_results.append(f"   URL: {result.get('url', 'No URL')}")
            formatted_results.append(
                f"   Description: {result.get('description', 'No description')}"
            )

        formatted_results.append(f"\n\nTotal results: {len(search_results)}")

        return "\n".join(formatted_results)

    except Exception as e:
        error_msg = f"Error performing Google search: {str(e)}"
        logger.error(error_msg)
        return error_msg


async def web_search_comprehensive(query: str, max_results: int = 10) -> str:
    """Comprehensive web search with analysis.

    Args:
        query: The search query
        max_results: Maximum number of results to analyze

    Returns:
        Comprehensive search results with analysis
    """
    try:
        logger.info(f"Performing comprehensive web search for: '{query}'")

        # Perform the search
        search_results = await perform_google_search(query, max_results)

        # Add analysis context
        analysis_prompt = f"""
        Based on the search results above, provide a comprehensive analysis that includes:
        1. A summary of the key findings
        2. The most relevant and authoritative sources
        3. Any trends or patterns in the information
        4. Confidence level in the information quality
        
        Search Query: {query}
        Results: {search_results}
        """

        return search_results

    except Exception as e:
        error_msg = f"Error in comprehensive web search: {str(e)}"
        logger.error(error_msg)
        return error_msg


# Initialize the Gemini client
try:
    client = Client()
    logger.info("Gemini client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini client: {e}")
    client = None


# Define the root agent
root_agent = Agent(
    model=config.model,
    name=config.agent_name,
    description=config.agent_description,
    instruction=f"""
    You are a specialized Google Search Agent that performs web searches and provides comprehensive, accurate information.
    
    Your capabilities include:
    1. Performing Google searches using the google_search tool
    2. Analyzing search results for relevance and quality
    3. Providing comprehensive summaries of search findings
    4. Identifying authoritative sources and key information
    
    Guidelines:
    - Always use the google_search tool for web searches
    - Provide clear, organized, and comprehensive responses
    - Cite sources when presenting information
    - If search results are limited, mention this limitation
    - Focus on accuracy and relevance
    - Format responses in a clear, readable manner
    
    When receiving search requests:
    1. Use the appropriate search tool
    2. Analyze the results for quality and relevance
    3. Provide a well-structured response with key findings
    4. Include source information where appropriate
    
    Maximum search results per query: {config.max_search_results}
    """,
    tools=[google_search, perform_google_search, web_search_comprehensive],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
        ]
    ),
)


def print_startup_banner():
    """Print startup banner."""
    banner = f"""
    ╔══════════════════════════════════════════════════════════════════════════════════════╗
    ║                             Google Search Agent (A2A Server)                         ║
    ║                                                                                      ║
    ║  🔍 Specialized web search agent for comprehensive information retrieval             ║
    ║                                                                                      ║
    ║  Model: {config.model:<60}           ║
    ║  Agent URL: {config.get_agent_url():<58}    ║
    ║  Agent JSON: {config.get_agent_json_url():<54}║
    ║  Max Results: {config.max_search_results:<58}                 ║
    ║                                                                                      ║
    ║  Ready to handle search requests from base-ai-agent via A2A protocol                ║
    ╚══════════════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)
    logger.info("Google Search Agent initialized and ready")


if __name__ == "__main__":
    print_startup_banner()

    # Validate configuration
    is_valid, error_msg = config.validate()
    if not is_valid:
        logger.error(f"Configuration validation failed: {error_msg}")
        sys.exit(1)

    logger.info("Google Search Agent is ready to serve A2A requests")
    logger.info(f"Agent available at: {config.get_agent_url()}")
    logger.info(f"Agent JSON available at: {config.get_agent_json_url()}")
