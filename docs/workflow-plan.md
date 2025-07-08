# Workflow Plan: Greenfield Full-Stack Application Development - Épica 2

<!-- WORKFLOW-PLAN-META
workflow-id: greenfield-fullstack
status: active
created: 2025-07-07T00:00:00Z
updated: 2025-07-08T12:00:00Z
version: 1.1
-->

**Created Date**: July 7, 2025
**Project**: IntelliPost-IA - Épica 2
**Type**: Greenfield
**Status**: Active - Development Phase
**Planning Duration**: 4-6 hours (COMPLETED)
**Progress**: 83% complete - Currently on Epic 2 Story 3

## Objective

Implement "épica 2" in the IntelliPost-IA project using a comprehensive greenfield full-stack development approach. This workflow will guide the development from conceptual planning through implementation, ensuring proper architecture, documentation, and quality assurance throughout the process.

## Selected Workflow

**Workflow**: `greenfield-fullstack`
**Reason**: This workflow is ideal for épica 2 as it provides comprehensive planning for complex full-stack features, supports both frontend and backend development, and ensures proper documentation and quality gates are in place for a production-ready implementation.

## Workflow Steps

### Planning Phase

- [x] Step 1: Project Brief Creation <!-- step-id: 1.1, agent: analyst, task: project-brief --> <!-- completed: 2025-06-30 13:23 -->
  - **Agent**: Analyst
  - **Action**: Create comprehensive project brief for épica 2, including optional brainstorming session and market research
  - **Output**: `project-brief.md`
  - **User Input**: Requirements and context for épica 2
  - **Optional Steps**: Brainstorming session, market research analysis

- [x] Step 2: Product Requirements Document <!-- step-id: 1.2, agent: pm, task: prd --> <!-- completed: 2025-06-30 13:23 -->
  - **Agent**: Product Manager
  - **Action**: Create detailed PRD from project brief using prd-tmpl template
  - **Output**: `prd.md`
  - **Requirements**: project-brief.md completed

- [x] Step 3: UI/UX Specification <!-- step-id: 1.3, agent: ux-expert, task: front-end-spec --> <!-- completed: 2025-06-30 13:23 -->
  - **Agent**: UX Expert
  - **Action**: Create UI/UX specification using front-end-spec-tmpl template
  - **Output**: `front-end-spec.md`
  - **Requirements**: prd.md completed
  - **Optional Steps**: User research prompt

- [x] Step 4: AI Frontend Prompt Generation <!-- step-id: 1.4, agent: ux-expert, task: generate-ai-frontend-prompt --> <!-- completed: 2025-06-30 13:23 --> <!-- decision: Skipped - proceeding with existing SvelteKit implementation -->
  - **Agent**: UX Expert
  - **Action**: Generate AI UI prompt for tools like v0, Lovable, etc.
  - **Output**: `v0_prompt` (optional but recommended)
  - **Requirements**: front-end-spec.md completed
  - **Decision Point**: User wants AI-generated UI <!-- decision-id: D1 -->

- [x] Step 5: Full-Stack Architecture Design <!-- step-id: 1.5, agent: architect, task: fullstack-architecture --> <!-- completed: 2025-07-03 03:02 -->
  - **Agent**: Architect
  - **Action**: Create comprehensive architecture using fullstack-architecture-tmpl template
  - **Output**: `fullstack-architecture.md`
  - **Requirements**: prd.md, front-end-spec.md completed
  - **Optional Steps**: Technical research, review generated UI structure

- [x] Step 6: PRD Updates (if needed) <!-- step-id: 1.6, agent: pm, task: update-prd --> <!-- completed: 2025-07-03 03:02 --> <!-- decision: Architecture aligned with PRD - no updates needed -->
  - **Agent**: Product Manager
  - **Action**: Update PRD based on architectural recommendations
  - **Output**: Updated `prd.md`
  - **Requirements**: fullstack-architecture.md completed
  - **Decision Point**: Architecture suggests PRD changes <!-- decision-id: D2 -->

- [x] Step 7: Artifact Validation <!-- step-id: 1.7, agent: po, task: validate-artifacts --> <!-- completed: 2025-07-03 03:02 -->
  - **Agent**: Product Owner
  - **Action**: Validate all documents for consistency and completeness using po-master-checklist
  - **Output**: Validation report
  - **Requirements**: All planning artifacts completed

