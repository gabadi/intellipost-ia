# CI Fix Command

Fix GitHub Actions CI failures through systematic analysis and thoughtful resolution.

## Mission
You are the **CI RESOLVER** - analyze failures, apply thoughtful fixes, iterate until success.

## Workflow (Max 3 Iterations)

### 1. Analysis Phase
- Check CI failures using `gh run view`
- Categorize errors by type and severity
- Identify root causes, not just symptoms
- Plan fixes that address underlying issues

### 2. Local Reproduction
- Run local CI commands (check project's CI scripts)
- Confirm you can reproduce the exact failures
- Understand the error context fully

### 3. Thoughtful Fix Implementation
- **Think first**: What's the root cause?
- **Consider impact**: Will this fix create new issues?
- **Follow standards**: Maintain code quality and patterns
- **Test locally**: Verify fix works before pushing

### 4. Iteration Decision
- **If CI passes**: Success! Document what was fixed
- **If CI fails**: Analyze new errors, plan next iteration
- **After 3 iterations**: Escalate with detailed analysis

## Error Types & Approach
- **Linting/Formatting**: Fix systematically, understand why rules exist
- **Type/Compilation**: Resolve properly, don't just cast or ignore
- **Tests**: Fix logic issues, don't just update expectations blindly
- **Build**: Resolve dependency conflicts thoughtfully
- **Complex**: Request architectural review before attempting fixes

## Iteration Strategy
```yaml
Iteration 1: Fix obvious, low-risk issues
Iteration 2: Address remaining errors with careful analysis
Iteration 3: Final attempt with comprehensive approach
```

## Commands
```bash
# Check CI status
gh run list --branch $(git branch --show-current) --limit 3

# Local reproduction (adapt to project)
# Check package.json, Makefile, or CI config for actual commands

# Monitor after push
gh run watch $(gh run list --limit 1 --json databaseId | jq -r '.[0].databaseId')
```

## Success Criteria
- All GitHub Actions checks pass
- Local CI commands succeed
- Changes are minimal and well-reasoned
- No new technical debt introduced
