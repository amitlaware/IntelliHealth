# -*- coding: utf-8 -*-
import json
from pathlib import Path

from .nlp_service import NLPService
from .safety_service import SafetyService
from .llm_service import LLMService
from .text_normalizer import TextNormalizer
from rag.rag_service import RAGService

class ChatbotService:
    def __init__(self):
        self.nlp = NLPService()
        self.safety = SafetyService()
        self.llm = LLMService()
        self.rag = RAGService()
        self.normalizer = TextNormalizer()
        
        path = Path(__file__).resolve().parent.parent / "data" / "health_topics.json"
        self.topics = json.loads(path.read_text(encoding="utf-8"))

    def respond(self, message):
        # 1. General Text Normalization
        normalized_message = self.normalizer.normalize(message)

        # 2. Emergency Detection bypasses normal RAG
        if self.safety.is_emergency(normalized_message):
            return {
                "intent": "emergency", 
                "urgent": True, 
                "response": (
                    "This may involve symptoms that require urgent medical attention. "
                    "Please contact a qualified healthcare professional or your local emergency "
                    "service immediately. In India, you can contact 112 for emergency assistance. "
                    "This chatbot cannot assess or diagnose emergencies."
                )
            }

        # 3. NLP Intent Classification (as a secondary signal)
        nlp_intent, nlp_confidence = self.nlp.predict(normalized_message)
        nlp_confidence = float(nlp_confidence)

        # 4. Semantic RAG Retrieval (MAIN RELEVANCE MECHANISM)
        # We retrieve with a LOOSE threshold to capture edge cases (typos, short natural language queries).
        # We then filter these candidates using a TWO-SIGNAL decision logic.
        loose_rag_results = self.rag.retrieve(normalized_message, threshold=self.rag.RAG_DISTANCE_THRESHOLD_LOOSE)
        
        rag_results = []
        for res in loose_rag_results:
            dist = res["distance"]
            topic_intent = res["document"]["intent"]
            
            # SIGNAL 1: Strong Semantic Relevance (distance < STRICT threshold)
            if dist <= self.rag.RAG_DISTANCE_THRESHOLD:
                rag_results.append(res)
            # SIGNAL 2: Weak Semantic Relevance + Strong NLP Correlation
            elif dist <= self.rag.RAG_DISTANCE_THRESHOLD_LOOSE and nlp_confidence >= 0.35 and nlp_intent == topic_intent:
                rag_results.append(res)
                
        # 5. Unknown / Out-of-Domain Protection
        if not rag_results:
            # Only trust general intents if confidence is reasonably high
            if nlp_confidence > 0.4:
                if nlp_intent == "greeting":
                    response = "Hello! I can provide general information about common health topics. What would you like to know?"
                    return {"intent": "greeting", "confidence": nlp_confidence, "urgent": False, "response": response}
                elif nlp_intent == "thanks":
                    response = "You're welcome. Remember that this chatbot provides general information and is not a substitute for professional medical advice."
                    return {"intent": "thanks", "confidence": nlp_confidence, "urgent": False, "response": response}
                elif nlp_intent == "goodbye":
                    response = "Take care. If you have concerning or severe symptoms, seek professional medical assistance."
                    return {"intent": "goodbye", "confidence": nlp_confidence, "urgent": False, "response": response}
            
            # If no RAG results and not a high-confidence greeting, it's unknown/out-of-domain
            return {
                "intent": "unknown", 
                "confidence": nlp_confidence, 
                "urgent": False, 
                "response": (
                    "I couldn't confidently identify a healthcare topic in your question, or your query may be outside my medical knowledge base. "
                    "Please describe your symptoms or question in more detail. If you have severe or concerning symptoms, please consult a qualified healthcare professional."
                )
            }

        # 6. Multi-topic / Response Generation
        rag_contexts = []
        intents_found = []
        
        for res in rag_results:
            rag_contexts.append(res["document"]["content"])
            intents_found.append(res["document"]["intent"])

        combined_rag_context = "\n\n---\n\n".join(rag_contexts)
        combined_rag_context = "\n\n---\n\n".join(rag_contexts)
        
        # 7. LLM integration
        # Pass the original natural language query to the LLM along with the combined contexts.
        llm_resp = self.llm.generate(message, combined_rag_context)
        if llm_resp:
            final_response = llm_resp
        else:
            final_response = "The AI response service is temporarily unavailable. Please try again later or consult a qualified healthcare professional for medical concerns."

        # Use the highest confidence intent for tracking (first RAG result or NLP fallback)
        primary_intent = intents_found[0] if intents_found else nlp_intent
        
        # Approximate confidence using distance (0 distance = 1.0 confidence)
        if rag_results:
            best_dist = rag_results[0]["distance"]
            computed_confidence = max(0.1, 1.0 - (best_dist / 2.0))
        else:
            computed_confidence = nlp_confidence

        return {
            "intent": primary_intent, 
            "confidence": round(computed_confidence, 3), 
            "urgent": False, 
            "response": final_response
        }
