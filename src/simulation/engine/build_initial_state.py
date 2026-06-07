from simulation.models.inputs import (
    FramingInput,
    LoadsInput,
    SettingsInput,
)
from simulation.models.state import SimulationState


def build_initial_state(
    framing: FramingInput, loads: LoadsInput, settings: SettingsInput
) -> SimulationState:
    initial_investments = {i.name: i.current_balance for i in loads.investments}
    initial_debt = {i.name: i.current_balance for i in loads.debts}
    initial_income = 0
    initial_expenses = 0

    return SimulationState(
        date=framing.start_date,
        cash=settings.starting_cash,
        investments=initial_investments,
        debts=initial_debt,
        income=initial_income,
        expenses=initial_expenses,
    )
