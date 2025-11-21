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
from .issue_manager import IssueManager, IssueManagerError

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
                ),
                types.Tool(
                    name="jira_projects",
                    description=(
                        "Perform Jira project operations: list projects and get project details.\n\n"
                        "Operations:\n"
                        "- list: List all accessible projects\n"
                        "- get: Get detailed information about a specific project\n"
                        "- get_issue_types: Get available issue types for a project\n\n"
                        "Use this tool to discover available projects and their configuration."
                    ),
                    inputSchema={
                        "type": "object",
                        "required": ["operation"],
                        "properties": {
                            "operation": {
                                "type": "string",
                                "enum": ["list", "get", "get_issue_types"],
                                "description": "Operation to perform"
                            },
                            "project_key": {
                                "type": "string",
                                "description": "Project key (for get, get_issue_types) - e.g., 'PROJ', 'DEV'"
                            }
                        },
                        "additionalProperties": False
                    }
                ),
                types.Tool(
                    name="jira_issues",
                    description=(
                        "Perform Jira issue operations: search, create, read, update, assign, transition, and manage comments.\n\n"
                        "Core Operations:\n"
                        "- search: Search issues using JQL (Jira Query Language)\n"
                        "- read: Get full details of a specific issue\n"
                        "- create: Create a new issue with fields\n"
                        "- update: Update issue fields\n"
                        "- assign: Assign issue to a user\n"
                        "- transition: Move issue through workflow (e.g., 'To Do' → 'In Progress')\n"
                        "- get_transitions: Get available transitions for an issue\n\n"
                        "Comment Operations:\n"
                        "- list_comments: Get all comments on an issue\n"
                        "- add_comment: Add a new comment to an issue\n"
                        "- update_comment: Update an existing comment\n"
                        "- delete_comment: Delete a comment\n\n"
                        "Attachment Operations:\n"
                        "- list_attachments: Get all attachments on an issue\n"
                        "- add_attachment: Upload a file attachment to an issue\n"
                        "- delete_attachment: Remove an attachment\n\n"
                        "Link Operations:\n"
                        "- create_link: Link two issues with a relationship type\n"
                        "- delete_link: Remove a link between issues\n"
                        "- list_links: Get all links for an issue\n\n"
                        "Subtask Operations:\n"
                        "- create_subtask: Create a subtask under a parent issue\n"
                        "- list_subtasks: Get all subtasks for an issue\n\n"
                        "Use this tool for complete issue lifecycle management."
                    ),
                    inputSchema={
                        "type": "object",
                        "required": ["operation"],
                        "properties": {
                            "operation": {
                                "type": "string",
                                "enum": [
                                    "search", "read", "create", "update", "assign", "transition",
                                    "get_transitions", "list_comments", "add_comment",
                                    "update_comment", "delete_comment", "list_attachments",
                                    "add_attachment", "delete_attachment", "create_link",
                                    "delete_link", "list_links", "create_subtask", "list_subtasks"
                                ],
                                "description": "Operation to perform"
                            },
                            "jql": {
                                "type": "string",
                                "description": "JQL query string (for search) - e.g., 'project = ENG AND status = Open'"
                            },
                            "issue_key": {
                                "type": "string",
                                "description": "Issue key (for read, update, assign, transition, get_transitions) - e.g., 'ENG-123'"
                            },
                            "project_key": {
                                "type": "string",
                                "description": "Project key (for create) - e.g., 'ENG'"
                            },
                            "summary": {
                                "type": "string",
                                "description": "Issue summary/title (for create, update)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Issue description (for create, update)"
                            },
                            "issue_type": {
                                "type": "string",
                                "description": "Issue type name (for create) - e.g., 'Task', 'Bug', 'Story'"
                            },
                            "assignee": {
                                "type": "string",
                                "description": "Assignee account ID or username (for create, update, assign)"
                            },
                            "priority": {
                                "type": "string",
                                "description": "Priority name (for create, update) - e.g., 'High', 'Medium', 'Low'"
                            },
                            "labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of labels (for create, update)"
                            },
                            "transition": {
                                "type": "string",
                                "description": "Transition name or ID (for transition) - e.g., 'In Progress', 'Done'"
                            },
                            "comment": {
                                "type": "string",
                                "description": "Optional comment (for transition)"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results (for search). Default: 50"
                            },
                            "body": {
                                "type": "string",
                                "description": "Comment text body (for add_comment, update_comment)"
                            },
                            "comment_id": {
                                "type": "string",
                                "description": "Comment ID (for update_comment, delete_comment)"
                            },
                            "filepath": {
                                "type": "string",
                                "description": "File path (for add_attachment) - local path to file to upload"
                            },
                            "attachment_id": {
                                "type": "string",
                                "description": "Attachment ID (for delete_attachment)"
                            },
                            "inward_issue": {
                                "type": "string",
                                "description": "Inward issue key (for create_link) - e.g., 'ENG-123'"
                            },
                            "outward_issue": {
                                "type": "string",
                                "description": "Outward issue key (for create_link) - e.g., 'ENG-456'"
                            },
                            "link_type": {
                                "type": "string",
                                "description": "Link type (for create_link) - e.g., 'Relates', 'Blocks', 'Duplicate'. Default: 'Relates'"
                            },
                            "link_id": {
                                "type": "string",
                                "description": "Link ID (for delete_link)"
                            },
                            "parent_key": {
                                "type": "string",
                                "description": "Parent issue key (for create_subtask) - e.g., 'ENG-123'"
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

        # Handle jira_projects tool
        if name == "jira_projects":
            return await self._route_projects_operation(arguments)

        # Handle jira_issues tool
        if name == "jira_issues":
            return await self._route_issues_operation(arguments)

        # Unknown tool
        return [
            types.TextContent(
                type="text",
                text=(
                    f"❌ **Unknown Tool**: '{name}'\n\n"
                    "✅ **Available tools**: jira_workspace, jira_projects, jira_issues"
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

    async def _handle_hello(self, _arguments: Dict[str, Any]) -> List[types.TextContent]:
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

    async def _handle_list_workspaces(self, _arguments: Dict[str, Any]) -> List[types.TextContent]:
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

    async def _handle_get_active_workspace(self, _arguments: Dict[str, Any]) -> List[types.TextContent]:
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

    async def _handle_get_current_user(self, _arguments: Dict[str, Any]) -> List[types.TextContent]:
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

    async def _route_projects_operation(
        self, arguments: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Route jira_projects operations to appropriate handlers."""
        operation = arguments.get("operation")
        if not operation:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Parameter Error**: Missing required parameter 'operation'\n\n"
                        "Available operations: list, get, get_issue_types"
                    )
                )
            ]

        # Route to handlers
        if operation == "list":
            return await self._handle_list_projects(arguments)
        if operation == "get":
            return await self._handle_get_project(arguments)
        if operation == "get_issue_types":
            return await self._handle_get_issue_types(arguments)

        return [
            types.TextContent(
                type="text",
                text=f"❌ **Invalid Operation**: '{operation}'\n\n"
                     "Available operations: list, get, get_issue_types"
            )
        ]

    async def _handle_list_projects(self, _arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle list projects operation."""
        try:
            credentials = self.workspace_manager.get_workspace_credentials()
            active = self.workspace_manager.get_active_workspace()

            jira_client = JiraClient(
                credentials['site_url'],
                credentials['email'],
                credentials['api_token']
            )

            projects = jira_client.get_projects()

            if not projects:
                return [
                    types.TextContent(
                        type="text",
                        text="ℹ️ **No projects found**\n\nYou may not have access to any projects."
                    )
                ]

            # Format project list
            result_lines = [f"📋 **Projects** ({active['name'] if active else 'Unknown'})\n"]

            for project in projects:
                result_lines.append(f"**{project['key']}** - {project['name']}")
                result_lines.append(f"  └─ ID: {project['id']}")
                result_lines.append(f"  └─ Type: {project['project_type']}")
                result_lines.append("")

            result_lines.append(f"**Total projects**: {len(projects)}")

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
            logger.error("Error listing projects: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_get_project(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle get project details operation."""
        project_key = arguments.get("project_key")

        if not project_key:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameter**: project_key\n\n"
                        "Example: jira_projects(operation=\"get\", project_key=\"PROJ\")"
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

            # Get project details
            project = jira_client.jira.project(project_key)

            result = (
                f"📊 **Project: {project.key}**\n\n"
                f"**Name**: {project.name}\n"
                f"**ID**: {project.id}\n"
                f"**Type**: {getattr(project, 'projectTypeKey', 'Unknown')}\n"
                f"**Description**: {getattr(project, 'description', 'No description')}\n"
                f"**Lead**: {getattr(project.lead, 'displayName', 'Unknown') if hasattr(project, 'lead') else 'Unknown'}\n"
            )

            return [
                types.TextContent(
                    type="text",
                    text=result
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
            logger.error("Error getting project details: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: Project '{project_key}' not found or access denied"
                )
            ]

    async def _handle_get_issue_types(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle get issue types for project operation."""
        project_key = arguments.get("project_key")

        if not project_key:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameter**: project_key\n\n"
                        "Example: jira_projects(operation=\"get_issue_types\", project_key=\"PROJ\")"
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

            # Get project to access issue types
            project = jira_client.jira.project(project_key)
            issue_types = project.issueTypes

            if not issue_types:
                return [
                    types.TextContent(
                        type="text",
                        text=f"ℹ️ **No issue types found** for project '{project_key}'"
                    )
                ]

            # Format issue types list
            result_lines = [f"🎫 **Issue Types for {project_key}**\n"]

            for issue_type in issue_types:
                result_lines.append(f"**{issue_type.name}**")
                result_lines.append(f"  └─ ID: {issue_type.id}")
                result_lines.append(f"  └─ Description: {getattr(issue_type, 'description', 'No description')}")
                result_lines.append(f"  └─ Subtask: {'Yes' if getattr(issue_type, 'subtask', False) else 'No'}")
                result_lines.append("")

            result_lines.append(f"**Total issue types**: {len(issue_types)}")

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
            logger.error("Error getting issue types: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: Project '{project_key}' not found or access denied"
                )
            ]

    async def _route_issues_operation(  # pylint: disable=too-many-branches
        self, arguments: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Route jira_issues operations to appropriate handlers."""
        operation = arguments.get("operation")
        if not operation:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Parameter Error**: Missing required parameter 'operation'\n\n"
                        "Available operations: search, read, create, update, assign, transition, get_transitions, "
                        "list_comments, add_comment, update_comment, delete_comment, "
                        "list_attachments, add_attachment, delete_attachment, "
                        "create_link, delete_link, list_links, create_subtask, list_subtasks"
                    )
                )
            ]

        # Route to handlers
        if operation == "search":
            return await self._handle_search_issues(arguments)
        if operation == "read":
            return await self._handle_read_issue(arguments)
        if operation == "create":
            return await self._handle_create_issue(arguments)
        if operation == "update":
            return await self._handle_update_issue(arguments)
        if operation == "assign":
            return await self._handle_assign_issue(arguments)
        if operation == "transition":
            return await self._handle_transition_issue(arguments)
        if operation == "get_transitions":
            return await self._handle_get_transitions(arguments)
        if operation == "list_comments":
            return await self._handle_list_comments(arguments)
        if operation == "add_comment":
            return await self._handle_add_comment(arguments)
        if operation == "update_comment":
            return await self._handle_update_comment(arguments)
        if operation == "delete_comment":
            return await self._handle_delete_comment(arguments)
        if operation == "list_attachments":
            return await self._handle_list_attachments(arguments)
        if operation == "add_attachment":
            return await self._handle_add_attachment(arguments)
        if operation == "delete_attachment":
            return await self._handle_delete_attachment(arguments)
        if operation == "create_link":
            return await self._handle_create_link(arguments)
        if operation == "delete_link":
            return await self._handle_delete_link(arguments)
        if operation == "list_links":
            return await self._handle_list_links(arguments)
        if operation == "create_subtask":
            return await self._handle_create_subtask(arguments)
        if operation == "list_subtasks":
            return await self._handle_list_subtasks(arguments)

        return [
            types.TextContent(
                type="text",
                text=f"❌ **Invalid Operation**: '{operation}'\n\n"
                     "Available operations: search, read, create, update, assign, transition, get_transitions, "
                     "list_comments, add_comment, update_comment, delete_comment, "
                     "list_attachments, add_attachment, delete_attachment, "
                     "create_link, delete_link, list_links, create_subtask, list_subtasks"
            )
        ]

    async def _handle_search_issues(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle search issues operation."""
        jql = arguments.get("jql")
        if not jql:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameter**: jql\n\n"
                        "Example: jira_issues(operation=\"search\", jql=\"project = ENG AND status = Open\")"
                    )
                )
            ]

        max_results = arguments.get("max_results", 50)

        try:
            credentials = self.workspace_manager.get_workspace_credentials()
            jira_client = JiraClient(
                credentials['site_url'],
                credentials['email'],
                credentials['api_token']
            )

            issue_manager = IssueManager(jira_client.jira, credentials['site_url'])
            issues = issue_manager.search_issues(jql, max_results)

            if not issues:
                return [
                    types.TextContent(
                        type="text",
                        text=f"ℹ️ **No issues found**\n\nJQL: `{jql}`"
                    )
                ]

            # Format issue list
            result_lines = [f"🔍 **Search Results**\n\nJQL: `{jql}`\n"]

            for issue in issues:
                status_emoji = "✓" if issue['status'] == "Done" else "○"
                result_lines.append(f"{status_emoji} **{issue['key']}**: {issue['summary']}")
                result_lines.append(f"  └─ Status: {issue['status']}")
                result_lines.append(f"  └─ Type: {issue['issue_type']}")
                if issue['assignee']:
                    result_lines.append(f"  └─ Assignee: {issue['assignee']['name']}")
                result_lines.append(f"  └─ URL: {issue['url']}")
                result_lines.append("")

            result_lines.append(f"**Total results**: {len(issues)}")

            return [
                types.TextContent(
                    type="text",
                    text="\n".join(result_lines)
                )
            ]

        except (WorkspaceError, JiraClientError, IssueManagerError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error searching issues: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_read_issue(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle read issue operation."""
        issue_key = arguments.get("issue_key")
        if not issue_key:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameter**: issue_key\n\n"
                        "Example: jira_issues(operation=\"read\", issue_key=\"ENG-123\")"
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

            issue_manager = IssueManager(jira_client.jira, credentials['site_url'])
            issue = issue_manager.get_issue(issue_key)

            # Format issue details
            result = (
                f"📋 **{issue['key']}**: {issue['summary']}\n\n"
                f"**Status**: {issue['status']}\n"
                f"**Type**: {issue['issue_type']}\n"
                f"**Project**: {issue['project']}\n"
                f"**Priority**: {issue['priority'] or 'None'}\n"
                f"**Assignee**: {issue['assignee']['name'] if issue['assignee'] else 'Unassigned'}\n"
                f"**Reporter**: {issue['reporter']['name'] if issue['reporter'] else 'Unknown'}\n"
                f"**Created**: {issue['created']}\n"
                f"**Updated**: {issue['updated']}\n\n"
                f"**Description**:\n{issue.get('description', 'No description')}\n\n"
            )

            if issue.get('labels'):
                result += f"**Labels**: {', '.join(issue['labels'])}\n"

            if issue.get('components'):
                result += f"**Components**: {', '.join(issue['components'])}\n"

            result += f"\n**URL**: {issue['url']}"

            return [
                types.TextContent(
                    type="text",
                    text=result
                )
            ]

        except (WorkspaceError, JiraClientError, IssueManagerError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error reading issue: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_create_issue(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle create issue operation."""
        project_key = arguments.get("project_key")
        summary = arguments.get("summary")
        issue_type = arguments.get("issue_type")

        if not project_key or not summary or not issue_type:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameters**: project_key, summary, issue_type\n\n"
                        "Example: jira_issues(operation=\"create\", project_key=\"ENG\", "
                        "summary=\"Fix bug\", issue_type=\"Bug\")"
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

            issue_manager = IssueManager(jira_client.jira, credentials['site_url'])

            # Extract optional fields
            description = arguments.get("description")
            assignee = arguments.get("assignee")
            priority = arguments.get("priority")
            labels = arguments.get("labels")

            issue = issue_manager.create_issue(
                project_key=project_key,
                summary=summary,
                issue_type=issue_type,
                description=description,
                assignee=assignee,
                priority=priority,
                labels=labels
            )

            result = (
                f"✅ **Issue Created**: {issue['key']}\n\n"
                f"**Summary**: {issue['summary']}\n"
                f"**Type**: {issue['issue_type']}\n"
                f"**Status**: {issue['status']}\n"
                f"**Project**: {issue['project']}\n"
                f"**URL**: {issue['url']}"
            )

            return [
                types.TextContent(
                    type="text",
                    text=result
                )
            ]

        except (WorkspaceError, JiraClientError, IssueManagerError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error creating issue: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_update_issue(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle update issue operation."""
        issue_key = arguments.get("issue_key")
        if not issue_key:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameter**: issue_key\n\n"
                        "Example: jira_issues(operation=\"update\", issue_key=\"ENG-123\", "
                        "summary=\"Updated summary\")"
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

            issue_manager = IssueManager(jira_client.jira, credentials['site_url'])

            # Extract optional update fields
            summary = arguments.get("summary")
            description = arguments.get("description")
            assignee = arguments.get("assignee")
            priority = arguments.get("priority")
            labels = arguments.get("labels")

            issue = issue_manager.update_issue(
                issue_key=issue_key,
                summary=summary,
                description=description,
                assignee=assignee,
                priority=priority,
                labels=labels
            )

            result = (
                f"✅ **Issue Updated**: {issue['key']}\n\n"
                f"**Summary**: {issue['summary']}\n"
                f"**Status**: {issue['status']}\n"
                f"**URL**: {issue['url']}"
            )

            return [
                types.TextContent(
                    type="text",
                    text=result
                )
            ]

        except (WorkspaceError, JiraClientError, IssueManagerError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error updating issue: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_assign_issue(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle assign issue operation."""
        issue_key = arguments.get("issue_key")
        assignee = arguments.get("assignee")

        if not issue_key or not assignee:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameters**: issue_key, assignee\n\n"
                        "Example: jira_issues(operation=\"assign\", issue_key=\"ENG-123\", "
                        "assignee=\"user@example.com\")"
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

            issue_manager = IssueManager(jira_client.jira, credentials['site_url'])
            issue = issue_manager.assign_issue(issue_key, assignee)

            result = (
                f"✅ **Issue Assigned**: {issue['key']}\n\n"
                f"**Assignee**: {issue['assignee']['name'] if issue['assignee'] else 'Unassigned'}\n"
                f"**URL**: {issue['url']}"
            )

            return [
                types.TextContent(
                    type="text",
                    text=result
                )
            ]

        except (WorkspaceError, JiraClientError, IssueManagerError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error assigning issue: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_transition_issue(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle transition issue operation."""
        issue_key = arguments.get("issue_key")
        transition = arguments.get("transition")

        if not issue_key or not transition:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameters**: issue_key, transition\n\n"
                        "Example: jira_issues(operation=\"transition\", issue_key=\"ENG-123\", "
                        "transition=\"In Progress\")"
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

            issue_manager = IssueManager(jira_client.jira, credentials['site_url'])
            comment = arguments.get("comment")

            issue = issue_manager.transition_issue(issue_key, transition, comment)

            result = (
                f"✅ **Issue Transitioned**: {issue['key']}\n\n"
                f"**New Status**: {issue['status']}\n"
                f"**URL**: {issue['url']}"
            )

            return [
                types.TextContent(
                    type="text",
                    text=result
                )
            ]

        except (WorkspaceError, JiraClientError, IssueManagerError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error transitioning issue: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_get_transitions(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle get transitions operation."""
        issue_key = arguments.get("issue_key")
        if not issue_key:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameter**: issue_key\n\n"
                        "Example: jira_issues(operation=\"get_transitions\", issue_key=\"ENG-123\")"
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

            issue_manager = IssueManager(jira_client.jira, credentials['site_url'])
            transitions = issue_manager.get_transitions(issue_key)

            if not transitions:
                return [
                    types.TextContent(
                        type="text",
                        text=f"ℹ️ **No transitions available** for {issue_key}"
                    )
                ]

            # Format transitions list
            result_lines = [f"🔄 **Available Transitions for {issue_key}**\n"]

            for trans in transitions:
                result_lines.append(f"- **{trans['name']}** (ID: {trans['id']})")

            return [
                types.TextContent(
                    type="text",
                    text="\n".join(result_lines)
                )
            ]

        except (WorkspaceError, JiraClientError, IssueManagerError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error getting transitions: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_list_comments(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle list comments operation."""
        issue_key = arguments.get("issue_key")
        if not issue_key:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameter**: issue_key\n\n"
                        "Example: jira_issues(operation=\"list_comments\", issue_key=\"ENG-123\")"
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

            issue_manager = IssueManager(jira_client.jira, credentials['site_url'])
            comments = issue_manager.list_comments(issue_key)

            if not comments:
                return [
                    types.TextContent(
                        type="text",
                        text=f"ℹ️ **No comments** on {issue_key}"
                    )
                ]

            # Format comments list
            result_lines = [f"💬 **Comments on {issue_key}**\n"]

            for comment in comments:
                result_lines.append(f"**Comment {comment['id']}** by {comment['author']['name']}")
                result_lines.append(f"  └─ Created: {comment['created']}")
                result_lines.append(f"  └─ Updated: {comment['updated']}")
                result_lines.append(f"  └─ Body: {comment['body'][:200]}{'...' if len(comment['body']) > 200 else ''}")
                result_lines.append("")

            result_lines.append(f"**Total comments**: {len(comments)}")

            return [
                types.TextContent(
                    type="text",
                    text="\n".join(result_lines)
                )
            ]

        except (WorkspaceError, JiraClientError, IssueManagerError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error listing comments: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_add_comment(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle add comment operation."""
        issue_key = arguments.get("issue_key")
        body = arguments.get("body")

        if not issue_key or not body:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameters**: issue_key, body\n\n"
                        "Example: jira_issues(operation=\"add_comment\", issue_key=\"ENG-123\", "
                        "body=\"This is my comment\")"
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

            issue_manager = IssueManager(jira_client.jira, credentials['site_url'])
            comment = issue_manager.add_comment(issue_key, body)

            result = (
                f"✅ **Comment Added** to {issue_key}\n\n"
                f"**Comment ID**: {comment['id']}\n"
                f"**Author**: {comment['author']['name']}\n"
                f"**Created**: {comment['created']}\n"
                f"**Body**: {comment['body']}"
            )

            return [
                types.TextContent(
                    type="text",
                    text=result
                )
            ]

        except (WorkspaceError, JiraClientError, IssueManagerError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error adding comment: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_update_comment(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle update comment operation."""
        issue_key = arguments.get("issue_key")
        comment_id = arguments.get("comment_id")
        body = arguments.get("body")

        if not issue_key or not comment_id or not body:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameters**: issue_key, comment_id, body\n\n"
                        "Example: jira_issues(operation=\"update_comment\", issue_key=\"ENG-123\", "
                        "comment_id=\"12345\", body=\"Updated comment text\")"
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

            issue_manager = IssueManager(jira_client.jira, credentials['site_url'])
            comment = issue_manager.update_comment(issue_key, comment_id, body)

            result = (
                f"✅ **Comment Updated** on {issue_key}\n\n"
                f"**Comment ID**: {comment['id']}\n"
                f"**Author**: {comment['author']['name']}\n"
                f"**Updated**: {comment['updated']}\n"
                f"**Body**: {comment['body']}"
            )

            return [
                types.TextContent(
                    type="text",
                    text=result
                )
            ]

        except (WorkspaceError, JiraClientError, IssueManagerError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error updating comment: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_delete_comment(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle delete comment operation."""
        issue_key = arguments.get("issue_key")
        comment_id = arguments.get("comment_id")

        if not issue_key or not comment_id:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameters**: issue_key, comment_id\n\n"
                        "Example: jira_issues(operation=\"delete_comment\", issue_key=\"ENG-123\", "
                        "comment_id=\"12345\")"
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

            issue_manager = IssueManager(jira_client.jira, credentials['site_url'])
            issue_manager.delete_comment(issue_key, comment_id)

            result = (
                f"✅ **Comment Deleted** from {issue_key}\n\n"
                f"**Comment ID**: {comment_id}"
            )

            return [
                types.TextContent(
                    type="text",
                    text=result
                )
            ]

        except (WorkspaceError, JiraClientError, IssueManagerError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error deleting comment: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_list_attachments(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle list attachments operation."""
        issue_key = arguments.get("issue_key")
        if not issue_key:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameter**: issue_key\n\n"
                        "Example: jira_issues(operation=\"list_attachments\", issue_key=\"ENG-123\")"
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

            issue_manager = IssueManager(jira_client.jira, credentials['site_url'])
            attachments = issue_manager.list_attachments(issue_key)

            if not attachments:
                return [
                    types.TextContent(
                        type="text",
                        text=f"ℹ️ **No attachments** on {issue_key}"
                    )
                ]

            # Format attachments list
            result_lines = [f"📎 **Attachments on {issue_key}**\n"]

            for attachment in attachments:
                size_kb = attachment['size'] / 1024
                result_lines.append(f"**{attachment['filename']}** (ID: {attachment['id']})")
                result_lines.append(f"  └─ Size: {size_kb:.1f} KB")
                result_lines.append(f"  └─ Type: {attachment['mime_type']}")
                result_lines.append(f"  └─ Author: {attachment['author']['name']}")
                result_lines.append(f"  └─ Created: {attachment['created']}")
                result_lines.append("")

            result_lines.append(f"**Total attachments**: {len(attachments)}")

            return [
                types.TextContent(
                    type="text",
                    text="\n".join(result_lines)
                )
            ]

        except (WorkspaceError, JiraClientError, IssueManagerError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error listing attachments: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_add_attachment(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle add attachment operation."""
        issue_key = arguments.get("issue_key")
        filepath = arguments.get("filepath")

        if not issue_key or not filepath:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameters**: issue_key, filepath\n\n"
                        "Example: jira_issues(operation=\"add_attachment\", issue_key=\"ENG-123\", "
                        "filepath=\"/path/to/file.pdf\")"
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

            issue_manager = IssueManager(jira_client.jira, credentials['site_url'])
            attachment = issue_manager.add_attachment(issue_key, filepath)

            size_kb = attachment['size'] / 1024
            result = (
                f"✅ **Attachment Added** to {issue_key}\n\n"
                f"**Filename**: {attachment['filename']}\n"
                f"**ID**: {attachment['id']}\n"
                f"**Size**: {size_kb:.1f} KB\n"
                f"**Type**: {attachment['mime_type']}\n"
                f"**Created**: {attachment['created']}"
            )

            return [
                types.TextContent(
                    type="text",
                    text=result
                )
            ]

        except (WorkspaceError, JiraClientError, IssueManagerError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error adding attachment: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_delete_attachment(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle delete attachment operation."""
        attachment_id = arguments.get("attachment_id")

        if not attachment_id:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameter**: attachment_id\n\n"
                        "Example: jira_issues(operation=\"delete_attachment\", attachment_id=\"12345\")"
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

            issue_manager = IssueManager(jira_client.jira, credentials['site_url'])
            issue_manager.delete_attachment(attachment_id)

            result = (
                f"✅ **Attachment Deleted**\n\n"
                f"**Attachment ID**: {attachment_id}"
            )

            return [
                types.TextContent(
                    type="text",
                    text=result
                )
            ]

        except (WorkspaceError, JiraClientError, IssueManagerError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error deleting attachment: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_create_link(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle create link operation."""
        inward_issue = arguments.get("inward_issue")
        outward_issue = arguments.get("outward_issue")
        link_type = arguments.get("link_type", "Relates")

        if not inward_issue or not outward_issue:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameters**: inward_issue, outward_issue\n\n"
                        "Example: jira_issues(operation=\"create_link\", inward_issue=\"ENG-123\", "
                        "outward_issue=\"ENG-456\", link_type=\"Relates\")"
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

            issue_manager = IssueManager(jira_client.jira, credentials['site_url'])
            link = issue_manager.create_link(inward_issue, outward_issue, link_type)

            result = (
                f"✅ **Link Created**\n\n"
                f"**Inward Issue**: {link['inward_issue']}\n"
                f"**Outward Issue**: {link['outward_issue']}\n"
                f"**Link Type**: {link['link_type']}"
            )

            return [
                types.TextContent(
                    type="text",
                    text=result
                )
            ]

        except (WorkspaceError, JiraClientError, IssueManagerError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error creating link: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_delete_link(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle delete link operation."""
        link_id = arguments.get("link_id")

        if not link_id:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameter**: link_id\n\n"
                        "Example: jira_issues(operation=\"delete_link\", link_id=\"12345\")"
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

            issue_manager = IssueManager(jira_client.jira, credentials['site_url'])
            issue_manager.delete_link(link_id)

            result = (
                f"✅ **Link Deleted**\n\n"
                f"**Link ID**: {link_id}"
            )

            return [
                types.TextContent(
                    type="text",
                    text=result
                )
            ]

        except (WorkspaceError, JiraClientError, IssueManagerError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error deleting link: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_list_links(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle list links operation."""
        issue_key = arguments.get("issue_key")
        if not issue_key:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameter**: issue_key\n\n"
                        "Example: jira_issues(operation=\"list_links\", issue_key=\"ENG-123\")"
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

            issue_manager = IssueManager(jira_client.jira, credentials['site_url'])
            links = issue_manager.list_links(issue_key)

            if not links:
                return [
                    types.TextContent(
                        type="text",
                        text=f"ℹ️ **No links** on {issue_key}"
                    )
                ]

            # Format links list
            result_lines = [f"🔗 **Links on {issue_key}**\n"]

            for link in links:
                result_lines.append(f"**{link['type']}** ({link['direction']}) - ID: {link['id']}")
                result_lines.append(f"  └─ Related Issue: {link['related_issue']}")
                result_lines.append(f"  └─ Summary: {link['related_summary']}")
                result_lines.append("")

            result_lines.append(f"**Total links**: {len(links)}")

            return [
                types.TextContent(
                    type="text",
                    text="\n".join(result_lines)
                )
            ]

        except (WorkspaceError, JiraClientError, IssueManagerError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error listing links: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_create_subtask(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle create subtask operation."""
        parent_key = arguments.get("parent_key")
        summary = arguments.get("summary")

        if not parent_key or not summary:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameters**: parent_key, summary\n\n"
                        "Example: jira_issues(operation=\"create_subtask\", parent_key=\"ENG-123\", "
                        "summary=\"Subtask title\")"
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

            issue_manager = IssueManager(jira_client.jira, credentials['site_url'])

            # Extract optional fields
            description = arguments.get("description")
            assignee = arguments.get("assignee")

            subtask = issue_manager.create_subtask(
                parent_key=parent_key,
                summary=summary,
                description=description,
                assignee=assignee
            )

            result = (
                f"✅ **Subtask Created**: {subtask['key']}\n\n"
                f"**Summary**: {subtask['summary']}\n"
                f"**Parent**: {parent_key}\n"
                f"**Status**: {subtask['status']}\n"
                f"**URL**: {subtask['url']}"
            )

            return [
                types.TextContent(
                    type="text",
                    text=result
                )
            ]

        except (WorkspaceError, JiraClientError, IssueManagerError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error creating subtask: %s", error)
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]

    async def _handle_list_subtasks(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle list subtasks operation."""
        issue_key = arguments.get("issue_key")
        if not issue_key:
            return [
                types.TextContent(
                    type="text",
                    text=(
                        "❌ **Missing Required Parameter**: issue_key\n\n"
                        "Example: jira_issues(operation=\"list_subtasks\", issue_key=\"ENG-123\")"
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

            issue_manager = IssueManager(jira_client.jira, credentials['site_url'])
            subtasks = issue_manager.list_subtasks(issue_key)

            if not subtasks:
                return [
                    types.TextContent(
                        type="text",
                        text=f"ℹ️ **No subtasks** on {issue_key}"
                    )
                ]

            # Format subtasks list
            result_lines = [f"📋 **Subtasks of {issue_key}**\n"]

            for subtask in subtasks:
                status_emoji = "✓" if subtask['status'] == "Done" else "○"
                result_lines.append(f"{status_emoji} **{subtask['key']}**: {subtask['summary']}")
                result_lines.append(f"  └─ Status: {subtask['status']}")
                if subtask['assignee']:
                    result_lines.append(f"  └─ Assignee: {subtask['assignee']['name']}")
                result_lines.append(f"  └─ URL: {subtask['url']}")
                result_lines.append("")

            result_lines.append(f"**Total subtasks**: {len(subtasks)}")

            return [
                types.TextContent(
                    type="text",
                    text="\n".join(result_lines)
                )
            ]

        except (WorkspaceError, JiraClientError, IssueManagerError) as error:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ **Error**: {str(error)}"
                )
            ]
        except Exception as error:
            logger.error("Error listing subtasks: %s", error)
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
            "registered_tools": ["jira_workspace", "jira_projects", "jira_issues"]
        }
