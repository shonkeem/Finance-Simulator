'''
  - Normal case — active load, no tax. Does cash increase by the right amount?
  - Tax applied — same, but with apply_income_tax=True.Does net correctly reduce gross?
  - Inactive load — state.date is before load.start_date. Does state come back unchanged?
  - Growth applied — state.date is 12 months after
load.start_date. Is gross higher than base by exactly one year of compound growth?
'''

from simulation.engine.apply_income import apply_income
from simulation.models.state import SimulationState
from datetime import date
from simulation.models.inputs import IncomeLoad, SettingsInput, DebtStrategies
import pytest


prev_state = SimulationState(date=date(2024, 1, 1), income=0, expenses=0)
same_day_load = IncomeLoad(name="test income", monthly_gross=100, annual_growth_rate=.1, start_date=date(2024, 1, 1))
tax_free_settings = SettingsInput(inflation_rate=0.01, starting_cash=0, income_tax_rate=.2, apply_income_tax=False, apply_inflation_to_expenses=True, debt_payoff_strategy=DebtStrategies.SNOWBALL)
taxed_settings = SettingsInput(inflation_rate=0.01, starting_cash=0, income_tax_rate=.2, apply_income_tax=True, apply_inflation_to_expenses=True, debt_payoff_strategy=DebtStrategies.SNOWBALL)
invalid_date_income = IncomeLoad(name="", monthly_gross=200, annual_growth_rate=.1, start_date=date(2024, 2, 1))
growth_load = IncomeLoad(name="", monthly_gross=100, annual_growth_rate=.1, start_date=date(2023, 1, 1))


def test_same_day_no_tax():
    new_state = apply_income(prev_state, same_day_load, tax_free_settings)
    assert new_state.income == pytest.approx(100)
    assert new_state.cash == pytest.approx(100)
    

def test_same_day_tax():
    new_state = apply_income(prev_state, same_day_load, taxed_settings)
    assert new_state.income == pytest.approx(100)
    assert new_state.cash == pytest.approx(80)

def test_invalid_date():
    new_state = apply_income(prev_state, invalid_date_income, taxed_settings)
    assert new_state == prev_state

def test_growth_applied():
    new_state = apply_income(prev_state, growth_load, tax_free_settings)
    assert new_state.cash == pytest.approx(110)
    assert new_state.income == pytest.approx(110)
