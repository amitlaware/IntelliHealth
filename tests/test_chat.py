from services.chatbot_service import ChatbotService
def test_chat():
    assert "response" in ChatbotService().respond("I have a headache")
