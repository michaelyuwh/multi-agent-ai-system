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

"""Configuration for Google Search Agent."""

import os
from typing import Optional


class GoogleSearchConfig:
    """Configuration for Google Search Agent."""

    def __init__(self):
        # Server configuration
        self.host = os.getenv("GOOGLE_SEARCH_AGENT_HOST", "localhost")
        self.port = int(os.getenv("GOOGLE_SEARCH_AGENT_PORT", "8001"))
        self.debug = os.getenv("GOOGLE_SEARCH_AGENT_DEBUG", "false").lower() == "true"

        # Agent configuration
        self.agent_name = "google_search_agent"
        self.agent_description = "A specialized agent for performing Google search queries and providing comprehensive search results."
        self.agent_version = "1.0.0"

        # Model configuration
        self.model = os.getenv("GOOGLE_SEARCH_AGENT_MODEL", "gemini-2.0-flash-001")

        # Google Search API configuration
        self.google_search_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.google_search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

        # Search configuration
        self.max_search_results = int(os.getenv("MAX_SEARCH_RESULTS", "10"))
        self.search_timeout = int(os.getenv("SEARCH_TIMEOUT", "30"))

        # Logging configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate configuration."""
        if not self.google_search_api_key:
            return False, "GOOGLE_SEARCH_API_KEY is required"
        if not self.google_search_engine_id:
            return False, "GOOGLE_SEARCH_ENGINE_ID is required"
        return True, None

    def get_agent_url(self) -> str:
        """Get the agent URL."""
        return f"http://{self.host}:{self.port}/a2a/{self.agent_name}"

    def get_agent_json_url(self) -> str:
        """Get the agent.json URL."""
        return f"{self.get_agent_url()}/.well-known/agent.json"


# Global configuration instance
config = GoogleSearchConfig()
