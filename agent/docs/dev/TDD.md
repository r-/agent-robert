# TDD.md
Project: Agent R.O.B.E.R.T.
Owner: Student team
Status: draft
Last updated: 2026-02-18
Related milestone: MS-01 (Agent Core)

## 1) Summary
- What this builds: The core logic of the R.O.B.E.R.T. agent.
- Technical approach: A pure Python package using Level 1/2 modules, exposing a single `process()` function. No HTTP/Web framework included.
- Key constraints: Python 3.11+, zero web dependencies, core logic < 2,000 lines.

## 2) Architecture (big picture)
### Modules / boundaries
- `agent` — responsibility: Orchestrate the receive-build-call-execute loop.
- `session` — responsibility: Persistent message storage (JSONL).
- `providers` — responsibility: Interface with LLM providers (ports/adapters).
- `tools` — responsibility: Local tool implementations (read-only file, opt-in shell).
- `config` — responsibility: Loading and validating agent behavior.

### Data ownership
- `session` owns the conversation history files (`sessions/{key}.jsonl`).
- `config` owns the behavioral defaults and security flags.

### Event / flow (if relevant)
Input (Message + Key) → Session Load → Context Build (System + History) → LLM Call → [Tool execution loop] → Response → Session Save → Output.

## 3) Core components
- Component: `ContextBuilder` — Assembles the system prompt from base identity + relevant skills.
- Component: `AgentLoop` — Handles the iterative LLM callback logic and max iteration termination.
- Component: `ToolRegistry` — Stores available tool ports and dispatches to adapters if enabled.

## 4) Public contracts
- Contract: `agent.process(message: str, session_key: str) -> str`
  - Input: User message and unique session identifier.
  - Output: Final assistant response string.

## 5) Key scenarios
### Scenario A: Simple Chat
1. User calls `process("Hi", "user1")`.
2. Session loads `user1.jsonl`.
3. LLM responds with "Hello".
4. "Hello" appended to `user1.jsonl`, returned to user.

### Scenario B: Tool Call (Disabled)
1. User asks "What's in my root folder?"
2. LLM requests `ls /`.
3. Agent checks `config.tools.shell.enabled` (is False).
4. Agent returns "Tool 'shell' is disabled by policy" to LLM.
5. LLM responds "I cannot access your shell."

## 6) Risks & mitigations
- Risk: Too many iteration loops — Mitigation: Maximum iteration counter (default 20).
- Risk: Session file corruption — Mitigation: Per-line JSONL storage (append-only).
- Risk: LLM escaping sandbox — Mitigation: Strict parameter type checking and allowlists at the Tool Adapter level.

## 7) Testing plan (minimal)
- Unit: Provider adapters (mocking network), ContextBuilder (prompt assembly), Config resolution.
- Integration: Agent loop with a fake provider returned predefined tool calls.
- Smoke test: Run `robert chat` and say "hello".

## 8) Decisions (technical)
- [2026-02-18] JSONL for sessions — Why: Simple, append-only, no database needed.
- [2026-02-18] Local path for skills — Why: Security (no remote injection vectors).
- [2026-02-18] No Library for LLM — Why: Keep it tiny, use direct HTTP calls via `httpx` to OpenRouter (same as router).

## 9) Links
- Product requirements: `PRD.md`
- Research notes: `RESEARCH.md`
- Plan: `BACKLOG.md`
