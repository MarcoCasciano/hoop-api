# tests/test_api.py
import pytest


BREW_PAYLOAD = {
    "coffee": "Ethiopia Yirgacheffe",
    "dose": 18.0,
    "ratio": 16.0,
    "temperature": 94,
    "grind": "medium",
}


# --- Helper ---

def create_brew(client, payload=None):
    """Crea una brew e ritorna la risposta."""
    return client.post("/brews", json=payload or BREW_PAYLOAD)


# --- Health ---

def test_health(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# --- POST /brews ---

def test_create_brew_returns_id(client):
    r = create_brew(client)
    assert r.status_code == 201
    assert "id" in r.json()


def test_create_brew_calculates_water(client):
    r = create_brew(client, {**BREW_PAYLOAD, "dose": 18.0, "ratio": 16.0})
    brew_id = r.json()["id"]
    brew = client.get(f"/brews/{brew_id}").json()
    assert brew["water"] == 288.0


def test_create_brew_strips_whitespace(client):
    r = create_brew(client, {**BREW_PAYLOAD, "coffee": "  Kenya  ", "notes": "  dolce  "})
    brew_id = r.json()["id"]
    brew = client.get(f"/brews/{brew_id}").json()
    assert brew["coffee"] == "Kenya"
    assert brew["notes"] == "dolce"


def test_create_brew_missing_required_field(client):
    r = client.post("/brews", json={"dose": 18.0})
    assert r.status_code == 422


def test_create_brew_invalid_grind(client):
    r = create_brew(client, {**BREW_PAYLOAD, "grind": "espresso"})
    assert r.status_code == 422


def test_create_brew_invalid_ratio_too_low(client):
    r = create_brew(client, {**BREW_PAYLOAD, "ratio": 5.0})
    assert r.status_code == 422


def test_create_brew_invalid_temperature(client):
    r = create_brew(client, {**BREW_PAYLOAD, "temperature": 110})
    assert r.status_code == 422


# --- GET /brews ---

def test_list_brews_empty(client):
    r = client.get("/brews")
    assert r.status_code == 200
    assert r.json() == []


def test_list_brews_returns_all(client):
    create_brew(client)
    create_brew(client)
    r = client.get("/brews")
    assert len(r.json()) == 2


def test_list_brews_limit(client):
    for _ in range(5):
        create_brew(client)
    r = client.get("/brews?limit=3")
    assert len(r.json()) == 3


def test_list_brews_ordered_by_most_recent(client):
    create_brew(client, {**BREW_PAYLOAD, "coffee": "Prima"})
    create_brew(client, {**BREW_PAYLOAD, "coffee": "Seconda"})
    brews = client.get("/brews").json()
    assert brews[0]["coffee"] == "Seconda"


# --- GET /brews/{id} ---

def test_get_brew_ok(client):
    brew_id = create_brew(client).json()["id"]
    r = client.get(f"/brews/{brew_id}")
    assert r.status_code == 200
    assert r.json()["coffee"] == BREW_PAYLOAD["coffee"]


def test_get_brew_not_found(client):
    r = client.get("/brews/99999")
    assert r.status_code == 404


# --- PATCH /brews/{id} ---

def test_update_brew_field(client):
    brew_id = create_brew(client).json()["id"]
    r = client.patch(f"/brews/{brew_id}", json={"coffee": "Guatemala"})
    assert r.status_code == 200
    assert r.json()["coffee"] == "Guatemala"


def test_update_brew_recalculates_water(client):
    brew_id = create_brew(client, {**BREW_PAYLOAD, "dose": 18.0, "ratio": 16.0}).json()["id"]
    r = client.patch(f"/brews/{brew_id}", json={"dose": 20.0})
    assert r.status_code == 200
    assert r.json()["water"] == round(20.0 * 16.0, 1)


def test_update_brew_not_found(client):
    r = client.patch("/brews/99999", json={"coffee": "X"})
    assert r.status_code == 404


# --- DELETE /brews/{id} ---

def test_delete_brew_ok(client):
    brew_id = create_brew(client).json()["id"]
    r = client.delete(f"/brews/{brew_id}")
    assert r.status_code == 204
    assert client.get(f"/brews/{brew_id}").status_code == 404


def test_delete_brew_not_found(client):
    r = client.delete("/brews/99999")
    assert r.status_code == 404


# --- GET /brews/{id}/tips ---

def test_tips_brew_not_found(client):
    r = client.get("/brews/99999/tips")
    assert r.status_code == 404


def test_tips_no_rating(client):
    brew_id = create_brew(client).json()["id"]
    r = client.get(f"/brews/{brew_id}/tips")
    assert r.status_code == 200
    assert r.json()["brew_id"] == brew_id
    assert "rating" in r.json()["tips"][0]


def test_tips_with_rating(client):
    brew_id = create_brew(client, {**BREW_PAYLOAD, "rating": 4}).json()["id"]
    tips = client.get(f"/brews/{brew_id}/tips").json()["tips"]
    assert len(tips) == 2
