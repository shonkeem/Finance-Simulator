# Session Log

## 2026-03-19
### Done
- Fixed all TypeScript errors in `frontend/src/App.tsx` — implicit `any` on event handler, `error` narrowing in catch block, `submitEvent.target` → `currentTarget`, extracted `MyForm` to module level
- Established and committed final directory structure: `api/`, `src/simulation/models/`, `src/simulation/engine/`, `frontend/`, `tests/simulation/`, three input JSON stubs
- Deleted `backend/` directory; updated `.gitignore` to use `.venv/`
- Authored full PRD at `docs/PRD.md` — vision, personas, ADRs, data schemas, simulation behavior spec, API spec, phased roadmap, acceptance criteria, risk register
- Created and verified `/shutdown` skill at `.claude/skills/shutdown/SKILL.md`
- Updated `CLAUDE.md` current build state and Code Organization diagram to reflect agreed structure

### Status
- Tests: SKIPPED — pytest not installed; vitest incompatible with Node v18
- Build: SKIPPED — `frontend/node_modules` not installed (npm install not yet run)
- Uncommitted files: 0 (working tree clean)

### Next Session
- Run `npm install` in `frontend/` and set up `.venv` at project root with `fastapi pydantic uvicorn`
- Fill in `framing.json` with the schema from `docs/PRD.md` Section 7, then resolve all Open Questions in Section 15 before writing any Python
- Write `src/simulation/models/inputs.py` starting with `FramingInput` — only after `framing.json` is agreed
---

## 2026-03-21
### Done
- Filled all three input JSON files: `framing.json` (10-year scenario), `loads.json` (salary, rent, groceries, student loans, 401k), `settings.json` (inflation, tax, avalanche strategy)
- Built complete Pydantic input layer in `src/simulation/models/inputs.py` — `FramingInput`, four load models (`IncomeLoad`, `ExpenseLoad`, `DebtLoad`, `InvestmentLoad`), `SettingsInput`, `LoadsInput` with field validators and uniqueness checks
- Built `SimulationState` frozen dataclass in `src/simulation/models/state.py` with `net_worth` as a derived property
- Scaffolded all engine files: `build_initial_state.py`, `core.py`, `apply_income.py`, `apply_expense.py`, `apply_debt.py`, `apply_investment.py`
- Identified and flagged bugs in `build_initial_state.py` (investments/debt typed as float instead of dict) and `core.py` (broken imports, broken month advancement, load vs loads in applicator calls)

### Status
- Tests: SKIPPED — pytest not installed in .venv
- Build: TypeScript — clean (no errors). Ruff — SKIPPED (not installed)
- Uncommitted files: 0 (working tree clean)

### Next Session
- Fix `build_initial_state.py`: change `investments` and `debt` to `dict[str, float]` using dict comprehensions keyed by load name
- Fix `core.py`: correct imports, replace broken `advance_one_month` with proper date arithmetic, change `loads` → `load` in all applicator calls
- Implement and test `apply_income.py` — write `tests/simulation/test_apply_income.py` first (normal case, inactive load, tax applied)
---

## 2026-05-16
### Done
- Returned to project after extended break; performed full codebase audit and confirmed prior bugs in `build_initial_state.py` and `core.py` were already resolved in previous commits
- Fixed `core.py`: `state.date` now updated each loop iteration via `dataclasses.replace` after `advance_one_month`
- Implemented `apply_income.py`: date gating, compound annual growth, tax calculation, accumulates into `state.income` (fixed overwrite bug), returns new state via `dataclasses.replace`
- Wrote `tests/simulation/test_apply_income.py`: 4 passing tests (no-tax, tax applied, inactive date, 1-year growth)
- Implemented `apply_expense.py`: inflation-linked scaling, takes `start_date` argument, accumulates into `state.expenses`, correct cash deduction using inflated amount
- Wrote `tests/simulation/test_apply_expense.py`: 2 passing tests (no inflation, inflation applied)
- Added defaults to `SettingsInput` fields to allow partial instantiation in tests
- Installed `pytest 9.0.3` into `.venv`; created `conftest.py` at project root

### Status
- Tests: 6 passed, 0 failed, 0 skipped
- Build: TypeScript — clean (no errors). Ruff — SKIPPED (not installed)
- Uncommitted files: 0 (working tree clean)

### Next Session
- Implement `apply_debt` in `src/simulation/engine/apply_debt.py`: accrue monthly interest (`balance * annual_rate / 12`), apply total payment (`minimum + extra`), floor balance at 0, update `state.debt[load.name]` and `state.cash`
- Write `tests/simulation/test_apply_debt.py`: normal payment, balance reaches zero, extra payment case
- After debt: implement and test `apply_investment.py` (contribution, employer match, monthly growth)
---

