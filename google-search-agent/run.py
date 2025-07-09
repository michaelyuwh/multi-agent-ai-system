#!/usr/bin/env python3
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

"""Runner script for Google Search Agent A2A Server."""

import sys
import os

# Add the parent directory to the path to import shared modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_search_agent.agent import root_agent, print_startup_banner, config, logger


def main():
    """Main entry point for the Google Search Agent."""
    try:
        print_startup_banner()

        # Validate configuration
        is_valid, error_msg = config.validate()
        if not is_valid:
            logger.error(f"Configuration validation failed: {error_msg}")
            print(f"\n❌ Configuration Error: {error_msg}")
            print("\nPlease set the required environment variables:")
            print("- GOOGLE_SEARCH_API_KEY: Your Google Search API key")
            print("- GOOGLE_SEARCH_ENGINE_ID: Your Custom Search Engine ID")
            print(
                "\nGet these from: https://developers.google.com/custom-search/v1/overview"
            )
            sys.exit(1)

        logger.info("Starting Google Search Agent A2A Server...")
        logger.info(f"Server will be available at: {config.get_agent_url()}")
        logger.info(f"Agent card available at: {config.get_agent_json_url()}")

        # The agent will be served via the ADK framework
        print(f"\n✅ Google Search Agent is ready!")
        print(f"🌐 Agent URL: {config.get_agent_url()}")
        print(f"📋 Agent JSON: {config.get_agent_json_url()}")
        print(f"🔍 Max search results: {config.max_search_results}")
        print("\nTo start the A2A server, use:")
        print(
            f"   uv run adk a2a-server --port {config.port} --agents google_search_agent.agent:root_agent"
        )

    except Exception as e:
        logger.error(f"Failed to start Google Search Agent: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