- [x] Step 8: Document Corrections <!-- step-id: 1.8, agent: various, task: fix-issues --> <!-- completed: 2025-07-03 03:02 --> <!-- decision: Validation passed - no corrections needed -->
  - **Agent**: Various (as needed)
  - **Action**: Fix any issues flagged by PO validation
  - **Output**: Updated documents
  - **Requirements**: PO validation completed
  - **Decision Point**: PO finds issues requiring fixes <!-- decision-id: D3 -->

### Development Phase (IDE)

- [x] Step 9: Document Sharding <!-- step-id: 2.1, agent: po, task: shard-doc --> <!-- completed: 2025-07-03 03:02 -->
  - **Agent**: Product Owner
  - **Action**: Shard documents for IDE development (prd.md → docs/prd/ and docs/architecture/)
  - **Output**: Sharded documents in organized folders
  - **Requirements**: All artifacts validated and in project docs/

- [x] Step 10: Story Development Cycle - Epic 1 <!-- step-id: 2.2, repeats: true --> <!-- completed: 2025-06-26 --> <!-- current-step -->
- [x] Step 10: Story Development Cycle - Epic 6 <!-- step-id: 2.2, repeats: true --> <!-- completed: 2025-07-06 -->
- [ ] Step 10: Story Development Cycle - Epic 2 <!-- step-id: 2.2, repeats: true --> <!-- in-progress -->
  - **Repeats**: For each epic in the sharded documents

  - [x] Step 10.1: Create Story - Epic 2 Story 1 <!-- step-id: 2.2.1, agent: sm, task: create-next-story --> <!-- completed: 2025-07-07 -->
    - **Agent**: Scrum Master
    - **Action**: Create next story from sharded docs
    - **Output**: `story.md` (READY status - validated with 9/10 score)
    - **Requirements**: Sharded docs available
    - **Status**: ✅ **COMPLETED WITH VALIDATION**

  - [ ] Step 10.2: Review Draft Story <!-- step-id: 2.2.2, agent: analyst, optional: true --> <!-- skipped: story validated directly -->
    - **Agent**: Analyst/PM
    - **Action**: Review and approve draft story (optional)
    - **Output**: Updated story.md (Draft → Approved)
    - **Requirements**: story.md in Draft status
    - **Decision Point**: User wants story review <!-- decision-id: D4 -->
    - **Status**: ⏭️ **SKIPPED** - Story validated directly with checklist

  - [x] Step 10.3: Implement Story <!-- step-id: 2.2.3, agent: dev --> <!-- completed: 2025-07-07 -->
    - **Agent**: Developer
    - **Action**: Implement approved story
    - **Output**: Implementation files, updated File List
    - **Requirements**: story.md (READY status with 9/10 validation score)
    - **Status**: ✅ **COMPLETED** - Full implementation with comprehensive testing

  - [x] Step 10.4: QA Review <!-- step-id: 2.2.4, agent: qa, optional: true --> <!-- completed: 2025-07-07 -->
    - **Agent**: QA Engineer
    - **Action**: Senior dev review with refactoring ability
    - **Output**: QA feedback, updated implementation files
    - **Requirements**: Implementation completed
    - **Decision Point**: User wants QA review <!-- decision-id: D5 -->
    - **Status**: ✅ **COMPLETED** - Comprehensive QA review completed with memory leak fixes

  - [x] Step 10.5: Address QA Feedback <!-- step-id: 2.2.5, agent: dev --> <!-- completed: 2025-07-08 -->
    - **Agent**: Developer
    - **Action**: Address remaining QA feedback items
    - **Output**: Final implementation files
    - **Requirements**: QA review with unchecked items
    - **Decision Point**: QA left unchecked items <!-- decision-id: D6 -->
    - **Status**: ✅ **COMPLETED** - SM DOD validation passed with 9.2/10 score, all criteria met

  - [x] Step 10.1: Create Story - Epic 2 Story 2 <!-- step-id: 2.2.1, agent: sm, task: create-next-story --> <!-- completed: 2025-07-08 -->
    - **Agent**: Scrum Master
    - **Action**: Create next story from sharded docs
    - **Output**: `story.md` (READY status - validated)
    - **Requirements**: Previous story completed
    - **Status**: ✅ **COMPLETED WITH VALIDATION**

  - [x] Step 10.2: Review Draft Story - Epic 2 Story 2 <!-- step-id: 2.2.2, agent: analyst, optional: true --> <!-- completed: 2025-07-08 -->
    - **Agent**: Analyst/PM
    - **Action**: Review and approve draft story
    - **Output**: Updated story.md (Draft → Approved)
    - **Requirements**: story.md in Draft status
    - **Status**: ✅ **COMPLETED** - Story validated and approved

  - [x] Step 10.3: Implement Story - Epic 2 Story 2 <!-- step-id: 2.2.3, agent: dev --> <!-- completed: 2025-07-08 -->
    - **Agent**: Developer
    - **Action**: Implement approved story
    - **Output**: Implementation files, updated File List
    - **Requirements**: story.md (READY status)
    - **Status**: ✅ **COMPLETED** - Full implementation with comprehensive functionality

  - [x] Step 10.4: QA Review - Epic 2 Story 2 <!-- step-id: 2.2.4, agent: qa, optional: true --> <!-- completed: 2025-07-08 -->
    - **Agent**: QA Engineer
    - **Action**: Senior dev review with refactoring ability
    - **Output**: QA feedback, updated implementation files
    - **Requirements**: Implementation completed
    - **Status**: ✅ **COMPLETED** - QA review passed with 95/100 score

  - [x] Step 10.5: Address QA Feedback - Epic 2 Story 2 <!-- step-id: 2.2.5, agent: dev --> <!-- completed: 2025-07-08 -->
    - **Agent**: Developer
    - **Action**: Address remaining QA feedback items
    - **Output**: Final implementation files
    - **Requirements**: QA review with feedback items
    - **Status**: ✅ **COMPLETED** - All QA feedback addressed, story finalized

  - [x] Step 10.6: SM DOD Validation - Epic 2 Story 2 <!-- step-id: 2.2.6, agent: sm --> <!-- completed: 2025-07-08 -->
    - **Agent**: Scrum Master
    - **Action**: Validate story completion against Definition of Done
    - **Output**: DOD validation report
    - **Requirements**: QA feedback addressed
    - **Status**: ✅ **COMPLETED** - DOD validation passed with 85/100 score (Done status)

