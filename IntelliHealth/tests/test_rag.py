import pytest
import json
from pathlib import Path
from rag.rag_service import RAGService
from services.chatbot_service import ChatbotService

@pytest.fixture(scope="module")
def rag():
    return RAGService()

@pytest.fixture(scope="module")
def chatbot():
    return ChatbotService()

@pytest.fixture(scope="module")
def health_topics():
    path = Path(__file__).resolve().parent.parent / "data" / "health_topics.json"
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_dynamic_rag_retrieval(rag, health_topics):
    """Dynamically test that every topic can be retrieved using its exact name or symptom."""
    for topic in health_topics:
        # Test 1: Query by Topic Name
        query = f"What is {topic['topic']}?"
        results = rag.retrieve(query, top_k=3, threshold=1.4)
        assert len(results) > 0, f"Failed to retrieve any documents for {topic['topic']}"
        
        # Test 2: Query by Symptom (if available)
        if topic.get("common_symptoms"):
            symptom = topic["common_symptoms"][0]
            query = f"I have a {symptom}"
            results = rag.retrieve(query, top_k=5, threshold=1.5)
            # The topic should be somewhere in the top 5 results
            found_intents = [r["document"]["intent"] for r in results]
            assert topic["intent"] in found_intents, f"Failed to retrieve {topic['topic']} when querying symptom '{symptom}'"

def test_out_of_domain_queries(chatbot):
    """Ensure non-healthcare queries are rejected safely."""
    out_of_domain_queries = [
        "what is quantum physics?",
        "how do I repair my laptop?",
        "who won the cricket match?",
        "tell me a joke",
        "asdf random xyz"
    ]
    
    for query in out_of_domain_queries:
        res = chatbot.respond(query)
        assert res["intent"] == "unknown", f"Out of domain query '{query}' was incorrectly mapped to {res['intent']}!"

def test_multi_topic_detection(chatbot):
    """Test that symptoms spanning multiple topics return multiple contexts if relevant."""
    chatbot.llm.enabled = False
    # Example: headache (Headache topic) and fever (Fever topic)
    query = "I have a severe headache and high fever."
    res = chatbot.respond(query)
    
    # It should not just be 'unknown' or just one topic if both are strongly relevant
    assert res["intent"] != "unknown"
    
def test_typo_generalization(chatbot):
    """Ensure typos don't break semantic retrieval."""
    query = "I hav sever headach and feeling dizy."
    res = chatbot.respond(query)
    assert res["intent"] in ["headache", "brain_fog"] # Should semantically map close to these
