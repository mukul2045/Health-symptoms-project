from fastapi.testclient import TestClient

from main import app
from symptom_mapper import parse_symptom_input, suggest_conditions


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_parse_symptom_aliases() -> None:
    parsed = parse_symptom_input("feverish, blocked nose, tiredness")
    assert parsed == {"fever", "congestion", "fatigue"}


def test_check_endpoint_returns_condition() -> None:
    response = client.post("/check", json={"symptoms": "fever, cough, fatigue", "top_k": 3})
    assert response.status_code == 200
    payload = response.json()
    assert payload["possible_conditions"]
    assert payload["possible_conditions"][0]["name"] in {"Influenza (Flu)", "COVID-19"}


def test_check_endpoint_rejects_empty_symptoms() -> None:
    response = client.post("/check", json={"symptoms": "   "})
    assert response.status_code == 400
    assert response.json()["detail"] == "Provide at least one symptom."


def test_direct_suggestion_empty_results() -> None:
    ranked = suggest_conditions({"unrelated symptom"})
    assert ranked == []
