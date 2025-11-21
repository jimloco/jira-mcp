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
        # Workspace storage paths
        self.accounts_dir = Path('accounts')
        self.active_workspace_file = Path('.env.active')
        
        # Workspace registry (workspace_name -> metadata)
        self._workspace_registry: Dict[str, Dict[str, Any]] = {}
        
        # Active workspace state
        self._active_workspace_name: Optional[str] = None
        
        # Ensure accounts directory exists
        self.accounts_dir.mkdir(exist_ok=True)
        
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
            logger.warning(f"Site URL doesn't contain .atlassian.net: {site_url}")
        
        return site_url

    def add_workspace(
        self,
        workspace_name: str,
        site_url: str,
        email: str,
        api_token: str
    ) -> Dict[str, Any]:
        """
        Add a new Jira workspace configuration.

        Args:
            workspace_name: Unique name for this workspace
            site_url: Jira site URL
            email: Email address for Jira authentication
            api_token: Jira API token

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
        
        # Validate email
        if not email or '@' not in email:
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
            'created': datetime.now().isoformat(),
            'last_validated': None
        }
        
        # Save workspace configuration
        workspace_file = self.accounts_dir / f'{workspace_name}.json'
        try:
            with open(workspace_file, 'w', encoding='utf-8') as f:
                json.dump(workspace_metadata, f, indent=2)
            
            # Set secure file permissions (600 - owner read/write only)
            workspace_file.chmod(0o600)
            
            logger.info(f"✅ Workspace '{workspace_name}' added successfully")
            
        except Exception as e:
            raise WorkspaceError(f"Failed to save workspace configuration: {e}") from e
        
        # Add to registry
        self._workspace_registry[workspace_name] = workspace_metadata
        
        # If this is the first workspace, make it active
        if len(self._workspace_registry) == 1:
            self._set_active_workspace(workspace_name)
            logger.info(f"🔑 '{workspace_name}' set as active workspace (first workspace)")
        
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
            Dictionary with site_url, email, and api_token

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
            'api_token': metadata['api_token']
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
        
        logger.info(f"✅ Switched to workspace '{workspace_name}'")
        
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
                logger.info(f"🗑️  Removed workspace file: {workspace_file}")
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
                logger.info(f"🔑 Switched to workspace '{first_workspace}'")
        
        logger.info(f"✅ Workspace '{workspace_name}' removed successfully")
        
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
                with open(workspace_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                workspace_name = workspace_file.stem
                self._workspace_registry[workspace_name] = metadata
                logger.debug(f"Loaded workspace: {workspace_name}")
                
            except Exception as e:
                logger.error(f"Failed to load workspace from {workspace_file}: {e}")

    def _load_active_workspace(self) -> None:
        """Load the active workspace from .env.active file."""
        if not self.active_workspace_file.exists():
            return
        
        try:
            workspace_name = self.active_workspace_file.read_text().strip()
            if workspace_name and workspace_name in self._workspace_registry:
                self._active_workspace_name = workspace_name
                logger.info(f"🔑 Active workspace: {workspace_name}")
            else:
                logger.warning(f"Active workspace '{workspace_name}' not found in registry")
                
        except Exception as e:
            logger.error(f"Failed to load active workspace: {e}")

    def _set_active_workspace(self, workspace_name: str) -> None:
        """
        Set the active workspace.

        Args:
            workspace_name: Name of workspace to activate
        """
        self._active_workspace_name = workspace_name
        
        try:
            self.active_workspace_file.write_text(workspace_name)
            logger.debug(f"Active workspace saved to {self.active_workspace_file}")
        except Exception as e:
            logger.error(f"Failed to save active workspace: {e}")
