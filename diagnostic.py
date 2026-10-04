import sys
import json
import logging
from pathlib import Path
from services.text_normalizer import TextNormalizer
from services.nlp_service import NLPService
from rag.rag_service import RAGService
from services.llm_service import LLMService

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def run_diagnostic(query):
    print("==================================================")
    print(f"DIAGNOSTIC TRACE FOR QUERY: '{query}'")
    print("==================================================")

    # 1. TEXT NORMALIZATION
    normalizer = TextNormalizer()
    normalized_query = normalizer.normalize(query)
    print(f"[1] Normalized Query: '{normalized_query}'")

    # 2. NLP CLASSIFICATION
    nlp = NLPService()
    nlp_intent, nlp_confidence = nlp.predict(normalized_query)
    print(f"[2] NLP Result: intent='{nlp_intent}', confidence={nlp_confidence:.4f}")

    # 3. KNOWLEDGE BASE
    kb_path = Path("data/health_topics.json")
    topics = json.loads(kb_path.read_text(encoding="utf-8"))
    print(f"[3] Knowledge Base: loaded {len(topics)} topics.")

    # 4. RAG RETRIEVAL (Independent)
    rag = RAGService()
    print(f"[4] FAISS Index: {rag.index.ntotal} vectors loaded.")
    
    # Try loose retrieval
    loose_results = rag.retrieve(normalized_query, threshold=rag.RAG_DISTANCE_THRESHOLD_LOOSE)
    print(f"[4] FAISS Retrieval (LOOSE threshold {rag.RAG_DISTANCE_THRESHOLD_LOOSE}): {len(loose_results)} candidates")
    
    for i, res in enumerate(loose_results):
        dist = res["distance"]
        doc = res["document"]
        print(f"    Candidate {i+1}: intent='{doc.get('intent')}', dist={dist:.4f}")

    # 5. RAG RELEVANCE FILTERING
    rag_results = []
    for res in loose_results:
        dist = res["distance"]
        topic_intent = res["document"]["intent"]
        
        if dist <= rag.RAG_DISTANCE_THRESHOLD:
            rag_results.append(res)
            print(f"[5] Candidate '{topic_intent}' ACCEPTED (Strong RAG: {dist:.4f} <= {rag.RAG_DISTANCE_THRESHOLD})")
        elif dist <= rag.RAG_DISTANCE_THRESHOLD_LOOSE and float(nlp_confidence) >= 0.35 and nlp_intent == topic_intent:
            rag_results.append(res)
            print(f"[5] Candidate '{topic_intent}' ACCEPTED (Weak RAG + Strong NLP)")
        else:
            print(f"[5] Candidate '{topic_intent}' REJECTED")

    print(f"[5] Final Relevant Contexts: {len(rag_results)}")

    # 6. UNKNOWN DECISION
    if not rag_results:
        print("[6] UNKNOWN DECISION: Query rejected. No relevant contexts found.")
    else:
        print("[6] UNKNOWN DECISION: Passed.")

    # 7. LLM INVOCATION
    llm = LLMService()
    print(f"[7] LLM Configuration: Enabled={llm.enabled}, Model='{llm.model}'")
    
    if llm.enabled and rag_results:
        combined_context = "\n\n".join([r["document"]["content"] for r in rag_results])
        print(f"[7] Invoking LLM with context length {len(combined_context)} characters...")
        llm_response = llm.generate(query, combined_context)
        print(f"[7] LLM Response: {llm_response}")

if __name__ == "__main__":
    test_query = "I have a terrible head ache and can't focus"
    run_diagnostic(test_query)
