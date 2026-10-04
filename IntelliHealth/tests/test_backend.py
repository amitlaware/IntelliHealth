import pytest
from app import app, db
from models.models import User, Conversation, Message
import json

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_auth_and_chat(client):
    # 1. Register User A
    res = client.post("/api/register", json={"username": "usera", "email": "a@a.com", "password": "pwd"})
    assert res.status_code == 201
    
    # 2. Register User B
    res = client.post("/api/register", json={"username": "userb", "email": "b@b.com", "password": "pwd"})
    assert res.status_code == 201
    
    # 3. Login User A
    res = client.post("/api/login", json={"username": "usera", "password": "pwd"})
    assert res.status_code == 200
    
    # 4. Create Conversation for User A
    res = client.post("/api/conversations")
    assert res.status_code == 201
    conv_a_id = res.json["id"]
    
    # 5. Chat as User A
    res = client.post("/api/chat", json={"message": "What are the symptoms of chickenpox?", "conversation_id": conv_a_id})
    assert res.status_code == 200
    assert res.json["intent"] == "chickenpox"
    
    res = client.post("/api/chat", json={"message": "How to deal with brain fog?", "conversation_id": conv_a_id})
    assert res.status_code == 200
    assert res.json["intent"] == "brain_fog"
    
    res = client.post("/api/chat", json={"message": "I have severe chest pain and cannot breathe", "conversation_id": conv_a_id})
    assert res.status_code == 200
    assert res.json["urgent"] == True
    
    # 6. Check History for User A
    res = client.get(f"/api/history?conversation_id={conv_a_id}")
    assert res.status_code == 200
    assert len(res.json) == 6 # 3 user messages + 3 bot messages
    
    # 7. Login User B
    res = client.get("/logout")
    res = client.post("/api/login", json={"username": "userb", "password": "pwd"})
    assert res.status_code == 200
    
    # 8. Attempt to access User A's conversation as User B
    res = client.get(f"/api/history?conversation_id={conv_a_id}")
    assert res.status_code == 404 # Isolated
    
    res = client.delete(f"/api/conversations/{conv_a_id}")
    assert res.status_code == 404 # Isolated
