from simulation.engine.apply_income import apply_income
from simulation.models.state import SimulationState
from datetime import date
from simulation.models.inputs import IncomeLoad, SettingsInput
import pytest

prev_state = SimulationState(date=date(2024, 1, 1), income=0, expenses=0)

same_day_load = IncomeLoad(name="test income", monthly_gross=100, annual_growth_rate=.1, start_date=date(2024, 1, 1))
tax_free_settings = SettingsInput(inflation_rate=0.01, starting_cash=0, income_tax_rate=.2, apply_income_tax=False, apply_inflation_to_expenses=True)
def test_same_day_no_tax():
    new_state = apply_income(prev_state, same_day_load, tax_free_settings)
    assert new_state.income == pytest.approx(100)
    assert new_state.cash == pytest.approx(100)
    
taxed_settings = SettingsInput(inflation_rate=0.01, starting_cash=0, income_tax_rate=.2, apply_income_tax=True, apply_inflation_to_expenses=True)
def test_same_day_tax():
    new_state = apply_income(prev_state, same_day_load, taxed_settings)
    assert new_state.income == pytest.approx(100)
    assert new_state.cash == pytest.approx(80)

invalid_date_income = IncomeLoad(name="", monthly_gross=200, annual_growth_rate=.1, start_date=date(2024, 2, 1))
def test_invalid_date():
    new_state = apply_income(prev_state, invalid_date_income, taxed_settings)
    assert new_state == prev_state

growth_load = IncomeLoad(name="", monthly_gross=100, annual_growth_rate=.1, start_date=date(2023, 1, 1))
def test_growth_applied():
    new_state = apply_income(prev_state, growth_load, tax_free_settings)
    assert new_state.cash == pytest.approx(110)
    assert new_state.income == pytest.approx(110)


def test_end_date_gating_returns_unchanged_state():
    expired_load = IncomeLoad(
        name="salary",
        monthly_gross=100,
        annual_growth_rate=0,
        start_date=date(2023, 1, 1),
        end_date=date(2023, 12, 1),
    )
    # prev_state.date = 2024-01-01, which is after end_date
    new_state = apply_income(prev_state, expired_load, tax_free_settings)
    assert new_state is prev_state


def test_accumulates_onto_existing_income():
    # income already accumulated from a previous load this period
    partial_state = SimulationState(date=date(2024, 1, 1), income=200, expenses=0)
    new_state = apply_income(partial_state, same_day_load, tax_free_settings)
    assert new_state.income == pytest.approx(300)  # 200 carried + 100 new
