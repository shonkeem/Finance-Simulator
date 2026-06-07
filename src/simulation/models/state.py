from dataclasses import dataclass, field, replace
from datetime import date


@dataclass(frozen=True)
class SimulationState:
    date: date
    cash: float = 0.0
    investments: dict[str, float] = field(default_factory=dict, hash=False)
    debts: dict[str, float] = field(default_factory=dict, hash=False)
    income: float = 0.0
    expenses: float = 0.0

    @property
    def net_worth(self) -> float:
        return self.cash + sum(self.investments.values()) - sum(self.debts.values())


def evolve(state: SimulationState, **kwargs) -> SimulationState:
    investments = dict(kwargs.pop("investments", state.investments))
    debts = dict(kwargs.pop("debts", state.debts))
    return replace(state, investments=investments, debts=debts, **kwargs)
