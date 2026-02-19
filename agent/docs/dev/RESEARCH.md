# RESEARCH.md
Project: Agent R.O.B.E.R.T.
Owner: Student team
Last updated: 2026-02-18

## 1) Purpose
This document captures findings from existing agent architectures (Nanobot, OpenClaw) and how they inform R.O.B.E.R.T.'s security-first, minimal design.

## 2) Questions we’re answering
- Q1: How to build a useful agent in < 2,000 lines of code?
- Q2: How to prevent common agent security risks (unrestricted shell, silent file edits)?
- Q3: How to decouple agent logic from web/platform concerns?

## 3) What we found (copy-ready)
- **Nanobot Complexity** → Most lightweight agents are still tightly coupled (e.g., agent loop directly importing tools and providers).
- **Security Posture** → "Default-on" dangerous tools are the norm. Even restricted workspaces are often optional/opt-in.
- **Async Indirection** → Event buses are great for decoupling but add overhead for single-user CLI agents. 
- **Two-Project Split** → Separating the Agent logic (pure Python) from the Routing/Web layer (FastAPI) significantly reduces complexity in the agent core.

## 4) Options (only if needed)

### A) Pure Async Message Bus (Nanobot style)
- Pros: Decouples handlers from agent engine.
- Cons: High cognitive overhead for simple CLI usage.
- Risks: Harder to trace logic in a small project.

### B) Functional/Iterative Loop (R.O.B.E.R.T. style)
- Pros: Extremely simple, easy to read, minimal lines of code.
- Cons: Blurs boundaries if not disciplined.
- Risks: Harder to add multi-user support later if logic isn't modular.

**Recommendation:** Functional Loop within a Pragmatic Modular Monolith. Use Level 1 modules for speed, promote to Level 2 for boundaries.

## 5) Spikes / experiments (only if done)
- Spike: API Router Proxy → Goal: Verify FastAPI as a proxy for LLM calls → Result: Successful (2.23s latency) → Next: Build Agent Bridge.

## 6) Sources & notes
- Nanobot Source Code — Lightweight inspiration.
- Pragmatic Modular Monolith — Architectural blueprint.
- Maker.nu FastAPI Proxy Article — Base for api-router.

## 7) Open questions / next steps
- How to handle tool allowlists in config? → Next: Define schema in TDD.md.
- Best way to stream tool outputs to CLI/Web? → Next: Research generator-based loop.
