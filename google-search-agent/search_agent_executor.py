"""Google Search Agent Executor for A2A communication."""

import asyncio
import logging
import os
from typing import Any

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from googleapiclient.discovery import build
from google.adk.models.lite_llm import LiteLlm

logger = logging.getLogger(__name__)


class GoogleSearchAgentExecutor(AgentExecutor):
    """Agent executor for Google Search functionality."""
    
    def __init__(self):
        """Initialize the Google Search Agent Executor."""
        self.search_api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
        if not self.search_api_key or not self.search_engine_id:
            logger.warning("Google Search API credentials not found. Agent will return error messages.")
        
        # Initialize Gemini model for processing search results
        self.model = LiteLlm(
            model="gemini-1.5-flash",
            temperature=0.3,
            max_tokens=1024,
        )
    
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Execute the search request."""
        try:
            # Extract the search query from the request
            query = self._extract_search_query(context)
            
            if not query:
                await event_queue.enqueue_event(
                    new_agent_text_message("❌ No search query provided. Please specify what you want to search for.")
                )
                return
            
            # Perform the search
            search_results = await self._perform_google_search(query)
            
            # Process and format the results
            formatted_response = await self._format_search_results(query, search_results)
            
            # Send the response
            await event_queue.enqueue_event(new_agent_text_message(formatted_response))
            
        except Exception as e:
            logger.error(f"Error in search execution: {e}")
            await event_queue.enqueue_event(
                new_agent_text_message(f"❌ Search failed: {str(e)}")
            )
    
    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """Cancel the search operation."""
        await event_queue.enqueue_event(
            new_agent_text_message("🛑 Search operation cancelled.")
        )
    
    def _extract_search_query(self, context: RequestContext) -> str:
        """Extract the search query from the request context."""
        # Get the last message from the user
        if hasattr(context, 'messages') and context.messages:
            last_message = context.messages[-1]
            if hasattr(last_message, 'parts'):
                for part in last_message.parts:
                    if hasattr(part, 'text'):
                        text = part.text.strip()
                        # Remove common prefixes
                        prefixes = ["search for:", "search for", "find:", "find", "look up:", "look up"]
                        for prefix in prefixes:
                            if text.lower().startswith(prefix.lower()):
                                return text[len(prefix):].strip()
                        return text
        
        # Fallback: check for task description
        if hasattr(context, 'task') and context.task:
            if hasattr(context.task, 'description'):
                return context.task.description.strip()
        
        return ""
    
    async def _perform_google_search(self, query: str) -> list[dict[str, Any]]:
        """Perform the actual Google search."""
        if not self.search_api_key or not self.search_engine_id:
            return []
        
        try:
            # Build the search service
            service = build("customsearch", "v1", developerKey=self.search_api_key)
            
            # Execute the search
            result = service.cse().list(
                q=query,
                cx=self.search_engine_id,
                num=5  # Get top 5 results
            ).execute()
            
            # Extract relevant information
            search_results = []
            if 'items' in result:
                for item in result['items']:
                    search_results.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'displayLink': item.get('displayLink', '')
                    })
            
            return search_results
            
        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return []
    
    async def _format_search_results(self, query: str, results: list[dict[str, Any]]) -> str:
        """Format the search results using Gemini."""
        if not results:
            return f"🔍 No search results found for '{query}'. This might be due to API configuration issues or the query being too specific."
        
        # Format results for processing
        results_text = f"Search query: {query}\\n\\nSearch results:\\n"
        for i, result in enumerate(results, 1):
            results_text += f"\\n{i}. **{result['title']}**\\n"
            results_text += f"   URL: {result['link']}\\n"
            results_text += f"   {result['snippet']}\\n"
        
        try:
            # Use Gemini to summarize and format the results
            prompt = f"""You are a helpful search assistant. Summarize these search results in a clear, informative way:

{results_text}

Please provide:
1. A brief summary of what was found
2. Key information from the search results
3. The most relevant links

Format your response to be helpful and easy to read.

IMPORTANT: At the end, include a section called "SCRAPABLE_URLS:" followed by the URLs that would be good for web scraping to get more detailed information. List each URL on a new line."""

            response = await asyncio.to_thread(
                self.model.completion,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract the response text
            if hasattr(response, 'choices') and response.choices:
                formatted_result = response.choices[0].message.content
                return f"🔍 **Search Results for '{query}':**\\n\\n{formatted_result}"
            else:
                # Fallback to simple formatting
                return self._simple_format_results(query, results)
                
        except Exception as e:
            logger.error(f"Error formatting results with Gemini: {e}")
            return self._simple_format_results(query, results)
    
    def _simple_format_results(self, query: str, results: list[dict[str, Any]]) -> str:
        """Simple fallback formatting for search results."""
        formatted = f"🔍 **Search Results for '{query}':**\\n\\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"**{i}. {result['title']}**\\n"
            formatted += f"🔗 {result['link']}\\n"
            formatted += f"📄 {result['snippet']}\\n\\n"
        
        # Add scrapable URLs section
        formatted += "\\n**SCRAPABLE_URLS:**\\n"
        for result in results[:3]:  # Limit to top 3 URLs
            formatted += f"{result['link']}\\n"
        
        return formatted
