---
name: startup
description: Start-of-session briefing for FinanceSimulator. Reads last session log, checks git state, runs tests, checks build, and prints a focused session brief so the developer can start working immediately.
---

# Start-of-Session Briefing — Financial Simulation Sandbox

**Read-only. Do NOT modify any files, fix anything, or commit anything.**
If any step fails to run (missing tool, no git repo), skip it, note the skip, and continue.

Optional developer note: $ARGUMENTS

---

## Step 1 — Last Session Recap

Read `docs/session-log.md` and extract only the **most recent entry**.

Print:
- The date of the last session
- The "Done" bullets (what was accomplished)
- The "Next Session" bullets (what was planned)
- How many days have passed since that session (calculate from today's date)

If more than 14 days have passed, flag it: **"Extended break detected — verify assumptions before starting."**

---

## Step 2 — Current Build State

Read the `## Current Build State` section of `CLAUDE.md`.

Print:
- The `*Last updated*` date
- The **Next step** field verbatim
- The **Does NOT exist yet** list (condensed — one line per item)

If `CLAUDE.md` last-updated date is older than the last session log entry, flag it: **"CLAUDE.md may be stale — session log is newer."**

---

## Step 3 — Uncommitted Work

Run `git status` and `git diff --stat`.

- List every changed file with a one-line description of what changed
- Categorize as: staged / unstaged / untracked
- If working tree is clean, say so explicitly

If there are uncommitted changes, flag it: **"Uncommitted work present — confirm this is intentional before starting new work."**

---

## Step 4 — Recent Commits

Run `git log --oneline -8`.

Print the last 8 commits. If the most recent commit is more than 14 days old, flag it: **"No recent commits — confirm you're on the right branch."**

---

## Step 5 — Test Health

Detect which test runners are present:
- Python: run `pytest --tb=short -q` if `pytest` is installed in `.venv`
- TypeScript: run `npx vitest run --reporter=verbose` from `frontend/` if vitest is configured

Report: total tests, passed, failed, skipped.

If any tests fail, list each failing test name and a one-line summary of the failure.
Flag: **"Tests are RED — fix before writing new code."**

If all tests pass: **"Baseline is green."**

---

## Step 6 — Build Check

Run `tsc --noEmit` from `frontend/`.
Run `ruff check src/ api/` if ruff is available in `.venv`.

Report all errors and warnings. Do not fix anything.

If there are errors: **"Build is broken — fix before writing new code."**

---

## Step 7 — Session Brief

Print a single, consolidated brief in this format:

```
=== SESSION BRIEF — [today's date] ===

LAST SESSION ([date], [N] days ago)
  Done:   [top 2–3 accomplishments from session log]
  Planned: [next-session bullets from session log]

CURRENT HEALTH
  Tests:  [X passed / Y failed / Z skipped — or SKIPPED]
  Build:  [clean / N errors — or SKIPPED]
  Git:    [clean / N uncommitted files]

IMMEDIATE NEXT TASK
  [The "Next step" from CLAUDE.md, verbatim]

  Files to open:
  [List the 1–3 files most relevant to the next task, based on CLAUDE.md context]

FLAGS
  [Any flags raised in steps 1–6, or "None"]
===
```

End with: **"Ready. Start with the task above."**
(Or if any flag is active: **"Resolve the flags above before starting new work."**)
