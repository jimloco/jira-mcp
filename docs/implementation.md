# Jira MCP Server Implementation

**Project:** Jira Model Context Protocol (MCP) Server  
**Repository:** `rosebud:/var/lib/git/jira-mcp`  
**Local Path:** `/Users/jhull/workarea/jira-mcp`

## Project Status

**Current Phase:** Phase 1 Complete ✅ - Ready for Phase 2  
**Last Updated:** November 20, 2025  
**Git Commit:** `01e6644` on `main` branch

### Completed Milestones
- ✅ **Phase 1: Project Bootstrap & Infrastructure** (Nov 20, 2025)
  - Poetry project initialized with all dependencies
  - Package structure created (jira_mcp/)
  - Core server files implemented
  - Configuration system in place
  - Documentation complete

### Current Status
- **Phase 2: Workspace Management** - Ready to start
- 3 tools planned: `jira_workspace`, `jira_issues`, `jira_projects`
- 31 operations total across all tools

## Overview

A Model Context Protocol (MCP) server that provides AI assistants with direct access to Jira Cloud instances. Enables natural language interaction with Jira for issue management, project navigation, and workflow automation across multiple Jira workspaces.

**Key Capabilities:**
- Multi-workspace support (switch between different Atlassian instances)
- Complete issue lifecycle management (create, read, update, transition)
- Comments, attachments, links, and subtasks
- JQL search integration
- Project and issue type discovery

**Pattern Source:** Follows google-workspace-mcp architecture for semantic tool aggregation and multi-account management.

## Key Requirements

1. **MCP Protocol Compliance**
   - STDIO transport with clean stdout/stderr separation
   - Structured tool registration with accurate schemas
   - Graceful error handling with user-friendly messages
   - JSON-based request/response format

2. **Multi-Workspace Architecture**
   - Support multiple Jira Cloud instances simultaneously
   - Workspace-specific configuration with API token authentication
   - Active workspace switching without server restart
   - Workspace validation and credential testing

3. **Issue Management**
   - Full CRUD operations on Jira issues
   - JQL-based search with result pagination
   - Workflow transitions with validation
   - Assignment, labels, and field updates
   - Comments (create, read, update, delete)
   - Attachments (upload, download, list, delete)
   - Issue links (create, delete, list relationships)
   - Subtask creation and management

4. **Security & Authentication**
   - Jira API token-based authentication
   - Secure credential storage (encrypted or file permissions)
   - No hardcoded credentials in source code
   - Workspace isolation (credentials never shared)

## Code Reuse Opportunities

### Existing Components (Fully Reusable)

| Component | Location | Reuse Strategy |
|-----------|----------|----------------|
| **MCP Server Pattern** | `../google-mcp/google_workspace_mcp/mcp_server.py` | Copy tool registration and dispatch architecture |
| **Multi-Account Manager** | `../google-mcp/google_workspace_mcp/account_manager.py` | Adapt for workspace management (API token vs OAuth) |
| **Configuration Loading** | `../google-mcp/config.py` | Reuse .env loading and validation patterns |
| **Server Entry Point** | `../google-mcp/google_workspace_mcp/server.py` | Copy async server initialization and signal handling |

### Integration Points (Extend Existing)

| Component | Location | Integration Strategy |
|-----------|----------|---------------------|
| **Tool Dispatch Pattern** | `../google-mcp/google_workspace_mcp/mcp_server.py#_dispatch_tool_call` | Implement similar routing for jira_workspace, jira_issues, jira_projects |
| **Operation Routing** | `../google-mcp/google_workspace_mcp/mcp_server.py#_route_*_operation` | Create jira-specific routers with operation enum validation |
| **Error Handling** | `../google-mcp/google_workspace_mcp/mcp_server.py#call_tool` | Reuse structured error response format |

### Code Reuse Benefits

- ✅ **Proven MCP Architecture** - Battle-tested tool aggregation pattern from google-mcp
- ✅ **Multi-Workspace Pattern** - Established account switching without server restart
- ✅ **Consistent Developer Experience** - Same tool structure as google-mcp for familiarity
- ✅ **Reduced Development Time** - ~60% code reuse for server infrastructure

### New Components Required

- ❌ **JiraClient** - Jira-specific API wrapper using jira Python library
- ❌ **IssueManager** - Issue CRUD operations, search, transitions
- ❌ **ProjectManager** - Project listing and metadata retrieval
- ❌ **WorkspaceManager** - Workspace config with API token (simpler than OAuth)

