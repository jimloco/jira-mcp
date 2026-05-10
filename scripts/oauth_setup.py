#!/usr/bin/env python3
"""
OAuth 2.0 Setup Helper for Jira MCP

Starts a local web server to handle the OAuth callback and automatically
updates the workspace configuration with the refresh token.
"""

import argparse
import json
import socket
import sys
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse
import requests


def _config_file_for(workspace_name: str) -> Path:
    return Path.home() / ".config" / "jira-mcp" / "workspaces" / f"{workspace_name}.json"


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback."""

    def log_message(self, format: str, *args: object) -> None:
        """Suppress default logging."""

    def do_GET(self) -> None:
        """Handle GET request with authorization code."""
        parsed_path = urlparse(self.path)

        if parsed_path.path != '/callback':
            self.send_error(404)
            return

        query_params = parse_qs(parsed_path.query)

        if 'code' not in query_params:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>Error: No authorization code received</h1></body></html>')
            return

        auth_code = query_params['code'][0]
        print("\nReceived authorization code")

        print("Exchanging code for tokens...")
        success = self.exchange_code_for_tokens(auth_code)

        workspace_name = self.server.workspace_name  # type: ignore[attr-defined]
        config_file = _config_file_for(workspace_name)

        if success:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            response_html = (
                "<html><head><meta charset='UTF-8'><title>OAuth Success</title></head>"
                "<body style='font-family: Arial, sans-serif; text-align: center; padding: 50px;'>"
                "<h1 style='color: green;'>Success!</h1>"
                "<p>Your Jira MCP workspace has been configured with OAuth 2.0.</p>"
                "<p>You can close this window and return to your terminal.</p>"
                f"<p style='margin-top: 40px; color: #666;'>"
                f"Workspace: <strong>{workspace_name}</strong><br>"
                f"Config: <code>{config_file}</code></p>"
                "</body></html>"
            )
            self.wfile.write(response_html.encode('utf-8'))
        else:
            self.send_response(500)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            error_html = (
                '<html><head><meta charset="UTF-8"></head><body>'
                '<h1 style="color: red;">Error exchanging code for tokens</h1>'
                '<p>Check the terminal for details.</p></body></html>'
            )
            self.wfile.write(error_html.encode('utf-8'))

        self.server.shutdown_requested = True  # type: ignore[attr-defined]

    def exchange_code_for_tokens(self, auth_code: str) -> bool:
        """Exchange authorization code for access and refresh tokens."""
        workspace_name = self.server.workspace_name  # type: ignore[attr-defined]
        redirect_uri = self.server.redirect_uri  # type: ignore[attr-defined]
        config_file = _config_file_for(workspace_name)

        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            oauth_config = config.get('oauth_config', {})
            client_id = oauth_config.get('client_id')
            client_secret = oauth_config.get('client_secret')

            if not client_id or not client_secret:
                print("Error: client_id or client_secret not found in config")
                return False

            token_url = oauth_config.get('token_url', 'https://auth.atlassian.com/oauth/token')

            data = {
                'grant_type': 'authorization_code',
                'client_id': client_id,
                'client_secret': client_secret,
                'code': auth_code,
                'redirect_uri': redirect_uri
            }

            response = requests.post(
                token_url,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )

            if response.status_code != 200:
                print(f"Token exchange failed: HTTP {response.status_code}")
                return False

            tokens = response.json()
            refresh_token = tokens.get('refresh_token')
            access_token = tokens.get('access_token')

            if not refresh_token:
                present_fields = list(tokens.keys())
                print(f"Error: No refresh_token in response. Fields present: {present_fields}")
                return False

            print("Got refresh token")

            if not oauth_config.get('cloud_id'):
                print("Discovering Cloud ID...")
                cloud_id = self._discover_cloud_id(access_token)
                if cloud_id:
                    oauth_config['cloud_id'] = cloud_id
                    print(f"Cloud ID: {cloud_id}")

            oauth_config['refresh_token'] = refresh_token
            config['oauth_config'] = oauth_config

            if '_instructions' in config:
                del config['_instructions']

            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            config_file.chmod(0o600)

            print(f"Configuration updated: {config_file}")
            print("\nOAuth 2.0 setup complete!")
            print("Restart your MCP server to use the new configuration.")

            return True

        except Exception as e:
            print(f"Error during token exchange: {type(e).__name__}")
            return False

    def _discover_cloud_id(self, access_token: str) -> str:
        """Discover Atlassian Cloud ID."""
        try:
            response = requests.get(
                'https://api.atlassian.com/oauth/token/accessible-resources',
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json'
                },
                timeout=30
            )

            if response.status_code == 200:
                resources = response.json()
                if resources and len(resources) > 0:
                    return resources[0]['id']

            return ''

        except Exception as e:
            print(f"Cloud ID discovery failed: {type(e).__name__}")
            return ''


def _bind_server_socket(port: int) -> socket.socket:
    """Bind a socket to the given port and return it (held open to prevent TOCTOU races)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost', port))
    return sock


