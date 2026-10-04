from services.nlp_service import NLPService
if __name__ == "__main__":
    model = NLPService()
    while True:
        text = input("Query (or quit): ").strip()
        if text.lower() == "quit": break
        print(model.predict(text))
