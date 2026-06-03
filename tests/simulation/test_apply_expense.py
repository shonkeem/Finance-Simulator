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