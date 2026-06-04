from simulation.engine.core import run_simulation
from simulation.models.inputs import (
    FramingInput, LoadsInput, SettingsInput, TimeStep,
    IncomeLoad, ExpenseLoad, DebtLoad, InvestmentLoad,
)
from datetime import date
import pytest

# --- shared framing ---

def make_framing(months: int) -> FramingInput:
    end_month = 1 + months
    end_year = 2025 + (end_month - 1) // 12
    end_month = ((end_month - 1) % 12) + 1
    return FramingInput(
        label="test",
        start_date=date(2025, 1, 1),
        end_date=date(end_year, end_month, 1),
        time_step=TimeStep.monthly,
    )


# --- timeline length ---

def test_run_simulation_one_month_returns_two_states():
    loads = LoadsInput(income=[], expenses=[], debts=[], investments=[])
    timeline = run_simulation(make_framing(1), loads, SettingsInput())
    assert len(timeline) == 2


def test_run_simulation_two_months_returns_three_states():
    loads = LoadsInput(income=[], expenses=[], debts=[], investments=[])
    timeline = run_simulation(make_framing(2), loads, SettingsInput())
    assert len(timeline) == 3


# --- income + expense accumulation ---

def test_run_simulation_cash_after_two_months_income_and_expense():
    # Month 1: 0 + 1000 - 400 = 600
    # Month 2: 600 + 1000 - 400 = 1200
    loads = LoadsInput(
        income=[IncomeLoad(name="salary", monthly_gross=1000, annual_growth_rate=0, start_date=date(2025, 1, 1))],
        expenses=[ExpenseLoad(name="rent", monthly_amount=400, category="housing", inflation_linked=False, start_date=date(2025, 1, 1))],
        debts=[],
        investments=[],
    )
    timeline = run_simulation(make_framing(2), loads, SettingsInput())
    assert timeline[-1].cash == pytest.approx(1200.0)


# --- debt paydown ---

def test_run_simulation_debt_balance_decreases_over_two_months():
    # Month 1: interest=10, balance=910, cash=4900
    # Month 2: interest=9.1, balance=819.1, cash=4800
    loads = LoadsInput(
        income=[],
        expenses=[],
        debts=[DebtLoad(name="loan", current_balance=1000.0, annual_interest_rate=0.12, minimum_monthly_payment=100.0, extra_monthly_payment=0.0, start_date=date(2025, 1, 1))],
        investments=[],
    )
    settings = SettingsInput(starting_cash=5000.0)
    timeline = run_simulation(make_framing(2), loads, settings)
    assert timeline[-1].debts["loan"] == pytest.approx(819.1)
    assert timeline[-1].cash == pytest.approx(4800.0)


# --- investment growth ---

def test_run_simulation_investment_grows_and_contributes_over_two_months():
    # Month 1: growth=10000*0.12/12=100, balance=10000+100+500=10600, cash=4500
    # Month 2: growth=10600*0.12/12=106, balance=10600+106+500=11206, cash=4000
    loads = LoadsInput(
        income=[],
        expenses=[],
        debts=[],
        investments=[InvestmentLoad(name="401k", account_type="401k", current_balance=10000.0, monthly_contribution=500.0, annual_return=0.12, start_date=date(2025, 1, 1))],
    )
    settings = SettingsInput(starting_cash=5000.0)
    timeline = run_simulation(make_framing(2), loads, settings)
    assert timeline[-1].investments["401k"] == pytest.approx(11206.0)
    assert timeline[-1].cash == pytest.approx(4000.0)


# --- determinism ---

def test_run_simulation_is_deterministic():
    loads = LoadsInput(
        income=[IncomeLoad(name="salary", monthly_gross=1000, annual_growth_rate=0.03, start_date=date(2025, 1, 1))],
        expenses=[ExpenseLoad(name="rent", monthly_amount=400, category="housing", inflation_linked=True, start_date=date(2025, 1, 1))],
        debts=[],
        investments=[],
    )
    settings = SettingsInput(starting_cash=500, inflation_rate=0.02, apply_inflation_to_expenses=True)
    framing = make_framing(6)
    run1 = run_simulation(framing, loads, settings)
    run2 = run_simulation(framing, loads, settings)
    assert [s.cash for s in run1] == [s.cash for s in run2]
