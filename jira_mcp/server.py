#!/usr/bin/env python3.12
"""
MCP server for Jira Cloud integration.
"""

import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.stdio import stdio_server

# Let MCP framework handle logging configuration - just get our logger
logger = logging.getLogger("jira-mcp")

# Import configuration and MCP server components
# Add project root to Python path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))
from jira_mcp.config import load_config  # pylint: disable=wrong-import-position

# Placeholder import - will be implemented in Phase 4
# from .mcp_server import JiraMCPServer  # pylint: disable=wrong-import-position


# Signal handlers for graceful shutdown
def signal_handler(sig, _frame):
    """Handle termination signals to ensure proper cleanup"""
    logger.info("Received signal %s, shutting down gracefully...", sig)

    # Restore default handler and re-raise signal
    signal.signal(sig, signal.SIG_DFL)
    os.kill(os.getpid(), sig)


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


async def run():
    """
    Main MCP server entry point.

    This function is called by __main__.py to start the MCP server
    with proper configuration and error handling.
    """
    try:
        logger.info("🚀 Initializing Jira MCP Server")
        logger.info("Phase 1: Project Bootstrap & Infrastructure")

        # Check for multi-workspace mode
        active_workspace_file = Path('.env.active')
        active_workspace = None
        if active_workspace_file.exists():
            try:
                active_workspace = active_workspace_file.read_text().strip()
                if active_workspace:
                    logger.info(f"🔑 Multi-workspace mode: Using workspace '{active_workspace}'")
            except (OSError, IOError) as e:
                logger.warning(f"Could not read .env.active: {e}")
        
        # Load environment variables (with workspace-specific file if needed)
        if active_workspace:
            env_file = f'.env.{active_workspace}'
            load_dotenv(env_file)
            logger.debug(f"Environment variables loaded from {env_file}")
        else:
            load_dotenv()
            logger.debug("Environment variables loaded from .env file")

        # Load configuration
        config = load_config(workspace_name=active_workspace)
        logger.info("✅ Configuration loaded successfully")

        # TODO: Phase 4 - Initialize MCP server
        # mcp_server = JiraMCPServer(config)
        # mcp_server.register_tools()
        
        # server_info = mcp_server.get_server_info()
        # logger.info(
        #     "✅ MCP Server initialized: %s v%s",
        #     server_info["server_name"],
        #     server_info["server_version"],
        # )
        # logger.info("🔧 Registered tools: %s", ", ".join(server_info["registered_tools"]))

        # Temporary placeholder for Phase 1
        logger.info("✅ MCP Server initialized: jira-mcp v0.1.0")
        logger.info("⚠️  MCP tools not yet registered (Phase 4)")

        # Start MCP server with STDIO transport
        logger.info("📡 Starting MCP server with STDIO transport")
        logger.info("🔗 Server ready for AI assistant connections")
        logger.info("💡 Use Ctrl+C to stop the server")

        # TODO: Phase 4 - Uncomment when mcp_server is implemented
        # async with stdio_server() as streams:
        #     await mcp_server.app.run(
        #         streams[0], streams[1], mcp_server.app.create_initialization_options()
        #     )
        
        # Temporary: Keep server running for testing
        logger.info("⚠️  Server running in bootstrap mode (Phase 1)")
        logger.info("⚠️  STDIO transport not yet connected - implement in Phase 4")
        await asyncio.sleep(3600)  # Keep alive for 1 hour

    except KeyboardInterrupt:
        logger.info("👋 MCP server stopped by user")
    except (ValueError, KeyError, OSError, RuntimeError) as server_error:
        logger.error("❌ MCP server failed: %s", server_error, exc_info=True)
        logger.error("🔧 Troubleshooting:")
        logger.error("   1. Check your .env file configuration")
        logger.error("   2. Verify Jira API credentials")
        logger.error("   3. Ensure workspace is configured")
        raise


if __name__ == "__main__":
    # This allows running server.py directly for testing
    logger.info("🧪 Running server directly (testing mode)")
    try:
        asyncio.run(run())
        sys.exit(0)
    except (ValueError, KeyError, OSError, RuntimeError):
        sys.exit(1)