## Security Considerations

### Security Requirements

| Area | Requirement | Implementation Notes |
|------|-------------|---------------------|
| **Authentication** | Jira API token authentication | Email + API token per workspace, stored in accounts/ directory |
| **Authorization** | Respect Jira permissions | API calls use user's token, honoring Jira's permission model |
| **Data Protection** | API tokens must be secured | File permissions 600, consider encryption for sensitive environments |
| **Input Validation** | Sanitize all user inputs | Validate issue keys, JQL queries, file paths, workspace names |

### Security Validation

- ✅ **API Token Storage** - Tokens stored in accounts/ with restricted file permissions
- ✅ **Input Validation** - All parameters validated before Jira API calls
- ✅ **No Token Logging** - API tokens never logged or exposed in error messages
- ✅ **Workspace Isolation** - Each workspace has independent credentials

### Security Risks

- ⚠️ **API Token Exposure** - Mitigation: File permissions 600, no git commits of accounts/
- ⚠️ **JQL Injection** - Mitigation: Use Jira Python library's query builders, not string concatenation
- ⚠️ **Path Traversal in Attachments** - Mitigation: Validate and sanitize file paths for downloads

## MCP Tools Architecture

### Tool 1: `jira_workspace`

**Purpose:** Workspace management and connectivity testing

**Operations:**
- `add_workspace` - Configure new Jira instance (name, site_url, email, api_token)
- `list_workspaces` - Show all configured workspaces with active indicator
- `get_active_workspace` - Display current workspace details
- `switch_workspace` - Change active workspace
- `validate_workspace` - Test credentials and API connectivity
- `remove_workspace` - Delete workspace configuration
- `hello` - Test MCP server and Jira API connectivity
- `get_current_user` - Get authenticated user info from active workspace
- `search_users` - Find users by name/email for assignment

### Tool 2: `jira_issues`

**Purpose:** Comprehensive issue management

**Core Operations:**
- `search` - JQL-based issue search with pagination
- `read` - Get full issue details (fields, status, assignee, etc.)
- `create` - Create new issue with validation
- `update` - Update issue fields (summary, description, custom fields)
- `transition` - Move issue through workflow (with available transitions lookup)
- `assign` - Assign/reassign issue to user

**Comments:**
- `list_comments` - Get all comments on an issue
- `add_comment` - Add comment to issue
- `update_comment` - Edit existing comment
- `delete_comment` - Remove comment

**Attachments:**
- `list_attachments` - List all attachments with metadata
- `upload_attachment` - Upload file to issue
- `download_attachment` - Download attachment to local filesystem
- `delete_attachment` - Remove attachment from issue

**Links & Subtasks:**
- `create_link` - Link issues (blocks, relates to, duplicates, etc.)
- `delete_link` - Remove issue link
- `list_links` - Get all linked issues with relationship types
- `create_subtask` - Create subtask under parent issue
- `list_subtasks` - List all subtasks of an issue

### Tool 3: `jira_projects`

**Purpose:** Project discovery and metadata

**Operations:**
- `list` - List all accessible projects
- `get` - Get project details (key, name, description, lead)
- `get_issue_types` - Get available issue types for project (needed for create)

## Implementation Files

### Core Server Infrastructure

| File | Purpose | Action |
|------|---------|--------|
| `pyproject.toml` | Poetry dependencies and project metadata | Create |
| `poetry.lock` | Locked dependency versions | Generate |
| `.env.active` | Active workspace pointer file | Create |
| `.gitignore` | Exclude accounts/, .env files, venv | Create |
| `README.md` | Installation and usage documentation | Create |

### Python Package Structure

| File | Purpose | Action |
|------|---------|--------|
| `jira_mcp/__init__.py` | Package initialization | Create |
| `jira_mcp/__main__.py` | Entry point for `python -m jira_mcp` | Create |
| `jira_mcp/server.py` | Main server entry point with async run() | Create |
| `jira_mcp/mcp_server.py` | MCP tool registration and dispatch | Create |
| `jira_mcp/config.py` | Configuration loading and validation | Create |

### Manager Components

| File | Purpose | Action |
|------|---------|--------|
| `jira_mcp/workspace_manager.py` | Multi-workspace configuration and switching | Create |
| `jira_mcp/jira_client.py` | Jira API client wrapper | Create |
| `jira_mcp/issue_manager.py` | Issue CRUD, search, comments, attachments | Create |
| `jira_mcp/project_manager.py` | Project listing and metadata | Create |

