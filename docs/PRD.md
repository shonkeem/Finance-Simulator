# FinanceSimulator — Product Requirements Document

**Version:** 0.3
**Date:** 2026-06-03
**Status:** Active

---

## Table of Contents

1. [Vision and Purpose](#1-vision-and-purpose)
2. [Users and Personas](#2-users-and-personas)
3. [Goals, Non-Goals, and Constraints](#3-goals-non-goals-and-constraints)
4. [Glossary](#4-glossary)
5. [Core Mental Model](#5-core-mental-model)
6. [Architectural Decision Records](#6-architectural-decision-records)
7. [Data Model and Schema Specification](#7-data-model-and-schema-specification)
8. [Simulation Behavior Specification](#8-simulation-behavior-specification)
9. [API Specification](#9-api-specification)
10. [Frontend Specification](#10-frontend-specification)
11. [Testing Strategy and Acceptance Criteria](#11-testing-strategy-and-acceptance-criteria)
12. [Phased Roadmap](#12-phased-roadmap)
13. [Edge Cases and Error Handling](#13-edge-cases-and-error-handling)
14. [Risk Register](#14-risk-register)
15. [Open Questions](#15-open-questions)

---

## 1. Vision and Purpose

### Problem Statement

Most personal finance tools answer *"where am I now?"* — net worth calculators, budget trackers, expense categorizers. A smaller number answer *"am I on track?"* by comparing your savings rate against a rule of thumb. Almost none answer the more important question:

**"If I keep doing what I'm doing, exactly where do I end up — and how does that change if I alter one variable?"**

The gap is between static snapshots and dynamic projection. Spreadsheets can do projection but require manual modeling of every financial relationship. Consumer apps (Mint, YNAB, Personal Capital) are backward-looking — they track what happened, not what will happen. Financial advisors project forward but in black-box software you don't control.

### Solution

A locally-run, open-input, deterministic simulation engine. The user defines their complete financial picture in three JSON files. The engine runs a month-by-month projection and returns a full timeline of states. The user can change any assumption and re-run in seconds. Every output number is traceable to an input field and a formula.

### Defining Properties

- **Deterministic** — identical inputs produce identical outputs every run, forever
- **Auditable** — no hidden assumptions; everything the engine knows came from the input files
- **Composable** — the engine is a pure function; the API and frontend are thin wrappers around it
- **Local-first** — runs entirely on your machine; no accounts, no sync, no telemetry
- **Discrete-time** — the world advances in defined steps (monthly); no continuous-time calculus

---

## 2. Users and Personas

### Primary Persona: The Deliberate Planner

- Age 25–45, early-to-mid career
- Has income, at least one debt (student loans, car, mortgage), some investment accounts
- Thinks about the future in terms of years, not months
- Comfortable editing JSON; has used a terminal before
- Wants to understand *why* their financial trajectory looks the way it does
- Does not trust black-box financial apps with their data

**Characteristic questions they ask:**
- "If I pay an extra $200/month on my student loans, how much earlier am I debt-free?"
- "What does my net worth look like at 55 if my investment return is 6% vs 8%?"
- "At what point do my investments start outpacing my income?"
- "If I take a lower-paying job I love, what's the 10-year cost?"

### Secondary Persona: The Scenario Thinker

- Same profile, but uses the tool comparatively rather than as a baseline tracker
- Primary workflow: define a "base case" then run variants
- Cares most about Phase 4 (scenario comparison) features
- Will accept rough input UX if the comparison output is clear

### Non-Persona (explicitly out of scope)

- Financial professionals needing compliance-grade output
- Users who want the app to pull in live data from their bank
- Users who are not comfortable with structured text input
- Anyone running this as a hosted service for other people

---

## 3. Goals, Non-Goals, and Constraints

### Goals

| # | Goal | Measurable Signal |
|---|---|---|
| G1 | Produce a correct timeline from structured input | Final net worth matches hand-calculation to the cent |
| G2 | Make assumption changes cheap to test | Re-run after a single JSON edit completes in < 2 seconds end-to-end |
| G3 | Make the output interpretable without documentation | A user can describe what the chart shows without reading a guide |
| G4 | Keep the engine layer perfectly isolated | Zero imports from `api/` or `frontend/` in `src/simulation/` |
| G5 | Every output traceable | Given any number in the UI, a developer can find the formula that produced it |

### Permanent Non-Goals

- **Live account sync** — Plaid, bank APIs, CSV import. The engine only knows what you tell it.
- **Tax filing output** — No Schedule forms, no compliance artifacts
- **Real-time market data** — All rates are user-defined assumptions
- **Mobile** — Desktop browser only
- **Multi-user** — Single-user, local-only

### Do Not Touch Until Specified

- Monte Carlo / stochastic simulation
- Event system
- Visualization / charting
- Tax optimization logic
- Multi-scenario comparison
- Export / reporting

### Constraints

- No new Python dependencies without justification — stdlib + FastAPI + Pydantic only for Phases 1–2
- No new npm dependencies without justification — React + Vite only until Phase 3 adds a charting library
- TypeScript strict mode is non-negotiable and cannot be loosened
- The engine must be testable without starting the API server
- The API must be testable without a running frontend

---

## 4. Glossary

| Term | Definition |
|---|---|
| **Load** | Anything that moves money each timestep: income, expense, debt payment, investment contribution |
| **Applicator** | A pure function that applies one category of loads to a state and returns a new state |
| **Timeline** | The ordered list of `SimulationState` objects produced by the core loop — one per timestep |
| **Period** | A single timestep; always one calendar month in the current implementation |
| **Framing** | The metadata defining who the simulation is for and what time range it covers |
| **Settings** | Simulation-level knobs (rates, strategies) that modify how loads are applied |
| **State** | The complete financial picture at a given point in time: cash, investments, debts, flows |
| **Net Worth** | Derived value: cash + sum(all investment balances) - sum(all debt balances) |
| **Surplus Cash** | Income minus expenses minus debt payments in a period; may be positive or negative |
| **FIRE Number** | 25× annual expenses; the investment balance at which returns theoretically cover living costs |
| **Amortization** | The process of paying down a debt in fixed installments, each partly principal and partly interest |
| **Avalanche** | Debt payoff strategy: direct extra payments to the highest-rate debt first |
| **Snowball** | Debt payoff strategy: direct extra payments to the smallest-balance debt first |

---

## 5. Core Mental Model

### The Simulation as a State Machine

```
┌──────────────────────────────────────────────────┐
│  INPUT                                           │
│  framing.json + loads.json + settings.json       │
└──────────────────┬───────────────────────────────┘
                   │ validated by Pydantic
                   ▼
┌──────────────────────────────────────────────────┐
│  INITIAL STATE                                   │
│  build_initial_state(framing, loads, settings)   │
└──────────────────┬───────────────────────────────┘
                   │
         ┌─────────▼──────────────────────────────┐
         │  CORE LOOP  (for each period)           │
         │                                         │
         │  state(t) → apply_income                │
         │           → apply_expenses              │
         │           → apply_debt_payments         │
         │           → apply_investments           │
         │                    │                    │
         │                    ▼                    │
         │           state(t+1) → append to list   │
         └────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│  OUTPUT                                          │
│  list[SimulationState]  (one per period)         │
└──────────────────────────────────────────────────┘
```

### Applicator Order (non-negotiable)

1. **Income** — cash increases first; you can only spend money you've received
2. **Expenses** — fixed outflows deducted from available cash
3. **Debt payments** — minimum payments are non-discretionary; come before investment contributions
4. **Investment contributions** — discretionary outflows; funded from remaining cash after obligations

This order encodes financial priority: income → obligations → savings. Changing the order changes every output.

### What the Engine Does NOT Model

- Tax withholding mid-period (income is treated as post-tax unless `apply_income_tax` is enabled)
- Overdraft or credit behavior (negative cash is reported but not resolved by the engine)
- Market volatility within a period (returns are applied as a fixed monthly rate)
- Rebalancing between investment accounts (each account grows independently)

---

## 6. Architectural Decision Records

### ADR-001: Three separate input files, not one

**Decision:** Define input as three distinct JSON files rather than a single config file.

**Rationale:** Each file has a different change frequency and conceptual role. Framing rarely changes. Loads change when life changes. Settings change when testing assumptions. Separating them makes it easier to swap one concern without touching the others, and makes validation errors localized.

**Consequence:** The API accepts all three as a combined request body. The engine's `run_simulation` signature takes three validated objects, not one.

---

### ADR-002: `SimulationState` as a dataclass, not a Pydantic model

**Decision:** Use Python `@dataclass` for `SimulationState`, not `pydantic.BaseModel`.

**Rationale:** Pydantic is for boundary validation (untrusted external input). `SimulationState` is internal — constructed and consumed entirely within the engine. Using `dataclass` avoids validation overhead on every timestep and keeps the dependency boundary clear.

**Consequence:** `SimulationState` cannot be directly serialized to JSON by FastAPI. The API layer must convert it to a Pydantic response model (`StateResponse`) before returning.

---

### ADR-003: `frontend/` at project root, not under `src/`

**Decision:** Keep the React app at `frontend/` (project root level) rather than `src/frontend/`.

**Rationale:** The frontend is a self-contained Node.js project with its own `package.json`, `tsconfig`, and `vite.config.ts`. Placing it under `src/` would require updating all Vite path assumptions, would cause Python tooling to scan TypeScript files, and diverges from the universal convention for fullstack monorepos.

**Consequence:** CLAUDE.md's Code Organization diagram has been updated to reflect this. The rule — `frontend/` never imports Python — is unchanged.

---

### ADR-004: All monetary values as `float`, rounded to 2 decimal places per operation

**Decision:** Use Python `float` for all monetary values, not `Decimal`. Round to 2 decimal places at the output of each applicator function.

**Rationale:** `Decimal` adds complexity unnecessary for the error tolerance of a 10-year projection. Floating point error on monthly values is immaterial at the scale of personal finance. Rounding consistently after each applicator prevents error accumulation.

**Consequence:** Every applicator must end with `round(value, 2)` on all monetary outputs. Tests assert equality to 2 decimal places, not exact float equality.

---

### ADR-006: Investment growth applies to pre-contribution balance

**Decision:** Apply monthly growth to the balance before adding the monthly contribution, not after.

**Rationale:** The existing balance has been compounding throughout the month. The new contribution arrives at month-end (dollar-cost averaging convention). Applying growth to the pre-contribution balance models this more accurately than the alternative, which would overstate returns on the new contribution.

**Formula:** `new_balance = (old_balance * (1 + annual_return/12)) + monthly_contribution`

**Consequence:** Tests assert this order explicitly. A one-line change in `apply_investment.py` would invert the behavior — the test locks it in.

---

### ADR-005: No simulation logic in the API layer

**Decision:** FastAPI routes contain zero financial computation. They receive, validate, delegate, and return.

**Rationale:** The engine must be independently testable without an HTTP server. Any financial formula in a route handler is a defect by definition.

**Consequence:** The `POST /simulate` route is exactly 4 steps: receive `SimulationRequest`, call `run_simulation(framing, loads, settings)`, convert result to `TimelineResponse`, return. No branching, no math.

---

## 7. Data Model and Schema Specification

### `framing.json`

```json
{
  "label": "My base case scenario",
  "start_date": "2025-01-01",
  "end_date": "2034-12-01",
  "time_step": "monthly"
}
```

**Validation rules:**
- `end_date` must be strictly after `start_date`
- `time_step` must be `"monthly"` (only supported value in Phases 1–3)
- Both dates must be the first of the month
- Maximum simulation length: 600 periods (50 years)

---

### `loads.json`

```json
{
  "income": [
    {
      "name": "primary_salary",
      "monthly_gross": 7500.00,
      "annual_growth_rate": 0.03,
      "start_date": "2025-01-01",
      "end_date": null
    }
  ],
  "expenses": [
    {
      "name": "rent",
      "monthly_amount": 1800.00,
      "category": "housing",
      "inflation_linked": true
    },
    {
      "name": "groceries",
      "monthly_amount": 400.00,
      "category": "food",
      "inflation_linked": true
    }
  ],
  "debts": [
    {
      "name": "student_loans",
      "current_balance": 28000.00,
      "annual_interest_rate": 0.055,
      "minimum_monthly_payment": 295.00,
      "extra_monthly_payment": 200.00,
      "start_date": "2025-01-01",
      "end_date": null
    }
  ],
  "investments": [
    {
      "name": "401k",
      "account_type": "401k",
      "current_balance": 15000.00,
      "monthly_contribution": 500.00,
      "annual_return": 0.07,
      "start_date": "2025-01-01",
      "end_date": null
    }
  ]
}
```

**Validation rules — Income:**
- `monthly_gross` > 0
- `end_date` null means "runs until end of simulation"
- Names must be unique across all income entries

**Validation rules — Expenses:**
- `monthly_amount` ≥ 0
- `category` must be a non-empty string
- Names must be unique across all expense entries

**Validation rules — Debts:**
- `current_balance` > 0
- `annual_interest_rate` ∈ [0, 1]
- `minimum_monthly_payment` > 0
- `extra_monthly_payment` ≥ 0
- `start_date` and optional `end_date` — same rules as income
- Names must be unique across all debt entries

**Validation rules — Investments:**
- `current_balance` ≥ 0
- `monthly_contribution` ≥ 0
- `annual_return` ∈ [0, 1]
- `start_date` and optional `end_date` — same rules as income
- Names must be unique across all investment entries
- Employer match deferred to Phase 5 — fields not present in schema

---

### `settings.json`

```json
{
  "inflation_rate": 0.03,
  "income_tax_rate": 0.22,
  "apply_income_tax": true,
  "apply_inflation_to_expenses": true,
  "debt_payoff_strategy": "avalanche",
  "starting_cash": 5000.00
}
```

**Validation rules:**
- `income_tax_rate` ∈ [0, 1]
- `debt_payoff_strategy` ∈ `["minimum_only", "avalanche", "snowball"]`
- `starting_cash` ≥ 0

---

## 8. Simulation Behavior Specification

### Period Arithmetic

- Periods are calendar months, always starting on the 1st
- A simulation from `2025-01-01` to `2025-03-01` produces exactly 3 states: Jan, Feb, Mar
- The range is inclusive on both ends

### Income Applicator

For each income load active in the current period:

1. Check `start_date ≤ period` and (`end_date is null` or `end_date ≥ period`)
2. If inactive, skip
3. Calculate months elapsed since `start_date`; `years_elapsed = months_elapsed / 12`
4. Apply growth: `effective_monthly = monthly_gross * (1 + annual_growth_rate)^years_elapsed`
5. If `apply_income_tax`: `net_income = effective_monthly * (1 - income_tax_rate)`
6. Add `net_income` to `state.cash`; add `effective_monthly` (gross) to `state.income`

### Expense Applicator

For each expense load:

1. Calculate months elapsed since `load.start_date`; `years_elapsed = months_elapsed / 12`
2. If `inflation_linked` and `apply_inflation_to_expenses`:
   `effective_amount = monthly_amount * (1 + inflation_rate)^years_elapsed`
3. Else: `effective_amount = monthly_amount`
4. Subtract `effective_amount` from `state.cash` and add to `state.expenses`

### Debt Payment Applicator

For each active debt load (Phase 1 — per-load, no cross-debt strategy):

```
monthly_interest = current_balance * (annual_interest_rate / 12)
total_payment = minimum_monthly_payment + extra_monthly_payment
new_balance = max(0, current_balance + monthly_interest - total_payment)
actual_cash_deducted = min(total_payment, current_balance + monthly_interest)
state.cash -= actual_cash_deducted
state.debts[load.name] = new_balance
```

The `actual_cash_deducted` guard handles the final period: when the remaining balance is less than the scheduled payment, only the true outstanding amount is deducted.

**Debt strategy cascade (avalanche / snowball) is deferred to Phase 5.** In Phase 1, `extra_monthly_payment` is a fixed field on each debt load and is applied directly to that debt only.

### Investment Contribution Applicator

For each active investment load:

```
growth = current_balance * (annual_return / 12)      # growth on pre-contribution balance
if monthly_contribution <= state.cash:
    new_balance = current_balance + growth + monthly_contribution
    state.cash -= monthly_contribution
else:
    new_balance = current_balance + growth             # skip contribution silently
state.investments[load.name] = new_balance
```

**Growth applies to the pre-contribution balance.** This models the convention that the existing balance compounds throughout the month while the new contribution lands at month-end.

**If cash is insufficient for the contribution, the contribution is skipped silently.** The balance still grows. No warning is emitted in Phase 1.

**Employer match is deferred to Phase 5** — fields not present in Phase 1 schema.

### Derived Values

`net_worth` is always computed, never stored independently:

```python
net_worth = state.cash + sum(state.investments.values()) - sum(state.debts.values())
# SimulationState field is `debts` (dict[str, float]), not `debt`
```

Any discrepancy between stored and computed net worth is a defect.

---

## 9. API Specification

### Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check |
| POST | `/simulate` | Run simulation, return timeline |

### Request Body — `POST /simulate`

```json
{
  "framing": { "...FramingInput fields..." },
  "loads":   { "...LoadsInput fields..." },
  "settings": { "...SettingsInput fields..." }
}
```

### Response Body — `POST /simulate`

```json
{
  "metadata": {
    "label": "My base case scenario",
    "period_count": 120,
    "start_date": "2025-01-01",
    "end_date": "2034-12-01",
    "time_step": "monthly",
    "warnings": [
      {
        "period": "2026-03-01",
        "type": "negative_cash",
        "message": "Cash went negative in March 2026. Contributions were reduced."
      }
    ]
  },
  "timeline": [
    {
      "period": "2025-01-01",
      "cash": 5842.50,
      "investments": { "401k": 16137.92 },
      "debts": { "student_loans": 27528.33 },
      "income_this_period": 5850.00,
      "expenses_this_period": 2254.00,
      "net_worth": -5547.91
    }
  ]
}
```

### Status Codes

| Code | Condition |
|---|---|
| 200 | Simulation ran successfully (warnings may be present in metadata) |
| 400 | Cross-field validation failure (e.g. end_date before start_date) |
| 422 | Pydantic field-level validation failure (missing field, wrong type) |
| 500 | Unexpected engine error — should never occur with valid input |

### Warnings vs. Errors

- **Errors (4xx):** Input is invalid; simulation did not run
- **Warnings (200 + `metadata.warnings`):** Input was valid; simulation ran; notable conditions occurred

A user with negative cash in month 6 should see their full timeline with the period flagged — not an error response.

---

## 10. Frontend Specification

### Component Hierarchy

```
App
├── SimulationForm
│   ├── FramingSection
│   ├── LoadsSection
│   │   ├── IncomeList
│   │   ├── ExpenseList
│   │   ├── DebtList
│   │   └── InvestmentList
│   └── SettingsSection
├── SimulationResults
│   ├── NetWorthChart
│   ├── SummaryPanel
│   └── WarningsPanel (conditional)
└── ErrorBanner (conditional)
```

### Application State Shape

```typescript
type SimulationStatus = 'idle' | 'loading' | 'success' | 'error';

interface AppState {
  status: SimulationStatus;
  timeline: TimelineResponse | null;
  error: string | null;
}
```

Discriminated union — no partial states. When `status === 'success'`, `timeline` is guaranteed non-null.

### `useSimulation` Hook

Owns the fetch lifecycle. Signature:

```typescript
useSimulation(): {
  status: SimulationStatus;
  timeline: TimelineResponse | null;
  error: string | null;
  run: (framing: FramingInput, loads: LoadsInput, settings: SettingsInput) => void;
}
```

Form components never call `fetch` directly — they call `run()`.

### Chart Specification (Phase 3)

**Library:** Recharts

**Series:**
- Net worth — primary line, bold
- Cash — secondary, dashed
- Total investments — secondary
- Total debt — secondary, red

**Reference lines:**
- `y = 0` (zero net worth baseline)
- `x = debt_free_date` (if debt is fully paid off before simulation ends)

**Behavior:**
- Series toggled via legend click
- Tooltip on hover: all values for that period
- Y-axis: `formatCurrency`
- X-axis: `formatPeriod`, ticks every 12 periods

### Summary Panel Metrics

| Metric | Source |
|---|---|
| Starting Net Worth | `timeline[0].net_worth` |
| Ending Net Worth | `timeline[-1].net_worth` |
| Net Worth Change | ending − starting |
| Total Interest Paid | sum of `interest_paid_this_period` across all periods |
| Investment Growth (returns only) | ending balances − starting balances − total contributions |
| Debt-Free Date | first period where all debt balances = 0 |
| First Negative Cash Period | first period where `cash < 0` |

### Formatters (`frontend/src/utils/formatters.ts`)

```typescript
formatCurrency(value: number): string  // 1234.5 → "$1,234.50"; -50 → "-$50.00"
formatPercent(value: number): string   // 0.07 → "7.00%"
formatPeriod(isoDate: string): string  // "2025-01-01" → "Jan 2025"
formatDelta(value: number): string     // 500 → "+$500.00"; -200 → "-$200.00"
```

All formatters are pure functions. Each gets its own unit test.

---

## 11. Testing Strategy and Acceptance Criteria

### Phase 1 Acceptance Criteria

**AC-1.1 — Pydantic models reject invalid input**
- Missing required field → `ValidationError`
- `end_date` before `start_date` → validator raises
- Negative `current_balance` on debt → `ValidationError`
- Duplicate load names → validator raises

**AC-1.2 — Income applicator**
- 0% growth: cash increases by `monthly_gross * (1 - tax_rate)` each period
- 3% annual growth: month 12 income ≠ month 1 income, difference matches formula
- Inactive income (before `start_date`): cash unchanged
- Zero income load: no state change

**AC-1.3 — Expense applicator**
- Inflation-linked at 3%: month 12 amount ≠ month 1 amount
- Non-inflation-linked: identical each period
- Zero expense: no state change

**AC-1.4 — Debt applicator**
- After full term: balance reaches 0 (within rounding tolerance)
- Interest charged before payment applied, not after
- Extra payment reduces balance correctly under each strategy
- Paid-off debt: no change to cash or balance in subsequent periods

**AC-1.5 — Investment applicator**
- 7% annual return: 12-month balance matches `balance * (1 + 0.07/12)^12 + contributions`
- Employer match applied correctly, capped at salary percentage
- Zero contribution: balance still grows by return rate

**AC-1.6 — Integration test**

Given: 1 income ($5,000/mo, 0% growth, 22% tax), 1 expense ($2,000/mo, not inflation-linked), 1 debt ($10,000 at 5%, $200/mo minimum), 1 investment ($500/mo, 7% return, no match, $0 starting), 12-month run, $5,000 starting cash — month 12 net worth must match a hand-calculated value to within $0.01.

**AC-1.7 — Determinism**

Run identical inputs twice. Every field of every state in both timelines must be equal.

### Phase 2 Acceptance Criteria

- **AC-2.1:** Valid body → 200 with correct `metadata.period_count`
- **AC-2.2:** Missing framing field → 422 with field name in error detail
- **AC-2.3:** `end_date < start_date` → 400 (not 422)
- **AC-2.4:** Route handler contains no arithmetic operations (code review criterion)
- **AC-2.5:** `GET /health` → 200 `{ "status": "ok" }` with no engine call

### Phase 3 Acceptance Criteria

- **AC-3.1:** Chart renders without error for a 120-period timeline
- **AC-3.2:** Toggling a legend item hides/shows the corresponding line
- **AC-3.3:** All summary panel values match corresponding timeline array values
- **AC-3.4:** Warnings panel appears if and only if `metadata.warnings` is non-empty
- **AC-3.5:** `formatCurrency(1234567.89)` → `"$1,234,567.89"`; `formatCurrency(-50)` → `"-$50.00"`
- **AC-3.6:** `tsc --noEmit` reports zero errors

### Test File Map

```
tests/
├── simulation/
│   ├── models/
│   │   └── test_inputs.py              ← AC-1.1
│   └── engine/
│       ├── test_apply_income.py        ← AC-1.2
│       ├── test_apply_expenses.py      ← AC-1.3
│       ├── test_apply_debts.py         ← AC-1.4
│       ├── test_apply_investments.py   ← AC-1.5
│       └── test_core.py               ← AC-1.6, AC-1.7
└── api/
    └── test_simulate_endpoint.py       ← AC-2.1 through AC-2.5

frontend/src/utils/
    formatters.test.ts                  ← AC-3.5
```

---

## 12. Phased Roadmap

### Phase 0 — Foundation ✅

- [x] Vite + React frontend scaffolded
- [x] FastAPI backend scaffolded
- [x] Final directory structure agreed and created
- [x] TypeScript strict mode enforced, errors resolved
- [x] Shutdown command and session logging workflow
- [x] CLAUDE.md fully specified

### Phase 1 — Core Simulation Engine ✅

**Goal:** A pure Python function that produces a correct timeline from the three input files.
**Exit criterion:** AC-1.1 through AC-1.7 pass. `pytest` green.

Implementation order:
1. ✅ Resolve Open Questions (Section 15) — schema settled
2. ✅ Write `src/simulation/models/inputs.py` — Pydantic models with `DateBoundLoad` base class
3. ⬜ Write `tests/simulation/models/test_inputs.py` — not yet written
4. ✅ Write `src/simulation/models/state.py` — `SimulationState` frozen dataclass
5. ✅ Write `apply_income` + `test_apply_income.py` (4 tests)
6. ✅ Write `apply_expense` + `test_apply_expense.py` (2 tests)
7. ✅ Write `apply_debt` + `test_apply_debt.py` (4 tests)
8. ✅ Write `apply_investment` + `test_apply_investment.py` (4 tests)
9. ✅ Write `core.py` core loop + `test_core.py` (6 integration tests, 20 total passing)

### Phase 2 — API Layer

**Goal:** FastAPI app accepts the three input files and returns the timeline as JSON.
**Exit criterion:** AC-2.1 through AC-2.5 pass. `curl` round-trip works.

1. Write `api/models.py` — request and response Pydantic models
2. Write `api/main.py` — CORS, `/health`, `/simulate`
3. Write `tests/api/test_simulate_endpoint.py` with mocked engine
4. Manual end-to-end test via `curl`

### Phase 3 — Basic Visualization

**Goal:** Frontend displays the timeline as a readable chart.
**Exit criterion:** AC-3.1 through AC-3.6 pass.

1. Add Recharts to `frontend/package.json`
2. Write `formatters.ts` + `formatters.test.ts`
3. Redesign `SimulationForm` to match the three-file input schema
4. Write `useSimulation` hook
5. Write `NetWorthChart`, `SummaryPanel`, `WarningsPanel`
6. Wire together in `App`

### Phase 4 — Scenario Comparison

**Goal:** Run two scenarios side by side and understand the divergence.

- `localStorage`-backed scenario save/load with named presets
- 3 built-in starter presets (Early career / Mid-career with debt / Pre-retirement)
- Dual input panels — Scenario A and Scenario B
- Shared chart with both net worth curves
- Difference summary: "By [end date], Scenario B outperforms by $X"
- Sensitivity slider: override one `settings.json` value, re-run on change (debounced 300ms)

### Phase 5 — Advanced Engine Features

Implementation order within this phase:

1. Inflation-linked income growth
2. One-time expenses (`frequency: "one_time"`)
3. Income end dates with replacement stream
4. Debt payoff cascade (redirect paid-off minimum to next debt)
5. Event system (one-time state mutations at a specified period)
6. FIRE milestone detection in metadata

### Phase 6 — Polish and Persistence

- In-browser JSON editor with syntax highlighting and real-time validation
- Toggle between structured form and raw JSON per section
- Simulation run history in `localStorage` (capped at 10)
- Timeline CSV export
- Chart PNG export
- Input file ZIP export
- Warnings center with explanations and suggested remediations

### Phase 7 — Stochastic Simulation

**Prerequisite:** Every deterministic test must pass and be stable. No exceptions.

- Monte Carlo runner: N simulations with return rates drawn from `Normal(mean, std_dev)`
- Adds `assumed_return_std_dev` to each investment load
- Chart overlay: 10th / 50th / 90th percentile envelope around base case
- Summary: "There is a 90% chance your net worth is above $X by [end date]"

---

## 13. Edge Cases and Error Handling

### Engine

| Case | Behavior |
|---|---|
| Debt balance reaches zero mid-term | Mark paid off; stop applying payments |
| Cash goes negative in a period | Clamp to 0; add warning to metadata; simulation continues |
| Investment contribution exceeds available cash | Skip contribution entirely; growth still applies; no warning in Phase 1 (Phase 5 adds shortfall tracking) |
| Simulation produces zero periods | `ValidationError` — end must be strictly after start |
| All debts paid off before simulation ends | Debt applicator becomes a no-op for remaining periods |
| Income load with future `start_date` | Load inactive until `period >= start_date` |
| Employer match cap results in zero match | No match applied; no error |

### API

| Case | Behavior |
|---|---|
| Request body missing `loads` entirely | 422 from Pydantic |
| `loads.income` is an empty array | Valid — simulation runs with no income |
| All load arrays empty | Valid — cash drains from starting balance; warnings generated |
| `start_date` not first of month | 400 — validator enforces this |

### Frontend

| Case | Behavior |
|---|---|
| API returns 422 | Parse Pydantic error detail; display field-level messages next to inputs |
| API returns 500 | Display generic error banner; log full error to console |
| Timeline has 1 period | Chart renders as single point; no crash |
| All net worth values negative | Chart renders correctly; y-axis includes negative range |
| Debt-free date never reached | Summary: "Debt not fully paid off in this scenario" |

---

## 14. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Debt amortization formula is wrong | Medium | High | Verify against a known loan calculator before writing tests |
| Monthly vs. annual compounding inconsistency | High | Medium | ADR-004 mandates monthly everywhere; document formula in code comments |
| Floating point error accumulates over 600 periods | Low | Low | Round to 2dp after each applicator; test at 120 periods |
| `loads.json` schema changes after Phase 1 tests are written | Medium | High | Resolve all Open Questions before writing any Python |
| Frontend re-renders cause performance issues | Medium | Low | Debounce API calls; don't simulate on every keystroke |
| Negative cash cascades into invalid subsequent states | Medium | High | Clamp to 0 immediately; unit test this boundary explicitly |
| Employer match calculation ambiguous (gross vs. net) | High | Medium | ADR: use gross; document and test explicitly |
| One-time expense applied every period instead of once | High | High | Requires `frequency` field + tracking; scoped to Phase 5 |
| Scope creep into visualization before engine is verified | High | High | CLAUDE.md Do Not Touch list; shutdown command checks next step |

---

## 15. Open Questions

These must be resolved before Phase 1 implementation begins. Leaving them open causes mid-build schema changes.

| # | Question | Stakes | Resolution |
|---|---|---|---|
| OQ-1 | Is income tax applied monthly or annually? | Affects every monthly cash flow | ✅ **Monthly** — `net = gross * (1 - income_tax_rate)` per period |
| OQ-2 | What happens when cash goes negative? | Core behavior decision | Open — not explicitly handled in Phase 1; cash can go negative |
| OQ-3 | Does employer match apply to gross or net income? | Affects every investment balance | Deferred — employer match removed from Phase 1 scope |
| OQ-4 | Are returns compounded monthly or annually? | Affects all investment balances | ✅ **Monthly** — `balance * (annual_return / 12)` per period |
| OQ-5 | When a debt is paid off, what happens to the extra payment budget? | Core debt strategy behavior | ✅ **Lost in Phase 1** — extra payment is per-load; cascade deferred to Phase 5 |
| OQ-6 | Can an expense have a `start_date` and `end_date`? | Affects expense schema | ✅ **Yes** — all loads inherit `DateBoundLoad` with `start_date` + optional `end_date` |
| OQ-7 | Is `starting_cash` in `settings.json` or implied from loads? | Affects initial state construction | ✅ **`settings.json`** — `starting_cash` field on `SettingsInput` |
| OQ-8 | In the final debt period, is a partial payment applied? | Affects final debt period accuracy | ✅ **Yes** — `actual_deducted = min(total_payment, balance + interest)` |
| OQ-9 | Is the FIRE milestone in Phase 1 output or Phase 5? | Affects `TimelineResponse` schema | ✅ **Phase 5** — not in Phase 1 response |
| OQ-10 | Should `income_this_period` be gross or net of tax? | Affects summary panel display | Open — currently `state.income` accumulates gross; net derivable from gross + tax rate |

---

*This document is versioned. Update it when architectural decisions change, open questions are resolved, or phases are completed. The `## Current Build State` section of `CLAUDE.md` must stay synchronized with this document's phase completion status.*
