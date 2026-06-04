from simulation.models.inputs import DebtLoad, SettingsInput
from simulation.models.state import SimulationState
from dataclasses import replace

def apply_debt(state: SimulationState, load: DebtLoad, setting: SettingsInput) -> SimulationState:
    # date gating
    if state.date < load.start_date or (load.end_date and state.date > load.end_date):
        return state

    # update debt balance
    total_monthly = load.minimum_monthly_payment + load.extra_monthly_payment
    interest = state.debts[load.name] * (load.annual_interest_rate / 12)
    new_balance = max(0.0, state.debts[load.name] + interest - total_monthly)

    new_debts = {**state.debts, load.name: new_balance}
    new_cash = state.cash - min(total_monthly, state.debts[load.name] + interest)
    return replace(state, cash=new_cash, debts=new_debts)
