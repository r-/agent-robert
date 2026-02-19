# ARCHITECTURE.md
## Pragmatic Modular Monolith
*(Modular Hard-Shell Architecture)*

**Version:** 1.1

> **Goal:** Build software that stays easy to change as teams, features, and integrations grow.  
> **Core idea:** *Outside is strict. Inside is free.*

---

## TL;DR

- Each module has **one hard public shell**: `/api`
- Everything else is **private**: `/internal`
- **No cross-module imports** from `/internal`
- **Dependencies point inward**
- **Composition (wiring) happens at the edge** (only the app’s startup/composition root is allowed to choose and connect implementations—modules never “pick” databases/providers internally)
- **Validation + stable errors** happen at the API boundary
- **Events are facts**, not “requests for work”
- **Data ownership** is per module (including in tests)
- Modules scale by **complexity levels** (Level 1 → Level 4)
- Strong module APIs make **later service extraction possible**
- Tests mirror the architecture + **fitness functions** enforce it

> **Architecture defines boundaries and dependencies.  
> Internals decide implementation.  
> Outside is strict. Inside is free.**

---

## 1. Purpose

This document defines a **pragmatic standard** for building maintainable systems without falling into either extreme:

- **Big Ball of Mud** (no boundaries, everything coupled)
- **Over-engineering too early** (ceremonial layers for trivial problems)

If code conflicts with this document, **the document wins**  
(or the document must be explicitly updated via ADR).

---

## 2. Core idea (hard shell, flexible internals)

Every module consists of:

- a **public API** (`/api`) — the module’s *contract*
- **private internals** (`/internal`) — the module’s *implementation*

This allows teams to:
- start simple
- refactor safely
- scale structure only when complexity demands it

### 2.1 Visual model (hard shell)

Think of each module as a sealed box:

    Outside world (UI / other modules / integrations)
                     |
                     v
              modules/<m>/api        (ONLY public surface)
                     |
                     v
            modules/<m>/internal     (everything else)
                     ^
                     |
            /composition (wiring only; no business logic)

**Rule of thumb:** If it’s not intentionally part of the contract, it does not belong in `/api`.

---

## 3. Dependency direction (non-negotiable)

Dependencies must always point **inward**:

    Details (UI / DB / Frameworks)
               ↓
    Use-cases (Application / Orchestration)
               ↓
    Policy (Domain / Core rules)

This is **not MVC**.  
It is a **system-wide dependency rule**.

Forbidden:
- policy/domain depending on UI, DB, network, OS, or framework
- use-cases choosing infrastructure details
- skipping layers “for convenience”

---

## 4. The hard-shell rule (one API per module)

Each module exposes **exactly one** public API.

- The API describes **capabilities**, not implementation
- Everything behind the API is private
- Other modules may depend **only** on the API

If refactoring internals breaks other modules,  
**the shell is leaking**.

---

## 5. `/internal` rule (physical enforcement)

- `/api` → **public**
- `/internal` → **private**

Rules:
- Code outside a module must **never** import from another module’s `/internal`
- **Only `/composition` may import from a module’s `/internal`** — and **only for wiring/instantiation**
- `/composition` must contain **no business logic**
- **No-bypass rule:** UI/controllers must call the module **via `/api`**, never by importing internal services directly (even if the codebase makes it “easy”).

Enforce with tooling where possible  
(linters, build rules, architecture tests / fitness functions).

---

## 6. What belongs in `/api` (avoid “API as a junk drawer”)

`/api` is the module’s **public contract** (not necessarily HTTP).

`/api` may contain:
- contracts / interfaces (ports)
- DTOs / public types
- commands/queries (if you use them)
- events (that others may subscribe to)
- stable error types / error codes

`/api` must NOT contain:
- database/network/framework code
- concrete implementations
- “helpers” that leak internals by convenience
- **internal entity types** (ORM entities, internal domain objects)
- **third-party SDK types** (Stripe/Google SDK objects, framework request/response objects)

### 6.1 No internal types cross the shell
Everything leaving a module boundary must be expressed as **native DTOs** defined in `/api`.

---

## 7. API evolution rules (keep contracts stable over time)

APIs are long-lived. Internals are free to change.

Rules:
- **Prefer additive changes** (new fields, new endpoints/commands) over breaking changes
- If breaking is unavoidable:
  - require an **ADR**
  - provide a **migration path** (adapter, transitional DTO, or deprecation window)
