import pytest
from fastapi.testclient import TestClient
from fitness_studio_api import app, init_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db():
    conn = init_db()
    yield conn
    conn.close()

def test_get_classes(client):
    response = client.get("/classes")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert all(key in response.json()[0] for key in ["id", "name", "datetime", "instructor", "available_slots"])

def test_book_class(client, db):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM classes LIMIT 1")
    class_id = cursor.fetchone()[0]
    
    booking_data = {
        "class_id": class_id,
        "client_name": "John Doe",
        "client_email": "john@example.com"
    }
    response = client.post("/book", json=booking_data)
    assert response.status_code == 200
    assert response.json()["client_email"] == "john@example.com"

def test_book_class_no_slots(client, db):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM classes LIMIT 1")
    class_id = cursor.fetchone()[0]
    cursor.execute("UPDATE classes SET available_slots = 0 WHERE id = ?", (class_id,))
    db.commit()
    
    booking_data = {
        "class_id": class_id,
        "client_name": "John Doe",
        "client_email": "john@example.com"
    }
    response = client.post("/book", json=booking_data)
    assert response.status_code == 400
    assert "No available slots" in response.json()["detail"]

def test_get_bookings(client):
    response = client.get("/bookings?client_email=john@example.com")
    assert response.status_code == 200
    assert isinstance(response.json(), list)