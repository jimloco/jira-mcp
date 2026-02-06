#!/usr/bin/env python3.12
"""
Multi-Workspace Management for Jira MCP Server

Manages multiple Jira Cloud workspace configurations with context switching support.
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Configure logging
logger = logging.getLogger(__name__)


class WorkspaceError(Exception):
    """Custom exception for workspace-related errors."""


class WorkspaceManager:
    """
    Multi-workspace manager for Jira MCP Server.

    Handles workspace registration, switching, and credential management for
    multiple Jira Cloud instances.
    """

    def __init__(self):
        """Initialize workspace manager."""
        # Workspace storage paths - use XDG config directory
        config_home = Path.home() / '.config' / 'jira-mcp'
        self.accounts_dir = config_home / 'workspaces'
        self.active_workspace_file = config_home / 'active_workspace'

        # Workspace registry (workspace_name -> metadata)
        self._workspace_registry: Dict[str, Dict[str, Any]] = {}

        # Active workspace state
        self._active_workspace_name: Optional[str] = None

        # Ensure config directories exist
        self.accounts_dir.mkdir(parents=True, exist_ok=True)

        # Load workspace registry
        self._load_workspace_registry()

        # Load active workspace
        self._load_active_workspace()

    def validate_workspace_name(self, workspace_name: str) -> bool:
        """
        Validate workspace name format.

        Workspace names must be:
        - Alphanumeric with dashes
        - 1-50 characters long
        - Not starting or ending with dash

        Args:
            workspace_name: Workspace name to validate

        Returns:
            True if valid, False otherwise
        """
        if not workspace_name:
            return False

        # Check length
        if not 1 <= len(workspace_name) <= 50:
            return False

        # Check format: alphanumeric and dashes only
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$'
        return bool(re.match(pattern, workspace_name))

    def validate_site_url(self, site_url: str) -> str:
        """
        Validate and normalize Jira site URL.

        Args:
            site_url: Jira site URL (e.g., "company.atlassian.net" or full URL)

        Returns:
            Normalized site URL (https://company.atlassian.net)

        Raises:
            WorkspaceError: If URL is invalid
        """
        if not site_url:
            raise WorkspaceError("Site URL cannot be empty")

        # Remove trailing slashes
        site_url = site_url.rstrip('/')

        # If no protocol, assume https
        if not site_url.startswith(('http://', 'https://')):
            site_url = f'https://{site_url}'

        # Validate it looks like an Atlassian URL
        if '.atlassian.net' not in site_url:
            logger.warning("Site URL doesn't contain .atlassian.net: %s", site_url)

        return site_url

    def create_workspace_skeleton(
        self,
        workspace_name: str,
        auth_type: str = 'cloud'
    ) -> Dict[str, Any]:
        """
        Create a skeleton workspace configuration file for user to fill in.

        Args:
            workspace_name: Unique name for this workspace
            auth_type: Authentication type - 'cloud' or 'pat' (default: 'cloud')

        Returns:
            Dictionary with skeleton file path and instructions

        Raises:
            WorkspaceError: If validation fails or workspace already exists
        """
        # Validate workspace name
        if not self.validate_workspace_name(workspace_name):
            raise WorkspaceError(
                f"Invalid workspace name format: {workspace_name}. "
                "Must be alphanumeric with dashes, 1-50 characters, "
                "not starting/ending with dash."
            )

        # Check if workspace already exists
        if workspace_name in self._workspace_registry:
            raise WorkspaceError(
                f"Workspace '{workspace_name}' already exists. "
                "Use a different name or remove the existing workspace first."
            )

        # Validate auth_type
        if auth_type not in ('cloud', 'pat'):
            raise WorkspaceError(f"Invalid auth_type: {auth_type}. Must be 'cloud' or 'pat'")

        # Create skeleton configuration
        if auth_type == 'cloud':
            skeleton_config = {
                'name': workspace_name,
                'site_url': 'https://YOUR_COMPANY.atlassian.net',
                'email': 'your.email@company.com',
                'api_token': 'YOUR_JIRA_CLOUD_API_TOKEN',
                'auth_type': 'cloud',
                'created': datetime.now().isoformat(),
                'last_validated': None,
                '_instructions': {
                    'site_url': 'Replace with your Jira Cloud site URL',
                    'email': 'Replace with your Jira account email',
                    'api_token': 'Get from https://id.atlassian.com/manage-profile/security/api-tokens',
                    'note': 'Remove this _instructions section after filling in your credentials'
                }
            }
        else:  # pat
            skeleton_config = {
                'name': workspace_name,
                'site_url': 'https://jira.company.com',
                'email': 'your_username',
                'api_token': 'YOUR_PERSONAL_ACCESS_TOKEN',
                'auth_type': 'pat',
                'created': datetime.now().isoformat(),
                'last_validated': None,
                '_instructions': {
                    'site_url': 'Replace with your Jira Server/Data Center URL',
                    'email': 'Replace with your username (not used for PAT auth, but kept for reference)',
                    'api_token': 'Replace with your Personal Access Token from Jira Server',
                    'note': 'Remove this _instructions section after filling in your credentials'
                }
            }

        # Save skeleton configuration
        workspace_file = self.accounts_dir / f'{workspace_name}.json'
        try:
            with open(workspace_file, 'w', encoding='utf-8') as file_handle:
                json.dump(skeleton_config, file_handle, indent=2)

            # Set secure file permissions (600 - owner read/write only)
            workspace_file.chmod(0o600)

            logger.info("📝 Skeleton configuration created for workspace '%s'", workspace_name)

        except Exception as e:
            raise WorkspaceError(f"Failed to create skeleton configuration: {e}") from e

        return {
            'success': True,
            'workspace_name': workspace_name,
            'config_file': str(workspace_file),
            'auth_type': auth_type
        }

    def add_workspace(  # pylint: disable=too-many-positional-arguments
        self,
        workspace_name: str,
        site_url: str,
        email: str,
        api_token: str,
        auth_type: str = 'cloud'
    ) -> Dict[str, Any]:
        """
        Add a new Jira workspace configuration.

        Args:
            workspace_name: Unique name for this workspace
            site_url: Jira site URL
            email: Email address for Jira authentication (Cloud) or username (Server)
            api_token: Jira API token (Cloud) or Personal Access Token (Server)
            auth_type: Authentication type - 'cloud' or 'pat' (default: 'cloud')

        Returns:
            Dictionary with add status and workspace info

        Raises:
            WorkspaceError: If validation fails or workspace already exists
        """
        # Validate workspace name
        if not self.validate_workspace_name(workspace_name):
            raise WorkspaceError(
                f"Invalid workspace name format: {workspace_name}. "
                "Must be alphanumeric with dashes, 1-50 characters, "
                "not starting/ending with dash."
            )

        # Check if workspace already exists
        if workspace_name in self._workspace_registry:
            raise WorkspaceError(
                f"Workspace '{workspace_name}' already exists. "
                "Use a different name or remove the existing workspace first."
            )

        # Validate and normalize site URL
        site_url = self.validate_site_url(site_url)

        # Validate auth_type
        if auth_type not in ('cloud', 'pat'):
            raise WorkspaceError(f"Invalid auth_type: {auth_type}. Must be 'cloud' or 'pat'")

        # Validate email (only required for Cloud)
        if auth_type == 'cloud' and (not email or '@' not in email):
            raise WorkspaceError(f"Invalid email address: {email}")

        # Validate API token
        if not api_token or len(api_token) < 10:
            raise WorkspaceError("API token appears to be invalid (too short)")

        # Create workspace metadata
        workspace_metadata = {
            'name': workspace_name,
            'site_url': site_url,
            'email': email,
            'api_token': api_token,  # In production, consider encryption
            'auth_type': auth_type,
            'created': datetime.now().isoformat(),
            'last_validated': None
        }

        # Save workspace configuration
        workspace_file = self.accounts_dir / f'{workspace_name}.json'
        try:
            with open(workspace_file, 'w', encoding='utf-8') as file_handle:
                json.dump(workspace_metadata, file_handle, indent=2)

            # Set secure file permissions (600 - owner read/write only)
            workspace_file.chmod(0o600)

            logger.info("✅ Workspace '%s' added successfully", workspace_name)

        except Exception as e:
            raise WorkspaceError(f"Failed to save workspace configuration: {e}") from e

        # Add to registry
        self._workspace_registry[workspace_name] = workspace_metadata

        # If this is the first workspace, make it active
        if len(self._workspace_registry) == 1:
            self._set_active_workspace(workspace_name)
            logger.info("🔑 '%s' set as active workspace (first workspace)", workspace_name)

        return {
            'success': True,
            'workspace_name': workspace_name,
            'site_url': site_url,
            'email': email,
            'active': workspace_name == self._active_workspace_name
        }

    def list_workspaces(self) -> List[Dict[str, Any]]:
        """
        List all configured workspaces with their status.

        Returns:
            List of workspace information dictionaries
        """
        workspaces = []
        for workspace_name, metadata in self._workspace_registry.items():
            workspaces.append({
                'name': workspace_name,
                'site_url': metadata.get('site_url', 'Unknown'),
                'email': metadata.get('email', 'Unknown'),
                'active': workspace_name == self._active_workspace_name,
                'last_validated': metadata.get('last_validated'),
                'created': metadata.get('created')
            })

        # Sort by name, with active workspace first
        workspaces.sort(key=lambda x: (not x['active'], x['name']))
        return workspaces

    def get_active_workspace(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the currently active workspace.

        Returns:
            Active workspace information or None if no active workspace
        """
        if not self._active_workspace_name:
            return None

        metadata = self._workspace_registry.get(self._active_workspace_name)
        if not metadata:
            return None

        return {
            'name': self._active_workspace_name,
            'site_url': metadata.get('site_url', 'Unknown'),
            'email': metadata.get('email', 'Unknown'),
            'last_validated': metadata.get('last_validated'),
            'created': metadata.get('created')
        }

    def get_workspace_credentials(self, workspace_name: Optional[str] = None) -> Dict[str, str]:
        """
        Get credentials for a workspace.

        Args:
            workspace_name: Workspace name (uses active if None)

        Returns:
            Dictionary with site_url, email, api_token, and auth_type

        Raises:
            WorkspaceError: If workspace doesn't exist
        """
        # Use active workspace if none specified
        if workspace_name is None:
            workspace_name = self._active_workspace_name

        if not workspace_name:
            raise WorkspaceError("No active workspace and no workspace specified")

        metadata = self._workspace_registry.get(workspace_name)
        if not metadata:
            raise WorkspaceError(f"Workspace '{workspace_name}' not found")

        return {
            'site_url': metadata['site_url'],
            'email': metadata['email'],
            'api_token': metadata['api_token'],
            'auth_type': metadata.get('auth_type', 'cloud')  # Default to cloud for backward compatibility
        }

    def switch_workspace(self, workspace_name: str) -> Dict[str, Any]:
        """
        Switch to a different workspace.

        Args:
            workspace_name: Name of workspace to switch to

        Returns:
            Dictionary with switch status and new workspace info

        Raises:
            WorkspaceError: If workspace doesn't exist
        """
        # Validate workspace name format
        if not self.validate_workspace_name(workspace_name):
            raise WorkspaceError(f"Invalid workspace name format: {workspace_name}")

        # Check if workspace exists
        if workspace_name not in self._workspace_registry:
            raise WorkspaceError(
                f"Workspace '{workspace_name}' not found. "
                f"Available workspaces: {', '.join(self._workspace_registry.keys())}"
            )

        # Already active?
        if workspace_name == self._active_workspace_name:
            return {
                'success': True,
                'message': f"Workspace '{workspace_name}' is already active",
                'workspace_name': workspace_name
            }

        # Switch to new workspace
        self._set_active_workspace(workspace_name)

        logger.info("✅ Switched to workspace '%s'", workspace_name)

        return {
            'success': True,
            'message': f"Switched to workspace '{workspace_name}'",
            'workspace_name': workspace_name,
            'site_url': self._workspace_registry[workspace_name]['site_url']
        }

    def remove_workspace(self, workspace_name: str) -> Dict[str, Any]:
        """
        Remove a workspace configuration.

        Args:
            workspace_name: Name of workspace to remove

        Returns:
            Dictionary with removal status

        Raises:
            WorkspaceError: If workspace doesn't exist or removal fails
        """
        # Check if workspace exists
        if workspace_name not in self._workspace_registry:
            raise WorkspaceError(f"Workspace '{workspace_name}' not found")

        # Remove workspace file
        workspace_file = self.accounts_dir / f'{workspace_name}.json'
        try:
            if workspace_file.exists():
                workspace_file.unlink()
                logger.info("🗑️  Removed workspace file: %s", workspace_file)
        except Exception as e:
            raise WorkspaceError(f"Failed to remove workspace file: {e}") from e

        # Remove from registry
        del self._workspace_registry[workspace_name]

        # If this was the active workspace, clear it
        if workspace_name == self._active_workspace_name:
            self._active_workspace_name = None
            self.active_workspace_file.unlink(missing_ok=True)
            logger.info("🔓 Cleared active workspace")

            # If there are other workspaces, activate the first one
            if self._workspace_registry:
                first_workspace = list(self._workspace_registry.keys())[0]
                self._set_active_workspace(first_workspace)
                logger.info("🔑 Switched to workspace '%s'", first_workspace)

        logger.info("✅ Workspace '%s' removed successfully", workspace_name)

        return {
            'success': True,
            'message': f"Workspace '{workspace_name}' removed"
        }

    def _load_workspace_registry(self) -> None:
        """Load all workspace configurations from accounts directory."""
        if not self.accounts_dir.exists():
            return

        for workspace_file in self.accounts_dir.glob('*.json'):
            try:
                with open(workspace_file, 'r', encoding='utf-8') as file_handle:
                    metadata = json.load(file_handle)

                workspace_name = workspace_file.stem
                self._workspace_registry[workspace_name] = metadata
                logger.debug("Loaded workspace: %s", workspace_name)

            except Exception as e:
                logger.error("Failed to load workspace from %s: %s", workspace_file, e)

    def _load_active_workspace(self) -> None:
        """Load the active workspace from .env.active file."""
        if not self.active_workspace_file.exists():
            return

        try:
            workspace_name = self.active_workspace_file.read_text(encoding='utf-8').strip()
            if workspace_name and workspace_name in self._workspace_registry:
                self._active_workspace_name = workspace_name
                logger.info("🔑 Active workspace: %s", workspace_name)
            else:
                logger.warning("Active workspace '%s' not found in registry", workspace_name)

        except Exception as e:
            logger.error("Failed to load active workspace: %s", e)

    def _set_active_workspace(self, workspace_name: str) -> None:
        """
        Set the active workspace.

        Args:
            workspace_name: Name of workspace to activate
        """
        self._active_workspace_name = workspace_name

        try:
            self.active_workspace_file.write_text(workspace_name, encoding='utf-8')
            logger.debug("Active workspace saved to %s", self.active_workspace_file)
        except Exception as e:
            logger.error("Failed to save active workspace: %s", e)
