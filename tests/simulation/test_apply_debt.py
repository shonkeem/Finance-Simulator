from simulation.engine.apply_debt import apply_debt
from simulation.models.inputs import DebtLoad, SettingsInput
from simulation.models.state import SimulationState
from datetime import date
import pytest

settings = SettingsInput()

loan = DebtLoad(
    name="student_loan",
    current_balance=1000.0,
    annual_interest_rate=0.12,
    minimum_monthly_payment=100.0,
    extra_monthly_payment=0.0,
    start_date=date(2024, 1, 1),
)

prev_state = SimulationState(
    date=date(2025, 1, 1),
    cash=5000.0,
    debts={"student_loan": 1000.0},
)


def test_apply_debt_normal_payment_reduces_balance():
    # interest = 1000 * 0.12 / 12 = 10.0; new_balance = 1000 + 10 - 100 = 910.0
    new_state = apply_debt(state=prev_state, load=loan, setting=settings)
    assert new_state.debts["student_loan"] == pytest.approx(910.0)
    assert new_state.cash == pytest.approx(4900.0)


def test_apply_debt_balance_floored_at_zero():
    # balance = 50; interest = 50 * 0.12 / 12 = 0.5; payment = 100 > owed (50.5)
    # new_balance = 0; cash deducted = 50.5 only, not the full 100
    small_balance_state = SimulationState(
        date=date(2025, 1, 1),
        cash=5000.0,
        debts={"student_loan": 50.0},
    )
    new_state = apply_debt(state=small_balance_state, load=loan, setting=settings)
    assert new_state.debts["student_loan"] == 0.0
    assert new_state.cash == pytest.approx(4949.5)


def test_apply_debt_extra_payment_reduces_balance_further():
    # total = 100 min + 200 extra = 300; interest = 10; new_balance = 710
    extra_loan = DebtLoad(
        name="student_loan",
        current_balance=1000.0,
        annual_interest_rate=0.12,
        minimum_monthly_payment=100.0,
        extra_monthly_payment=200.0,
        start_date=date(2024, 1, 1),
    )
    new_state = apply_debt(state=prev_state, load=extra_loan, setting=settings)
    assert new_state.debts["student_loan"] == pytest.approx(710.0)
    assert new_state.cash == pytest.approx(4700.0)


def test_apply_debt_inactive_load_returns_unchanged_state():
    future_loan = DebtLoad(
        name="student_loan",
        current_balance=1000.0,
        annual_interest_rate=0.12,
        minimum_monthly_payment=100.0,
        extra_monthly_payment=0.0,
        start_date=date(2026, 1, 1),
    )
    new_state = apply_debt(state=prev_state, load=future_loan, setting=settings)
    assert new_state is prev_state
