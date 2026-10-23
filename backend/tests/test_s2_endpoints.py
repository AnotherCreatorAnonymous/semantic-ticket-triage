import pytest
from fastapi.testclient import TestClient
from main import app
from core import queue_store
from api.schemas import RolUsuario

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup_queue():
    """Clean queue before and after each test."""
    queue_store.limpiar()
    yield
    queue_store.limpiar()

def test_health_endpoint():
    """GET /api/health returns status and model state."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "model" in data
    assert data["model"] in ["loaded", "heuristic_fallback"]

def test_delete_ticket_success():
    """DELETE /api/queue/{id} removes ticket."""
    # Add a ticket
    response = client.post(
        "/api/triage",
        json={
            "titulo": "Test ticket",
            "texto": "Testing delete functionality",
            "rol_usuario": "Empleado General"
        }
    )
    assert response.status_code == 200
    ticket_id = response.json()["id"]
    
    # Verify it's in queue
    queue_response = client.get("/api/queue")
    assert queue_response.json()["total"] == 1
    
    # Delete it
    delete_response = client.delete(f"/api/queue/{ticket_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "deleted"
    
    # Verify it's gone
    queue_response = client.get("/api/queue")
    assert queue_response.json()["total"] == 0

def test_delete_ticket_not_found():
    """DELETE /api/queue/{id} returns 404 for non-existent ticket."""
    response = client.delete("/api/queue/nonexistent-id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_delete_multiple_tickets():
    """DELETE removes specific ticket, not all."""
    # Add 3 tickets
    ids = []
    for i in range(3):
        response = client.post(
            "/api/triage",
            json={
                "titulo": f"Ticket {i}",
                "texto": f"Description {i}",
                "rol_usuario": "Empleado General"
            }
        )
        ids.append(response.json()["id"])
    
    assert client.get("/api/queue").json()["total"] == 3
    
    # Delete middle ticket
    delete_response = client.delete(f"/api/queue/{ids[1]}")
    assert delete_response.status_code == 200
    
    # Verify only 2 remain
    queue_response = client.get("/api/queue")
    assert queue_response.json()["total"] == 2
    remaining_ids = [t["id"] for t in queue_response.json()["tickets"]]
    assert ids[1] not in remaining_ids
    assert ids[0] in remaining_ids
    assert ids[2] in remaining_ids
