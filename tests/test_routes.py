import json
from main import app


def test_homepage_loads():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200

def test_chat_route():
    client = app.test_client()
    response = client.post("/chat", json={"message": "weather in Oxford"})
    assert response.status_code == 200
    assert "response" in response.get_json()