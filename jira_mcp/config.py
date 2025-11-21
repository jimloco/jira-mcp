#!/usr/bin/env python3.12
"""
Configuration Loading and Validation Utilities

Configuration management for the Jira MCP Server.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, Optional

# Handle non-UTF-8 locales - force UTF-8 for I/O
# This prevents UnicodeEncodeError on systems with Latin-1 or other encodings
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

# Reconfigure stdout/stderr to use UTF-8 with error handling
if sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8', errors='replace', line_buffering=True)

# Configure logging (level set by main application)
logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Custom exception for configuration errors."""


class ConfigManager:
    """
    Configuration management for Jira MCP Server.

    Handles loading, validation, and secure storage of configuration data.
    """

    def __init__(self, workspace_name: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            workspace_name: Optional workspace name for multi-workspace support.
                           If provided, loads .env.{workspace_name} instead of .env
        """
        if workspace_name:
            self.env_file_path = Path(f'.env.{workspace_name}')
        else:
            self.env_file_path = Path('.env')

    def load_existing_env(self) -> Dict[str, Optional[str]]:
        """
        Load existing .env configuration.

        Returns:
            Dictionary of configuration values from .env file

        Raises:
            ConfigurationError: If .env file cannot be read
        """
        try:
            from dotenv import dotenv_values  # pylint: disable=import-outside-toplevel
            return dict(dotenv_values(self.env_file_path))
        except Exception as error:
            raise ConfigurationError(
                f"Failed to load .env file: {str(error)}"
            ) from error


def load_config(workspace_name: Optional[str] = None) -> Dict[str, str]:
    """
    Convenience function to load configuration for application use.
    
    Args:
        workspace_name: Optional workspace name for multi-workspace support

    Returns:
        Dictionary of configuration values

    Raises:
        ConfigurationError: If configuration cannot be loaded
    """
    config_manager = ConfigManager(workspace_name=workspace_name)

    # For Phase 1, allow running without .env file
    if not config_manager.env_file_path.exists():
        logger.warning("⚠️  No .env file found - using default configuration")
        logger.warning("⚠️  Configure workspaces using jira_workspace(operation='add_workspace')")
        
        # Return default configuration for Phase 1
        return {
            'MCP_SERVER_NAME': 'jira-mcp',
            'MCP_SERVER_VERSION': '0.1.0',
            'DEBUG': 'false'
        }

    config = config_manager.load_existing_env()

    # Convert None values to empty strings for application use
    return {k: v or '' for k, v in config.items()}


def get_default_config() -> Dict[str, str]:
    """
    Get default configuration values.
    
    Returns:
        Dictionary with default configuration
    """
    return {
        'MCP_SERVER_NAME': 'jira-mcp',
        'MCP_SERVER_VERSION': '0.1.0',
        'DEBUG': 'false'
    }


if __name__ == "__main__":
    # Test the configuration manager
    print("🧪 Testing Configuration Manager...")

    try:
        config = load_config()
        print("✅ Configuration loaded successfully")
        print(f"📊 Server: {config.get('MCP_SERVER_NAME')} v{config.get('MCP_SERVER_VERSION')}")
    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
