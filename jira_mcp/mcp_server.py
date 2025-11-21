#!/usr/bin/env python3.12
"""
MCP Server Implementation

Model Context Protocol server for Jira Cloud integration.
Implements STDIO transport and tool registration.
"""

import logging
from typing import Any, Dict, List
from mcp import types
from mcp.server.lowlevel import Server

# Import managers
from .workspace_manager import WorkspaceManager, WorkspaceError
from .jira_client import JiraClient, JiraClientError

# Configure logging
logger = logging.getLogger(__name__)


class MCPServerError(Exception):
    """Custom exception for MCP server errors."""


class JiraMCPServer:
    """
    MCP server for Jira Cloud integration.

    Provides tools for workspace management and Jira operations.
    """

    def __init__(self, server_config: Dict[str, str]):
        """
        Initialize MCP server with configuration.

        Args:
            server_config: Configuration dictionary with server settings
        """
        self.config = server_config
        self.server_name = server_config.get("MCP_SERVER_NAME", "jira-mcp")
        self.server_version = server_config.get("MCP_SERVER_VERSION", "0.1.0")

        # Initialize MCP server
        self.app = Server(self.server_name)

        # Initialize workspace manager
        self.workspace_manager = WorkspaceManager()

    def register_tools(self) -> None:
        """
        Register all MCP tools with the server.
        """
        logger.info("🔧 Registering MCP tools...")

        @self.app.list_tools()
        async def list_tools() -> List[types.Tool]:
            """List all available MCP tools."""
            return [
                types.Tool(
                    name="jira_workspace",
                    description=(
                        "Perform Jira workspace operations: workspace management and connectivity testing.\n\n"
                        "Workspace Management:\n"
                        "- add_workspace: Configure new Jira instance (name, site_url, email, api_token)\n"
                        "- list_workspaces: Show all configured workspaces with active indicator\n"
                        "- get_active_workspace: Display current workspace details\n"
                        "- switch_workspace: Change active workspace\n"
                        "- validate_workspace: Test credentials and API connectivity\n"
                        "- remove_workspace: Delete workspace configuration\n\n"
                        "Connectivity & User:\n"
                        "- hello: Test MCP server and Jira API connectivity\n"
                        "- get_current_user: Get authenticated user info from active workspace\n"
                        "- search_users: Find users by name/email for assignment\n\n"
                        "URL Format: https://yourcompany.atlassian.net"
                    ),
                    inputSchema={
                        "type": "object",
                        "required": ["operation"],
                        "properties": {
                            "operation": {
                                "type": "string",
                                "enum": [
                                    "hello",
                                    "add_workspace",
                                    "list_workspaces",
                                    "get_active_workspace",
                                    "switch_workspace",
                                    "validate_workspace",
                                    "remove_workspace",
                                    "get_current_user",
                                    "search_users"
                                ],
                                "description": "Operation to perform"
                            },
                            "workspace_name": {
                                "type": "string",
                                "description": "Workspace name (for add_workspace, switch_workspace, validate_workspace, remove_workspace)"
                            },
                            "site_url": {
                                "type": "string",
                                "description": "Jira site URL (for add_workspace) - e.g., company.atlassian.net or https://company.atlassian.net"
                            },
                            "email": {
                                "type": "string",
                                "description": "Email address for Jira authentication (for add_workspace)"
                            },
                            "api_token": {
                                "type": "string",
                                "description": "Jira API token (for add_workspace) - get from https://id.atlassian.com/manage-profile/security/api-tokens"
                            },
                            "query": {
                                "type": "string",
                                "description": "Search query for users (for search_users)"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results (for search_users). Default: 50"
                            }
                        },
                        "additionalProperties": False
                    }
                )
            ]

        @self.app.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle MCP tool calls with parameter validation."""
            try:
                return await self._dispatch_tool_call(name, arguments)

            except (ValueError, KeyError, OSError, RuntimeError) as tool_error:
                logger.error("❌ Tool call error for %s: %s", name, tool_error)
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ **Tool Error**: {str(tool_error)}"
                    )
                ]

        logger.info("✅ MCP tools registered successfully")

    async def _dispatch_tool_call(
        self, name: str, arguments: Dict[str, Any]
    ) -> List[types.TextContent]:
        """
        Dispatch tool calls to appropriate handlers.

        Args:
            name: Tool name to call
            arguments: Tool arguments

        Returns:
            List of text content blocks with tool results
        """
        # Handle jira_workspace tool
        if name == "jira_workspace":
            return await self._route_workspace_operation(arguments)

        # Unknown tool
        return [
            types.TextContent(
                type="text",
                text=(
                    f"❌ **Unknown Tool**: '{name}'\n\n"
                    "✅ **Available tools**: jira_workspace"
                ),
            )
        ]

    async def _route_workspace_operation(
        self, arguments: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Route jira_workspace operations to appropriate handlers."""
        operation = arguments.get("operation")
        if not operation:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Parameter Error**: Missing required parameter 'operation'\n\n"
                        "Available operations: hello, add_workspace, list_workspaces, "
                        "get_active_workspace, switch_workspace, validate_workspace, "
                        "remove_workspace, get_current_user, search_users"
                    )
                )
            ]

        # Route to handlers
        if operation == "hello":
            return await self._handle_hello(arguments)
        if operation == "add_workspace":
            return await self._handle_add_workspace(arguments)
        if operation == "list_workspaces":
            return await self._handle_list_workspaces(arguments)
        if operation == "get_active_workspace":
            return await self._handle_get_active_workspace(arguments)
        if operation == "switch_workspace":
            return await self._handle_switch_workspace(arguments)
        if operation == "validate_workspace":
            return await self._handle_validate_workspace(arguments)
        if operation == "remove_workspace":
            return await self._handle_remove_workspace(arguments)
        if operation == "get_current_user":
            return await self._handle_get_current_user(arguments)
        if operation == "search_users":
            return await self._handle_search_users(arguments)

        return [
            types.TextContent(
                type="text",
                text=f"❌ **Invalid Operation**: '{operation}'\n\n"
                     "Available operations: hello, add_workspace, list_workspaces, "
                     "get_active_workspace, switch_workspace, validate_workspace, "
                     "remove_workspace, get_current_user, search_users"
            )
        ]

    async def _handle_hello(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle hello operation - test connectivity."""
        try:
            # Get active workspace
            active_workspace = self.workspace_manager.get_active_workspace()
            
            if not active_workspace:
                return [
                    types.TextContent(
                        type="text",
                        text=(
                            "✅ **Jira MCP Server Status**\n\n"
                            f"**Server**: {self.server_name} v{self.server_version}\n"
                            "**Status**: Running\n"
                            "**Workspaces**: No workspaces configured\n\n"
                            "ℹ️ Add a workspace to get started:\n"
                            "```\n"
                            "jira_workspace(operation=\"add_workspace\", workspace_name=\"mycompany\", "
                            "site_url=\"mycompany.atlassian.net\", email=\"your.email@company.com\", "
                            "api_token=\"YOUR_API_TOKEN\")\n"
                            "```"
                        )
                    )
                ]
            
            # Test Jira connection
            try:
                credentials = self.workspace_manager.get_workspace_credentials()
                jira_client = JiraClient(
                    credentials['site_url'],
                    credentials['email'],
                    credentials['api_token']
                )
                
                server_info = jira_client.test_connection()
                
                return [
                    types.TextContent(
                        type="text",
                        text=(
                            "✅ **Jira MCP Server Status**\n\n"
                            f"**Server**: {self.server_name} v{self.server_version}\n"
                            "**Status**: Running\n\n"
                            f"**Active Workspace**: {active_workspace['name']}\n"
                            f"**Jira Site**: {active_workspace['site_url']}\n"
                            f"**Jira Server**: {server_info['server_title']}\n"
                            f"**Jira Version**: {server_info['version']}\n"
                            f"**Email**: {active_workspace['email']}\n\n"
                            "✅ Jira API connection: OK"
                        )
                    )
                ]
                
            except JiraClientError as e:
                return [
                    types.TextContent(
                        type="text",
                        text=(
                            "⚠️ **Jira MCP Server Status**\n\n"
                            f"**Server**: {self.server_name} v{self.server_version}\n"
                            "**Status**: Running\n\n"
                            f"**Active Workspace**: {active_workspace['name']}\n"
                            f"**Jira Site**: {active_workspace['site_url']}\n"
                            f"**Email**: {active_workspace['email']}\n\n"
                            f"❌ Jira API connection failed: {str(e)}\n\n"
                            "Check your credentials and network connectivity."
                        )
                    )
                ]
        
        except Exception as error:
            logger.error("Error in hello operation: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_add_workspace(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle add_workspace operation."""
        try:
            workspace_name = arguments.get("workspace_name")
            site_url = arguments.get("site_url")
            email = arguments.get("email")
            api_token = arguments.get("api_token")
            
            # Validate required parameters
            if not all([workspace_name, site_url, email, api_token]):
                return [
                    types.TextContent(
                        type="text",
                        text=(
                            "❌ **Missing Required Parameters**\n\n"
                            "Required: workspace_name, site_url, email, api_token\n\n"
                            "Example:\n"
                            "```\n"
                            "jira_workspace(operation=\"add_workspace\", "
                            "workspace_name=\"mycompany\", "
                            "site_url=\"mycompany.atlassian.net\", "
                            "email=\"your.email@company.com\", "
                            "api_token=\"YOUR_API_TOKEN\")\n"
                            "```\n\n"
                            "Get your API token from: https://id.atlassian.com/manage-profile/security/api-tokens"
                        )
                    )
                ]
            
            # Add workspace
            result = self.workspace_manager.add_workspace(
                workspace_name, site_url, email, api_token
            )
            
            # Test connection
            try:
                jira_client = JiraClient(result['site_url'], result['email'], api_token)
                server_info = jira_client.test_connection()
                
                return [
                    types.TextContent(
                        type="text",
                        text=(
                            f"✅ **Workspace '{workspace_name}' Added Successfully**\n\n"
                            f"**Site URL**: {result['site_url']}\n"
                            f"**Email**: {result['email']}\n"
                            f"**Active**: {'Yes' if result['active'] else 'No'}\n\n"
                            f"**Jira Connection**: ✅ OK\n"
                            f"**Server**: {server_info['server_title']}\n"
                            f"**Version**: {server_info['version']}\n\n"
                            "You can now use Jira operations with this workspace."
                        )
                    )
                ]
            
            except JiraClientError as e:
                return [
                    types.TextContent(
                        type="text",
                        text=(
                            f"⚠️ **Workspace '{workspace_name}' Added (with warnings)**\n\n"
                            f"**Site URL**: {result['site_url']}\n"
                            f"**Email**: {result['email']}\n"
                            f"**Active**: {'Yes' if result['active'] else 'No'}\n\n"
                            f"⚠️ **Jira Connection Test Failed**: {str(e)}\n\n"
                            "The workspace was saved, but the connection test failed. "
                            "Please verify your credentials and network connectivity."
                        )
                    )
                ]
        
        except WorkspaceError as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Workspace Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error adding workspace: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_list_workspaces(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle list_workspaces operation."""
        try:
            workspaces = self.workspace_manager.list_workspaces()
            
            if not workspaces:
                return [
                    types.TextContent(
                        type="text",
                        text=(
                            "ℹ️ **No Workspaces Configured**\n\n"
                            "Add a workspace to get started:\n"
                            "```\n"
                            "jira_workspace(operation=\"add_workspace\", workspace_name=\"mycompany\", "
                            "site_url=\"mycompany.atlassian.net\", email=\"your.email@company.com\", "
                            "api_token=\"YOUR_API_TOKEN\")\n"
                            "```"
                        )
                    )
                ]
            
            # Format workspace list
            result_lines = ["📋 **Configured Jira Workspaces**\n"]
            
            for workspace in workspaces:
                status_icon = "✓" if workspace['active'] else "○"
                active_label = " (ACTIVE)" if workspace['active'] else ""
                
                result_lines.append(f"{status_icon} **{workspace['name']}**{active_label}")
                result_lines.append(f"  └─ Site: {workspace['site_url']}")
                result_lines.append(f"  └─ Email: {workspace['email']}")
                
                if workspace.get('created'):
                    result_lines.append(f"  └─ Created: {workspace['created']}")
                
                result_lines.append("")
            
            result_lines.append(f"**Total workspaces**: {len(workspaces)}")
            
            return [
                types.TextContent(
                    type="text",
                    text="\n".join(result_lines)
                )
            ]
        
        except Exception as error:
            logger.error("Error listing workspaces: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_get_active_workspace(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle get_active_workspace operation."""
        try:
            active_workspace = self.workspace_manager.get_active_workspace()
            
            if not active_workspace:
                return [
                    types.TextContent(
                        type="text",
                        text=(
                            "⚠️ **No Active Workspace**\n\n"
                            "No workspace is currently active. Add a workspace or switch to an existing one:\n"
                            "```\n"
                            "jira_workspace(operation=\"list_workspaces\")\n"
                            "jira_workspace(operation=\"switch_workspace\", workspace_name=\"<name>\")\n"
                            "```"
                        )
                    )
                ]
            
            result = (
                f"✓ **Active Workspace**: {active_workspace['name']}\n\n"
                f"**Site URL**: {active_workspace['site_url']}\n"
                f"**Email**: {active_workspace['email']}\n"
            )
            
            if active_workspace.get('created'):
                result += f"**Created**: {active_workspace['created']}\n"
            
            return [
                types.TextContent(
                    type="text",
                    text=result
                )
            ]
        
        except Exception as error:
            logger.error("Error getting active workspace: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_switch_workspace(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle switch_workspace operation."""
        workspace_name = arguments.get("workspace_name")
        
        if not workspace_name:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameter**: workspace_name\n\n"
                        "Example: jira_workspace(operation=\"switch_workspace\", workspace_name=\"mycompany\")"
                    )
                )
            ]
        
        try:
            result = self.workspace_manager.switch_workspace(workspace_name)
            
            return [
                types.TextContent(
                    type="text",
                    text=(
                        f"✅ **{result['message']}**\n\n"
                        f"**Workspace**: {result['workspace_name']}\n"
                        f"**Site URL**: {result.get('site_url', 'N/A')}"
                    )
                )
            ]
        
        except WorkspaceError as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Workspace Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error switching workspace: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_validate_workspace(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle validate_workspace operation."""
        workspace_name = arguments.get("workspace_name")
        
        try:
            # Use active workspace if none specified
            if workspace_name:
                credentials = self.workspace_manager.get_workspace_credentials(workspace_name)
            else:
                credentials = self.workspace_manager.get_workspace_credentials()
                active = self.workspace_manager.get_active_workspace()
                workspace_name = active['name'] if active else "Unknown"
            
            # Test connection
            jira_client = JiraClient(
                credentials['site_url'],
                credentials['email'],
                credentials['api_token']
            )
            
            server_info = jira_client.test_connection()
            user_info = jira_client.get_current_user()
            
            return [
                types.TextContent(
                    type="text",
                    text=(
                        f"✅ **Workspace '{workspace_name}' Validation Successful**\n\n"
                        f"**Site**: {credentials['site_url']}\n"
                        f"**Server**: {server_info['server_title']}\n"
                        f"**Version**: {server_info['version']}\n\n"
                        f"**Authenticated User**: {user_info['display_name']}\n"
                        f"**Email**: {user_info['email']}\n"
                        f"**Account ID**: {user_info['account_id']}\n"
                        f"**Status**: {'Active' if user_info['active'] else 'Inactive'}\n\n"
                        "✅ All connectivity tests passed"
                    )
                )
            ]
        
        except (WorkspaceError, JiraClientError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Validation Failed**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error validating workspace: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_remove_workspace(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle remove_workspace operation."""
        workspace_name = arguments.get("workspace_name")
        
        if not workspace_name:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameter**: workspace_name\n\n"
                        "Example: jira_workspace(operation=\"remove_workspace\", workspace_name=\"mycompany\")"
                    )
                )
            ]
        
        try:
            result = self.workspace_manager.remove_workspace(workspace_name)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"✅ **{result['message']}**"
                )
            ]
        
        except WorkspaceError as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Workspace Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error removing workspace: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_get_current_user(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle get_current_user operation."""
        try:
            credentials = self.workspace_manager.get_workspace_credentials()
            active = self.workspace_manager.get_active_workspace()
            
            jira_client = JiraClient(
                credentials['site_url'],
                credentials['email'],
                credentials['api_token']
            )
            
            user_info = jira_client.get_current_user()
            
            return [
                types.TextContent(
                    type="text",
                    text=(
                        f"👤 **Current User** ({active['name'] if active else 'Unknown'})\n\n"
                        f"**Name**: {user_info['display_name']}\n"
                        f"**Email**: {user_info['email']}\n"
                        f"**Account ID**: {user_info['account_id']}\n"
                        f"**Status**: {'Active' if user_info['active'] else 'Inactive'}"
                    )
                )
            ]
        
        except (WorkspaceError, JiraClientError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error getting current user: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_search_users(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle search_users operation."""
        query = arguments.get("query")
        max_results = arguments.get("max_results", 50)
        
        if not query:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameter**: query\n\n"
                        "Example: jira_workspace(operation=\"search_users\", query=\"john\")"
                    )
                )
            ]
        
        try:
            credentials = self.workspace_manager.get_workspace_credentials()
            
            jira_client = JiraClient(
                credentials['site_url'],
                credentials['email'],
                credentials['api_token']
            )
            
            users = jira_client.search_users(query, max_results)
            
            if not users:
                return [
                    types.TextContent(
                        type="text",
                        text=f"ℹ️ **No users found** matching '{query}'"
                    )
                ]
            
            # Format user list
            result_lines = [f"👥 **User Search Results** (query: '{query}')\n"]
            
            for user in users[:max_results]:
                status = "✓" if user['active'] else "○"
                result_lines.append(f"{status} **{user['display_name']}**")
                result_lines.append(f"  └─ Email: {user['email']}")
                result_lines.append(f"  └─ Account ID: {user['account_id']}")
                result_lines.append("")
            
            result_lines.append(f"**Total results**: {len(users)}")
            
            return [
                types.TextContent(
                    type="text",
                    text="\n".join(result_lines)
                )
            ]
        
        except (WorkspaceError, JiraClientError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error searching users: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    def get_server_info(self) -> Dict[str, Any]:
        """
        Get server information.

        Returns:
            Dictionary with server name, version, and registered tools
        """
        return {
            "server_name": self.server_name,
            "server_version": self.server_version,
            "registered_tools": ["jira_workspace"]
        }
