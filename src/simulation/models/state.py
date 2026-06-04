from dataclasses import dataclass, field
from datetime import date

@dataclass(frozen=True)
class SimulationState:
    date: date
    cash: float = 0.0
    investments: dict[str, float] = field(default_factory=dict)
    debts: dict[str, float] = field(default_factory=dict)
    income: float = 0.0
    expenses: float = 0.0

    @property
    def net_worth(self) -> float:
        return self.cash + sum(self.investments.values()) - sum(self.debts.values())
