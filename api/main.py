from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.models import SimulationRequest, SimulationStateResponse, TimelineResponse
from simulation.engine.core import run_simulation

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


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