- [x] Step 11: Epic Retrospective - Epic 1 <!-- step-id: 2.3, agent: po, optional: true --> <!-- completed: 2025-06-26 -->
- [x] Step 11: Epic Retrospective - Epic 6 <!-- step-id: 2.3, agent: po, optional: true --> <!-- completed: 2025-07-06 -->
- [ ] Step 11: Epic Retrospective - Epic 2 <!-- step-id: 2.3, agent: po, optional: true --> <!-- pending -->
  - **Agent**: Product Owner
  - **Action**: Conduct epic retrospective after completion
  - **Output**: `epic-retrospective.md`
  - **Requirements**: All epic stories completed
  - **Decision Point**: User wants retrospective <!-- decision-id: D7 -->

## Key Decision Points

1. **AI Frontend Generation** (Step 4): <!-- decision-id: D1, status: completed -->
   - Trigger: UI/UX specification complete
   - Options: Generate v0/Lovable prompt or skip AI generation
   - Impact: Affects frontend development approach and timeline
   - Decision Made: _Skipped_ - Proceeding with existing SvelteKit implementation

2. **Architecture-Driven PRD Changes** (Step 6): <!-- decision-id: D2, status: completed -->
   - Trigger: Architecture document suggests story changes
   - Options: Update PRD stories or maintain current scope
   - Impact: Affects project scope and development sequence
   - Decision Made: _No Changes Needed_ - Architecture aligned with PRD

3. **PO Validation Issues** (Step 8): <!-- decision-id: D3, status: completed -->
   - Trigger: PO finds consistency or completeness issues
   - Options: Fix issues or proceed with known gaps
   - Impact: Affects documentation quality and development clarity
   - Decision Made: _No Issues Found_ - Validation passed successfully

4. **Story Review Process** (Step 10.2): <!-- decision-id: D4, status: completed -->
   - Trigger: Story created in Draft status
   - Options: Review and approve or proceed directly to implementation
   - Impact: Affects story quality and developer clarity
   - Decision Made: _Skipped_ - Story validated directly with checklist (9/10 score, READY status)

5. **QA Review Process** (Step 10.4): <!-- decision-id: D5, status: completed -->
   - Trigger: Story implementation completed
   - Options: Conduct QA review or proceed to next story
   - Impact: Affects code quality and technical debt
   - Decision Made: _QA Review Completed_ - Comprehensive review with critical memory leak fixes performed

6. **QA Feedback Resolution** (Step 10.5): <!-- decision-id: D6, status: completed -->
   - Trigger: QA review completed with unchecked items
   - Options: Address all feedback or proceed with partial completion
   - Impact: Affects story completion quality
   - Decision Made: _SM DOD Validation Passed_ - Epic 2 Story 1 completed with 9.2/10 score, all DOD criteria met

