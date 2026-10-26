"""Lightweight connection handling for MCP servers (mcp Python SDK 2.x)."""

from abc import ABC, abstractmethod
from contextlib import AsyncExitStack
from typing import Any

import httpx2
from mcp import Client, StdioServerParameters
from mcp.client import Transport
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamable_http_client
from mcp.types import CallToolResult


class MCPConnection(ABC):
    """Base class for MCP server connections."""

    def __init__(self):
        self.client: Client | None = None
        self._stack: AsyncExitStack | None = None

    @abstractmethod
    async def _create_target(self, stack: AsyncExitStack) -> StdioServerParameters | Transport:
        """Return what `mcp.Client` should connect to for this connection type."""

    async def __aenter__(self):
        """Connect to the MCP server. `Client` probes `server/discover` and falls back to `initialize`."""
        self._stack = AsyncExitStack()
        await self._stack.__aenter__()

        try:
            target = await self._create_target(self._stack)
            self.client = await self._stack.enter_async_context(Client(target))
            return self
        except BaseException:
            await self._stack.__aexit__(None, None, None)
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up MCP server connection resources."""
        if self._stack:
            await self._stack.__aexit__(exc_type, exc_val, exc_tb)
        self.client = None
        self._stack = None

    async def list_tools(self) -> list[dict[str, Any]]:
        """Retrieve available tools from the MCP server."""
        response = await self.client.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
            for tool in response.tools
        ]

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> CallToolResult:
        """Call a tool on the MCP server with provided arguments."""
        return await self.client.call_tool(tool_name, arguments)


class MCPConnectionStdio(MCPConnection):
    """MCP connection using standard input/output."""

    def __init__(self, command: str, args: list[str] | None = None, env: dict[str, str] | None = None):
        super().__init__()
        self.command = command
        self.args = args or []
        self.env = env

    async def _create_target(self, stack: AsyncExitStack) -> StdioServerParameters:
        return StdioServerParameters(command=self.command, args=self.args, env=self.env)


class MCPConnectionSSE(MCPConnection):
    """MCP connection using the deprecated HTTP+SSE transport (legacy servers only)."""

    def __init__(self, url: str, headers: dict[str, str] | None = None):
        super().__init__()
        self.url = url
        self.headers = headers or {}

    async def _create_target(self, stack: AsyncExitStack) -> Transport:
        return sse_client(url=self.url, headers=self.headers)


class MCPConnectionHTTP(MCPConnection):
    """MCP connection using Streamable HTTP."""

    def __init__(self, url: str, headers: dict[str, str] | None = None):
        super().__init__()
        self.url = url
        self.headers = headers or {}

    async def _create_target(self, stack: AsyncExitStack) -> Transport:
        http_client = await stack.enter_async_context(
            httpx2.AsyncClient(headers=self.headers, timeout=httpx2.Timeout(30, read=300))
        )
        return streamable_http_client(self.url, http_client=http_client)


def create_connection(
    transport: str,
    command: str | None = None,
    args: list[str] | None = None,
    env: dict[str, str] | None = None,
    url: str | None = None,
    headers: dict[str, str] | None = None,
) -> MCPConnection:
    """Factory function to create the appropriate MCP connection.

    Args:
        transport: Connection type ("stdio", "sse", or "http")
        command: Command to run (stdio only)
        args: Command arguments (stdio only)
        env: Extra environment variables for the server process (stdio only).
            The SDK passes only HOME, LOGNAME, PATH, SHELL, TERM and USER by default.
        url: Server URL (sse and http only)
        headers: HTTP headers (sse and http only)

    Returns:
        MCPConnection instance
    """
    transport = transport.lower()

    if transport == "stdio":
        if not command:
            raise ValueError("Command is required for stdio transport")
        return MCPConnectionStdio(command=command, args=args, env=env)

    elif transport == "sse":
        if not url:
            raise ValueError("URL is required for sse transport")
        return MCPConnectionSSE(url=url, headers=headers)

    elif transport in ["http", "streamable_http", "streamable-http"]:
        if not url:
            raise ValueError("URL is required for http transport")
        return MCPConnectionHTTP(url=url, headers=headers)

    else:
        raise ValueError(f"Unsupported transport type: {transport}. Use 'stdio', 'sse', or 'http'")
