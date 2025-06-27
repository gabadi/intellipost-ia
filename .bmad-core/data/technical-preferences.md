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

## Decision Tree
- Need to **interact** with a web app? → `mcp__playwright__*`
- Need to **read/research** content from web? → `WebFetch`
- Creating story implementation files? → `.story-implementation/` only