## 2026-05-28
### Done
- Created `/startup` skill at `.claude/skills/startup/SKILL.md` — read-only start-of-session briefing: reads last session log, checks git state/tests/build, prints consolidated session brief with flags
- Updated `.gitignore` with Claude-related file patterns
- Committed all changes (CLAUDE.md, session-log.md, startup skill) as "restored claude files"

### Status
- Tests: 6 passed, 0 failed, 0 skipped
- Build: TypeScript — clean (no errors). Ruff — SKIPPED (not installed)
- Uncommitted files: 0 (working tree clean, 1 commit ahead of origin)

### Next Session
- Implement `apply_debt` in `src/simulation/engine/apply_debt.py`: accrue monthly interest (`balance * annual_rate / 12`), apply total payment (`minimum + extra`), floor balance at 0, update `state.debt[load.name]` and `state.cash`
- Write `tests/simulation/test_apply_debt.py`: normal payment, balance reaches zero, extra payment case
- After debt: implement and test `apply_investment.py` (contribution, employer match, monthly growth)
---

## 2026-06-02
### Done
- Refactored `src/simulation/models/inputs.py`: added `DateBoundLoad(BaseModel)` base class with shared `end_after_start` model validator; all four load models now inherit from it, eliminating duplicated date fields and validation logic
- Renamed `DebtLoad.annual_rate` → `annual_interest_rate` and simplified `InvestmentLoad` (`assumed_annual_return` → `annual_return`, employer match fields deferred)
- Implemented `src/simulation/engine/apply_debt.py`: monthly interest accrual, total payment applied, balance floored at 0, cash deducted only for what was actually owed (handles payoff edge case correctly)
- Updated `apply_expense.py` to use `load.start_date` directly (removed separate `start_date` argument)
- Fixed both test files to match model changes: added `start_date` to `ExpenseLoad` fixtures, removed stale `DebtStrategies` references from income tests

### Status
- Tests: 6 passed, 0 failed, 0 skipped
- Build: TypeScript — clean (no errors). Ruff — SKIPPED (not installed)
- Uncommitted files: 0 (working tree clean)

### Next Session
- Write `tests/simulation/test_apply_debt.py` with three cases: normal payment, balance hits zero (cash floored), extra payment on top of minimum
- Implement `apply_investment.py`: date gating, monthly contribution deducted from cash, monthly growth applied to balance, update `state.investments[load.name]` and `state.cash`
- Write `tests/simulation/test_apply_investment.py` to match
---

## 2026-06-03
### Done
- Fixed `debt` → `debts` field rename propagation: corrected `state.py` `net_worth` property, `apply_debt.py`, and `build_initial_state.py` which had all diverged from the renamed field
- Wrote `tests/simulation/test_apply_debt.py`: 4 tests covering normal payment, balance floored at zero (cash deducted only for what was owed), extra payment on top of minimum, and inactive load date gating
- Implemented and cleaned `apply_investment.py`: growth on pre-contribution balance, silent skip on insufficient cash (removed `print` side effect), added return type annotation
- Wrote `tests/simulation/test_apply_investment.py`: 4 tests covering normal growth+contribution, zero starting balance, cash shortage skip, and inactive load
- Wrote `tests/simulation/test_core.py`: 6 end-to-end integration tests covering timeline length, income+expense accumulation, debt paydown, investment growth, and determinism — core loop is now fully verified

### Status
- Tests: 20 passed, 0 failed, 0 skipped
- Build: TypeScript — clean (no errors). Ruff — SKIPPED (not installed)
- Uncommitted files: 0 (working tree clean)

### Next Session
- Implement `api/main.py`: single POST `/simulate` endpoint accepting `FramingInput`, `LoadsInput`, `SettingsInput` in the request body; calls `run_simulation`; returns timeline as list of response objects
- Define `SimulationStateResponse` and `TimelineResponse` Pydantic models for the response shape — separate from the input models even if fields overlap
- Write `tests/api/` endpoint tests: valid input returns 200 + correct shape, invalid input returns 422
---

## 2026-06-03 (addendum — documentation)
### Done
- Updated `docs/PRD.md` to v0.3: corrected field names (`annual_rate` → `annual_interest_rate`, `assumed_annual_return` → `annual_return`), fixed income/expense growth formulas, rewrote debt and investment applicator specs to match implementation, added ADR-006 (investment growth-before-contribution convention), marked Phase 1 items complete, resolved OQ-1/4/5/6/7/8/9 with actual decisions

### Status
- Tests: 20 passed, 0 failed, 0 skipped
- Build: TypeScript — clean (no errors). Ruff — SKIPPED (not installed)
- Uncommitted files: 3 (CLAUDE.md, docs/PRD.md, docs/session-log.md — documentation only)

