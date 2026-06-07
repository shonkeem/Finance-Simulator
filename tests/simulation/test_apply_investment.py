from simulation.engine.apply_investment import apply_investment
from simulation.models.inputs import InvestmentLoad, SettingsInput
from simulation.models.state import SimulationState
from datetime import date
import pytest

settings = SettingsInput()

fund = InvestmentLoad(
    name="401k",
    account_type="401k",
    current_balance=10000.0,
    monthly_contribution=500.0,
    annual_return=0.12,
    start_date=date(2024, 1, 1),
)

prev_state = SimulationState(
    date=date(2025, 1, 1),
    cash=5000.0,
    investments={"401k": 10000.0},
)


def test_apply_investment_normal_grows_and_contributes():
    # growth = 10000 * 0.12 / 12 = 100; new_balance = 10000 + 100 + 500 = 10600
    new_state = apply_investment(state=prev_state, load=fund, setting=settings)
    assert new_state.investments["401k"] == pytest.approx(10600.0)
    assert new_state.cash == pytest.approx(4500.0)


def test_apply_investment_zero_balance_only_contributes():
    # growth = 0 * 0.12 / 12 = 0; new_balance = 0 + 0 + 500 = 500
    zero_balance_state = SimulationState(
        date=date(2025, 1, 1),
        cash=5000.0,
        investments={"401k": 0.0},
    )
    new_state = apply_investment(state=zero_balance_state, load=fund, setting=settings)
    assert new_state.investments["401k"] == pytest.approx(500.0)
    assert new_state.cash == pytest.approx(4500.0)


def test_apply_investment_cash_shortage_skips_contribution():
    # cash = 100 < contribution = 500; growth still applies, cash unchanged
    low_cash_state = SimulationState(
        date=date(2025, 1, 1),
        cash=100.0,
        investments={"401k": 10000.0},
    )
    new_state = apply_investment(state=low_cash_state, load=fund, setting=settings)
    assert new_state.investments["401k"] == pytest.approx(10100.0)
    assert new_state.cash == pytest.approx(100.0)


def test_apply_investment_inactive_load_returns_unchanged_state():
    future_fund = InvestmentLoad(
        name="401k",
        account_type="401k",
        current_balance=10000.0,
        monthly_contribution=500.0,
        annual_return=0.12,
        start_date=date(2026, 1, 1),
    )
    new_state = apply_investment(state=prev_state, load=future_fund, setting=settings)
    assert new_state is prev_state


def test_apply_investment_end_date_gating_returns_unchanged_state():
    expired_fund = InvestmentLoad(
        name="401k",
        account_type="401k",
        current_balance=10000.0,
        monthly_contribution=500.0,
        annual_return=0.12,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 6, 1),
    )
    # prev_state.date = 2025-01-01, which is after end_date
    new_state = apply_investment(state=prev_state, load=expired_fund, setting=settings)
    assert new_state is prev_state


def test_apply_investment_zero_annual_return_only_contributes():
    no_return_fund = InvestmentLoad(
        name="401k",
        account_type="401k",
        current_balance=10000.0,
        monthly_contribution=500.0,
        annual_return=0.0,
        start_date=date(2024, 1, 1),
    )
    new_state = apply_investment(state=prev_state, load=no_return_fund, setting=settings)
    assert new_state.investments["401k"] == pytest.approx(10500.0)
    assert new_state.cash == pytest.approx(4500.0)
