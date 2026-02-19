# ONBOARDING.md
Project: <name>
Owner: <name/role>
Last updated: <YYYY-MM-DD>

## 1) What is this project?
<1–3 lines: what we're building, for whom, and why. Link to PRD/GDD for the full picture.>

- Product doc: `PRD.md` (or `GDD.md`)

## 2) Current status
- **Phase:** <concept / research / building MVP / user testing / launched>
- **Milestone:** <MS-XX — 1 line goal>
- **Sprint:** <NN — 1 line goal> (see `/sprints/`)
- **Biggest open risk:** <1 line>

## 3) Team & roles
| Name | Role | Responsible for |
|------|------|----------------|
| <name> | <role> | <area> |
| <name> | <role> | <area> |

## 4) Quick setup
### Prerequisites
- <tool / runtime / SDK + version>
- <tool / runtime / SDK + version>

### Get running
```bash
# Clone and install
<commands>

# Run locally
<commands>

# Run tests
<commands>
```

### Verify it works
- <what you should see when it's running correctly>

## 5) Project structure
```
<project root>/
├── docs/              # Project documentation
│   ├── PRD.md         # (or GDD.md) — what & why
│   ├── RESEARCH.md    # Research notes
│   ├── TDD.md         # Technical design
│   ├── BACKLOG.md     # Prioritized work
│   └── sprints/       # Sprint docs
├── src/               # Source code
│   ├── <folder>/      # <description>
│   └── <folder>/      # <description>
├── tests/             # Tests
└── <other>/           # <description>
```

## 6) Key documents (reading order)
1. **This file** — you are here
2. **PRD.md / GDD.md** — understand the problem, goals, and MVP scope
3. **TDD.md** — understand the architecture and how things are built
4. **BACKLOG.md** — see what's been done, what's next, and what's out of scope
5. **Latest sprint** — see what the team is working on right now

## 7) Conventions & rules
### Branching / version control
- <branching model, e.g. main + feature branches>
- <commit message format>

### Code style
- <language + style guide or linter>
- <naming conventions>

### Documentation
- Product decisions → PRD/GDD
- Technical decisions → TDD
- Research & links → RESEARCH
- Tasks → BACKLOG
- Sprint work → /sprints/

### Definition of Done (project-level)
- <what "done" means here, e.g. tests pass, reviewed, demo-able>

## 8) How to contribute
1. Check `BACKLOG.md` for available items
2. Pick an item (or ask the owner for guidance)
3. <create branch / work in main / etc.>
4. Make sure the item's DoD checklist is met
5. <submit PR / push / demo>

## 9) Useful links
- Repo: <url>
- Live version: <url> (if deployed)
- Design files: <url> (if any)
- Communication: <Slack / Discord / etc.>

## 10) FAQ / gotchas
- **Q: <common question>**
  A: <answer>

- **Q: <common question>**
  A: <answer>
