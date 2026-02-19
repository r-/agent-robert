# BACKLOG.md
Project: Agent R.O.B.E.R.T.
Owner: Student team
Last updated: 2026-02-18

## 1) Current milestone
**Milestone:** MS-01 — Agent Core
**Milestone goal:** A functional CLI agent that can chat and persist sessions.

## 2) Active backlog (prioritized)

### P1 — Must (MVP)
#### BL-001 — Project Scaffold
- Milestone: MS-01
- Outcome: `pyproject.toml`, folder structure, and basic CLI entry point.
- DoD: `robert --version` works. (Done)

#### BL-002 — Agent Loop & Context
- Milestone: MS-01
- Outcome: `agent.process()` can take a message and return a hardcoded response.
- DoD: ContextBuilder assembles a system prompt. (Done)

#### BL-003 — Provider Integration
- Milestone: MS-01
- Outcome: Connection to OpenRouter via `httpx`.
- DoD: Real chat response returned from an LLM. (Done)

#### BL-004 — Session Persistence
- Milestone: MS-01
- Outcome: Messages saved to `.jsonl` files.
- DoD: Conversation "remembers" previous messages. (Done)

### P2 — Should (Integration)
#### BL-020 — Router Bridge
- Milestone: MS-02
- Outcome: `api-router` can call `agent-robert` via Python API.
- DoD: `curl /agent` results in a chat response. (Done)

#### BL-021 — Tool System (Read-only)
- Milestone: MS-02
- Outcome: File system read tool implemented and enabled by default.
- DoD: Agent can read its own `PRD.md`. (Done)

### P3 — Could (Extra Features)
#### BL-030 — Dangerous Tools (Shell/Write)
- Milestone: MS-03
- Outcome: Shell and File Write tools built but disabled.
- DoD: Opt-in via config works; security logs recorded. (Done)

#### BL-040 — Voice Interaction (Audio)
- Milestone: MS-04
- Outcome: Frontend records audio, Backend processes `input_audio`.
- DoD: Voice query returns a sensible text response. (Done)

#### BL-050 — Smart Home Control (Home Assistant)
- Milestone: MS-05
- Outcome: `robert_bridge` for HA voice input + `homeassistant` toolset for control.
- DoD: Can receive voice command from HA and execute service call via API. (Done)

## 3) Tech debt / chores (time-boxed)
#### TD-001 — Architecture Enforcement
- Milestone: MS-01
- Why: Ensure boundaries are respected early.
- DoD: Script verifies no internal imports across modules.

## 4) LATER
- Multi-user session management in Router.
- Streaming responses (SSE).
- Memory consolidation (summaries).

## 5) ICEBOX
- Telegram plugin.
- Discord plugin.
- Skill marketplace (local only).
