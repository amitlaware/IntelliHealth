from services.nlp_service import NLPService
def test_greeting():
    intent, confidence = NLPService().predict("hello")
    assert intent == "greeting"
