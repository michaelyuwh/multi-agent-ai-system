"""Web Scraper Agent Executor for A2A communication."""

import asyncio
import logging
import os
import re
from typing import Any, List
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.models.lite_llm import LiteLlm

logger = logging.getLogger(__name__)


class WebScraperAgentExecutor(AgentExecutor):
    """Agent executor for web scraping and content summarization."""
    
    def __init__(self):
        """Initialize the Web Scraper Agent Executor."""
        # Initialize Gemini model for content processing
        self.model = LiteLlm(
            model="gemini-1.5-flash",
            temperature=0.3,
            max_tokens=2048,
        )
        
        # Configuration
        self.max_content_length = 10000  # Maximum content length to process
        self.timeout = 10  # Request timeout in seconds
        self.max_urls = 3  # Maximum number of URLs to scrape
        
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Execute the web scraping request."""
        try:
            # Extract URLs from the request
            urls = self._extract_urls(context)
            
            if not urls:
                await event_queue.enqueue_event(
                    new_agent_text_message("❌ No URLs provided for scraping. Please provide URLs to scrape.")
                )
                return
            
            # Limit number of URLs to scrape
            if len(urls) > self.max_urls:
                urls = urls[:self.max_urls]
                await event_queue.enqueue_event(
                    new_agent_text_message(f"📝 Limiting to first {self.max_urls} URLs for performance...")
                )
            
            # Scrape the URLs
            scraped_results = await self._scrape_urls(urls)
            
            # Process and summarize the content
            if scraped_results:
                summary = await self._summarize_content(scraped_results)
                await event_queue.enqueue_event(new_agent_text_message(summary))
            else:
                await event_queue.enqueue_event(
                    new_agent_text_message("❌ Failed to scrape any content from the provided URLs.")
                )
            
        except Exception as e:
            logger.error(f"Error in web scraping execution: {e}")
            await event_queue.enqueue_event(
                new_agent_text_message(f"❌ Web scraping failed: {str(e)}")
            )
    
    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """Cancel the scraping operation."""
        await event_queue.enqueue_event(
            new_agent_text_message("🛑 Web scraping operation cancelled.")
        )
    
    def _extract_urls(self, context: RequestContext) -> List[str]:
        """Extract URLs from the request context."""
        urls = []
        
        # Get the last message from the user
        if hasattr(context, 'messages') and context.messages:
            last_message = context.messages[-1]
            if hasattr(last_message, 'parts'):
                for part in last_message.parts:
                    if hasattr(part, 'text'):
                        text = part.text.strip()
                        # Extract URLs using regex
                        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
                        found_urls = re.findall(url_pattern, text)
                        urls.extend(found_urls)
        
        # Fallback: check for task description
        if not urls and hasattr(context, 'task') and context.task:
            if hasattr(context.task, 'description'):
                text = context.task.description.strip()
                url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
                found_urls = re.findall(url_pattern, text)
                urls.extend(found_urls)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        return unique_urls
    
    async def _scrape_urls(self, urls: List[str]) -> List[dict]:
        """Scrape content from the provided URLs."""
        results = []
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={'User-Agent': 'Mozilla/5.0 (compatible; WebScraperBot/1.0)'}
        ) as session:
            
            for url in urls:
                try:
                    logger.info(f"Scraping URL: {url}")
                    
                    async with session.get(url) as response:
                        if response.status == 200:
                            content_type = response.headers.get('content-type', '').lower()
                            
                            # Only process HTML content
                            if 'text/html' in content_type:
                                html_content = await response.text()
                                extracted_content = self._extract_content(html_content, url)
                                
                                if extracted_content:
                                    results.append({
                                        'url': url,
                                        'title': extracted_content['title'],
                                        'content': extracted_content['content'],
                                        'status': 'success'
                                    })
                                else:
                                    results.append({
                                        'url': url,
                                        'status': 'failed',
                                        'error': 'Failed to extract meaningful content'
                                    })
                            else:
                                results.append({
                                    'url': url,
                                    'status': 'skipped',
                                    'error': f'Unsupported content type: {content_type}'
                                })
                        else:
                            results.append({
                                'url': url,
                                'status': 'failed',
                                'error': f'HTTP {response.status}'
                            })
                            
                except Exception as e:
                    logger.error(f"Error scraping {url}: {e}")
                    results.append({
                        'url': url,
                        'status': 'failed',
                        'error': str(e)
                    })
        
        return results
    
    def _extract_content(self, html_content: str, url: str) -> dict:
        """Extract meaningful content from HTML."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script, style, and other unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'ads']):
                element.decompose()
            
            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else urlparse(url).netloc
            
            # Try to find main content areas
            content_selectors = [
                'main', 'article', '.content', '#content', '.post', '.entry-content',
                '.article-body', '.story-body', '.post-content', '.entry', '.text'
            ]
            
            content_element = None
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    break
            
            # If no specific content area found, use body
            if not content_element:
                content_element = soup.find('body')
            
            if not content_element:
                return None
            
            # Extract text content
            content_text = content_element.get_text(separator=' ', strip=True)
            
            # Clean up the text
            content_text = re.sub(r'\s+', ' ', content_text)  # Normalize whitespace
            content_text = content_text.strip()
            
            # Limit content length
            if len(content_text) > self.max_content_length:
                content_text = content_text[:self.max_content_length] + "..."
            
            if len(content_text) < 100:  # Too short to be meaningful
                return None
            
            return {
                'title': title,
                'content': content_text
            }
            
        except Exception as e:
            logger.error(f"Error extracting content: {e}")
            return None
    
    async def _summarize_content(self, scraped_results: List[dict]) -> str:
        """Summarize the scraped content using Gemini."""
        try:
            # Prepare content for summarization
            content_for_summary = "Web scraping results:\n\n"
            
            successful_scrapes = [r for r in scraped_results if r.get('status') == 'success']
            failed_scrapes = [r for r in scraped_results if r.get('status') != 'success']
            
            # Add successful scrapes
            for i, result in enumerate(successful_scrapes, 1):
                content_for_summary += f"{i}. **{result['title']}**\n"
                content_for_summary += f"   URL: {result['url']}\n"
                content_for_summary += f"   Content: {result['content'][:1000]}...\n\n"
            
            # Add failed scrapes summary
            if failed_scrapes:
                content_for_summary += "\nFailed to scrape:\n"
                for result in failed_scrapes:
                    content_for_summary += f"- {result['url']}: {result.get('error', 'Unknown error')}\n"
            
            if not successful_scrapes:
                return "❌ Failed to extract content from any of the provided URLs."
            
            # Create prompt for Gemini
            prompt = f"""You are a web content summarizer. Analyze the following scraped web content and provide a comprehensive summary:

{content_for_summary}

Please provide:
1. A brief overview of the main topics covered
2. Key insights and important information from each source
3. A synthesis of the information across all sources
4. Relevant conclusions or takeaways

Format your response to be clear, informative, and well-structured with appropriate headings."""

            response = await asyncio.to_thread(
                self.model.completion,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract the response text
            if hasattr(response, 'choices') and response.choices:
                summary = response.choices[0].message.content
                
                # Add source information
                sources_info = "\n\n📋 **Sources:**\n"
                for i, result in enumerate(successful_scrapes, 1):
                    sources_info += f"{i}. [{result['title']}]({result['url']})\n"
                
                return f"🌐 **Web Content Summary:**\n\n{summary}{sources_info}"
            else:
                return self._simple_summary(successful_scrapes)
                
        except Exception as e:
            logger.error(f"Error creating summary with Gemini: {e}")
            return self._simple_summary(successful_scrapes)
    
    def _simple_summary(self, results: List[dict]) -> str:
        """Simple fallback summary without AI processing."""
        summary = "🌐 **Web Content Summary:**\n\n"
        
        for i, result in enumerate(results, 1):
            summary += f"**{i}. {result['title']}**\n"
            summary += f"🔗 {result['url']}\n"
            # Show first 300 characters of content
            content_preview = result['content'][:300] + "..." if len(result['content']) > 300 else result['content']
            summary += f"📄 {content_preview}\n\n"
        
        return summary
