import pytest
from services.chatbot_service import ChatbotService

@pytest.fixture(scope="module")
def chatbot():
    return ChatbotService()

def test_strong_single_topic(chatbot):
    chatbot.llm.enabled = False # Bypass LLM latency for precision test
    # A. Strong single-topic query
    res = chatbot.respond("What are the symptoms of chickenpox?")
    assert res["intent"] == "chickenpox"

def test_genuine_multi_topic(chatbot):
    chatbot.llm.enabled = False
    # B. Genuine multi-topic query
    res = chatbot.respond("I have a severe headache and high fever.")
    assert res["intent"] != "unknown"

def test_completely_unrelated(chatbot):
    # C. Completely unrelated query
    res = chatbot.respond("How do I repair my laptop?")
    assert res["intent"] == "unknown"

def test_low_confidence_query(chatbot):
    # D. Low-confidence query
    res = chatbot.respond("asdfghjkl")
    assert res["intent"] == "unknown"

def test_unsupported_topic(chatbot):
    # F. Unsupported topic
    res = chatbot.respond("I have Ebola")
    # Even if it retrieves something weakly, relative margin or absolute threshold should reject it
    # Assuming ebola is not in the knowledge base, it should be unknown
    # or at worst a very generic fallback if it matched 'fever' strongly.
    # It should not claim to have specific knowledge about Ebola.
    assert "ebola" not in res["response"].lower()