### Configuration & Storage

| File | Purpose | Action |
|------|---------|--------|
| `accounts/` | Workspace configuration directory | Create |
| `accounts/.gitkeep` | Ensure directory tracked but empty | Create |
| `accounts/*.json` | Per-workspace configuration files | Runtime |

## Implementation Task Checklist

### Phase 1: Project Bootstrap & Infrastructure ✅ **COMPLETED**
- [x] Initialize Poetry project with pyproject.toml
- [x] Add dependencies (mcp, jira, python-dotenv)
- [x] Create package structure (jira_mcp/)
- [x] Copy server.py pattern from google-mcp
- [x] Implement config.py for workspace loading
- [x] Create .gitignore for accounts/ and .env files
- [x] Write README.md with installation instructions

**Status:** Committed and pushed to `rosebud:/var/lib/git/jira-mcp` (commit `01e6644`)  
**Date Completed:** November 20, 2025

### Phase 2: Workspace Management
- [ ] Implement WorkspaceManager for add/list/switch operations
- [ ] Create accounts/ directory structure
- [ ] Implement .env.active file handling
- [ ] Add workspace validation with Jira API connectivity test
- [ ] Handle workspace switching without server restart
- [ ] Implement remove_workspace operation

### Phase 3: Jira API Client
- [ ] Create JiraClient wrapper around jira Python library
- [ ] Implement authentication with API token
- [ ] Add error handling for API failures
- [ ] Implement rate limiting and retry logic
- [ ] Add logging for API calls (without exposing tokens)

### Phase 4: MCP Server & Tool Registration
- [ ] Implement mcp_server.py with tool registration
- [ ] Define jira_workspace tool schema and operations
- [ ] Define jira_issues tool schema and operations
- [ ] Define jira_projects tool schema and operations
- [ ] Implement _dispatch_tool_call router
- [ ] Implement operation routers (_route_workspace_operation, etc.)

### Phase 5: jira_workspace Tool Implementation
- [ ] Implement hello operation (connectivity test)
- [ ] Implement add_workspace with validation
- [ ] Implement list_workspaces with active indicator
- [ ] Implement get_active_workspace
- [ ] Implement switch_workspace
- [ ] Implement validate_workspace
- [ ] Implement remove_workspace
- [ ] Implement get_current_user
- [ ] Implement search_users

### Phase 6: jira_issues Core Operations
- [ ] Implement search with JQL
- [ ] Implement read with full issue details
- [ ] Implement create with field validation
- [ ] Implement update with field mapping
- [ ] Implement transition with workflow validation
- [ ] Implement assign operation

### Phase 7: jira_issues Comments
- [ ] Implement list_comments
- [ ] Implement add_comment
- [ ] Implement update_comment
- [ ] Implement delete_comment

### Phase 8: jira_issues Attachments
- [ ] Implement list_attachments
- [ ] Implement upload_attachment with file validation
- [ ] Implement download_attachment with path sanitization
- [ ] Implement delete_attachment

### Phase 9: jira_issues Links & Subtasks
- [ ] Implement create_link with link types
- [ ] Implement delete_link
- [ ] Implement list_links
- [ ] Implement create_subtask
- [ ] Implement list_subtasks

### Phase 10: jira_projects Tool
- [ ] Implement list projects
- [ ] Implement get project details
- [ ] Implement get_issue_types for project

### Phase 11: Testing & Documentation
- [ ] Test multi-workspace switching
- [ ] Test all jira_issues operations
- [ ] Test error handling and edge cases
- [ ] Write usage examples in README
- [ ] Document workspace configuration format
- [ ] Add troubleshooting guide

### Phase 12: Polish & Deployment
- [ ] Add comprehensive logging
- [ ] Implement graceful shutdown
- [ ] Add signal handlers (SIGINT, SIGTERM)
- [ ] Create example .env files
- [ ] Performance testing with large result sets
- [ ] Security review of credential storage

---

> **Implementation Notes:**
> - Follow google-mcp patterns for consistency and code reuse
> - Use Poetry for all dependency management
> - Maintain Python 3.12+ compliance
> - All API calls through JiraClient for centralized error handling
> - Respect Jira rate limits and implement backoff strategies
> - No persistent content storage - all data fetched on-demand
