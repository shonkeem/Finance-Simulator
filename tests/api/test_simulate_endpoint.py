import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

VALID_REQUEST = {
    "framing": {
        "label": "test",
        "start_date": "2025-01-01",
        "end_date": "2025-02-01",
        "time_step": "monthly",
    },
    "loads": {
        "income": [
            {
                "name": "salary",
                "start_date": "2025-01-01",
                "monthly_gross": 5000.0,
                "annual_growth_rate": 0.0,
            }
        ],
        "expenses": [],
        "debts": [],
        "investments": [],
    },
    "settings": {},
}


def test_simulate_valid_input_returns_200():
    response = client.post("/simulate", json=VALID_REQUEST)
    assert response.status_code == 200


def test_simulate_response_has_timeline_key():
    response = client.post("/simulate", json=VALID_REQUEST)
    body = response.json()
    assert "timeline" in body
    assert isinstance(body["timeline"], list)


def test_simulate_timeline_entries_have_expected_fields():
    response = client.post("/simulate", json=VALID_REQUEST)
    entry = response.json()["timeline"][0]
    for field in (
        "date",
        "cash",
        "investments",
        "debts",
        "income",
        "expenses",
        "net_worth",
    ):
        assert field in entry


def test_simulate_invalid_input_returns_422():
    response = client.post("/simulate", json={"framing": "not_an_object"})
    assert response.status_code == 422


def test_simulate_missing_required_field_returns_422():
    response = client.post("/simulate", json={"framing": {}, "loads": {}, "settings": {}})
    assert response.status_code == 422


TWO_MONTH_REQUEST = {
    "framing": {
        "label": "test",
        "start_date": "2025-01-01",
        "end_date": "2025-03-01",
        "time_step": "monthly",
    },
    "loads": {"income": [], "expenses": [], "debts": [], "investments": []},
    "settings": {},
}


def test_simulate_one_month_returns_two_states():
    response = client.post("/simulate", json=VALID_REQUEST)
    assert len(response.json()["timeline"]) == 2


def test_simulate_two_months_returns_three_states():
    response = client.post("/simulate", json=TWO_MONTH_REQUEST)
    assert len(response.json()["timeline"]) == 3


def test_simulate_dates_are_sequential():
    response = client.post("/simulate", json=TWO_MONTH_REQUEST)
    dates = [entry["date"] for entry in response.json()["timeline"]]
    assert dates == ["2025-01-01", "2025-02-01", "2025-03-01"]


def test_simulate_net_worth_matches_cash_with_no_loads():
    request = {
        "framing": {"label": "test", "start_date": "2025-01-01", "end_date": "2025-02-01", "time_step": "monthly"},
        "loads": {"income": [], "expenses": [], "debts": [], "investments": []},
        "settings": {"starting_cash": 500.0},
    }
    response = client.post("/simulate", json=request)
    for entry in response.json()["timeline"]:
        assert entry["net_worth"] == pytest.approx(entry["cash"])
