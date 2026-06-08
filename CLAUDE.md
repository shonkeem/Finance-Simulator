<!-- Scope: Project-specific context for the Financial Simulation Sandbox. Version this file. -->

# Financial Simulation Sandbox

Personal finance simulation engine with interactive frontend. Discrete-time, deterministic state evolution — not a static calculator.

## Stack

- **Frontend:** React + TypeScript, Vite
- **Backend:** FastAPI, Python, Pydantic
- **Simulation:** Pure Python engine (no external sim frameworks)

## Three-File Input Architecture

All simulation scenarios are defined by three JSON files:

- **framing.json** — Defines the simulation timeframe and identity: start date, end date, time step granularity (monthly), person/household metadata
- **loads.json** — Defines all financial "loads" (things that move money): income streams, expense categories, debt instruments (with terms/rates), investment accounts (with contribution rules and growth assumptions)
- **settings.json** — Simulation-level knobs: inflation assumptions, tax parameters, rebalancing rules, output granularity, flags for optional features

These three files are the ONLY input to the simulation engine. The engine must never assume data that is not in these files.

## Conceptual Data Model

The simulation tracks these state variables at each timestep:

- **Cash** — liquid funds available
- **Investments** — account balances by type, subject to growth/contribution rules
- **Debt** — outstanding balances by instrument, subject to payment/interest rules
- **Income** — inflows per period from all sources
- **Expenses** — outflows per period by category
- **Net Worth** — derived: cash + investments - debt

## Architecture Layers (Separation of Concerns)

1. **Input Layer** — Reads and validates the three JSON files via Pydantic models
2. **Simulation Engine** — Pure Python. Takes validated input, produces a timeline of states. No I/O, no side effects
3. **API Layer** — FastAPI. Thin orchestrator: receives requests, calls engine, returns results. No simulation logic here
4. **Frontend** — React. Presentational. Displays results, collects input. No business logic

## Simulation Philosophy

- Each timestep produces a new state from the previous state + loads. This is **discrete-time state evolution**
- The core loop is: `state(t+1) = apply_loads(state(t), loads, settings)`
- State is immutable between steps — never mutate in place
- The engine must be deterministic given identical inputs

## Guidance Style

When asked for step-by-step instructions on how to implement something, follow this format for every step:

- **File** — exact file path to open or create
- **Location** — where in that file the change goes (after which line, inside which function, new section, etc.)
- **What it must do** — the behavior or contract required (inputs, outputs, side effects, constraints) — not how to write it
- **How it connects** — one sentence explaining how this piece fits into the layer above or below it (data flow, caller, dependency direction)

Do NOT include actual code, exact method signatures, library API calls, or syntax. The developer must write all of that.

When a task spans multiple files or layers, number the steps in dependency order — the developer should be able to complete them sequentially without backtracking.

## Current Build State

*Last updated: 2026-06-07*

