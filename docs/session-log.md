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
