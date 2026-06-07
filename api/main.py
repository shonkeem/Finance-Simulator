from fastapi import FastAPI
from api.models import SimulationRequest, SimulationStateResponse, TimelineResponse
from simulation.engine.core import run_simulation

app = FastAPI()


@app.post("/simulate", response_model=TimelineResponse)
def simulate(request: SimulationRequest) -> TimelineResponse:
    timeline = run_simulation(request.framing, request.loads, request.settings)
    return TimelineResponse(
        timeline=[
            SimulationStateResponse(
                date=state.date,
                cash=state.cash,
                investments=state.investments,
                debts=state.debts,
                income=state.income,
                expenses=state.expenses,
                net_worth=state.net_worth,
            )
            for state in timeline
        ]
    )
