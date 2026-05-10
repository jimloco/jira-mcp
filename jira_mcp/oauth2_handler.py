#!/usr/bin/env python3.12
"""
OAuth 2.0 Token Management for Jira MCP Server

Handles OAuth 2.0 authentication flows, token refresh, and cloud ID discovery
for Jira Cloud instances using OAuth 2.0.
"""

import logging
import time
from typing import Dict, Optional, Any
import requests

logger = logging.getLogger(__name__)


class OAuth2Error(Exception):
    """Custom exception for OAuth 2.0 errors."""


class OAuth2Handler:
    """
    OAuth 2.0 token manager for Jira Cloud.

    Handles access token refresh using refresh tokens and maintains
    token lifecycle for OAuth 2.0 authenticated Jira instances.
    """

    def __init__(  # pylint: disable=too-many-positional-arguments
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        token_url: str = "https://auth.atlassian.com/oauth/token",
        cloud_id: Optional[str] = None
    ) -> None:
        """
        Initialize OAuth 2.0 handler.

        Args:
            client_id: OAuth 2.0 client ID
            client_secret: OAuth 2.0 client secret
            refresh_token: OAuth 2.0 refresh token
            token_url: Token endpoint URL (default: Atlassian)
            cloud_id: Atlassian Cloud ID (optional, can be discovered)

        Raises:
            OAuth2Error: If initialization fails
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.token_url = token_url
        self.cloud_id = cloud_id

        # Token state
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[float] = None

        # Validate inputs
        if not all([client_id, client_secret, refresh_token, token_url]):
            raise OAuth2Error("Missing required OAuth 2.0 credentials")

    def get_access_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.

        Returns:
            Valid access token

        Raises:
            OAuth2Error: If token refresh fails
        """
        if self._access_token and self._token_expiry:
            # Add 60 second buffer before expiry
            if time.time() < (self._token_expiry - 60):
                logger.debug("Using cached access token")
                return self._access_token

        logger.info("Refreshing OAuth 2.0 access token")
        return self._refresh_access_token()

    def _refresh_access_token(self) -> str:
        """
        Refresh the access token using the refresh token.

        Returns:
            New access token

        Raises:
            OAuth2Error: If refresh fails
        """
        try:
            data = {
                'grant_type': 'refresh_token',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token
            }

            logger.debug("Requesting new access token from %s", self.token_url)

            response = requests.post(
                self.token_url,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )

            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_code = error_data.get('error', 'unknown')
                except Exception:
                    error_code = 'unknown'
                logger.error("Token refresh failed: status=%d error=%s", response.status_code, error_code)
                raise OAuth2Error(f"Token refresh failed: HTTP {response.status_code}")

            token_data = response.json()
            self._access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 3600)

            if not self._access_token:
                raise OAuth2Error("No access_token in refresh response")

            self._token_expiry = time.time() + expires_in

            logger.info("Access token refreshed successfully (expires in %d seconds)", expires_in)

            return self._access_token

        except requests.RequestException as e:
            logger.error("Network error during token refresh: %s", type(e).__name__)
            raise OAuth2Error("Network error during token refresh") from e
        except OAuth2Error:
            raise
        except Exception as e:
            logger.error("Unexpected error during token refresh: %s", type(e).__name__)
            raise OAuth2Error("Unexpected error during token refresh") from e

    def discover_cloud_id(self) -> str:
        """
        Discover the Atlassian Cloud ID for the authenticated user.

        Uses the accessible-resources endpoint to find the cloud ID.

        Returns:
            Cloud ID string

        Raises:
            OAuth2Error: If discovery fails or no resources found
        """
        if self.cloud_id:
            logger.debug("Using cached cloud ID: %s", self.cloud_id)
            return self.cloud_id

        try:
            access_token = self.get_access_token()

            url = "https://api.atlassian.com/oauth/token/accessible-resources"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }

            logger.debug("Discovering cloud ID from accessible resources")

            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code != 200:
                logger.error("Cloud ID discovery failed: status=%d", response.status_code)
                raise OAuth2Error(f"Failed to discover cloud ID: HTTP {response.status_code}")

            resources = response.json()

            if not resources or not isinstance(resources, list) or len(resources) == 0:
                raise OAuth2Error("No accessible Jira resources found")

            # Use the first resource (most common case)
            # In multi-site scenarios, this could be configurable
            resource = resources[0]
            self.cloud_id = resource.get('id')

            if not self.cloud_id:
                raise OAuth2Error("Cloud ID not found in resource response")

            logger.info("Discovered cloud ID: %s (site: %s)", self.cloud_id, resource.get('name', 'Unknown'))

            return self.cloud_id

        except requests.RequestException as e:
            logger.error("Network error during cloud ID discovery: %s", type(e).__name__)
            raise OAuth2Error("Network error during cloud ID discovery") from e
        except OAuth2Error:
            raise
        except Exception as e:
            logger.error("Unexpected error during cloud ID discovery: %s", type(e).__name__)
            raise OAuth2Error("Unexpected error during cloud ID discovery") from e

    def get_api_base_url(self) -> str:
        """
        Get the API base URL for Jira Cloud with OAuth 2.0.

        For OAuth 2.0, Jira Cloud uses:
        https://api.atlassian.com/ex/jira/{cloudId}

        Returns:
            API base URL

        Raises:
            OAuth2Error: If cloud ID cannot be determined
        """
        cloud_id = self.cloud_id or self.discover_cloud_id()
        return f"https://api.atlassian.com/ex/jira/{cloud_id}"

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.

        Returns:
            Dictionary with Authorization header

        Raises:
            OAuth2Error: If token cannot be obtained
        """
        access_token = self.get_access_token()
        return {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }

    def test_connection(self) -> Dict[str, Any]:
        """
        Test OAuth 2.0 connection and retrieve server info.

        Returns:
            Dictionary with connection test results

        Raises:
            OAuth2Error: If connection test fails
        """
        try:
            base_url = self.get_api_base_url()
            headers = self.get_auth_headers()

            url = f"{base_url}/rest/api/3/serverInfo"
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code != 200:
                logger.error("Connection test failed: status=%d", response.status_code)
                raise OAuth2Error(f"Connection test failed: HTTP {response.status_code}")

            server_info = response.json()

            logger.info("OAuth 2.0 connection test successful")

            return {
                'success': True,
                'server_title': server_info.get('serverTitle', 'Jira'),
                'version': server_info.get('version', 'Unknown'),
                'cloud_id': self.cloud_id,
                'base_url': base_url
            }

        except requests.RequestException as e:
            logger.error("Network error during connection test: %s", type(e).__name__)
            raise OAuth2Error("Network error during connection test") from e
        except OAuth2Error:
            raise
        except Exception as e:
            logger.error("Unexpected error during connection test: %s", type(e).__name__)
            raise OAuth2Error("Unexpected error during connection test") from e

    def __repr__(self) -> str:
        """String representation of OAuth 2.0 handler."""
        return f"OAuth2Handler(client_id='{self.client_id[:8]}...', cloud_id='{self.cloud_id}')"
