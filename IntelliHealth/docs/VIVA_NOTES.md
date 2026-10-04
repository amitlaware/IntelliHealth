# Viva Notes - AI Healthcare Bot

## 1. Generalization
The architecture heavily emphasizes generalization. Rather than hard-coding conditional logic for specific diseases (e.g., `if intent == 'fever'`), the system depends on a centralized `health_topics.json` knowledge base. When a user inputs a query:
- Text is normalized (removing punctuation, lowercasing, whitespace).
- `sentence-transformers` creates mathematical vector embeddings.
- FAISS retrieves the closest matching healthcare topics based on semantic similarity.
- Any topic below an L2 distance threshold of 1.4 is deemed highly relevant.
This means an admin can add 100 new diseases to the knowledge base without writing a single line of new Python code.

## 2. Multi-Topic Detection
If a user submits a query encompassing multiple distinct health domains (e.g., "I have a severe headache and a high fever"), FAISS will mathematically align the embeddings closer to both "Headache" and "Fever". The system is configured to retrieve the top-3 results. It then aggregates their distinct guidelines into a single, cohesive informative response.

## 3. Unknown Query Protection
If someone asks "Who won the cricket match?", FAISS will compute the L2 distance between the sports query and the healthcare topics. The distance will far exceed our strict `1.4` threshold, resulting in 0 retrieved documents. Since the NLP ML classifier will also output a very low confidence score, the chatbot will safely bypass generation and inform the user that it does not recognize the query as a supported health topic.

## 4. Current Capacity
The system currently natively supports all healthcare conditions defined within `data/health_topics.json` and dynamically scales as more objects are added to the JSON array. All tests are generated procedurally by iterating over the knowledge base itself.
