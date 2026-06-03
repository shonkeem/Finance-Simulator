from simulation.models.inputs import FramingInput, LoadsInput, SettingsInput, TimeStep
from simulation.models.state import SimulationState
from simulation.engine.build_initial_state import build_initial_state
from simulation.engine.apply_debt import apply_debt
from simulation.engine.apply_expense import apply_expense
from simulation.engine.apply_income import apply_income
from simulation.engine.apply_investment import apply_investment
from datetime import date
from dataclasses import replace


def advance_one_month(current_date: date):
    if current_date.month == 12:
        return date(current_date.year + 1, 1, 1)
    return date(current_date.year, current_date.month + 1, 1)

def run_simulation(
        framing: FramingInput,
        loads: LoadsInput,
        settings: SettingsInput
) -> list[SimulationState]:
    state = build_initial_state(framing, loads, settings)
    timeline = [state]
    current_date = framing.start_date

    while current_date < framing.end_date:
        for load in loads.income:
            state = apply_income(state, load, settings)
        for load in loads.expenses:
            state = apply_expense(state, load, settings)
        for load in loads.debts:
            state = apply_debt(state, load, settings)
        for load in loads.investments:
            state = apply_investment(state, load, settings)

        timeline.append(state)

        if framing.time_step == TimeStep.monthly:
            current_date = advance_one_month(current_date)
            state = replace(state, date=current_date)


    return timeline
