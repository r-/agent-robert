# Sprint 01 — Foundation & Bridge
Dates: 2026-02-18 → 2026-02-18
Owner: Student team

## 1) Sprint goal
Establish the core "Agent R.O.B.E.R.T." logic and bridge it to the "python-api-router" to prove the multi-project architecture works.

## 2) Scope (selected from BACKLOG.md)
- BL-001 — Project Scaffold (Done)
- BL-002 — Agent Loop & Context (Done)
- BL-003 — Provider Integration (Done)
- BL-004 — Session Persistence (Done)
- BL-020 — Router Bridge (Done)
- BL-021 — Tool System (Done)
- BL-030 — Dangerous Tools (Done)

## 3) Definition of Done (for this sprint)
- [x] All scoped items meet their DoD
- [x] CLI `robert chat` works end-to-end
- [x] Router `/agent` endpoint calls robert.process() successfully
- [x] Security defaults verified (tools off unless configured)

## 4) Plan (simple)
- Build core agent package with pure Python modules.
- Create composition root for dependency injection.
- Expose `robert.process()` as the single public API.
- Add `agent-robert` as local dependency to `api-router`.
- Implement tool registry with safety checks.

## 5) Demo checklist
- [x] Run `test_full.py` to see "Proxy OK" and "Hallå! Jag är Agent R.O.B.E.R.T."
- [x] Ask Robert to "read ARCHITECTURE.md" to verify the first tool.
- [x] Ask Robert to "run dir" and see it fail (security default).
- [x] Run `pytest` and see 6 passing tests.

## 6) Retro
### What went well
- The Level 1 single-file module pattern worked perfectly for speed.
- The two-project split successfully isolated web concerns from agent logic.

### What was painful / confusing
- Terminal deadlocks when running server + client simultaneously in the same environment.
- Missing `__init__.py` exports caused a 500 error during initial bridge test.

### Improvements / actions (next sprint)
- [ ] Implement progress streaming (Milestone 04).
- [ ] Add Docker support for easy deployment.

## 7) Links
- Backlog: `../BACKLOG.md`
- PRD: `../PRD.md`
- TDD: `../TDD.md`
- Research: `../RESEARCH.md`
