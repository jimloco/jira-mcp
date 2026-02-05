# Jira MCP Server Configuration

## Configuration Location

All configuration files are stored in `~/.config/jira-mcp/`:

```
~/.config/jira-mcp/
├── workspaces/          # Workspace configuration files
│   ├── intuit.json
│   └── mycompany.json
└── active_workspace     # Currently active workspace name
```

## Adding a New Workspace

### Recommended Method: Skeleton File

1. **Create a skeleton configuration file**:
   ```python
   jira_workspace(
       operation="create_workspace_skeleton",
       workspace_name="intuit",
       auth_type="pat"  # or "cloud" for Jira Cloud
   )
   ```

2. **Edit the generated file** at `~/.config/jira-mcp/workspaces/intuit.json`:
   ```bash
   vim ~/.config/jira-mcp/workspaces/intuit.json
   ```

3. **Fill in your credentials**:
   
   For **Jira Server/Data Center (PAT)**:
   ```json
   {
     "name": "intuit",
     "site_url": "https://jira.intuit.com",
     "email": "james_hull@intuit.com",
     "api_token": "YOUR_PERSONAL_ACCESS_TOKEN",
     "auth_type": "pat",
     "created": "2026-02-05T07:16:00.000000",
     "last_validated": null
   }
   ```
   
   For **Jira Cloud**:
   ```json
   {
     "name": "mycompany",
     "site_url": "https://mycompany.atlassian.net",
     "email": "your.email@company.com",
     "api_token": "YOUR_JIRA_CLOUD_API_TOKEN",
     "auth_type": "cloud",
     "created": "2026-02-05T07:16:00.000000",
     "last_validated": null
   }
   ```

4. **Remove the `_instructions` section** from the file

5. **Restart the MCP server** (close and reopen Windsurf)

### Alternative Method: Direct Add (Programmatic)

Only use this if you're scripting or automating workspace creation:

```python
jira_workspace(
    operation="add_workspace",
    workspace_name="intuit",
    site_url="https://jira.intuit.com",
    email="james_hull@intuit.com",
    api_token="YOUR_PERSONAL_ACCESS_TOKEN",
    auth_type="pat"
)
```

## Authentication Types

### Jira Cloud (`auth_type="cloud"`)
- **URL**: `https://yourcompany.atlassian.net`
- **Email**: Your Jira account email
- **Token**: API token from https://id.atlassian.com/manage-profile/security/api-tokens
- **Authentication**: Basic auth (email + API token)

### Jira Server/Data Center (`auth_type="pat"`)
- **URL**: `https://jira.yourcompany.com`
- **Email**: Your username (for reference, not used in auth)
- **Token**: Personal Access Token from your Jira Server
- **Authentication**: Bearer token (PAT)

## Managing Workspaces

### List all workspaces
```python
jira_workspace(operation="list_workspaces")
```

### Switch active workspace
```python
jira_workspace(
    operation="switch_workspace",
    workspace_name="intuit"
)
```

### Validate workspace credentials
```python
jira_workspace(
    operation="validate_workspace",
    workspace_name="intuit"
)
```

### Remove a workspace
```python
jira_workspace(
    operation="remove_workspace",
    workspace_name="intuit"
)
```

## Security

- All workspace configuration files have **600 permissions** (owner read/write only)
- Credentials are stored in **plain JSON** (consider using system keychain in production)
- Configuration directory is in user's home directory, not in project repository
- Never commit workspace configuration files to version control

## File Permissions

The configuration files are automatically created with secure permissions:
```bash
chmod 600 ~/.config/jira-mcp/workspaces/*.json
```

## Troubleshooting

### Workspace not loading
1. Check file exists: `ls ~/.config/jira-mcp/workspaces/`
2. Check file permissions: `ls -la ~/.config/jira-mcp/workspaces/`
3. Validate JSON syntax: `cat ~/.config/jira-mcp/workspaces/intuit.json | python -m json.tool`
4. Restart MCP server (close and reopen Windsurf)

### Authentication failures
1. Verify auth_type matches your Jira instance (Cloud vs Server)
2. For PAT: Ensure token is valid and not expired
3. For Cloud: Verify email and API token are correct
4. Test connection: `jira_workspace(operation="validate_workspace", workspace_name="intuit")`

### Multiple workspaces
- Only one workspace can be active at a time
- Use `switch_workspace` to change between workspaces
- Active workspace is stored in `~/.config/jira-mcp/active_workspace`
