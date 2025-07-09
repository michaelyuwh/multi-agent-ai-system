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

"""MCP (Model Context Protocol) integration utilities."""

import logging
import os
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class MCPConfiguration:
    """Configuration manager for MCP servers and tools."""

    def __init__(self):
        self.enabled_servers = []
        self.tool_filters = {}

    def add_filesystem_server(
        self, allowed_path: str, tools: Optional[List[str]] = None
    ):
        """Add a filesystem MCP server configuration.

        Args:
            allowed_path: Path that the filesystem server can access
            tools: List of allowed tools (None for all safe tools)
        """
        if tools is None:
            tools = [
                "read_file",
                "read_multiple_files",
                "list_directory",
                "directory_tree",
                "search_files",
                "get_file_info",
            ]

        server_config = {
            "type": "filesystem",
            "allowed_path": allowed_path,
            "tools": tools,
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", allowed_path],
        }

        self.enabled_servers.append(server_config)
        logger.info(f"Added filesystem MCP server for path: {allowed_path}")

    def add_custom_server(
        self,
        server_type: str,
        command: str,
        args: List[str],
        tools: Optional[List[str]] = None,
    ):
        """Add a custom MCP server configuration.

        Args:
            server_type: Type identifier for the server
            command: Command to run the server
            args: Arguments for the command
            tools: List of allowed tools
        """
        server_config = {
            "type": server_type,
            "command": command,
            "args": args,
            "tools": tools or [],
        }

        self.enabled_servers.append(server_config)
        logger.info(f"Added custom MCP server: {server_type}")

    def get_toolsets(self):
        """Get configured MCP toolsets for agent integration.

        Returns:
            List of MCPToolset objects ready for agent integration
        """
        toolsets = []

        try:
            from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
            from mcp import StdioServerParameters

            for server in self.enabled_servers:
                connection_params = StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command=server["command"], args=server["args"]
                    ),
                    timeout=5,
                )

                toolset = MCPToolset(
                    connection_params=connection_params, tool_filter=server.get("tools")
                )

                toolsets.append(toolset)
                logger.info(f"Created MCP toolset for {server['type']}")

        except ImportError as e:
            logger.warning(f"MCP tools not available: {e}")
            logger.info("Install MCP support with: uv add mcp 'google-adk[mcp]'")

        return toolsets


def create_default_mcp_config() -> MCPConfiguration:
    """Create a default MCP configuration with safe filesystem access.

    Returns:
        MCPConfiguration with default settings
    """
    config = MCPConfiguration()

    # Add current working directory access (read-only)
    current_dir = os.getcwd()
    config.add_filesystem_server(
        allowed_path=current_dir,
        tools=[
            "read_file",
            "list_directory",
            "directory_tree",
            "search_files",
            "get_file_info",
        ],
    )

    return config


def validate_mcp_dependencies() -> bool:
    """Validate that MCP dependencies are available.

    Returns:
        True if MCP dependencies are available, False otherwise
    """
    try:
        import mcp
        from google.adk.tools.mcp_tool import MCPToolset

        return True
    except ImportError:
        logger.warning("MCP dependencies not found")
        logger.info("Install with: uv add mcp 'google-adk[mcp]'")
        return False


# Future: Add more MCP server types
# - Database MCP servers
# - Git MCP servers
# - Custom API MCP servers
# - Notion MCP servers
# - etc.