7. **Epic Retrospective** (Step 11): <!-- decision-id: D7, status: pending -->
   - Trigger: All epic stories completed
   - Options: Conduct retrospective or proceed to next epic
   - Impact: Affects process improvement and team learning
   - Decision Made: _Pending_

## Expected Outputs

### Planning Documents
- [x] `docs/project-brief.md` - Comprehensive project brief for épica 2 ✅
- [x] `docs/prd.md` - Product requirements document with detailed stories ✅
- [x] `docs/front-end-spec/` - UI/UX specification and design guidelines ✅
- [x] `docs/architecture/` - Complete technical architecture ✅
- [x] `v0_prompt` - AI frontend generation prompt (skipped - using existing SvelteKit) ✅

### Development Artifacts
- [x] Stories in `docs/stories/` - Epic 1 (3 stories) ✅, Epic 6 (3 stories) ✅, Epic 2 Stories 1-2 ✅ (Story 3 pending) 🔄
- [x] Implementation code - Epic 1 FastAPI/SvelteKit foundation ✅, Epic 6 Authentication ✅, Epic 2 Stories 1-2 ✅ (Story 3 pending) 🔄
- [x] Tests - Epic 1 comprehensive test suite ✅, Epic 6 auth tests ✅, Epic 2 Stories 1-2 ✅ (Story 3 pending) 🔄
- [x] Updated documentation - Epic 1 & 6 docs complete ✅, Epic 2 Stories 1-2 ✅ (Story 3 pending) 🔄

### Quality Assurance
- [x] Validation reports - PO artifact validation results ✅
- [x] QA feedback - Epic 1 & 6 code review completed ✅, Epic 2 Stories 1-2 ✅ (Story 3 pending) 🔄
- [x] Epic retrospective - Epic 1 ✅, Epic 6 ✅, Epic 2 (pending) 📋

## Prerequisites Checklist

Before starting this workflow, ensure you have:

- [x] Clear understanding of épica 2 requirements and scope ✅
- [x] Access to existing project documentation and codebase ✅
- [x] Understanding of current system architecture and constraints ✅
- [x] Stakeholder availability for decision points and reviews ✅
- [x] Development environment set up and configured ✅
- [x] Testing framework and deployment pipeline ready ✅
- [x] Team member availability for assigned roles ✅

## Project Setup Guidance

**For Generated UI Integration**:
- If using v0/Lovable for UI generation, consider project structure:
  - **Polyrepo setup**: Place downloaded project in separate frontend repo alongside backend repo
  - **Monorepo setup**: Place in `apps/web` or `packages/frontend` directory
  - Review architecture document for specific integration guidance

**Development Order**:
- **Frontend-heavy stories**: Start with frontend project/directory first
- **Backend-heavy or API-first**: Start with backend implementation
- **Tightly coupled features**: Follow story sequence in monorepo setup
- Reference sharded PRD epics for optimal development order

## Customization Options

Based on your project needs, you may:
- Skip AI frontend generation if using existing UI patterns
- Skip optional review steps if working with experienced team
- Add additional technical research if working with new technologies
- Choose monorepo over polyrepo setup based on team preferences
- Adjust story review process based on team size and experience

## Risk Considerations

- **Integration complexity**: Épica 2 may require significant integration with existing system
- **Scope creep**: Architecture phase may reveal additional requirements
- **Technical debt**: Balance between rapid development and code quality
- **Team coordination**: Multiple agents require clear handoff procedures
- **Testing strategy**: Ensure comprehensive testing approach for full-stack features

## Next Steps

1. Review this plan and confirm it matches your expectations for épica 2
2. Gather any missing prerequisites from the checklist above
3. Start workflow with: `*task workflow greenfield-fullstack`
4. Or begin with first agent: `@analyst`

**Available Options**:
- a) Review the plan together and make adjustments
- b) Start the workflow now with the analyst agent
- c) Gather prerequisites and prepare project context
- d) Modify the plan for specific épica 2 requirements

## Notes

- This workflow is designed for comprehensive full-stack development with quality gates
- Each phase builds upon previous outputs, ensuring consistency and completeness
- Optional steps can be skipped based on team experience and project constraints
- Decision points allow for workflow customization based on specific needs
- IDE development phase follows BMad Method patterns for story-driven development
- All planning artifacts should be saved to the project's `docs/` folder for reference

---

## 🔄 **CURRENT STATUS UPDATE** (Updated: 2025-07-08)

### Overall Progress: 85% Complete

**Current Phase**: Development Phase - Epic 2 Story Development
**Current Branch**: `feature/epic2_story2`
**Current Status**: ✅ **STORY 2 COMPLETE** - Ready to create Epic 2 Story 3