- DTOs crossing module boundaries should be:
  - explicit
  - version-tolerant (ignore unknown fields; avoid fragile positional formats)
- Public error codes are **part of the contract**: add new codes carefully, avoid changing meaning

---

## 8. Events & messaging rules (facts, not requests)

Events reduce coupling *when used correctly*.

### 8.1 Event vs API (the core rule)
- **API/Command**: “please do X” (expects a result/decision)
- **Event**: “X happened” (a fact others may react to)

**Red flag:** events used to “request work” (that’s a command in disguise).

### 8.2 Event ownership
- The module that owns the behavior/data **publishes** the event.
- Other modules **subscribe** and update their own internals/data.
- Subscribers should be safe to run:
  - **idempotent** where possible
  - resilient to duplicates/out-of-order delivery (if applicable)

### 8.3 Event payload discipline
- Prefer stable identifiers (e.g., `userId`, `paymentId`) over deep internal structures
- Never leak internal DB schema or internal models through events

---

## 9. Data ownership (and yes, it applies to tests)

Each module **owns its data**.

Rules:
- No other module reads/writes the owning module’s tables/collections directly
- If you need data from another module:
  - call its `/api`, or
  - subscribe to its events and build a **projection/read model**

**Testing rule:**  
Module A’s tests must not require populating Module B’s database tables.  
If A needs B behavior, use **contract/integration tests** and go through B’s `/api`.

### 9.1 Performance guideline (avoid “distributed joins”)
A common failure mode is *Distributed Joins*:
- “Call Module A, then Module B for each item, then Module C… merge in memory.”

Preferred approach:
- Build a **projection/read model** inside the consuming module.
- Update it via **events** (or scheduled sync where appropriate).
- Accept **eventual consistency** and make it explicit in UX and expectations.

### 9.2 Cross-module consistency (the Transaction Rule)
If a business process spans multiple modules, prefer:

- **Atomic within a module**
- **Eventually consistent across modules**

**The rule:** Use events to trigger downstream changes in other modules.

**The boundary test:**  
If you find that absolute database atomicity (a single transaction) is required across two modules, the boundary is likely wrong.  
You should either:
- merge the modules, or
- redefine data ownership to eliminate the hard dependency.

---

## 10. Shared code (make “shared” explicit or it becomes mud)

Shared code is a common leak path. Handle it explicitly.

Allowed patterns:
- **Shared contracts module** (rare): e.g. `/modules/platform/api` for cross-cutting *interfaces only*
- Copy small utilities locally instead of creating a “shared utils” dumping ground
- If shared grows, it must have:
  - an owner
  - a stable API
  - its own tests

### 10.1 The Rule of Three (anti-premature sharing)
Don’t create shared modules/utilities until the code is needed by **three distinct modules**.

Until then:
- local duplication is cheaper than the wrong abstraction
- shared too early becomes coupling disguised as convenience

Forbidden:
- random `/shared` folder with “helpers everyone imports”
- shared domain models that couple unrelated modules

---

## 11. Canonical repository layout

    /src
      /composition                # startup & wiring (only place that chooses implementations)
      /modules
        /<module>
          /api                    # PUBLIC – contracts only
          /internal               # PRIVATE – never imported by other modules
            /application          # use-cases (optional structure)
            /domain               # rules, invariants (optional structure)
            /infrastructure       # adapters (optional structure)
      /plugins                    # optional extensions
    /tests
      /unit
      /contract
      /integration
    /docs
      /adr

---

## 12. Module complexity levels (solve “all or nothing”)

Modules scale **by complexity**, not ideology.  
Levels describe **packaging and enforcement**, not internal patterns.

### Level 1 — Flat module (prototype / single-file)
Use when:
- exploring ideas
- teaching / learning
- very small features
- module fits comfortably in one file

Rules:
- **Single file allowed** (e.g. `modules/bus.py`). No folders needed.
- **`__all__` declares the public API.** Other modules may only import names listed in `__all__`.
- **`_` prefix marks internals.** Everything prefixed with `_` is private implementation.
- **Visual separator recommended.** Use a comment block to make the split obvious:

