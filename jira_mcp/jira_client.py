#!/usr/bin/env python3.12
"""
Jira API Client Wrapper

Provides a secure wrapper around the Jira Python library with authentication,
error handling, and logging.
"""

import logging
from typing import Any, Dict, Optional
from jira import JIRA
from jira.exceptions import JIRAError

from .utils import get_user_attribute

# Configure logging
logger = logging.getLogger(__name__)


class JiraClientError(Exception):
    """Custom exception for Jira client errors."""


class JiraClient:
    """
    Jira API client wrapper with authentication and error handling.

    Supports both Jira Cloud (email + API token) and Jira Server/Data Center (PAT).
    """

    def __init__(self, site_url: str, email: str, api_token: str, auth_type: str = 'cloud'):
        """
        Initialize Jira client.

        Args:
            site_url: Jira site URL (e.g., https://company.atlassian.net)
            email: Email address for authentication (Cloud) or username (Server with basic auth)
            api_token: Jira API token (Cloud) or Personal Access Token (Server)
            auth_type: Authentication type - 'cloud' (email+token) or 'pat' (Personal Access Token)

        Raises:
            JiraClientError: If initialization fails
        """
        self.site_url = site_url
        self.email = email
        self._api_token = api_token  # Keep private
        self.auth_type = auth_type
        self._jira: Optional[JIRA] = None

        # Initialize connection
        self._connect()

    def _connect(self) -> None:
        """
        Establish connection to Jira instance.

        Raises:
            JiraClientError: If connection fails
        """
        try:
            logger.info("Connecting to Jira: %s (auth_type: %s)", self.site_url, self.auth_type)

            if self.auth_type == 'pat':
                # Jira Server/Data Center with Personal Access Token
                # PAT uses Bearer token authentication
                self._jira = JIRA(
                    server=self.site_url,
                    token_auth=self._api_token
                )
                logger.info("✅ Connected to Jira Server/Data Center with PAT")
            else:
                # Jira Cloud with email + API token (basic auth)
                self._jira = JIRA(
                    server=self.site_url,
                    basic_auth=(self.email, self._api_token)
                )
                logger.info("✅ Connected to Jira Cloud with API token")

        except JIRAError as e:
            error_msg = f"Failed to connect to Jira: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise JiraClientError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error connecting to Jira: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise JiraClientError(error_msg) from e

    def test_connection(self) -> Dict[str, Any]:
        """
        Test Jira connection and retrieve server info.

        Returns:
            Dictionary with connection test results

        Raises:
            JiraClientError: If connection test fails
        """
        try:
            # Get server info
            server_info = self._jira.server_info()

            logger.info("✅ Jira connection test successful: %s", server_info.get('serverTitle', 'Unknown'))

            return {
                'success': True,
                'server_title': server_info.get('serverTitle', 'Unknown'),
                'version': server_info.get('version', 'Unknown'),
                'base_url': server_info.get('baseUrl', self.site_url)
            }

        except JIRAError as e:
            error_msg = f"Connection test failed: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise JiraClientError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error during connection test: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise JiraClientError(error_msg) from e

    def get_current_user(self) -> Dict[str, Any]:
        """
        Get current authenticated user information.

        Returns:
            Dictionary with user information

        Raises:
            JiraClientError: If request fails
        """
        try:
            # Get current user
            user = self._jira.current_user()

            # Get user details
            user_info = self._jira.user(user)

            return {
                'account_id': get_user_attribute(user_info, 'accountId', 'name', 'N/A'),
                'email': get_user_attribute(user_info, 'emailAddress', 'emailAddress', 'N/A'),
                'display_name': get_user_attribute(user_info, 'displayName', 'displayName', 'Unknown'),
                'active': get_user_attribute(user_info, 'active', 'active', True)
            }

        except JIRAError as e:
            error_msg = f"Failed to get current user: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise JiraClientError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error getting current user: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise JiraClientError(error_msg) from e

    def search_users(self, query: str, max_results: int = 50) -> list:
        """
        Search for users by name or email.

        Args:
            query: Search query (name or email)
            max_results: Maximum number of results to return

        Returns:
            List of user dictionaries

        Raises:
            JiraClientError: If search fails
        """
        try:
            # Search users
            users = self._jira.search_users(query, maxResults=max_results)

            # Format user information
            user_list = []
            for user in users:
                user_list.append({
                    'account_id': get_user_attribute(user, 'accountId', 'name', 'N/A'),
                    'email': get_user_attribute(user, 'emailAddress', 'emailAddress', 'N/A'),
                    'display_name': get_user_attribute(user, 'displayName', 'displayName', 'Unknown'),
                    'active': get_user_attribute(user, 'active', 'active', True)
                })

            return user_list

        except JIRAError as e:
            error_msg = f"Failed to search users: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise JiraClientError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error searching users: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise JiraClientError(error_msg) from e

    def get_projects(self) -> list:
        """
        Get all accessible projects.

        Returns:
            List of project dictionaries

        Raises:
            JiraClientError: If request fails
        """
        try:
            projects = self._jira.projects()

            # Format project information
            project_list = []
            for project in projects:
                project_list.append({
                    'key': project.key,
                    'name': project.name,
                    'id': project.id,
                    'project_type': getattr(project, 'projectTypeKey', 'Unknown')
                })

            return project_list

        except JIRAError as e:
            error_msg = f"Failed to get projects: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise JiraClientError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error getting projects: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise JiraClientError(error_msg) from e

    @property
    def jira(self) -> JIRA:
        """
        Get the underlying JIRA client instance.

        Returns:
            JIRA client instance

        Raises:
            JiraClientError: If not connected
        """
        if self._jira is None:
            raise JiraClientError("Jira client not connected")
        return self._jira

    def __repr__(self) -> str:
        """String representation of client."""
        return f"JiraClient(site_url='{self.site_url}', email='{self.email}')"
