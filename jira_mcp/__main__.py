#!/usr/bin/env python3.12
"""
Main entry point for the Jira MCP package.
"""

import os
import sys
import logging
import asyncio
import argparse
from .server import run

# Let MCP framework handle logging configuration - just get our logger
logger = logging.getLogger("jira-mcp")
logger.setLevel(logging.INFO)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Jira MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m jira_mcp              # Run with stdio transport
  python -m jira_mcp --debug      # Run with debug logging

This MCP server provides tools for interacting with Jira Cloud:
- jira_workspace: Workspace management and connectivity testing
- jira_issues: Issue CRUD, search, comments, attachments, links
- jira_projects: Project discovery and metadata
        """,
    )

    # Transport type (currently only stdio, but future-ready)
    parser.add_argument(
        "--transport",
        choices=["stdio"],
        default="stdio",
        help="Transport type to use (currently only stdio)",
    )

    # Debug mode
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    return parser.parse_args()


async def main():
    """Main entry point for the Jira MCP package."""
    try:
        args = parse_args()

        # Set debug logging if requested
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Debug logging enabled")
            # Also set debug in environment for other modules
            os.environ["DEBUG"] = "true"

        logger.info("🚀 Starting Jira MCP Server")
        logger.info("📡 Transport: %s", args.transport)

        # Run the MCP server
        await run()

    except KeyboardInterrupt:
        logger.info("👋 Shutdown requested by user")
        sys.exit(0)
    except (ValueError, KeyError, OSError, RuntimeError) as error:
        logger.error("❌ Fatal error: %s", error, exc_info=True)
        sys.exit(1)


def run_main():
    """
    Synchronous wrapper for the async main function.
    This function is used as the entry point for the console script.
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handle KeyboardInterrupt gracefully
        logger.info("👋 Server stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    run_main()
