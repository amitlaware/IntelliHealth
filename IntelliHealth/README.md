# AI Healthcare Bot

## Overview
An upgraded AI Healthcare Bot designed to act as a Hybrid AI Healthcare Assistant. The chatbot provides general educational health information and detects emergency situations effectively.

## Objectives
- Deliver accurate, trusted healthcare knowledge.
- Avoid unsafe medical advice, diagnosis, or prescription suggestions.
- Automatically classify user intents using NLP.
- Detect emergencies and prompt users to seek immediate medical help.

## Features
- Natural Language Intent Classification (TF-IDF + Logistic Regression).
- Confidence Thresholding to prevent hallucinating responses for unknown queries.
- Safety Layer with strict pattern matching for emergency situations.
- Extensible API for future RAG (Retrieval-Augmented Generation) and local LLM integration (Ollama).

## Architecture
```
User -> Flask Web App -> Safety Check -> NLP Intent -> Confidence Check -> LLM Fallback -> Response
```

## Setup & Running
1. `python -m venv venv`
2. `venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. `python app.py`

## Testing
Run tests using: `pytest`

## Limitations
- This bot does NOT provide professional medical diagnosis.
- Designed for educational purposes only.
- In-memory mock database implemented; robust SQLAlchemy migration is scoped for future phases.

## How RAG Works
Check out the detailed RAG architecture in docs/RAG.md.


## Knowledge-Base Driven Architecture
This chatbot now utilizes a generalized architecture. Instead of hardcoding logic for specific diseases, it dynamically ingests data/health_topics.json. You can add new diseases, and the FAISS RAG semantic retrieval will automatically support them without any Python code modifications!