### ✅ **COMPLETED PHASES**

#### Planning Phase (100% Complete)
- **Duration**: June 30, 2025 - July 3, 2025
- **All 8 planning steps completed successfully**
- **Key Outputs**: project-brief.md, prd.md, front-end-spec/, architecture/
- **Quality**: All artifacts validated by PO

#### Epic 1 Development Cycle (100% Complete)
- **Duration**: June 22-26, 2025
- **Epic**: "The Smart Foundation" - Base Platform and Initial Control Panel
- **Stories**: 3/3 completed and delivered
- **Quality Score**: 9.5/10 average
- **Key Deliverables**: FastAPI backend, SvelteKit frontend, complete development infrastructure
- **Retrospective**: Completed with 36 learning items captured
- **Status**: ✅ **FULLY COMPLETE WITH RETROSPECTIVE**

#### Epic 6 Development Cycle (100% Complete)
- **Duration**: July 3-6, 2025
- **Epic**: "Security & Authentication Foundation"
- **Stories**: 3/3 completed and delivered
- **Key Deliverables**: JWT authentication, MercadoLibre OAuth integration, secure credential management
- **Final PR**: #14 merged July 6, 2025
- **Status**: ✅ **FULLY COMPLETE**

### 🔄 **CURRENT DEVELOPMENT PHASE**

#### Epic 2 Development Cycle (In Progress)
- **Current Status**: Story 2 DONE - SM DOD validation passed with 85/100 score
- **Branch**: `feature/epic2_story2`
- **Epic Focus**: AI content generation and core product features
- **Progress**: 66% (Stories 1-2 complete, Story 3 pending)
- **Completion Point**: ✅ Story 2 fully complete with all DOD criteria met
- **Next Actions**: Create Epic 2 Story 3 using SM agent

### 📊 **DEVELOPMENT METRICS**

| Metric | Value | Status |
|--------|-------|--------|
| Planning Phase | 100% | ✅ Complete |
| Epic 1 (Foundation) | 100% | ✅ Complete |
| Epic 6 (Security) | 100% | ✅ Complete |
| Epic 2 (AI Features) | 66% | ✅ Stories 1-2 DONE |
| **Overall Project** | **85%** | **🔄 Active** |

### 🏆 **KEY ACHIEVEMENTS**

1. **Complete Foundation**: Production-ready FastAPI/SvelteKit platform
2. **Security Implementation**: Full authentication and OAuth integration
3. **AI Content Generation**: Epic 2 Story 2 completed with comprehensive AI features
4. **Quality Standards**: 9.0/10 average quality score maintained across all stories
5. **Learning Integration**: 36+ learning items captured and applied
6. **Process Optimization**: Streamlined development workflow established

#### Epic 2 Story 2 Achievements:
- **PO Validation**: 94/100 - Strong alignment with business requirements
- **Dev Implementation**: All 6 development tasks completed successfully
- **QA Review**: 95/100 - High quality implementation with minimal issues
- **SM DOD Validation**: 85/100 - Done status achieved with all criteria met
- **Technical Deliverables**: AI content generation, validation systems, and user interfaces

### 🎯 **NEXT STEPS**

1. **Immediate**: Create Epic 2 Story 3 using SM agent (*agent sm)
2. **Current Story**: Epic 2 Story 2 DONE - AI content generation and validation complete
3. **Short-term**: Complete Epic 2 development cycle (Story 3 remaining)
4. **Medium-term**: Conduct Epic 2 retrospective
5. **Long-term**: Continue with remaining epics per PRD

### 🔄 **WORK RESUMPTION NOTES**
- **Story Status**: Epic 2 Story 2 is DONE (85/100 SM DOD validation score)
- **Story Location**: `docs/stories/epic2_story2.md`
- **Agent Required**: Scrum Master (@sm)
- **Implementation Focus**: Create Epic 2 Story 3 for final AI features
- **Branch**: `feature/epic2_story2` (complete, ready for merge)
- **Next Action**: Call SM agent to create next story

### 🔍 **WORKFLOW HEALTH**

- **Timeline**: On track - 85% complete
- **Quality**: Excellent - all quality gates passing (85/100 latest story score)
- **Team Velocity**: Consistent - averaging 2 stories/sprint
- **Learning**: Active - continuous process improvement
- **Risk**: Low - stable foundation with proven patterns
- **Current State**: ✅ **STORY 2 COMPLETE** - Ready to create Story 3

**Status**: ✅ **HEALTHY AND READY FOR NEXT STORY**

---
*This plan can be updated as you progress through the workflow. Check off completed items to track progress.*
