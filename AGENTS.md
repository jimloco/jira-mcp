# AI Agent Implementation Guide: Google Workspace ↔ Markdown MCP Server

> **CRITICAL:** This document is MANDATORY reading for ALL AI agents (primary and sub-agents) working on this project. No exceptions.

## CRITICAL WORKFLOW RULES

**Git Commit Policy:**
- **NEVER commit without explicit user instruction**
- Always verify functionality is working before committing
- Wait for user confirmation after testing
- Exception: Only commit when user explicitly says "commit" or "git commit"

## Project Overview

**Project Name:** Google Workspace ↔ Markdown MCP Server  
**Type:** MCP Server / Document Conversion Tool  
**Architecture:** Single Repository Python Package with Poetry Dependency Management  
**Classification:** Personal Productivity Tool / Developer Enhancement  

## MANDATORY: Documentation Review Requirements

### Before ANY Implementation Work

**ALL AI agents MUST:**

1. **Read Complete Project Documentation**
   - `docs/project-charter.md` - Business objectives and scope
   - `docs/requirements.md` - MVP features and technical requirements  
   - `docs/functional-spec.md` - Solution design and security requirements
   - `docs/implementation-spec.md` - Technical architecture and implementation roadmap

2. **Understand Project Context**
   - **Document Conversion Integration**: Bidirectional Google Docs ↔ Markdown conversion for AI coding assistants
   - **Security Criticality**: Confidential - Personal Google Drive access and OAuth credentials
   - **Single Repository Architecture**: Professional Python 3.12 package with MCP server implementation
   - **Python 3.12+ Compliance**: Strict dependency management and virtual environment requirements

3. **Confirm Understanding Before Proceeding**
   - Verify business requirements understanding (personal productivity for documentation workflows)
   - Acknowledge security classification requirements (Google OAuth desktop flow, no persistent content storage)
   - Confirm single repository coordination approach (no sub-agent delegation to external repositories)
   - Validate Python 3.12 workflow execution plan (virtual environment, MCP SDK, Google API integration)

### At Each Major Implementation Step

**MANDATORY CHECKPOINT PROCESS:**

1. **Reference Documentation**: Re-read relevant documentation sections
2. **Validate Approach**: Ensure approach aligns with documented specifications
3. **Security Review**: Confirm security requirements are being met
4. **Integration Check**: Verify work integrates with existing architecture
5. **Progress Update**: Document progress against implementation spec

## Security Requirements (CRITICAL)

### Data Classification and Handling

**Confidential - Personal Google Drive Data:**
- Google Document content, file metadata, user authentication tokens
- **Requirements**: No persistent storage, in-memory processing only, secure OAuth credential management

**Internal - Application Configuration:**
- MCP server configuration, environment variables, dependency information
- **Requirements**: Secure storage in .env files with 600 permissions, no secrets in code

### Security Implementation Requirements

**Authentication & Authorization:**
- Google Workspace OAuth 2.0 desktop flow with secure credential storage
- Refresh token management with automatic renewal and validation
- Respect Google Drive document permissions and sharing settings
- No bypass of Google API authentication or authorization

**Data Protection Standards:**
- End-to-end encryption for all Google API communications (HTTPS/TLS)
- No persistent storage of document content (temporary processing only)
- Secure display and processing of sensitive document content
- Immediate memory cleanup after document processing

**MCP Server Compliance:**
- STDIO transport protocol with clean stdout/stderr separation
- Input validation for all MCP tool parameters
- Graceful error handling without exposing system internals
- Secure logging practices (no sensitive data in logs)

### Technology-Specific Security Requirements

**Python 3.12 Security Standards:**
- **Input Sanitization**: All user inputs (URLs, file paths, parameters) must be validated and sanitized
- **Dependency Security**: Use safety and bandit for vulnerability scanning of all dependencies
- **Type Safety**: Comprehensive type hints with mypy validation for security-critical code

**Zero Trust Security Model Implementation:**
- **Never Trust, Always Verify**: Validate all Google Document URLs, file paths, and API responses
- **Principle of Least Privilege**: Minimal Google API scopes, restricted file system access
- **Continuous Verification**: OAuth token validation before every API call
- **Assume Breach**: No sensitive data persistence, immediate cleanup after processing
- **Identity-Centric Security**: All operations require valid Google authentication context

