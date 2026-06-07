from simulation.engine.apply_expense import apply_expense
from simulation.models.state import SimulationState
from datetime import date
from simulation.models.inputs import ExpenseLoad, SettingsInput
import pytest

start_date = date(2024, 1, 1)
prev_state = SimulationState(date=date(2025, 1, 1), income=0, expenses=0, cash=100)

non_inflation_expense = ExpenseLoad(name="test_expense", monthly_amount=50, category="test_category", inflation_linked=False, start_date=start_date)
non_inflation_settings = SettingsInput(inflation_rate=0.02, apply_inflation_to_expenses=False)

def test_non_inflation_expense():
    new_state = apply_expense(state=prev_state, load=non_inflation_expense, settings=non_inflation_settings)
    assert new_state.cash == 50
    assert new_state.expenses == 50

inflation_expense = ExpenseLoad(name="test_expense", monthly_amount=50, category="test_category", inflation_linked=True, start_date=start_date)
inflation_settings = SettingsInput(inflation_rate=0.02, apply_inflation_to_expenses=True)

def test_inflation_expense():
    new_state = apply_expense(state=prev_state, load=inflation_expense, settings=inflation_settings)
    assert new_state.cash == 49
    assert new_state.expenses == 51


def test_inactive_load_returns_unchanged_state():
    future_expense = ExpenseLoad(
        name="rent",
        monthly_amount=50,
        category="housing",
        inflation_linked=False,
        start_date=date(2026, 1, 1),
    )
    # prev_state.date = 2025-01-01, which is before start_date
    new_state = apply_expense(state=prev_state, load=future_expense, settings=non_inflation_settings)
    assert new_state is prev_state


def test_end_date_gating_returns_unchanged_state():
    expired_expense = ExpenseLoad(
        name="rent",
        monthly_amount=50,
        category="housing",
        inflation_linked=False,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 6, 1),
    )
    future_state = SimulationState(date=date(2025, 1, 1), cash=100, expenses=0)
    # state.date = 2025-01-01, which is after end_date = 2024-06-01
    new_state = apply_expense(state=future_state, load=expired_expense, settings=non_inflation_settings)
    assert new_state is future_state


def test_inflation_linked_but_setting_disabled_applies_flat_amount():
    # inflation_linked=True on the load but apply_inflation_to_expenses=False in settings
    disabled_settings = SettingsInput(inflation_rate=0.02, apply_inflation_to_expenses=False)
    new_state = apply_expense(state=prev_state, load=inflation_expense, settings=disabled_settings)
    assert new_state.cash == pytest.approx(50.0)  # flat 50, not inflated
    assert new_state.expenses == pytest.approx(50.0)