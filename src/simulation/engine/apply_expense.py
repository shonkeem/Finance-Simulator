from simulation.models.inputs import ExpenseLoad, SettingsInput
from simulation.models.state import SimulationState
from dataclasses import replace
from datetime import date

def apply_expense(state: SimulationState, load: ExpenseLoad, settings: SettingsInput, start_date: date) -> SimulationState:
    
    # inflation calculation
    if load.inflation_linked and settings.apply_inflation_to_expenses:
        months_elapsed = (state.date.year - start_date.year) * 12 + (state.date.month - start_date.month)
        years_elapsed = months_elapsed / 12
        new_expense_amount = load.monthly_amount * (1 + settings.inflation_rate) ** years_elapsed
        expense_total = state.expenses + new_expense_amount
        new_balance = state.cash - new_expense_amount
    else:
        expense_total = state.expenses + load.monthly_amount
        new_balance = state.cash - load.monthly_amount
    

    return replace(state, cash=new_balance, expenses=expense_total)
