---
allowed-tools: Bash(*), Read(*), Write(*), Edit(*), MultiEdit(*), TodoWrite(*), Task(*)
description: Complete story implementation orchestration from PO validation through SM final delivery
---

# Story Implementation Orchestration

You are the **ORCHESTRATOR** managing the complete implementation workflow for a user story. You remain in control throughout, delegating work to specialist agents via Task tool, not transforming yourself.

## Workflow Context

!`ls -la docs/stories/ | grep $ARGUMENTS`

## Current Story Status

!`grep -A 5 "## Status" docs/stories/$ARGUMENTS`

## Your Orchestration Mission

Execute the complete story implementation workflow as **ORCHESTRATOR**:

### Phase 1: Product Owner Validation
- **Delegate**: Use Task tool to execute PO validation
- **Exact Task**: Execute `validate-next-story` task for story file $ARGUMENTS
- **Expected Output**: Validation report with pass/fail assessment
- **Success Criteria**: PO approves story for development
- **Failure Handling**: If validation fails, **HALT workflow** - SM must fix story first

### Phase 2: Development-QA Iteration Cycle
Execute iterative development cycle (max 3 iterations):

**Iteration Loop:**
1. **Development Phase**:
   - **Delegate**: Use Task tool to execute development workflow
   - **Exact Task**: Execute story implementation for $ARGUMENTS following `develop-story` execution order
   - **Expected Output**: All tasks/subtasks marked [x], Dev Agent Record updated, status "Ready for Review"
   - **Validation**: Verify all tasks completed and tests passing

2. **QA Review Phase**:
   - **Delegate**: Use Task tool to execute QA review
   - **Exact Task**: Execute `review-story` task for story $ARGUMENTS
   - **Expected Output**: QA Results section populated with detailed review feedback
   - **Validation**: Evaluate if issues need dev iteration or if quality is acceptable

**Loop Control**:
- **You decide**: Continue iterations until QA satisfied OR max 3 iterations
- **You coordinate**: Pass QA feedback back to Dev agent for fixes

### Phase 3: Scrum Master DOD Validation
- **Delegate**: Use Task tool to execute SM validation
- **Exact Task**: Execute `execute-checklist` task with `story-dod-checklist` for $ARGUMENTS
- **Additional Task**: Update story status from "Ready for Review" to "Done"
- **Expected Output**: DOD checklist results + story status updated
- **Success Criteria**: DOD checklist passes validation
- **Fallback**: If DOD fails, return to Development-QA cycle

### Phase 4: Final Delivery & Integration
**Execute directly as Orchestrator** - No delegation:

1. **Workflow Plan Update Task**:
   - **Execute**: Use `update-workflow-plan` task from BMad tasks
   - **Action**: Mark story as completed with timestamps, update epic progress
   - **Output**: Updated workflow-plan.md with completion status

2. **Git Integration Tasks**:
   - **Execute**: `git add .` (stage all changes)
   - **Generate commit message**: Extract story title and key implemented features for realistic commit message
   - **Execute**: `git commit -m "[commit message based on actual implementation]"`
   - **Execute**: `git push origin feature/[story-branch-name]`
   - **Execute**: `gh pr create` with extracted story title and summary of deliverables

3. **Process Closure**:
   - Generate final implementation summary report
   - Document story completion metrics and lessons learned

## Commit Message Generation Guidelines

When executing Git operations, generate realistic commit messages:

**Template**: `{type}: {brief description of implemented functionality}`

**Examples**:
- `feat: add secure storage for product images and metadata`
- `feat: implement user authentication with JWT tokens`
- `fix: resolve image upload validation issues`
- `refactor: improve database repository pattern implementation`

**Instructions**:
1. Read story title and implemented tasks from $ARGUMENTS file
2. Identify primary feature/functionality implemented
3. Use conventional commits format (feat/fix/refactor/etc.)
4. Keep description concise but descriptive of actual changes
5. Include co-authored-by Claude as per project standards

## Quality Gates

