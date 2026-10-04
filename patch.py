import sys

content = open('services/chatbot_service.py', 'r', encoding='utf-8').read()

if 'from rag.rag_service import RAGService' not in content:
    content = content.replace('from .llm_service import LLMService', 'from .llm_service import LLMService\nfrom rag.rag_service import RAGService')

if 'self.rag = RAGService()' not in content:
    content = content.replace('self.llm = LLMService()', 'self.llm = LLMService()\n\n        self.rag = RAGService()')

old_logic = '''        topic = self._find_topic(intent, message)

        if topic:

            response = self._format_topic(topic)'''

new_logic = '''        topic = self._find_topic(intent, message)
        
        rag_context = ""
        rag_results = self.rag.retrieve(message)
        if rag_results:
            rag_doc = rag_results[0]["document"]
            rag_context = rag_doc["content"]
            response = f"Based on our healthcare knowledge base:\\n\\n{rag_context}\\n\\nDisclaimer: This information is educational only and is not a medical diagnosis."
        elif topic:
            response = self._format_topic(topic)'''

content = content.replace(old_logic, new_logic)

old_llm_logic = 'llm_resp = self.llm.generate(message, response)'
new_llm_logic = 'llm_resp = self.llm.generate(message, rag_context if rag_context else response)'
content = content.replace(old_llm_logic, new_llm_logic)

open('services/chatbot_service.py', 'w', encoding='utf-8').write(content)
print("Patched.")