```python
# modules/bus.py

__all__ = ["InboundMessage", "OutboundMessage", "MessageBusPort"]

# ─── API (public contract) ───────────────────────────

from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class InboundMessage:
    channel: str
    content: str

@dataclass
class OutboundMessage:
    channel: str
    chat_id: str
    content: str

class MessageBusPort(ABC):
    @abstractmethod
    async def publish(self, msg: InboundMessage) -> None: ...

# ─── INTERNAL (private — do not import from outside) ──

import asyncio

class _AsyncQueueBus(MessageBusPort):
    def __init__(self):
        self._queue = asyncio.Queue()

    async def publish(self, msg):
        await self._queue.put(msg)
```

- Avoid creating 2,000-line "mega-files" just to stay in Level 1; **move to Level 2** if organization is needed.
- Still exposes **one API** (via `__all__`)
- Internals never imported externally (enforced by `_` prefix convention)

**Promotion path (split, never rewrite):**

```
Level 1:  modules/bus.py                  ← single file, __all__ + _ separation
             ↓ grows enough
Level 2:  modules/bus/api.py              ← cut at the separator comment
          modules/bus/internal.py
             ↓ grows more
Level 3:  modules/bus/api/types.py        ← split further as needed
          modules/bus/internal/queue.py
          modules/bus/internal/dispatch.py
```

### Level 2 — Hard shell module (recommended early default)
Use when:
- the module is real and expected to evolve
- logic still fits in a few files

Rules:
- API separated
- internals private
- internal structure optional

### Level 3 — Structured internals (use when helpful)
Use when:
- multiple use-cases
- growing rule complexity
- multiple contributors
- integrations appear (DB, network, files)

Rules:
- same hard shell as Level 2
- internals organized for clarity and testability
- **any internal pattern allowed**

### Level 4 — Large or critical module
Use when:
- business-critical logic
- high risk or high complexity
- many contributors
- long-term maintenance cost matters

Rules:
- stable API
- strong tests
- explicit ownership
- internals may contain sub-features (still private)

> A module may move up levels over time,  
> but must never break its API contract without an ADR + migration plan.

---

## 13. Modules vs Plugins (key distinction)

### Module
A **module** is:
- part of the core system
- always present at runtime
- compiled and deployed with the application
- governed by the hard-shell rules

Default choice: **build a module**.

### Plugin
A **plugin** is:
- an optional extension
- enabled/disabled by configuration or runtime discovery
- replaceable without changing core code

**Rule:** Core modules must never depend on plugins.

---

## 14. Composition root (critical enforcement point)

Composition is where the system is assembled.

Only composition may decide:
- which database or API implementation to use
- which plugins are enabled
- which adapters are real or fake

Rules:
- composition contains **no business logic**
- composition may depend on everything
- business logic must not choose infrastructure

### 14.1 How modules receive dependencies (pragmatic DI)
Modules should receive their dependencies via **constructor injection** (or factory injection):

- dependencies are passed in explicitly (db handles, clients, loggers, clocks, config)
- no internal “reach out” to globals/singletons/service locators
- easy to substitute fakes in tests

Anti-patterns:
- `GlobalContainer.resolve(...)` inside module internals
- modules “creating their own” DB clients/providers internally
- hidden static singletons

### 14.2 Modularized wiring (supporting the Delete Rule)
To support the Delete Rule, the Composition Root wiring must be modular.

Each module should expose **one internal “wire-up/registration” function** (inside `modules/<m>/internal/...`) that `/composition` calls.

This ensures deleting a module folder requires:
- removing the module folder, and
- removing **one line** in the main startup/composition file

…instead of hunting for scattered references.

Rules:
- registration functions contain **wiring only** (no business logic)
- registration is **not** a second public API (it is internal-only)

---

## 15. Ports & adapters

When core logic needs something external, it defines a **port** (interface) in `/api`, e.g.:
- time / clock
- randomness
- repositories
- payment providers
- file storage
- telemetry

Infrastructure provides **adapters** implementing these ports in `/internal`.  
Composition wires ports to adapters.

---

## 16. API validation

All input crossing an API must be validated **at the API**:
- type / format
- required fields
- constraints
- permissions

Rules:
- fail fast
- clear, actionable errors
- prefer safe defaults

---

## 17. Error handling (stable across boundaries)

Rules:
- prefer explicit error values (`Result<T>`, `Either`)
- exceptions only for unrecoverable failures
- do not leak internal exception details
- errors must be stable across APIs (error codes/messages part of the contract)

Recommended public error taxonomy:
- `InvalidInput`
- `NotAuthorized`
- `NotFound`
- `Conflict`
- `ExternalServiceUnavailable`
- `Unexpected` (last resort)