def main() -> None:
    """Main function to run OAuth setup."""
    parser = argparse.ArgumentParser(description='Jira MCP OAuth 2.0 Setup')
    parser.add_argument('--workspace', required=True, help='Workspace name (must match config filename)')
    parser.add_argument('--port', type=int, default=0, help='Callback port (0 = auto-assign)')
    args = parser.parse_args()

    workspace_name: str = args.workspace
    config_file = _config_file_for(workspace_name)

    print("=" * 70)
    print("  Jira MCP OAuth 2.0 Setup")
    print("=" * 70)
    print()

    # Bind socket now so the port stays reserved until HTTPServer takes over
    try:
        server_sock = _bind_server_socket(args.port)
        port: int = server_sock.getsockname()[1]
    except Exception as e:
        print(f"Error reserving port: {type(e).__name__}")
        sys.exit(1)

    redirect_uri = f"http://localhost:{port}/callback"

    print(f"Selected port: {port}")
    print()
    print("=" * 70)
    print("IMPORTANT: Update Your OAuth App Callback URL")
    print("=" * 70)
    print()
    print("Before proceeding, update your OAuth app's redirect URI:")
    print()
    print("1. Go to: https://developer.atlassian.com/console/myapps/")
    print("2. Click on your OAuth app")
    print("3. Go to 'Authorization' -> 'OAuth 2.0 (3LO)'")
    print("4. Update the Callback URL to:")
    print()
    print(f"   {redirect_uri}")
    print()
    print("5. Click 'Save changes'")
    print()
    print("=" * 70)
    print()

    response = input("Have you updated the callback URL? (yes/no): ").strip().lower()
    if response not in ('yes', 'y'):
        print("\nSetup cancelled. Please update the callback URL and run again.")
        server_sock.close()
        sys.exit(0)

    print()

    if not config_file.exists():
        print(f"Error: Config file not found: {config_file}")
        print("Run the create_workspace_skeleton operation first.")
        server_sock.close()
        sys.exit(1)

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)

        oauth_config = config.get('oauth_config', {})
        client_id = oauth_config.get('client_id')

        if not client_id or client_id == 'YOUR_OAUTH2_CLIENT_ID':
            print(f"Error: client_id not configured in {config_file}")
            print("Please edit the config file and add your OAuth client_id and client_secret.")
            server_sock.close()
            sys.exit(1)

    except Exception as e:
        print(f"Error reading config: {type(e).__name__}")
        server_sock.close()
        sys.exit(1)

    encoded_redirect_uri = quote(redirect_uri, safe='')

    auth_url = (
        f"https://auth.atlassian.com/authorize?"
        f"audience=api.atlassian.com&"
        f"client_id={client_id}&"
        f"scope=read:jira-work%20write:jira-work%20read:jira-user%20read:me%20read:account%20offline_access&"
        f"redirect_uri={encoded_redirect_uri}&"
        f"response_type=code&"
        f"prompt=consent"
    )

    print(f"Workspace: {workspace_name}")
    print(f"Config: {config_file}")
    print()
    print(f"Starting OAuth callback server on {redirect_uri}...")
    print()

    # Hand the already-bound socket to HTTPServer to avoid TOCTOU race
    server = HTTPServer(('localhost', port), OAuthCallbackHandler, bind_and_activate=False)
    server.socket = server_sock
    server.server_address = server_sock.getsockname()
    server.shutdown_requested = False
    server.workspace_name = workspace_name
    server.redirect_uri = redirect_uri

    print("Server started!")
    print()
    print("Opening authorization URL in your browser...")
    print()
    print("If the browser doesn't open automatically, visit:")
    print(f"   {auth_url}")
    print()
    print("Waiting for OAuth callback...")
    print("(Grant permission in your browser to continue)")
    print()

    try:
        webbrowser.open(auth_url)
    except Exception as e:
        print(f"Could not open browser automatically: {type(e).__name__}")

    while not server.shutdown_requested:
        server.handle_request()

    print("\n" + "=" * 70)
    print("  Setup Complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
