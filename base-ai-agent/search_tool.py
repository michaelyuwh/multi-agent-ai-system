"""Google Search tool for the base AI agent."""

import requests
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def google_search(query: str, num_results: int = 5) -> str:
    """
    Perform a Google search and return formatted results.
    
    Args:
        query: The search query string
        num_results: Number of results to return (default: 5, max: 10)
        
    Returns:
        Formatted search results as a string
    """
    
    # Get API credentials from environment
    api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
    search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
    
    if not api_key or not search_engine_id:
        return "❌ Google Search is not configured. Missing API key or Search Engine ID in environment variables."
    
    # Limit results to max 10
    num_results = min(num_results, 10)
    
    try:
        # Build the search URL
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': query,
            'num': num_results
        }
        
        # Make the search request
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        search_data = response.json()
        
        # Check if we got results
        if 'items' not in search_data:
            return f"🔍 No search results found for: {query}"
        
        # Format the results
        results = []
        results.append(f"🔍 **Google Search Results for: {query}**\n")
        
        for i, item in enumerate(search_data['items'], 1):
            title = item.get('title', 'No title')
            link = item.get('link', '')
            snippet = item.get('snippet', 'No description available')
            
            results.append(f"**{i}. {title}**")
            results.append(f"   🔗 {link}")
            results.append(f"   📝 {snippet}")
            results.append("")  # Empty line for spacing
        
        # Add search statistics if available
        if 'searchInformation' in search_data:
            search_info = search_data['searchInformation']
            total_results = search_info.get('totalResults', 'Unknown')
            search_time = search_info.get('searchTime', 'Unknown')
            results.append(f"📊 Found {total_results} results in {search_time} seconds")
        
        return "\n".join(results)
        
    except requests.exceptions.RequestException as e:
        return f"❌ Search request failed: {str(e)}"
    except Exception as e:
        return f"❌ Search error: {str(e)}"
