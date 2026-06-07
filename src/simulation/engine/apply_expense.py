from simulation.models.inputs import ExpenseLoad, SettingsInput
from simulation.models.state import SimulationState, evolve


def apply_expense(
    state: SimulationState, load: ExpenseLoad, settings: SettingsInput
) -> SimulationState:
    # date gating
    if state.date < load.start_date or (load.end_date and state.date > load.end_date):
        return state

    # inflation calculation
    if load.inflation_linked and settings.apply_inflation_to_expenses:
        months_elapsed = (state.date.year - load.start_date.year) * 12 + (
            state.date.month - load.start_date.month
        )
        years_elapsed = months_elapsed / 12
        new_expense_amount = (
            load.monthly_amount * (1 + settings.inflation_rate) ** years_elapsed
        )
        expense_total = state.expenses + new_expense_amount
        new_balance = state.cash - new_expense_amount
    else:
        expense_total = state.expenses + load.monthly_amount
        new_balance = state.cash - load.monthly_amount

    return evolve(state, cash=new_balance, expenses=expense_total)