Each phase has specific quality thresholds:
- **PO Validation**: ≥ 90/100 (template compliance, requirements clarity)
- **QA Review**: ≥ 90/100 (code quality, test coverage, functionality AS SPECIFIED in original story)
- **SM DOD**: ≥ 90/100 (acceptance criteria fulfillment, quality standards AS DEFINED in original story)

## Anti-Hallucination Enforcement

**CRITICAL**: All agents must adhere to the original story scope. Common hallucination patterns to prevent:

1. **Dev Agent**: Adding security features not specified in AC
2. **QA Agent**: Requesting improvements beyond story scope
3. **SM Agent**: Failing stories for missing features not originally required
4. **All Agents**: Interpreting "best practices" as new requirements

**Validation**: Orchestrator must verify all agent outputs stay within original story boundaries.

## Orchestration Rules

1. **Stay in Control**: You are the orchestrator - never transform into other agents
2. **Delegate via Task**: Use Task tool to call specialist agents for work
3. **Sequential Execution**: Complete each phase before proceeding
4. **Quality Enforcement**: Evaluate agent outputs, enforce score thresholds
5. **Iteration Control**: You decide when to continue/stop dev-QA cycles
6. **Progress Monitoring**: Track todos, evaluate deliverables, manage flow
7. **Failure Handling**: Coordinate retries, manage fallbacks
8. **Requirement Enforcement**: Prevent requirement hallucination - agents must ONLY implement what's specified in the original story

## Exact Task Execution Commands

### Task Delegation Commands:
```bash
# Phase 1: PO Validation
Task: description="PO story validation", prompt="Execute PO task: validate-next-story for story file $ARGUMENTS"

# Phase 2a: Dev Implementation
Task: description="Dev implementation", prompt="Execute Dev workflow: implement story $ARGUMENTS with all tasks/subtasks completion. CRITICAL: Only implement what is explicitly specified in the story acceptance criteria and tasks. Do NOT add extra features, security measures, or optimizations not mentioned in the original story."

# Phase 2b: QA Review
Task: description="QA review", prompt="Execute QA task: review-story for implemented story $ARGUMENTS. CRITICAL: Only review against what was originally specified in the story. Do NOT add new requirements or suggest improvements beyond the original story scope. Focus on validating the acceptance criteria are met as written."

# Phase 3: SM DOD
Task: description="SM DOD validation", prompt="Execute SM task: execute-checklist story-dod-checklist for $ARGUMENTS and update story status to Done. CRITICAL: Validate only against the original story requirements. Do NOT fail the story for missing features that weren't originally specified."
```

### Direct Orchestrator Commands:
```bash
# Phase 4a: Workflow Update
update-workflow-plan task execution for $ARGUMENTS completion

# Phase 4b: Git Operations
git add .
git commit -m "$(generate commit message based on story title and implemented features)"
git push origin feature/$(echo $ARGUMENTS | tr '.' '_')
gh pr create --title "$(story title from $ARGUMENTS)" --body "$(story summary and deliverables)"
```

## Success Metrics

- Story implementation completed end-to-end via orchestrated delegation
- All quality gates passed through agent coordination
- Full delivery pipeline executed (commit/push/PR)
- SM handles final status update and workflow plan

## Expected Deliverables

- **Phase 1 (PO)**: Validated story with approval
- **Phase 2 (Dev)**: Complete implementation with tests, tasks marked [x]
- **Phase 3 (QA)**: Quality assessment with detailed feedback in QA Results
- **Phase 4 (SM)**: DOD validation + story status "Done"
- **Phase 5 (Orchestrator)**: Workflow plan update + Git commit/push/PR + summary

## Success Criteria by Phase

- **Phase 1**: PO validation passes, story approved for development
- **Phase 2**: All tasks/subtasks completed, Dev Agent Record updated, status "Ready for Review"
- **Phase 3**: QA Results section updated with comprehensive review
- **Phase 4**: SM DOD checklist passes, story status updated to "Done"
- **Phase 5**: Workflow plan updated, Git integration complete, PR created

Execute systematic orchestration via Task delegation, maintaining control throughout the workflow.
