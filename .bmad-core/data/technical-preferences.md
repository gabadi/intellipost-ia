# User-Defined Preferred Patterns and Preferences

## MANDATORY Tool Selection

### Browser Automation & Testing
- **ALWAYS use `mcp__playwright__*` tools** for:
    - Testing web applications
    - Interacting with web UIs (clicks, forms, navigation)
    - Taking screenshots of applications
    - Automating browser workflows

### Research & Content Fetching
- **Use `WebFetch`** for:
    - Reading documentation from URLs
    - Fetching API responses
    - Scraping static content
    - Research tasks without interaction

### Story Implementation Files
- **Story implementation temp files go in `.story-implementation/` ONLY**
    - DoD validation files
    - Implementation notes
    - Story-related temporary documentation
    - As defined in expansion-packs/story-implementation/manifest.yml

### Library Documentation & Research
- **ALWAYS use Context7 MCP (`mcp__context7__*`) for external libraries**
    - Use `mcp__context7__resolve-library-id` to find the exact library ID
    - Use `mcp__context7__get-library-docs` to get current version documentation
    - Ensures we always use the latest version and proper usage patterns
    - Critical for maintaining up-to-date dependency knowledge

## Decision Tree
- Need to **interact** with a web app? → `mcp__playwright__*`
- Need to **read/research** content from web? → `WebFetch`
- Creating story implementation files? → `.story-implementation/` only
