from simulation.models.inputs import IncomeLoad, SettingsInput
from simulation.models.state import SimulationState, evolve


def apply_income(
    state: SimulationState, load: IncomeLoad, settings: SettingsInput
) -> SimulationState:
    # date gating
    if state.date < load.start_date or (load.end_date and state.date > load.end_date):
        return state

    # growth calculation
    months_elapsed = (state.date.year - load.start_date.year) * 12 + (
        state.date.month - load.start_date.month
    )
    years_elapsed = months_elapsed / 12
    monthly_gross = load.monthly_gross * (1 + load.annual_growth_rate) ** years_elapsed

    # tax calculation
    net = (
        monthly_gross * (1 - settings.income_tax_rate)
        if settings.apply_income_tax
        else monthly_gross
    )

    new_balance = state.cash + net
    new_income = state.income + monthly_gross
    return evolve(state, cash=new_balance, income=new_income)
