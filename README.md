> ## ⚠️ IMPORTANT DISCLAIMER
>
> **This code is 100% AI-generated.** Use at your own risk. The authors make no guarantees about the reliability, security, or fitness for any particular purpose. Thoroughly review and test all code before using in production environments.

# Jira MCP Server

> **Enterprise-grade Model Context Protocol server for comprehensive Jira Cloud and Server/Data Center integration**

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Code Quality](https://img.shields.io/badge/pylint-10.00%2F10-brightgreen.svg)](https://pylint.org/)
[![MCP Protocol](https://img.shields.io/badge/MCP-STDIO-orange.svg)](https://modelcontextprotocol.io/)

A production-ready MCP server that provides AI assistants with complete access to Jira Cloud and Jira Server/Data Center. Enables natural language interaction with Jira for issue management, project navigation, and workflow automation across multiple Jira workspaces.

## ✨ Features

### 🏢 Multi-Workspace Management
- Connect to multiple Jira Cloud and Server/Data Center instances
- Support for both Cloud (API token) and Server/Data Center (PAT) authentication
- Seamlessly switch between workspaces
- XDG-compliant configuration storage (~/.config/jira-mcp/)
- Secure skeleton file workflow for credential management
- Workspace validation and credential management

### 🎫 Complete Issue Lifecycle
- **Search**: Powerful JQL-based issue search
- **CRUD Operations**: Create, read, update, and delete issues
- **Workflow Management**: Transition issues through custom workflows
- **Assignment**: Assign issues to team members
- **Custom Fields**: Support for custom field manipulation

### 💬 Collaboration Features
- **Comments**: Full CRUD operations on issue comments
- **Attachments**: Upload, list, and delete file attachments
- **Links**: Create relationships between issues (Relates, Blocks, Duplicate, etc.)
- **Subtasks**: Create and manage parent-child task hierarchies

### 📊 Project & Discovery
- List all accessible projects
- Get detailed project information
- Enumerate available issue types
- User search for assignments

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** - Required for modern Python features
- **Poetry** - Dependency management
- **Jira Cloud or Server/Data Center** - Active instance with API access

### Installation

```bash
# Clone the repository
git clone [repository-url]
cd jira-mcp

# Install dependencies with Poetry
poetry install

# Start the MCP server
poetry run start-mcp
```

The server runs using STDIO transport and communicates via the Model Context Protocol.

## 🔧 Configuration

### Configuration Location

All workspace configurations are stored in **`~/.config/jira-mcp/workspaces/`** with secure 600 permissions.

### Getting Your Credentials

**For Jira Cloud:**
1. Navigate to [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click **"Create API token"**
3. Label it (e.g., "AI Assistant MCP")
4. **Copy the token immediately** (you won't be able to view it again!)

**For Jira Server/Data Center:**
1. Generate a Personal Access Token (PAT) from your Jira Server instance
2. Follow your organization's process for PAT creation
3. Copy the token for use in configuration

### Adding a Workspace

**Recommended Method: Skeleton File (Secure)**

Create a skeleton configuration file that you edit directly:

```python
# 1. Create skeleton file
jira_workspace(
    operation="create_workspace_skeleton",
    workspace_name="mycompany",
    auth_type="cloud"  # or "pat" for Server/Data Center
)

# 2. Edit the file at ~/.config/jira-mcp/workspaces/mycompany.json
# 3. Fill in your actual credentials
# 4. Remove the _instructions section
# 5. Restart the MCP server
```

**Alternative: Direct Add (Programmatic)**

For Jira Cloud:
```python
jira_workspace(
    operation="add_workspace",
    workspace_name="mycompany",
    site_url="mycompany.atlassian.net",
    email="your.email@company.com",
    api_token="YOUR_API_TOKEN_HERE",
    auth_type="cloud"
)
```

For Jira Server/Data Center:
```python
jira_workspace(
    operation="add_workspace",
    workspace_name="mycompany",
    site_url="jira.company.com",
    email="your.username",
    api_token="YOUR_PERSONAL_ACCESS_TOKEN",
    auth_type="pat"
)
```

The server will:
- Validate your credentials
- Test the connection
- Store the configuration securely in `~/.config/jira-mcp/workspaces/mycompany.json`
- Set it as the active workspace (if it's your first)

See **[CONFIGURATION.md](CONFIGURATION.md)** for detailed setup instructions.

### Managing Workspaces

```python
# List all configured workspaces
jira_workspace(operation="list_workspaces")

# Switch to a different workspace
jira_workspace(operation="switch_workspace", workspace_name="otherworkspace")

# Get current workspace info
jira_workspace(operation="get_active_workspace")

# Validate workspace credentials
jira_workspace(operation="validate_workspace", workspace_name="mycompany")

# Remove a workspace
jira_workspace(operation="remove_workspace", workspace_name="oldworkspace")
```

## 📖 Usage Guide

### 🔍 Searching & Reading Issues

**Search with JQL:**
```python
jira_issues(
    operation="search",
    jql="project = ENG AND status = Open AND assignee = currentUser()",
    max_results=50
)
```

**Get issue details:**
```python
jira_issues(operation="read", issue_key="ENG-123")
```

**Get available transitions:**
```python
jira_issues(operation="get_transitions", issue_key="ENG-123")
```

### ✏️ Creating & Updating Issues

**Create a new issue:**
```python
jira_issues(
    operation="create",
    project_key="ENG",
    issue_type="Task",
    summary="Implement new feature",
    description="Detailed description here",
    priority="High",
    labels=["backend", "urgent"],
    assignee="user@example.com"  # Optional
)
```

**Update an issue:**
```python
jira_issues(
    operation="update",
    issue_key="ENG-123",
    summary="Updated task title",
    description="Updated description",
    priority="Medium"
)
```

**Assign an issue:**
```python
jira_issues(
    operation="assign",
    issue_key="ENG-123",
    assignee="user@example.com"
)
```

**Transition through workflow:**
```python
jira_issues(
    operation="transition",
    issue_key="ENG-123",
    transition="In Progress",
    comment="Starting work on this task"  # Optional
)
```

### 💬 Comments

**List comments:**
```python
jira_issues(operation="list_comments", issue_key="ENG-123")
```

**Add a comment:**
```python
jira_issues(
    operation="add_comment",
    issue_key="ENG-123",
    body="This is a comment from the AI assistant"
)
```

**Update a comment:**
```python
jira_issues(
    operation="update_comment",
    issue_key="ENG-123",
    comment_id="12345",
    body="Updated comment text"
)
```

**Delete a comment:**
```python
jira_issues(
    operation="delete_comment",
    issue_key="ENG-123",
    comment_id="12345"
)
```

### 📎 Attachments

**List attachments:**
```python
jira_issues(operation="list_attachments", issue_key="ENG-123")
```

**Upload a file:**
```python
jira_issues(
    operation="add_attachment",
    issue_key="ENG-123",
    filepath="/path/to/document.pdf"
)
```

**Delete an attachment:**
```python
jira_issues(
    operation="delete_attachment",
    attachment_id="67890"
)
```

### 🔗 Issue Links & Relationships

**Create a link:**
```python
jira_issues(
    operation="create_link",
    inward_issue="ENG-123",
    outward_issue="ENG-456",
    link_type="Blocks"  # or "Relates", "Duplicate", etc.
)
```

**List links:**
```python
jira_issues(operation="list_links", issue_key="ENG-123")
```

**Delete a link:**
```python
jira_issues(operation="delete_link", link_id="11111")
```

### 📋 Subtasks

**Create a subtask:**
```python
jira_issues(
    operation="create_subtask",
    parent_key="ENG-123",
    summary="Subtask: Implement unit tests",
    description="Write comprehensive tests",
    assignee="developer@example.com"  # Optional
)
```

**List subtasks:**
```python
jira_issues(operation="list_subtasks", issue_key="ENG-123")
```

### 📊 Projects

**List all projects:**
```python
jira_projects(operation="list")
```

**Get project details:**
```python
jira_projects(operation="get", project_key="ENG")
```

**Get issue types for a project:**
```python
jira_projects(operation="get_issue_types", project_key="ENG")
```

### 👥 Users

**Get current user:**
```python
jira_workspace(operation="get_current_user")
```

**Search for users:**
```python
jira_workspace(
    operation="search_users",
    query="john",
    max_results=10
)
```

## 🏗️ Architecture

### Project Structure

```
jira-mcp/
├── jira_mcp/
│   ├── __init__.py           # Package initialization
│   ├── __main__.py           # Entry point for module execution
│   ├── server.py             # Main server & STDIO transport
│   ├── mcp_server.py         # MCP tool registration & routing
│   ├── config.py             # Configuration management
│   ├── workspace_manager.py  # Multi-workspace handling
│   ├── jira_client.py        # Jira API client wrapper
│   └── issue_manager.py      # Issue operations (CRUD, comments, etc.)
├── docs/                     # Documentation
│   ├── implementation.md     # Implementation specification
│   ├── requirements.md       # Requirements document
│   └── ...
├── pyproject.toml           # Poetry dependencies & config
├── poetry.lock              # Locked dependencies
├── CONFIGURATION.md         # Detailed configuration guide
└── README.md                # This file

~/.config/jira-mcp/          # XDG config directory (created automatically)
├── workspaces/              # Workspace configurations
│   ├── workspace1.json
│   └── workspace2.json
└── active_workspace         # Currently active workspace
```

### MCP Tools

The server exposes **3 MCP tools** with **32 total operations**:

1. **`jira_workspace`** (10 operations) - Workspace management (includes `create_workspace_skeleton`)
2. **`jira_projects`** (3 operations) - Project discovery
3. **`jira_issues`** (19 operations) - Complete issue management

### Technology Stack

- **Python 3.12+** - Modern Python with type hints
- **MCP SDK** - Model Context Protocol implementation
- **Jira Python Library** - Official Jira API client
- **Poetry** - Dependency management and packaging
- **STDIO Transport** - Standard MCP communication protocol

## 🧪 Development

### Code Quality

```bash
# Run pylint (target: 10.00/10)
poetry run pylint jira_mcp/

# Type checking with mypy
poetry run mypy jira_mcp/

# Security analysis
poetry run bandit -r jira_mcp/

# Dependency security audit
poetry run pip-audit
```

### Testing

```bash
# Run test suite
poetry run pytest

# With coverage
poetry run pytest --cov=jira_mcp
```

### Project Standards

- **Code Quality**: Pylint score of 10.00/10 maintained
- **Type Safety**: Full type hints with mypy validation
- **Security**: Bandit security scanning, no secrets in code
- **Documentation**: Comprehensive docstrings for all functions
- **Error Handling**: Proper exception handling at all layers

## 📊 Statistics

- **Total Operations**: 32 across 3 MCP tools
- **Lines of Code**: ~4,600 production code
- **Code Quality**: 10.00/10 pylint score
- **Test Coverage**: Manual MCP integration testing
- **Python Version**: 3.12+
- **Supported Platforms**: Jira Cloud + Jira Server/Data Center

## 🔒 Security

### Best Practices

- **API Tokens**: Stored in `~/.config/jira-mcp/workspaces/` with 600 permissions
- **XDG Compliance**: Configuration follows XDG Base Directory specification
- **No Secrets in Code**: All credentials loaded from configuration files
- **Authentication Types**: Supports both Cloud (API token) and Server/Data Center (PAT)
- **Input Validation**: All parameters validated before API calls
- **Error Handling**: Secure error messages without sensitive data
- **Skeleton Workflow**: Recommended approach to avoid passing credentials through tool calls

### Workspace Storage

Workspace configurations are stored in `~/.config/jira-mcp/workspaces/*.json` with restricted permissions:

**Jira Cloud:**
```json
{
  "name": "mycompany",
  "site_url": "https://mycompany.atlassian.net",
  "email": "user@company.com",
  "api_token": "YOUR_API_TOKEN",
  "auth_type": "cloud",
  "created": "2026-02-05T07:20:00.000000",
  "last_validated": null
}
```

**Jira Server/Data Center:**
```json
{
  "name": "myserver",
  "site_url": "https://jira.company.com",
  "email": "username",
  "api_token": "YOUR_PERSONAL_ACCESS_TOKEN",
  "auth_type": "pat",
  "created": "2026-02-05T07:20:00.000000",
  "last_validated": null
}
```

**Security Notes**:
- Files are automatically created with 600 permissions (owner read/write only)
- Configuration directory is in user's home directory, not in project repository
- Use `create_workspace_skeleton` operation to avoid passing credentials via tool calls

## 🐛 Troubleshooting

### Common Issues

**"No active workspace" error:**
```bash
# Add a workspace first
jira_workspace(operation="add_workspace", ...)
```

**"Authentication failed" error:**
- Verify your API token is correct
- Check that your email matches your Atlassian account
- Ensure the site URL is correct (e.g., `company.atlassian.net`)

**"Invalid JQL" error:**
- Test your JQL in Jira's web interface first
- Ensure field names are correct (case-sensitive)
- Check for proper quoting of values

**File attachment upload fails:**
- Verify the file path exists and is readable
- Check file size limits (Jira defaults to 10MB)
- Ensure you have attachment permissions in the project

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Maintain 10.00/10 pylint score
5. Add tests for new functionality
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with the [Model Context Protocol](https://modelcontextprotocol.io/)
- Uses the [Jira Python Library](https://jira.readthedocs.io/)
- Developed with [Poetry](https://python-poetry.org/)

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the `docs/` directory for detailed documentation
- Review `docs/implementation.md` for technical details

---

**Made with ❤️ for AI-powered Jira management**