### Exists now
- Final directory structure in place: `api/`, `src/simulation/models/`, `src/simulation/engine/`, `frontend/`, `tests/simulation/`, `framing.json`, `loads.json`, `settings.json`
- Frontend form (`frontend/src/App.tsx`) — TypeScript errors resolved, `MyForm` extracted to module level, correct event types and error narrowing. `node_modules` installed.
- `.gitignore` updated — `.venv/` replacing old `my_venv/` entry
- `backend/` deleted — venv recreated at project root as `.venv/`
- `/shutdown` skill — `.claude/skills/shutdown/SKILL.md` working and verified
- `/startup` skill — `.claude/skills/startup/SKILL.md` created and committed: reads session log, checks git/tests/build, prints consolidated session brief
- `docs/PRD.md` — v0.3: updated to match implemented behavior — field renames, formula corrections, ADR-006 (investment growth order), Phase 1 completion status, resolved Open Questions
- `framing.json` — filled with 10-year scenario (2025-01-01 → 2034-12-01, monthly)
- `loads.json` — filled with income, expenses, debts, investments
- `settings.json` — filled with inflation, tax, debt strategy, starting cash
- `src/simulation/models/inputs.py` — refactored: `DateBoundLoad(BaseModel)` base class added with shared `end_after_start` model validator; all four load models inherit from it; `DebtLoad.annual_rate` renamed to `annual_interest_rate`; `InvestmentLoad` simplified (`assumed_annual_return` → `annual_return`, employer match fields deferred/commented out)
- `src/simulation/models/state.py` — `SimulationState` frozen dataclass with `net_worth` property; `hash=False` on dict fields to prevent unhashable type error; `evolve()` helper added to safely copy state with dict field protection
- `src/simulation/engine/build_initial_state.py` — complete and correct: investments/debts as `dict[str, float]` keyed by load name; `income` and `expenses` seeded at `0.0`
- `src/simulation/engine/core.py` — complete: date advance happens before append (fixes duplicate-date bug); `income`/`expenses` reset to `0.0` at top of each loop iteration; uses `evolve()` throughout
- `src/simulation/engine/apply_income.py` — implemented: date gating, compound annual growth, tax, accumulates into `state.income`, returns new state via `evolve()`
- `src/simulation/engine/apply_expense.py` — implemented: inflation-linked scaling; uses `load.start_date` for elapsed time; accumulates into `state.expenses`; uses `evolve()`
- `src/simulation/engine/apply_debt.py` — implemented: date gating, monthly interest accrual, total payment applied, balance floored at 0; uses `evolve()`
- `src/simulation/engine/apply_investment.py` — implemented: date gating, monthly growth on pre-contribution balance, contribution skipped silently if insufficient cash; uses `evolve()`
- `api/models.py` — `SimulationRequest`, `SimulationStateResponse`, `TimelineResponse` Pydantic models
- `api/main.py` — POST `/simulate` endpoint with CORS middleware: allows `http://localhost:5173`, `Content-Type` header, POST method; no simulation logic in route
- `api/__init__.py` — empty, makes `api/` importable as a package
- `tests/simulation/test_apply_income.py` — 6 passing tests
- `tests/simulation/test_apply_expense.py` — 6 passing tests
- `tests/simulation/test_apply_debt.py` — 6 passing tests
- `tests/simulation/test_apply_investment.py` — 6 passing tests
- `tests/simulation/test_core.py` — 12 passing integration tests: length, dates sequential, initial state, period reset, end_date gating, net_worth correctness, determinism
- `tests/simulation/test_inputs.py` — 15 passing validation tests: all Pydantic validators across FramingInput, load types, LoadsInput uniqueness, SettingsInput
- `tests/api/test_simulate_endpoint.py` — 8 passing tests: status codes, response shape, timeline length, sequential dates, net_worth
- `conftest.py` — at project root, adds `src/` to `sys.path` for pytest imports
- `pytest 9.0.3` — installed in `.venv`
- `recharts ^3.8.1` — installed in `frontend/`
- `frontend/src/components/TimelineChart.tsx` — created (in progress, not yet committed)
- `CLAUDE.md` — added `## Guidance Style` section encoding preferred step-by-step instruction format

### Does NOT exist yet
- `TimelineChart.tsx` not yet wired into `App.tsx`
- `App.tsx` fetch body and result handler not yet updated to match `SimulationRequest` / `TimelineResponse` shape
- `ruff` not installed in `.venv/`

### Next step
Rework `frontend/src/App.tsx`: replace placeholder form with a single "Run Simulation" button, fix the fetch body to match `SimulationRequest` (inline the three JSON file contents as a JS object), fix the result handler to read `result.timeline`, add `timeline` state typed as `SimulationStateResponse[] | null`, and conditionally render `<TimelineChart timeline={timeline} />` when non-null.

## Do Not Touch List

These features are OFF LIMITS until the deterministic core loop is verified working with tests:

- **Monte Carlo / stochastic simulation** — deterministic baseline first
- **Event system** (life events, job changes, windfalls) — core loads first
- **Visualization / charting** — engine must produce correct numbers first
- **Tax optimization logic** — basic tax rates in settings.json are sufficient for now
- **Multi-scenario comparison** — single scenario must work first
- **Export / reporting** — premature until output format is stable

