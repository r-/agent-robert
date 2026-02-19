# PRD.md
Project: Agent R.O.B.E.R.T.
Owner: Student team
Status: draft
Last updated: 2026-02-18

## 1) Summary
- What we're building: An ultra-minimal, security-first personal AI assistant in Python with a clean Python API
- For who: Developers who want a small, understandable, safe agent they fully control
- Why now: Existing agents (nanobot, OpenClaw) sacrifice safety for features — we want the opposite tradeoff
- Success looks like:
  - Core agent works in < 2,000 lines of code
  - Dangerous tools exist but are **off by default** (opt-in, never opt-out)
  - A developer can read and understand the entire codebase in one sitting
  - Follows Pragmatic Modular Monolith architecture (ARCHITECTURE.md)
  - Agent is callable via Python API — no web framework dependency in the agent itself

## 2) Problem & users
### Problem statement
Current lightweight AI agents (e.g. nanobot) pack in features like shell execution, file editing, web fetching, and remote skill installation — all enabled by default. This creates a large attack surface and makes the agent unpredictable for users who want a safe, controllable assistant.

### Target users
- Primary: Developers who want a personal AI assistant they can trust and modify
- Secondary: Students learning how AI agents work by reading clean, small code

### Context / use cases
- Chat with an LLM through a CLI with persistent conversation history
- Use bundled skills (not downloaded) to guide the agent's behavior
- Optionally enable file/shell tools in a sandboxed workspace when explicitly needed
- Extend with new LLM providers without changing core code
- Expose agent capabilities to web clients via api-router (separate project)

### System context (two projects)
agent-robert is one half of a two-project architecture:

- **agent-robert** — pure Python agent. Exposes a **Python API** (no HTTP, no web framework). Handles agent logic, tools, session, skills.
- **api-router** — separate FastAPI project. Handles HTTP endpoints, client authentication (clientKey), rate limiting, CORS, and multi-tenant access. Can proxy to LLM providers AND call agent-robert's Python API.

The agent never handles HTTP or auth. The router never handles agent logic.

```
Browser / App / External client
        │
        ▼
┌─────────────────────────────────┐
│  api-router (FastAPI)           │  ← HTTP, auth, rate limiting, multi-tenant
│  - POST /proxy  → LLM provider │
│  - POST /agent  → agent-robert │
└─────────┬───────────────────────┘
          │ Python API (in-process)
          ▼
┌─────────────────────────────────┐
│  agent-robert (pure Python)     │  ← Agent logic, tools, session, skills
│  - No web framework             │
│  - No HTTP                      │
│  - No auth                      │
│  - Clean Python API              │
└─────────────────────────────────┘
```

## 3) Goals & non-goals
### Goals
- G1: Minimal core — the agent loop, context building, session, provider, and config in ~2,000 lines
- G2: Security by default — all dangerous capabilities disabled until explicitly enabled in config
- G3: Clean architecture — follows ARCHITECTURE.md (hard shell, modular, testable)
- G4: Understandable — a developer can read the entire agent in one sitting
- G5: Extensible — new providers/tools can be added without modifying core code
- G6: Python API first — the agent's primary interface is a Python API; CLI and api-router are consumers of it

### Non-goals
- NG1: NOT a multi-channel chat platform (no Telegram, Discord, Slack, etc.)
- NG2: NOT a skill marketplace (no downloading/installing skills from the internet)
- NG3: NOT a web-connected agent (no web search, web fetch, or URL reading)
- NG4: NOT an agent social network participant (no Moltbook, ClawdChat, etc.)
- NG5: NOT OAuth/SSO complexity (simple API key configuration only)
- NG6: NOT a web server — agent-robert has no HTTP layer (that's api-router's job)

## 4) Scope (MVP)

### MVP: must-have (always on)
- **Python API** — the primary interface: `agent.process(message, session_key) → response`
- CLI chat interface (interactive mode, built on top of the Python API)
- Agent loop (receive → build context → call LLM → respond)
- Context builder (system prompt + conversation history + bundled skills)
- Session persistence (JSONL, per-conversation)
- LLM provider abstraction (at least one provider working, e.g. OpenRouter)
- Configuration (JSON config file, safe defaults)
- Bundled skills (markdown files shipped with the agent, read-only)
- Read-only file tool (read files within workspace only)

### MVP: must-have (built but disabled by default)
- File write/edit tools — **requires** `tools.fileWrite.enabled = true` + workspace restriction
- Shell/exec tool — **requires** `tools.shell.enabled = true` + workspace restriction + command allowlist
- Subagent spawning — **requires** `tools.spawn.enabled = true`
- Cron / scheduled tasks — **requires** `cron.enabled = true`
- Heartbeat / proactive wake-up — **requires** `heartbeat.enabled = true`
- MCP server connections — **requires** `tools.mcp.enabled = true`

### Should-have (if time)
- Message bus (async queue) for future channel support
- Progress streaming (show intermediate output while tools run)
- Memory consolidation (summarize old messages into persistent memory)

### Could-have (nice to have)
- One external channel (e.g. Telegram) as a plugin
- Docker support

## 5) Requirements (acceptance-level)

