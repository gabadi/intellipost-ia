# User-Defined Preferred Patterns and Preferences

## Frontend Development Requirements

### Playwright MCP Integration
- **MANDATORY**: All frontend stories MUST use Playwright MCP for both development and validation
- **CRITICAL**: If Playwright MCP is not available, execution MUST be interrupted immediately with an error
- **NO EXCEPTIONS**: Do not proceed with frontend work without Playwright MCP access

### Library Management Protocol
- **FIRST STEP**: Before using ANY library, verify correct usage via Context7 MCP
- **VALIDATION**: When adding a new library, check implementation patterns in Context7 MCP first
- **BLOCKING**: If Context7 MCP is not available when library verification is needed, interrupt execution immediately

## Error Handling
- Frontend stories without Playwright MCP access: HALT with error message
- Library usage without Context7 MCP verification: HALT with error message
- These are blocking requirements, not suggestions
