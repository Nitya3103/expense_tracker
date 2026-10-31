def test_health(client):
    assert client.get("/health").status_code == 200


def test_create_and_read(client):
    created = client.post("/expenses", json={
        "title": "Chai",
        "amount": "40.00",
        "category": "food",
        "spent_on": "2026-10-31",
    })
    assert created.status_code == 201

    expense_id = created.json()["id"]
    fetched = client.get(f"/expenses/{expense_id}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "Chai"


def test_missing_expense_returns_404(client):
    assert client.get("/expenses/999999").status_code == 404


def test_negative_amount_rejected(client):
    response = client.post("/expenses", json={
        "title": "Galat",
        "amount": "-10.00",
        "category": "food",
        "spent_on": "2026-10-31",
    })
    assert response.status_code == 422


def test_delete_then_gone(client):
    created = client.post("/expenses", json={
        "title": "Delete me",
        "amount": "10.00",
        "category": "other",
        "spent_on": "2026-10-31",
    }).json()

    assert client.delete(f"/expenses/{created['id']}").status_code == 204
    assert client.get(f"/expenses/{created['id']}").status_code == 404
