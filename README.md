# Jira MCP Server

A Model Context Protocol (MCP) server for Jira Cloud integration. Enables AI assistants to interact with Jira issues, projects, and workflows through natural language.

## Features

- **Multi-workspace support** - Connect to multiple Jira Cloud instances
- **Complete issue management** - Search, create, update, transition issues
- **Comments & collaboration** - Add, read, update, delete comments
- **Attachments** - Upload, download, and manage file attachments
- **Issue relationships** - Create links and subtasks
- **Project discovery** - List projects and available issue types

## Installation

### Prerequisites

- Python 3.12+
- Poetry
- Jira Cloud instance with API token access

### Setup

```bash
# Clone the repository
cd /Users/jhull/workarea/jira-mcp

# Install dependencies
poetry install

# Run the MCP server
poetry run jira-mcp
```

## Configuration

### Adding a Workspace

Configure Jira workspaces directly through the AI assistant:

```
jira_workspace(
    operation="add_workspace",
    workspace_name="mycompany",
    site_url="mycompany.atlassian.net",
    email="your.email@company.com",
    api_token="YOUR_API_TOKEN"
)
```

### Getting a Jira API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a label (e.g., "AI Assistant MCP")
4. Copy the token (you can't view it again!)

## Usage

### Basic Operations

**Test connectivity:**
```
jira_workspace(operation="hello")
```

**Search issues:**
```
jira_issues(operation="search", jql="project = MYPROJ AND status = Open")
```

**Create an issue:**
```
jira_issues(
    operation="create",
    project_key="MYPROJ",
    issue_type="Task",
    summary="New task from AI",
    description="Task description here"
)
```

**Add a comment:**
```
jira_issues(
    operation="add_comment",
    issue_key="MYPROJ-123",
    comment="This is a comment from the AI assistant"
)
```

## Architecture

- `jira_mcp/server.py` - Main server entry point
- `jira_mcp/mcp_server.py` - MCP tool registration and routing
- `jira_mcp/workspace_manager.py` - Multi-workspace configuration
- `jira_mcp/jira_client.py` - Jira API client wrapper
- `jira_mcp/issue_manager.py` - Issue operations
- `jira_mcp/project_manager.py` - Project operations

## Development

```bash
# Run tests
poetry run pytest

# Lint code
poetry run pylint jira_mcp/

# Type checking
poetry run mypy jira_mcp/
```

## License

MIT License

## Contributing

Contributions welcome! Please read CONTRIBUTING.md for details.