- R1: Python API works end-to-end
  Acceptance: Calling `agent.process("hello", "test")` returns an LLM response

- R2: CLI chat works end-to-end
  Acceptance: User runs `robert chat`, types a message, gets an LLM response

- R3: Conversation persists across sessions
  Acceptance: User exits, restarts, and previous conversation is available

- R4: Dangerous tools are off by default
  Acceptance: With default config, shell/write/edit/spawn/cron/heartbeat/mcp do nothing even if the LLM tries to call them

- R5: Enabling a tool requires explicit config + workspace restriction
  Acceptance: Setting `tools.shell.enabled = true` without `restrictToWorkspace = true` logs a security warning

- R6: Shell tool has command allowlist
  Acceptance: Only commands matching the allowlist execute; others are rejected with a clear error

- R7: Provider is swappable via config
  Acceptance: Changing `provider` in config switches the LLM without code changes

- R8: Bundled skills load from local files only
  Acceptance: Skills are read from a directory shipped with the agent; no network requests for skills

- R9: Codebase stays under 2,000 lines (core agent)
  Acceptance: A line-count script confirms core modules total < 2,000 lines

- R10: Architecture fitness functions pass
  Acceptance: No cross-module internal imports; no circular dependencies

- R11: Agent has no web framework dependency
  Acceptance: agent-robert's dependencies do not include FastAPI, Flask, or any HTTP server library

- R12: api-router can call agent-robert's Python API
  Acceptance: api-router imports agent-robert and calls `agent.process()` to get a response

## 6) UX / flows (lightweight)

### Main flow: CLI
1. User runs `robert chat`
2. Agent loads config, initializes provider, loads session
3. User types a message
4. Agent builds context (system prompt + history + skills), calls LLM
5. If LLM returns tool calls AND the tool is enabled → execute tool, loop back to step 4
6. If LLM returns tool calls AND the tool is disabled → return "tool not available" to LLM, loop
7. Agent displays response
8. Session is saved
9. Repeat from step 3 (or user types `exit`)

### Main flow: via api-router
1. Client sends `POST /agent` to api-router with clientKey + message
2. api-router authenticates clientKey, checks policy
3. api-router calls `agent.process(message, session_key)` (Python API, in-process)
4. Agent processes as above (steps 4–8)
5. api-router returns the response as JSON to the client

### Edge cases
- LLM requests a disabled tool → agent returns a clear refusal, does not error
- LLM loops too many times → max iteration limit (default: 20), agent explains and stops
- No API key configured → clear error message on startup with setup instructions
- Config file missing → auto-create with safe defaults

### Security flow (enabling dangerous tools)
1. User edits config: `tools.shell.enabled = true`
2. If `restrictToWorkspace` is not set → agent logs a **warning** on startup
3. Shell tool only executes commands matching the allowlist
4. All tool executions are logged with timestamp, tool name, parameters, and result

## 7) Success metrics
- Metric: Core line count — Target: < 2,000 lines
- Metric: Time to understand codebase — Target: < 1 hour for a Python developer
- Metric: Default config attack surface — Target: 0 dangerous tools enabled
- Metric: Architecture fitness tests — Target: 100% pass rate

## 8) Risks & assumptions

- Risk: LLM providers change their API format — Mitigation: Provider abstraction isolates changes to one adapter
- Risk: "Just 2,000 lines" becomes a constraint that hurts quality — Mitigation: The limit is a goal, not a hard rule; quality > brevity
- Risk: Disabled tools frustrate users who expect full functionality — Mitigation: Clear error messages explaining how to enable, with security implications
- Assumption: Users are developers comfortable editing JSON config — How to validate: Target user interviews
- Assumption: OpenRouter/LiteLLM provides sufficient provider coverage — How to validate: Test with 3+ LLM providers

## 9) Decisions (product-level)
- [2026-02-18] Python API is the primary interface — Why: Keeps agent web-framework-free and testable — Impact: CLI and api-router are both consumers of the same API
- [2026-02-18] Two-project architecture (agent-robert + api-router) — Why: Separation of concerns — agent handles logic, router handles HTTP/auth/multi-tenant — Impact: Agent stays tiny; web concerns don't leak in
- [2026-02-18] Dangerous tools built but disabled by default — Why: Security-first without sacrificing capability — Impact: Every tool needs an enable flag and config check
- [2026-02-18] No skill downloading — Why: Remote markdown → system prompt is an injection vector — Impact: Skills are bundled only; users add skills by placing files locally
- [2026-02-18] CLI only for MVP — Why: Each channel adds ~500-1000 lines + platform dependencies — Impact: No Telegram/Discord/etc. in core; possible as plugins later
- [2026-02-18] No web search/fetch — Why: Data exfiltration risk + network dependency — Impact: Agent cannot access the internet
- [2026-02-18] Shell tool requires allowlist — Why: Open shell = arbitrary code execution — Impact: Users must explicitly list allowed commands

## 10) Links
- Architecture: `ARCHITECTURE.md`
- Research: `RESEARCH.md`
- Technical design: `TDD.md`
- Plan: `BACKLOG.md` + `/sprints/`