---

## 18. Testing strategy (mirrors architecture)

1. domain tests (unit)
2. application tests (use-cases)
3. API tests (contracts)
4. integration tests (composition wiring)
5. end-to-end smoke tests

If tests require booting everything for simple rules, the shell is leaking.

---

## 19. Fitness functions (automated enforcement)

Start small (1 rule per sprint). Prioritize these:

1) **No imports from another module’s `/internal`** (except `/composition`)  
2) **No circular module dependencies**  
3) **Policy/domain does not import frameworks**  
4) **Data access only inside owning module** (or via projections/read models)  
5) **No internal/third-party types in `/api` signatures** (DTO-only boundary)

### 19.1 Tooling examples (pick what fits your stack)
- **TypeScript/JavaScript:** dependency-cruiser, ESLint import rules, custom lint scripts  
- **Java/Kotlin:** ArchUnit  
- **.NET:** NetArchTest (or custom Roslyn analyzers)  
- **Go:** go-arch-lint (or build-tag + package rules)  
- **Python:** import-linter (or custom AST checks)

If a rule must be broken:
- create an ADR
- scope the exception
- add a “trigger” for paying it back (date, metric, or condition)

---

## 20. Architecture red flags

Stop immediately if you see:
- imports from another module’s `/internal` (outside `/composition`)
- core code importing framework packages
- UI code containing business rules
- events used to request work
- composition containing business logic
- modules choosing infrastructure internally
- a growing “shared utils” folder that everyone depends on
- API returning ORM entities / SDK objects / internal models

---

## 21. Definition of Done (architecture)

A feature is complete when:
1. it is reachable through the API
2. core behavior lives in policy/use-cases
3. dependencies point inward
4. composition wires it explicitly
5. tests exist at the correct layer
6. relevant fitness functions still pass

---

## 22. Architecture Decision Record (ADR) template

When a rule in this document must be broken (see Section 19), create a file in:

`/docs/adr/YYYY-MM-DD-short-title.md`

Use this format:

- **Context:** What technical or business constraint forces breaking the rule?  
  (Example: “Critical performance bottleneck in reporting”)

- **Decision:** What specific rule is bypassed, and what is the temporary implementation?

- **Consequences:** What technical debt is incurred? What risks are introduced?

- **The Trigger:** The specific condition that triggers repayment and a return to standard architecture  
  (date, metric, or feature milestone)

---

# Architecture Constitution (enforceable rules)

> The Constitution is the short, enforceable subset of this document.  
> If there is a conflict, **the Constitution wins**.

1) **One module = one public boundary:** `modules/<m>/api`  
2) **Everything else is private:** `modules/<m>/internal`  
3) **No cross-module imports from `/internal`** (only `/composition` may wire implementations)  
4) **No bypass:** UI/controllers must call the module via `/api` (never internal services directly)  
5) **Dependencies point inward** (policy/domain must not depend on details)  
6) **Modules do not share databases/tables directly** (data ownership is per module)  
7) **Cross-module reads happen via `/api` or projections/read models** (avoid distributed joins/N+1 calls)  
8) **Events are facts, commands are requests** (no “request-work events”)  
9) **Public DTOs and error codes are contracts** (additive by default; breaking requires ADR + migration path)  
10) **Composition contains no business logic** (only wiring/configuration)  
11) **Ports live in `/api`, adapters live in `/internal`** (wired in composition)  
12) **Validation happens at boundaries** (module `/api`)  
13) **Testing mirrors boundaries** (unit inside module, contract at `/api`, integration at composition)  
14) **No “shared utils” dumping ground** (shared must be explicit, owned, stable, tested; follow the Rule of Three)  
15) **Delete rule:** a module should be removable by deleting its folder + composition wiring, without breaking unrelated module internals  
16) **Exceptions require ADR + scope + trigger** (visible and repayable)  
17) **Atomicity is local:** transactions must not span module boundaries; use events for cross-module consistency

---

## Final summary

**Pragmatic Modular Monolith** avoids both extremes:
- no spaghetti (hard boundaries)
- no early over-engineering (levels + pragmatic structure)

It is enforceable, scalable, and realistic for long-lived systems.

> **Architecture defines boundaries and dependencies.  
> Internals decide implementation.  
> Outside is strict. Inside is free.**
