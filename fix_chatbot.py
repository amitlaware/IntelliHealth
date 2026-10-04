import sys, re

content = open('services/chatbot_service.py', 'r', encoding='utf-8').read()

pattern = re.compile(r'topic = self._find_topic\(intent, message\).*?return \{\"intent\": intent', re.DOTALL)
new_logic = '''topic = self._find_topic(intent, message)
        
        rag_context = ""
        rag_results = self.rag.retrieve(message)
        if rag_results:
            rag_doc = rag_results[0]["document"]
            rag_context = rag_doc["content"]
            response = f"Based on our healthcare knowledge base:\\n\\n{rag_context}\\n\\nDisclaimer: This information is educational only and is not a medical diagnosis."
        elif topic:
            response = self._format_topic(topic)
        elif intent == "greeting":
            response = "Hello! I can provide general information about common health topics. What would you like to know?"
        elif intent == "thanks":
            response = "You're welcome. Remember that this chatbot provides general information and is not a substitute for professional medical advice."
        elif intent == "goodbye":
            response = "Take care. If you have concerning or severe symptoms, seek professional medical assistance."
        else:
            response = ("I couldn't confidently match your question. Please describe your symptoms "
                        "or question in more detail. If symptoms are severe or concerning, contact a qualified healthcare professional.")
                        
        llm_resp = self.llm.generate(message, rag_context if rag_context else response)
        if llm_resp:
            response = llm_resp

        return {"intent": intent'''

content = re.sub(pattern, new_logic, content)
open('services/chatbot_service.py', 'w', encoding='utf-8').write(content)
print("Fixed chatbot_service.py")
