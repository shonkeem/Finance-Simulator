from simulation.models.inputs import InvestmentLoad, SettingsInput
from simulation.models.state import SimulationState, evolve


def apply_investment(
    state: SimulationState, load: InvestmentLoad, setting: SettingsInput
) -> SimulationState:
    # date gating
    if state.date < load.start_date or (load.end_date and state.date > load.end_date):
        return state

    # update investment balance
    interest = state.investments[load.name] * (load.annual_return / 12)

    # check if enough cash to invest
    if load.monthly_contribution > state.cash:
        new_balance = state.investments[load.name] + interest
        new_investments = {**state.investments, load.name: new_balance}
        return evolve(state, investments=new_investments)

    new_balance = state.investments[load.name] + interest + load.monthly_contribution
    new_investments = {**state.investments, load.name: new_balance}
    new_cash = state.cash - load.monthly_contribution

    return evolve(state, cash=new_cash, investments=new_investments)