### Next Session
- Implement `api/main.py`: single POST `/simulate` endpoint accepting `FramingInput`, `LoadsInput`, `SettingsInput` in the request body; calls `run_simulation`; returns timeline as list of response objects
- Define `SimulationStateResponse` and `TimelineResponse` Pydantic models in `api/models.py` — separate from input models
- Write `tests/api/test_simulate_endpoint.py`: 200 + correct shape on valid input, 422 on invalid input
---

## 2026-06-05
### Done
- No code changes — session was a startup/shutdown audit only
- Confirmed baseline: 20 tests passing, TypeScript build clean, working tree clean

### Status
- Tests: 20 passed, 0 failed, 0 skipped
- Build: TypeScript — clean (no errors). Ruff — SKIPPED (not installed)
- Uncommitted files: 0 (working tree clean)

### Next Session
- Implement `api/main.py`: single POST `/simulate` endpoint accepting `FramingInput`, `LoadsInput`, `SettingsInput` in the request body; calls `run_simulation`; returns timeline as list of response objects
- Define `SimulationStateResponse` and `TimelineResponse` Pydantic models in `api/models.py` — separate from input models
- Write `tests/api/test_simulate_endpoint.py`: 200 + correct shape on valid input, 422 on invalid input
---

## 2026-06-07
### Done
- Fixed three bugs in the simulation engine: `frozen=True` + dict field unhashability (added `hash=False`, introduced `evolve()` helper in `state.py`), `income`/`expenses` initial seeding at non-zero values in `build_initial_state.py` (now seeded at `0.0`), and duplicate-date entries in timeline caused by date advance happening after append in `core.py` (now advances before append)
- Added `evolve()` to `state.py` and migrated all applicators (`apply_income`, `apply_expense`, `apply_debt`, `apply_investment`) and `core.py` from `dataclasses.replace()` to `evolve()`, ensuring dict fields are always deep-copied between states
- Implemented `api/models.py` (`SimulationRequest`, `SimulationStateResponse`, `TimelineResponse`) and `api/main.py` (POST `/simulate` endpoint — thin orchestration only, no simulation logic)
- Expanded test suite from 24 to 61 passing tests: added `end_date` gating, accumulation, period reset, and net_worth tests to all applicator test files; added date-sequencing and load-expiry integration tests to `test_core.py`; created `tests/simulation/test_inputs.py` with 15 Pydantic validation tests; expanded `tests/api/test_simulate_endpoint.py` with timeline length, date, and net_worth assertions

### Status
- Tests: 61 passed, 0 failed, 0 skipped
- Build: TypeScript — clean (no errors). Ruff — SKIPPED (not installed)
- Uncommitted files: 0 (working tree clean, 3 commits ahead of origin)

### Next Session
- Begin frontend visualization: create `frontend/src/components/TimelineChart.tsx` — presentational component accepting `timeline: SimulationStateResponse[]`, renders net_worth line chart; install `recharts` in `frontend/`
- Wire `TimelineChart` into `App.tsx`: add form submission that calls `POST /simulate` and passes the response to the chart component
- Add CORS middleware to `api/main.py` (`fastapi.middleware.cors.CORSMiddleware`) to allow the Vite dev server to call the API
---

## 2026-06-07 (addendum — frontend setup)
### Done
- Added `## Guidance Style` section to `CLAUDE.md` — encodes preferred instruction format: file path, location, contract, layer connection per step; no code or signatures
- Added CORS middleware to `api/main.py`: correct origin (`http://localhost:5173`), `allow_headers=["Content-Type"]`, `allow_methods=["POST"]`; caught and fixed two bugs (wrong port, `allow_headers` had method name instead of header name)
- Installed `recharts ^3.8.1` in `frontend/` (`package.json` + `package-lock.json` updated); confirmed recharts 3.x ships its own types — no separate `@types` package needed
- Created `frontend/src/components/TimelineChart.tsx` (in progress, not yet committed)

### Status
- Tests: 61 passed, 0 failed, 0 skipped
- Build: TypeScript — clean (no errors). Ruff — SKIPPED (not installed)
- Uncommitted files: 4 modified (CLAUDE.md, api/main.py, frontend/package.json, frontend/package-lock.json), 1 untracked directory (frontend/src/components/)

### Next Session
- Complete `frontend/src/components/TimelineChart.tsx` if not finished: accepts `timeline: SimulationStateResponse[]` prop, renders recharts `LineChart` with `date` on X axis and `net_worth` on Y axis — no state, no fetching
- Rework `frontend/src/App.tsx`: replace placeholder form with a single "Run Simulation" button; fix fetch body to match `SimulationRequest` shape (inline the three JSON files as a JS object); fix result handler to read `result.timeline` instead of `result.payload`
- Add `timeline` state to `App.tsx` typed as `SimulationStateResponse[] | null`; conditionally render `<TimelineChart timeline={timeline} />` when non-null
---
