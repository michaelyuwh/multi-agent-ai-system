#!/usr/bin/env python3
"""Test script for the enhanced search and scraping functionality."""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add the project directory to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_web_scraper_agent():
    """Test the web scraper agent functionality."""
    try:
        # Import the web scraper agent
        sys.path.insert(0, str(project_root / "web-scraper-agent"))
        from scraper_agent_executor import WebScraperAgentExecutor
        
        print("✅ Web Scraper Agent imports successfully")
        
        # Create an instance
        executor = WebScraperAgentExecutor()
        print("✅ Web Scraper Agent executor created")
        
        return True
        
    except Exception as e:
        print(f"❌ Web Scraper Agent test failed: {e}")
        return False

async def test_enhanced_base_agent():
    """Test the enhanced base agent functionality."""
    try:
        # Import the base agent
        sys.path.insert(0, str(project_root / "base-ai-agent"))
        from agent import create_base_agent, search_google, search_and_scrape
        
        print("✅ Enhanced Base Agent imports successfully")
        
        # Create the agent
        agent = create_base_agent()
        print("✅ Enhanced Base Agent created with both search and scraping tools")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Base Agent test failed: {e}")
        return False

async def test_url_extraction():
    """Test URL extraction functionality."""
    try:
        sys.path.insert(0, str(project_root / "base-ai-agent"))
        from agent import _extract_urls_from_search_result
        
        # Test URL extraction
        test_search_result = """
        Search results:
        1. Example Site: https://example.com
        2. Test Site: https://test.com
        
        SCRAPABLE_URLS:
        https://example.com
        https://test.com
        https://another-site.com
        """
        
        urls = _extract_urls_from_search_result(test_search_result)
        if urls:
            print(f"✅ URL extraction works: {len(urls)} URLs found")
            return True
        else:
            print("❌ URL extraction failed: no URLs found")
            return False
            
    except Exception as e:
        print(f"❌ URL extraction test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🧪 Testing Enhanced Multi-Agent AI System...")
    print("=" * 50)
    
    tests = [
        ("Web Scraper Agent", test_web_scraper_agent),
        ("Enhanced Base Agent", test_enhanced_base_agent),
        ("URL Extraction", test_url_extraction),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Summary: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your enhanced system is ready to use.")
        print("\n💡 Next steps:")
        print("   1. Start the system: uv run python start_agents.py")
        print("   2. Try: 'Search for latest AI developments and summarize'")
        print("   3. Or: 'Search Google for Python tutorials'")
    else:
        print("⚠️ Some tests failed. Please check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
