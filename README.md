# Jira MCP Server

> **Enterprise-grade Model Context Protocol server for comprehensive Jira Cloud integration**

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Code Quality](https://img.shields.io/badge/pylint-10.00%2F10-brightgreen.svg)](https://pylint.org/)
[![MCP Protocol](https://img.shields.io/badge/MCP-STDIO-orange.svg)](https://modelcontextprotocol.io/)

A production-ready MCP server that provides AI assistants with complete access to Jira Cloud. Enables natural language interaction with Jira for issue management, project navigation, and workflow automation across multiple Jira workspaces.

## ✨ Features

### 🏢 Multi-Workspace Management
- Connect to multiple Jira Cloud instances simultaneously
- Seamlessly switch between workspaces
- Secure API token authentication
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
- **Jira Cloud** - Active instance with API access

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

### Getting Your Jira API Token

1. Navigate to [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click **"Create API token"**
3. Label it (e.g., "AI Assistant MCP")
4. **Copy the token immediately** (you won't be able to view it again!)

### Adding a Workspace

Configure workspaces directly through your AI assistant:

```python
jira_workspace(
    operation="add_workspace",
    workspace_name="mycompany",
    site_url="mycompany.atlassian.net",  # or https://mycompany.atlassian.net
    email="your.email@company.com",
    api_token="YOUR_API_TOKEN_HERE"
)
```

The server will:
- Validate your credentials
- Test the connection
- Store the configuration securely in `accounts/mycompany.json`
- Set it as the active workspace (if it's your first)

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
├── accounts/                 # Workspace configurations (gitignored)
├── docs/                     # Documentation
│   ├── implementation.md     # Implementation specification
│   ├── requirements.md       # Requirements document
│   └── ...
├── pyproject.toml           # Poetry dependencies & config
├── poetry.lock              # Locked dependencies
└── README.md                # This file
```

### MCP Tools

The server exposes **3 MCP tools** with **31 total operations**:

1. **`jira_workspace`** (9 operations) - Workspace management
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

- **Total Operations**: 31 across 3 MCP tools
- **Lines of Code**: ~4,600 production code
- **Code Quality**: 10.00/10 pylint score
- **Test Coverage**: Manual MCP integration testing
- **Python Version**: 3.12+

## 🔒 Security

### Best Practices

- **API Tokens**: Stored in local JSON files with 600 permissions
- **No Secrets in Code**: All credentials loaded from configuration
- **OAuth Flow**: Supports Jira API token authentication
- **Input Validation**: All parameters validated before API calls
- **Error Handling**: Secure error messages without sensitive data

### Workspace Storage

Workspace configurations are stored in `accounts/*.json` with restricted permissions:
```json
{
  "name": "mycompany",
  "site_url": "https://mycompany.atlassian.net",
  "email": "user@company.com",
  "api_token": "YOUR_TOKEN",
  "created_at": "2025-11-21T10:30:00"
}
```

**Important**: Add `accounts/` to your `.gitignore` to prevent credential leaks!

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
