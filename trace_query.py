import logging
from dotenv import load_dotenv
load_dotenv()
from services.chatbot_service import ChatbotService

logging.basicConfig(level=logging.DEBUG)

def trace_query():
    chatbot = ChatbotService()
    query = "What is dehydration, and what are the common signs that someone may be dehydrated?"
    print(f"QUERY: {query}")
    res = chatbot.respond(query)
    print(f"RESULT: {res}")

if __name__ == "__main__":
    trace_query()
