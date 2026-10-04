import pytest
from unittest.mock import patch, MagicMock
from services.chatbot_service import ChatbotService
from services.llm_service import LLMService

@pytest.fixture
def chatbot():
    return ChatbotService()

def test_llm_disabled_fallback(chatbot):
    # LLM is disabled by default in the test environment (unless patched)
    chatbot.llm.enabled = False
    
    response = chatbot.respond("I have a headache")
    
    # Should safely fall back to technical unavailability message
    assert "temporarily unavailable" in response["response"]

@patch('services.llm_service.requests.post')
def test_llm_enabled_valid_context(mock_post, chatbot):
    chatbot.llm.enabled = True
    
    # Mock Ollama response
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "This is a natural LLM response about headaches."}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    response = chatbot.respond("I have a headache")
    
    # Verify LLM was actually called
    mock_post.assert_called_once()
    
    # Verify response matches LLM output
    assert response["response"] == "This is a natural LLM response about headaches."

@patch('services.llm_service.requests.post')
def test_ollama_unavailable_fallback(mock_post, chatbot):
    chatbot.llm.enabled = True
    
    # Simulate connection error
    import requests
    mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")
    
    response = chatbot.respond("I have a headache")
    
    # Should safely fall back to technical unavailability message
    assert "temporarily unavailable" in response["response"]

def test_rag_unavailable(chatbot):
    chatbot.llm.enabled = True
    # Totally unrelated query should hit UNKNOWN BEFORE the LLM gets called
    # (Since LLM is only called if rag_results exist)
    response = chatbot.respond("How do I bake a chocolate cake?")
    
    assert response["intent"] == "unknown"
    assert "couldn't confidently identify a healthcare topic" in response["response"]

def test_emergency_query(chatbot):
    chatbot.llm.enabled = True
    
    response = chatbot.respond("I think I am having a heart attack with severe chest pain")
    
    # Should trigger safety emergency layer BEFORE LLM
    assert response["intent"] == "emergency"
    assert response["urgent"] is True
    assert "urgent medical attention" in response["response"]

@patch('services.llm_service.requests.post')
def test_multiple_contexts(mock_post, chatbot):
    chatbot.llm.enabled = True
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "You mentioned both brain fog and headaches."}
    mock_post.return_value = mock_response
    
    response = chatbot.respond("I have a pounding headache and bad brain fog")
    
    # Verify LLM was called
    mock_post.assert_called_once()
    
    # Extract the payload that was sent to the LLM to verify multiple contexts were passed
    payload = mock_post.call_args[1]['json']
    assert "Topic: Headache" in payload['prompt']
    assert "Topic: Brain Fog" in payload['prompt']
    
    assert response["response"] == "You mentioned both brain fog and headaches."

@patch('services.llm_service.requests.post')
def test_same_context_different_queries(mock_post, chatbot):
    chatbot.llm.enabled = True
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "Mocked response"}
    mock_post.return_value = mock_response
    
    # Query 1
    chatbot.respond("What is a headache?")
    payload1 = mock_post.call_args[1]['json']
    assert "USER:\nWhat is a headache?" in payload1['prompt']
    
    # Query 2
    chatbot.respond("How can I avoid getting a headache?")
    payload2 = mock_post.call_args[1]['json']
    assert "USER:\nHow can I avoid getting a headache?" in payload2['prompt']
    
    # The RAG context retrieved should be identical (both hit headache topic)
    # but the original user queries injected into the prompt are different!