If I mention any of these, remind me of this list and redirect to the current milestone.

## Conventions
<!-- Scope: Developer reference for naming, organization, testing, and complexity management. Not a Claude config file. -->

### Naming Conventions

#### Python (simulation engine + API)
- Files: `snake_case.py` — name describes the module's single responsibility (e.g., `apply_income.py`, `state_model.py`)
- Functions: `snake_case` — verb-first for actions (`apply_debt_payment`, `validate_loads`), noun for accessors (`net_worth`)
- Classes: `PascalCase` — Pydantic models suffixed by role: `FramingInput`, `SimulationState`, `TimelineResponse`
- Constants: `UPPER_SNAKE_CASE`
- Private helpers: prefix with `_` only if genuinely internal to one module

#### TypeScript / React (frontend)
- Component files: `PascalCase.tsx` matching the component name
- Utility files: `camelCase.ts`
- Hooks: `useCamelCase.ts`
- Interfaces/types: `PascalCase`, prefixed with `I` only if needed to disambiguate from a class (prefer no prefix)
- Constants: `UPPER_SNAKE_CASE`
- Enum values: `PascalCase`

#### JSON input files
- Keys: `snake_case` — matches Python field names directly, no translation layer needed
- File names: exactly `framing.json`, `loads.json`, `settings.json`

### Code Organization

```
project-root/
├── api/                  # FastAPI routes + dependencies
├── src/
│   └── simulation/       # Pure Python engine — no I/O, no imports from api/
│       ├── models/       # Pydantic input models + state dataclass
│       ├── engine/       # Core loop + load applicators
│       └── __init__.py
├── frontend/             # React + TypeScript (self-contained Node project)
│   └── src/
│       ├── components/   # Presentational components
│       ├── hooks/        # Reusable custom hooks
│       └── utils/        # Formatters, helpers
├── tests/
│   ├── simulation/       # Unit + integration tests for engine
│   └── api/              # Endpoint tests
├── .venv/                # Python virtual environment
├── framing.json          # Simulation input files
├── loads.json
└── settings.json
```

**Rules:**
- `simulation/` never imports from `api/` or `frontend/`
- `api/` imports from `simulation/` but never from `frontend/`
- `frontend/` calls API endpoints only — never imports Python modules

### Testing Strategy

#### What to test at each layer

**Simulation engine (highest priority):**
- Each load applicator function: normal case, zero amount, boundary conditions
- Core loop integration: multi-timestep run, assert final state against hand calculation
- Input validation: malformed JSON fields, missing required fields, out-of-range values
- Determinism: same input produces same output across runs

**API layer:**
- Endpoint returns correct status codes for valid and invalid input
- Response shape matches Pydantic response model
- No need to re-test simulation logic — mock the engine, test orchestration

**Frontend:**
- Component renders without crashing given expected props
- User interactions trigger expected callbacks
- Formatters produce correct output for edge cases (zero, negative, large numbers)

#### Test file conventions
- Mirror the source structure under `tests/`
- One test file per source file: `test_apply_income.py` tests `apply_income.py`
- Test function names: `test_<what>_<condition>_<expected>` (e.g., `test_apply_income_zero_amount_no_state_change`)

### Complexity Budget Checklist

Before adding ANY new feature, answer these questions. If you answer "no" to any, stop and reconsider.

1. **Is the current milestone working and tested?** — If the deterministic core loop isn't verified, nothing else matters
2. **Does this feature serve the current milestone?** — If not, it goes on the Do Not Touch list
3. **Can I explain the feature in one sentence?** — If not, it's too complex or too vague to build
4. **What is the smallest version of this I can build?** — Build that version. Not the ambitious one
5. **Does this add a new dependency?** — Justify it. Can you do it with what you have?
6. **Will this require changes in more than one layer?** — If yes, plan the changes before coding any of them
7. **Can I write a test for this before I build it?** — If you can't describe the test, you don't understand the feature yet