**Google Workspace API Security Integration:**
- **OAuth Token Security**: Secure storage with encrypted refresh tokens, automatic renewal
- **API Permission Validation**: Verify document access before processing, respect sharing permissions
- **Rate Limiting Compliance**: Honor Google API quotas and implement backoff strategies

**Linting and Code Security:**
- **Bandit Security Rules**: Scan for common Python security vulnerabilities
- **No Secrets in Code**: Use git-secrets or similar to prevent credential commits
- **Python Strict Mode**: Use mypy strict mode for type safety validation
- **Dependency Security**: Regular safety audits and automated vulnerability scanning
- **Git Pre-commit Hooks**: Security validation before all commits

**Required Security Linting Configuration:**
```python
# .banditrc - Python security linting
[bandit]
exclude_dirs = ["tests", "venv", ".venv"]
skips = ["B101"]  # Only skip after security review

# pyproject.toml - Type checking security
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

**Google API Security Controls:**
- **Token Validation**: Verify OAuth tokens before every API request
- **Permission Checking**: Validate document access rights before processing
- **Rate Limit Compliance**: Implement exponential backoff for API calls

**Data Flow Security:**
- **Input Validation**: Sanitize all Google Document URLs and file paths
- **Output Sanitization**: Clean all markdown content before return to prevent injection
- **Memory Management**: Immediate cleanup of document content after processing

### Security Validation Checkpoints

**Before Each Implementation Phase:**
- [ ] Security requirements reviewed and understood
- [ ] Data classification confirmed for new/modified data
- [ ] Access control patterns validated
- [ ] Audit logging requirements confirmed
- [ ] Python 3.12 type safety enabled and configured
- [ ] Security linting rules active and passing
- [ ] Zero trust principles applied to design
- [ ] Google API security patterns followed

**During Implementation:**
- [ ] Security controls implemented as coded
- [ ] No sensitive data exposed inappropriately
- [ ] Authentication/authorization properly integrated
- [ ] Compliance requirements met
- [ ] All linting rules passing (bandit, mypy, safety)
- [ ] Input validation implemented at every boundary
- [ ] Error handling follows security guidelines
- [ ] Zero trust verification at every interaction

## Coding Style and Standards

### MCP Protocol Compliance

**MANDATORY MCP Adherence:**
- STDIO transport protocol with clean stdout for MCP communication
- All logs and debug output must go to stderr, never stdout
- Proper MCP tool registration with accurate schemas
- Graceful error handling with structured MCP error responses

**Python Package Architecture Requirements:**
- Professional package structure with pyproject.toml (Poetry) and console script entry points
- Automatic virtual environment isolation with Poetry dependency management
- Modular design with clear separation of concerns (server, auth, conversion, drive operations)
- Comprehensive logging with structured error reporting
- Deterministic builds with poetry.lock for reproducibility

### Code Quality Standards

**Python 3.12 Development Requirements:**
- **Python Execution**: Always use `poetry run python` to execute Python scripts (Poetry-managed environment)
- **Code Compliance**: All code must be PEP8 compliant with Black code formatting
- **Type Safety**: Use type hints for all function parameters and return values
- **Documentation**: Include docstrings for all modules, classes, and functions
- **Environment Isolation**: Always use a virtual environment for development

**Zero Trust Security Model Implementation:**
- **Input Validation**: Never trust input from any source - validate all inputs
- **Database Security**: Use parameterized queries for database operations - never string interpolation
- **Least Privilege**: Implement least privilege principle for all components
- **Allowlist Validation**: Use strong input validation with explicit allowlists rather than denylists
- **Secret Management**: Never store secrets in code - use environment variables or secure vaults
- **Exception Handling**: Implement proper exception handling that doesn't leak sensitive information
- **Authorization Layers**: Apply proper authentication and authorization checks at every layer
- **Output Sanitization**: Sanitize all output to prevent XSS and injection attacks
- **API Verification**: Verify each API request independently - don't rely on session state
- **Security Logging**: Log all security events without exposing sensitive data

**Dependency Management Standards:**
- **Poetry Only**: Use Poetry (pyproject.toml) for all dependency management with automatic virtual environment
- **Version Pinning**: Poetry automatically pins dependencies with exact versions in poetry.lock
- **Security Auditing**: Review dependencies regularly for security vulnerabilities using `poetry audit`
- **Environment Isolation**: Poetry automatically manages virtual environments for complete dependency isolation
- **Version Control**: pyproject.toml and poetry.lock files committed for reproducible builds
- **No Manual Management**: Never manually manage dependencies or virtual environments

**Testing Requirements:**
- **Unit Testing**: Write unit tests for all functionality with high coverage using pytest
- **Integration Testing**: Include integration tests for system boundaries
- **Test Automation**: Use pytest framework for all test automation
- **Dependency Mocking**: Implement proper mocking for external dependencies

**Code Quality Enforcement:**
- **Static Analysis**: Run static analysis tools as part of development workflow
- **Security Analysis**: Use bandit for security-focused static analysis
- **Pre-commit Validation**: Include pre-commit hooks for automatic code quality checks
- **Security Warnings**: Never disable security warnings without explicit justification
- **Code Validation**: Use pylint for comprehensive code validation and maintain 10.00/10 score

**Performance Standards:**
- **Profiling**: Use profiling tools to identify bottlenecks in document processing
- **Data Pagination**: Implement proper pagination for large data sets (Google Drive folder listings)
- **Async I/O**: Use async I/O for I/O-bound operations (MCP protocol, Google API calls)
- **Caching**: Apply caching strategies appropriately with TTL for API responses

**Deployment Requirements:**
- **Container Security**: Use containerized deployments with minimal base images
- **Image Scanning**: Scan container images for vulnerabilities before deployment
- **Infrastructure**: Follow immutable infrastructure principles

**Code Security Patterns:**
```python
# Secure document URL validation
def validate_document_url(url: str) -> str:
    """Validate and sanitize Google Document URL."""
    if not url or not isinstance(url, str):
        raise ValueError("Invalid document URL format")
    
    # Extract document ID safely
    url = url.strip()
    if not url.startswith('https://docs.google.com/'):
        raise ValueError("URL must be a Google Document")
    
    return url

