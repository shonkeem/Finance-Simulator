import pytest
from pydantic import ValidationError
from datetime import date
from simulation.models.inputs import (
    FramingInput,
    TimeStep,
    IncomeLoad,
    ExpenseLoad,
    DebtLoad,
    InvestmentLoad,
    LoadsInput,
    SettingsInput,
)


def make_framing(**kwargs):
    defaults = {
        "label": "test",
        "start_date": date(2025, 1, 1),
        "end_date": date(2025, 2, 1),
        "time_step": TimeStep.monthly,
    }
    return FramingInput(**{**defaults, **kwargs})


# --- FramingInput ---

def test_framing_end_before_start_raises():
    with pytest.raises(ValidationError, match="end_date must be after start_date"):
        make_framing(start_date=date(2025, 6, 1), end_date=date(2025, 1, 1))


def test_framing_start_not_first_of_month_raises():
    with pytest.raises(ValidationError, match="start_date must be the first of the month"):
        make_framing(start_date=date(2025, 1, 15))


def test_framing_end_not_first_of_month_raises():
    with pytest.raises(ValidationError, match="end_date must be the first of the month"):
        make_framing(end_date=date(2025, 2, 15))


def test_framing_same_start_and_end_raises():
    with pytest.raises(ValidationError, match="end_date must be after start_date"):
        make_framing(start_date=date(2025, 1, 1), end_date=date(2025, 1, 1))


# --- IncomeLoad ---

def test_income_load_zero_monthly_gross_raises():
    with pytest.raises(ValidationError, match="monthly_gross must be > 0"):
        IncomeLoad(name="salary", monthly_gross=0, annual_growth_rate=0, start_date=date(2025, 1, 1))


def test_income_load_negative_monthly_gross_raises():
    with pytest.raises(ValidationError, match="monthly_gross must be > 0"):
        IncomeLoad(name="salary", monthly_gross=-500, annual_growth_rate=0, start_date=date(2025, 1, 1))


# --- DebtLoad ---

def test_debt_load_interest_rate_above_one_raises():
    with pytest.raises(ValidationError, match="annual_interest_rate must be between 0 and 1"):
        DebtLoad(
            name="loan", current_balance=1000.0, annual_interest_rate=1.5,
            minimum_monthly_payment=100.0, extra_monthly_payment=0.0,
            start_date=date(2025, 1, 1),
        )


def test_debt_load_negative_interest_rate_raises():
    with pytest.raises(ValidationError, match="annual_interest_rate must be between 0 and 1"):
        DebtLoad(
            name="loan", current_balance=1000.0, annual_interest_rate=-0.05,
            minimum_monthly_payment=100.0, extra_monthly_payment=0.0,
            start_date=date(2025, 1, 1),
        )


def test_debt_load_zero_current_balance_raises():
    with pytest.raises(ValidationError, match="must be > 0"):
        DebtLoad(
            name="loan", current_balance=0.0, annual_interest_rate=0.05,
            minimum_monthly_payment=100.0, extra_monthly_payment=0.0,
            start_date=date(2025, 1, 1),
        )


def test_debt_load_negative_extra_payment_raises():
    with pytest.raises(ValidationError, match="extra_monthly_payment must be >= 0"):
        DebtLoad(
            name="loan", current_balance=1000.0, annual_interest_rate=0.05,
            minimum_monthly_payment=100.0, extra_monthly_payment=-50.0,
            start_date=date(2025, 1, 1),
        )


# --- DateBoundLoad (inherited by all load types) ---

def test_date_bound_load_end_before_start_raises():
    with pytest.raises(ValidationError, match="end_date must be after start_date"):
        IncomeLoad(
            name="salary", monthly_gross=1000, annual_growth_rate=0,
            start_date=date(2025, 6, 1), end_date=date(2025, 1, 1),
        )


# --- LoadsInput uniqueness ---

def test_duplicate_income_names_raises():
    with pytest.raises(ValidationError, match="Income names must be unique"):
        LoadsInput(
            income=[
                IncomeLoad(name="salary", monthly_gross=3000, annual_growth_rate=0, start_date=date(2025, 1, 1)),
                IncomeLoad(name="salary", monthly_gross=1000, annual_growth_rate=0, start_date=date(2025, 1, 1)),
            ],
            expenses=[], debts=[], investments=[],
        )


def test_duplicate_expense_names_raises():
    with pytest.raises(ValidationError, match="Expense names must be unique"):
        LoadsInput(
            income=[],
            expenses=[
                ExpenseLoad(name="rent", monthly_amount=1000, category="housing", inflation_linked=False, start_date=date(2025, 1, 1)),
                ExpenseLoad(name="rent", monthly_amount=500, category="housing", inflation_linked=False, start_date=date(2025, 1, 1)),
            ],
            debts=[], investments=[],
        )


def test_duplicate_debt_names_raises():
    with pytest.raises(ValidationError, match="Debt names must be unique"):
        LoadsInput(
            income=[], expenses=[],
            debts=[
                DebtLoad(name="loan", current_balance=1000.0, annual_interest_rate=0.05, minimum_monthly_payment=100.0, extra_monthly_payment=0.0, start_date=date(2025, 1, 1)),
                DebtLoad(name="loan", current_balance=500.0, annual_interest_rate=0.05, minimum_monthly_payment=50.0, extra_monthly_payment=0.0, start_date=date(2025, 1, 1)),
            ],
            investments=[],
        )


# --- SettingsInput ---

def test_settings_negative_starting_cash_raises():
    with pytest.raises(ValidationError, match="starting_cash must be >= 0"):
        SettingsInput(starting_cash=-100.0)


def test_settings_income_tax_rate_above_one_raises():
    with pytest.raises(ValidationError, match="income_tax_rate must be between 0 and 1"):
        SettingsInput(income_tax_rate=1.5)


def test_settings_negative_income_tax_rate_raises():
    with pytest.raises(ValidationError, match="income_tax_rate must be between 0 and 1"):
        SettingsInput(income_tax_rate=-0.1)
