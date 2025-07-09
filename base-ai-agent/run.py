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

"""Runner script for Base AI Agent."""

import sys
import os

# Add the parent directory to the path to import shared modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_ai_agent.agent import root_agent
from shared.utils import logger


def main():
    """Main entry point for the Base AI Agent."""
    try:
        logger.info("Starting Base AI Agent...")
        logger.info("Agent ready for web interface")

        print("\n✅ Base AI Agent is ready!")
        print("🌐 Web interface will be available at: http://localhost:8000")
        print("🤖 Agent is configured with memory and A2A capabilities")
        print("\nTo start the web interface, use:")
        print("   uv run adk web --port 8000 --agents base_ai_agent.agent:root_agent")

    except Exception as e:
        logger.error(f"Failed to start Base AI Agent: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