# Secure file path handling
def validate_file_path(path: str) -> Path:
    """Validate file path to prevent directory traversal."""
    if not path or '..' in path:
        raise ValueError("Invalid file path")
    
    return Path(path).resolve()
```

**Testing Requirements:**
- **Unit Tests**: pytest framework with 80% minimum coverage for all modules
- **Integration Tests**: Full OAuth flow and Google API integration testing
- **Security Tests**: Input validation, authentication flow, and error handling validation
- **Performance Tests**: Document processing time validation (sub-10-second requirement)
- **MCP Protocol Tests**: Tool registration, STDIO communication, and error response validation

## MCP Server Execution Standards

### Workflow Discipline

**MANDATORY MCP Server Implementation Adherence:**
- Follow selenium-mcp architectural patterns for launcher scripts and process management
- Implement robust signal handling for graceful server shutdown
- Use stderr for all logging to maintain clean STDIO transport protocol
- Implement comprehensive error handling with MCP-compliant error responses

**Single Repository Coordination:**
- No sub-agent delegation to external repositories (all work contained in single repository)
- Modular code organization with clear separation between MCP server, Google API client, and conversion logic
- Consistent error handling and logging patterns across all modules
- Integration testing to validate all components work together

### Configuration Management

**Python Package Configuration Standards:**
- Virtual environment isolation with Python 3.12 requirements
- Environment variable configuration with .env file management (600 permissions)
- Secure OAuth credential storage and automatic refresh handling
- MCP server configuration with proper tool registration and schema validation

## Single Repository Implementation Protocol

### Development Requirements (CRITICAL)

**When Working within Google Workspace MCP Repository:**

1. **MANDATORY Development Environment:**
   ```markdown
   - Python Version: 3.12+ (EXACT - no variations)
   - Dependency Manager: Poetry (REQUIRED)
   - Virtual Environment: Automatic with Poetry
   - Package Installation: `poetry install`
   - Configuration: .env file with secure permissions (600)
   ```

2. **Complete Code Organization:**
   - Main package code in `google_workspace_mcp/` directory
   - MCP server implementation in `server.py` and `mcp_server.py`
   - Google API integration in `google_workspace_client.py` and `oauth_manager.py`
   - Document conversion logic in `document_converter.py`
   - Drive operations in `drive_manager.py`

3. **MANDATORY Post-Implementation Validation:**
   - MCP server starts without errors using `python run.py`
   - All MCP tools register correctly and respond to test calls
   - OAuth authentication works with Google Workspace APIs
   - Virtual environment contains all required dependencies

### Integration Validation Protocol

**After Each Implementation Completion:**

1. **Package Integration Audit:**
   - [ ] All imports work correctly within package structure
   - [ ] No circular dependencies between modules
   - [ ] MCP server registers all tools without errors
   - [ ] Virtual environment is self-contained and portable

2. **Functional Testing:**
   - [ ] MCP server responds to tool calls via STDIO transport
   - [ ] Google OAuth authentication completes successfully
   - [ ] Document conversion functions work end-to-end
   - [ ] Error handling provides meaningful feedback

3. **Security Validation:**
   - [ ] No secrets or credentials stored in code
   - [ ] .env file has proper permissions (600)
   - [ ] All input validation prevents injection attacks
   - [ ] OAuth tokens are handled securely

## Performance and Quality Requirements

### MCP Server Performance Standards

**Personal Productivity Tool SLA Requirements:**
- Document conversion time: < 10 seconds for typical Google Documents
- MCP server startup time: < 5 seconds in development environment
- Memory usage: < 100MB for document processing operations
- Response time: < 2 seconds for MCP tool calls (excluding Google API latency)

**Quality Assurance:**
- 10.00/10 pylint score for all production code
- 80%+ test coverage for all modules
- Zero security vulnerabilities in dependency scan
- PEP8 compliance with Black formatting

### Monitoring and Observability

**Required Implementation:**
- Structured logging with appropriate levels (DEBUG, INFO, WARNING, ERROR)
- Error tracking with full stack traces for debugging
- Performance logging for document processing times
- OAuth authentication success/failure tracking

## Communication and Documentation Standards

### Progress Documentation

**During Implementation:**
- Document all major design decisions and rationale in code comments
- Update implementation spec with actual progress and any deviations
- Record any challenges encountered and solutions implemented
- Maintain clear commit messages following conventional commit format

**At Major Milestones:**
- Update README with current functionality status
- Validate all documentation remains accurate and current
- Test all setup instructions for new developer onboarding
- Confirm all acceptance criteria are met for completed phases

### Issue Escalation

**When to Escalate:**
- Google Workspace API authentication or permission issues
- MCP protocol compliance or tool registration problems
- Security vulnerability discoveries or concerns
- Performance requirements that cannot be met with current architecture

**Escalation Process:**
1. Document the specific issue with reproduction steps
2. Provide relevant logs and error messages
3. Research alternative solutions with trade-off analysis
4. Present options with recommendations for stakeholder decision

## Implementation Phase Guidelines

### Phase 1: Foundation & Environment Setup (MCP Development Workflow)

**Pre-Execution Checklist:**
- [ ] Python 3.12+ installed and available
- [ ] Virtual environment created and activated
- [ ] All project documentation read and understood
- [ ] Security requirements confirmed and internalized

**During Execution:**
- [ ] Create professional package structure with setup.py
- [ ] Install MCP SDK and Google Workspace API dependencies
- [ ] Configure OAuth credentials with secure storage
- [ ] Implement basic MCP server with STDIO transport

**Post-Execution Validation:**
- [ ] MCP server starts without errors
- [ ] Virtual environment is properly isolated
- [ ] OAuth setup completes successfully
- [ ] Ready for Google API integration

### Phase 2: MCP Server & Authentication (Google Workspace Integration)

**Pre-Execution Checklist:**
- [ ] Phase 1 completed and validated
- [ ] MCP protocol understanding confirmed
- [ ] Google Workspace API documentation reviewed
- [ ] Security patterns for OAuth integration understood

**During Execution:**
- [ ] Implement MCP protocol server with tool registration
- [ ] Integrate Google Drive and Docs API clients
- [ ] Create OAuth authentication flow with refresh token management
- [ ] Add hello_google_workspace test tool for connectivity verification

**Post-Execution Validation:**
- [ ] MCP server registers tools correctly
- [ ] Google authentication works end-to-end
- [ ] Test tool returns successful API connectivity
- [ ] Ready for document conversion implementation

### Phase 3: Document Conversion Implementation (Business Logic Implementation)

**Pre-Execution Checklist:**
- [ ] Phases 1-2 completed and validated
- [ ] Document conversion requirements understood
- [ ] Markdown processing libraries identified
- [ ] Academic formatting requirements clarified

**During Execution:**
- [ ] Implement pull_doc_from_drive tool with tab support
- [ ] Create enhanced markdown conversion engine
- [ ] Implement Drive file operations (add_file_to_drive, replace_file_in_drive)
- [ ] Add comprehensive error handling and validation

**Post-Execution Validation:**
- [ ] All MCP tools work end-to-end with real Google Documents
- [ ] Document conversion preserves formatting correctly
- [ ] Drive operations handle file upload and updates properly
- [ ] Performance meets sub-10-second requirements

## Success Criteria and Completion Standards

### Technical Completion

**MCP Server Implementation:**
- [ ] STDIO transport protocol working correctly
- [ ] All tools registered and responding to calls
- [ ] Comprehensive error handling with meaningful messages
- [ ] Performance meets stated SLA requirements

**Business Requirements:**
- [ ] Google Document to Markdown conversion with formatting preservation
- [ ] Markdown file upload to Google Drive with format options
- [ ] Seamless AI coding assistant integration via MCP protocol
- [ ] Sub-10-second processing for typical documents

**Security and Compliance:**
- [ ] OAuth 2.0 desktop flow implemented securely
- [ ] No persistent storage of document content
- [ ] Input validation prevents all common attack vectors
- [ ] Dependency security scanning passes with no high-severity vulnerabilities

### Quality Validation

**Performance Standards:**
- [ ] Document processing < 10 seconds for typical Google Documents
- [ ] MCP server startup < 5 seconds
- [ ] Memory efficient processing with immediate cleanup
- [ ] Responsive tool calls with appropriate error handling

**Integration Success:**
- [ ] Works seamlessly with AI coding assistants (Cursor, Windsurf)
- [ ] Virtual environment is portable and self-contained
- [ ] All setup instructions work for new developers
- [ ] Documentation is accurate and comprehensive

---

## CRITICAL REMINDERS FOR ALL AI AGENTS

### MANDATORY ACTIONS
- ✅ READ ALL PROJECT DOCUMENTATION before any implementation work
- ✅ FOLLOW security requirements without exception
- ✅ USE `poetry run python` to execute Python scripts (Poetry-managed environment)
- ✅ VALIDATE all Google API interactions with proper authentication
- ✅ DOCUMENT progress and decisions throughout implementation
- ✅ RUN security linting (bandit, safety) after every code change
- ✅ AUDIT dependencies before any commits using `poetry audit`
- ✅ APPLY zero trust principles to all implementation decisions
- ✅ VALIDATE Python strict mode compliance with mypy
- ✅ SANITIZE all data inputs and outputs
- ✅ USE Poetry for ALL dependency management
- ✅ DEPENDENCIES automatically pinned with Poetry (poetry.lock)
- ✅ RUN pylint and flake8 to verify PEP8 compliance
- ✅ INCLUDE type hints for all function parameters and return values
- ✅ WRITE docstrings for all modules, classes, and functions
- ✅ USE pytest for all test automation with high coverage
- ✅ IMPLEMENT proper mocking for external dependencies
- ✅ RUN static analysis tools as part of development workflow
- ✅ VALIDATE input using explicit allowlists rather than denylists

### FORBIDDEN ACTIONS
- ❌ NEVER skip documentation review
- ❌ NEVER compromise security requirements
- ❌ NEVER work outside Poetry-managed virtual environment
- ❌ NEVER use pip or manual dependency management
- ❌ NEVER store Google credentials in code or commit to git
- ❌ NEVER proceed without validating OAuth integration
- ❌ NEVER commit code with linting errors or security vulnerabilities
- ❌ NEVER store sensitive document content persistently
- ❌ NEVER use unsafe types for security-critical code
- ❌ NEVER bypass input validation or authentication checks
- ❌ NEVER expose detailed error information to end users
- ❌ NEVER trust external data without validation
- ❌ NEVER commit secrets, tokens, or credentials to repository
- ❌ NEVER use string interpolation for database operations
- ❌ NEVER disable security warnings without explicit justification
- ❌ NEVER store secrets in code - use environment variables or secure vaults
- ❌ NEVER use denylists instead of explicit allowlists for validation
- ❌ NEVER skip dependency security audits before commits
- ❌ NEVER deploy without scanning container images for vulnerabilities
- ❌ NEVER modify .pylintrc or other linting configuration files without explicit user authorization and explanation of intent

### SUCCESS INDICATORS
- MCP server starts and registers all tools without errors
- Google Workspace authentication completes successfully  
- Document conversion tools work end-to-end with real content
- Performance meets sub-10-second processing requirements
- Security validation passes with no vulnerabilities
- Integration testing confirms AI coding assistant compatibility
- All acceptance criteria met for MVP functionality

---

**This document is the authoritative guide for all AI agents working on this project. Adherence to these guidelines is mandatory for successful project completion.**

**Version: 1.0 | Created: September 2025 | Status: ACTIVE**
