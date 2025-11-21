# Jira MCP Server Implementation

**Project:** Jira Model Context Protocol (MCP) Server  
**Repository:** `rosebud:/var/lib/git/jira-mcp`  
**Local Path:** `/Users/jhull/workarea/jira-mcp`

## Project Status

**Current Phase:** Phase 5 Complete ✅ - Comments Implemented  
**Last Updated:** November 21, 2025  
**Git Commit:** `d51da8b` on `main` branch

### Completed Milestones
- ✅ **Phase 1: Project Bootstrap & Infrastructure** (Nov 20, 2025)
  - Poetry project initialized with all dependencies
  - Package structure created (jira_mcp/)
  - Core server files implemented
  - Configuration system in place
  - Documentation complete

- ✅ **Phase 2: MCP Server + Workspace Management (MVP)** (Nov 20, 2025)
  - Complete MCP server with STDIO transport
  - jira_workspace tool with 9 operations
  - WorkspaceManager for multi-workspace support
  - JiraClient wrapper with API token authentication
  - Workspace add/list/switch/validate/remove operations
  - User search and current user info

- ✅ **Phase 3: jira_projects Tool** (Nov 21, 2025)
  - jira_projects tool with 3 operations
  - List all accessible projects
  - Get project details by key
  - Get issue types for projects

- ✅ **Phase 4: jira_issues Core Operations** (Nov 21, 2025)
  - jira_issues tool with 7 operations
  - Full issue lifecycle management (CRUD + workflow)
  - JQL search integration
  - Issue creation, updates, assignments, and transitions

- ✅ **Phase 5: jira_issues Comments** (Nov 21, 2025)
  - Added 4 comment operations to jira_issues tool
  - Full comment CRUD (list, add, update, delete)
  - Comment management with author tracking

### Current Status
- **Core + Comments Complete** ✅
- 3 tools implemented: `jira_workspace` (9 operations), `jira_projects` (3 operations), `jira_issues` (11 operations)
- Total: 23 operations across 3 MCP tools
- Complete Jira integration for AI assistants with comment support
- Optional: Phase 6 (Attachments) for file management

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

### Phase 2: MCP Server + Workspace Management (MVP) ✅ **COMPLETED**
**Goal:** Working MCP server with `jira_workspace` tool for testing workspace configuration

#### MCP Server Infrastructure
- [x] Implement mcp_server.py with tool registration framework
- [x] Define jira_workspace tool schema
- [x] Implement _dispatch_tool_call router
- [x] Implement _route_workspace_operation router
- [x] Connect server.py to mcp_server.py with STDIO transport

#### Workspace Manager
- [x] Implement WorkspaceManager for add/list/switch operations
- [x] Implement accounts/ JSON file storage
- [x] Implement .env.active file handling
- [x] Handle workspace switching without server restart
- [x] Implement remove_workspace operation

#### Jira Client (Basic)
- [x] Create JiraClient wrapper around jira Python library
- [x] Implement authentication with API token
- [x] Add basic error handling for API failures
- [x] Add logging for API calls (without exposing tokens)

#### jira_workspace Tool Operations
- [x] Implement hello operation (connectivity test)
- [x] Implement add_workspace with validation
- [x] Implement list_workspaces with active indicator
- [x] Implement get_active_workspace
- [x] Implement switch_workspace
- [x] Implement validate_workspace
- [x] Implement remove_workspace
- [x] Implement get_current_user
- [x] Implement search_users

**Phase 2 Deliverable:** Working MCP server that can manage workspaces and test Jira connectivity ✅

**Status:** Committed and pushed to `rosebud:/var/lib/git/jira-mcp` (commit `3f9f477`)  
**Date Completed:** November 20, 2025

**Files Created:**
- `jira_mcp/workspace_manager.py` (436 lines) - Multi-workspace management
- `jira_mcp/jira_client.py` (237 lines) - Jira API client wrapper
- `jira_mcp/mcp_server.py` (732 lines) - MCP server with jira_workspace tool

**Server Ready For Testing:** Run `poetry run start-mcp` to start the MCP server

### Phase 3: jira_projects Tool ✅ **COMPLETED**
- [x] Define jira_projects tool schema
- [x] Implement _route_projects_operation router
- [x] Implement list operation
- [x] Implement get operation
- [x] Implement get_issue_types operation

**Status:** Committed and pushed to `rosebud:/var/lib/git/jira-mcp` (commit `906c8b0`)  
**Date Completed:** November 21, 2025

**Operations Available:**
- `list` - List all accessible projects
- `get` - Get detailed project information by key
- `get_issue_types` - Get available issue types for a project

### Phase 4: jira_issues Core Operations ✅ **COMPLETED**
- [x] Define jira_issues tool schema
- [x] Implement _route_issues_operation router
- [x] Implement IssueManager class
- [x] Implement search with JQL
- [x] Implement read with full issue details
- [x] Implement create with field validation
- [x] Implement update with field mapping
- [x] Implement transition with workflow validation
- [x] Implement assign operation

**Status:** Committed and pushed to `rosebud:/var/lib/git/jira-mcp` (commit `c7b0336`)  
**Date Completed:** November 21, 2025

**Operations Available:**
- `search` - JQL-based issue search
- `read` - Get full issue details
- `create` - Create new issues with fields
- `update` - Update issue fields
- `assign` - Assign issues to users
- `transition` - Move issues through workflow
- `get_transitions` - Get available transitions

**Files Created:**
- `jira_mcp/issue_manager.py` (465 lines) - Complete issue lifecycle management

### Phase 5: jira_issues Comments ✅ **COMPLETED**
- [x] Implement list_comments
- [x] Implement add_comment
- [x] Implement update_comment
- [x] Implement delete_comment

**Status:** Committed and pushed to `rosebud:/var/lib/git/jira-mcp` (commit `d51da8b`)  
**Date Completed:** November 21, 2025

**Operations Added:**
- `list_comments` - Get all comments on an issue
- `add_comment` - Add new comment with body text
- `update_comment` - Update existing comment
- `delete_comment` - Remove comment from issue

**Code Added:**
- 168 lines in `issue_manager.py`
- 242 lines in `mcp_server.py`

### Phase 6: jira_issues Attachments
- [ ] Implement list_attachments
- [ ] Implement upload_attachment with file validation
- [ ] Implement download_attachment with path sanitization
- [ ] Implement delete_attachment

### Phase 7: jira_issues Links & Subtasks
- [ ] Implement create_link with link types
- [ ] Implement delete_link
- [ ] Implement list_links
- [ ] Implement create_subtask
- [ ] Implement list_subtasks

### Phase 8: Testing & Documentation
- [ ] Test multi-workspace switching
- [ ] Test all jira_issues operations
- [ ] Test error handling and edge cases
- [ ] Write usage examples in README
- [ ] Document workspace configuration format
- [ ] Add troubleshooting guide

### Phase 9: Polish & Deployment
- [ ] Add comprehensive logging
- [ ] Implement graceful shutdown (already done in Phase 1)
- [ ] Add signal handlers (SIGINT, SIGTERM - already done in Phase 1)
- [ ] Create example .env files
- [ ] Performance testing with large result sets
- [ ] Security review of credential storage
- [ ] Implement rate limiting and retry logic

---

> **Implementation Notes:**
> - Follow google-mcp patterns for consistency and code reuse
> - Use Poetry for all dependency management
> - Maintain Python 3.12+ compliance
> - All API calls through JiraClient for centralized error handling
> - Respect Jira rate limits and implement backoff strategies
> - No persistent content storage - all data fetched on-demand
