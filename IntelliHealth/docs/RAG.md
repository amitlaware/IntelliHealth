# RAG Pipeline Architecture

## How RAG Works
The Retrieval-Augmented Generation (RAG) pipeline is designed to strictly limit the chatbot's healthcare facts to our verified, internal `health_topics.json` knowledge base to avoid any hallucinations or incorrect medical advice.

### Process Flow
1. **User Query**: The user asks a healthcare-related question.
2. **Embedding generation**: Using the `all-MiniLM-L6-v2` model from `sentence-transformers`, the query is transformed into a highly dense numerical vector.
3. **FAISS Similarity Search**: This query vector is queried against a local `FAISS` (Facebook AI Similarity Search) index containing embeddings of all our verified health topics.
4. **Relevant Context**: The most relevant document is extracted based on L2 distance if it meets our relevance threshold.
5. **Optional LLM / Deterministic Response**: If an LLM (Ollama) is enabled, it uses the document as strict context. Otherwise, it generates a deterministic structured response displaying the topic, description, and guidance.
6. **Safety Check**: The response is strictly appended with a medical disclaimer.

### Why RAG reduces hallucination
By forcing the generative process to condition its outputs strictly on the retrieved local document metadata, the RAG model essentially transforms the LLM from a "creative story-generator" into a "reading-comprehension bot". If the FAISS threshold fails to retrieve any document, the bot safely responds with an unknown clarification request.


## Knowledge-Base Driven vs Disease-Specific
The traditional approach involved if intent == 'headache': return x. This RAG architecture extracts the query's embeddings and performs an L2 similarity search to evaluate mathematical relevance to ANY topic present in health_topics.json. It will combine multiple topics if overlapping symptoms (e.g. fever + headache) are detected.
