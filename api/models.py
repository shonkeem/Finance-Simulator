from pydantic import BaseModel
from simulation.models.inputs import FramingInput, LoadsInput, SettingsInput
from datetime import date


class SimulationRequest(BaseModel):
    framing: FramingInput
    loads: LoadsInput
    settings: SettingsInput


class SimulationStateResponse(BaseModel):
    date: date
    cash: float
    investments: dict[str, float]
    debts: dict[str, float]
    income: float
    expenses: float
    net_worth: float


class TimelineResponse(BaseModel):
    timeline: list[SimulationStateResponse]
