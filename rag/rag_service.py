import json
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class RAGService:
    def __init__(self):
        self.data_dir = Path(__file__).resolve().parent.parent / "data"
        self.index_dir = self.data_dir / "faiss_index"
        self.index_path = self.index_dir / "index.faiss"
        self.docs_path = self.index_dir / "documents.json"
        
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.documents = []
        
        if self.index_path.exists() and self.docs_path.exists():
            self._load_index()
        else:
            self.rebuild_index()
            
    def _load_index(self):
        self.index = faiss.read_index(str(self.index_path))
        with open(self.docs_path, 'r', encoding='utf-8') as f:
            self.documents = json.load(f)

    def rebuild_index(self):
        self.index_dir.mkdir(exist_ok=True)
        topics_file = self.data_dir / "health_topics.json"
        
        with open(topics_file, 'r', encoding='utf-8') as f:
            topics = json.load(f)
            
        self.documents = []
        texts_to_embed = []
        
        for topic in topics:
            content = f"Topic: {topic.get('topic')}\n"
            if topic.get('aliases'):
                content += f"Aliases: {', '.join(topic.get('aliases'))}\n"
            if topic.get('keywords'):
                content += f"Keywords: {', '.join(topic.get('keywords'))}\n"
            content += f"Description: {topic.get('description')}\n"
            content += f"Symptoms: {', '.join(topic.get('common_symptoms', []))}\n"
            content += f"Guidance: {', '.join(topic.get('general_guidance', []))}\n"
            content += f"Seek Help: {topic.get('seek_medical_help')}"
            
            doc = {
                "intent": topic.get("intent"),
                "topic": topic.get("topic"),
                "content": content
            }
            self.documents.append(doc)
            texts_to_embed.append(content)
            
        if texts_to_embed:
            embeddings = self.model.encode(texts_to_embed, convert_to_numpy=True)
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings)
            
            faiss.write_index(self.index, str(self.index_path))
            with open(self.docs_path, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, indent=4)

    # Configuration parameters for retrieval precision
    RAG_TOP_K = 3
    RAG_DISTANCE_THRESHOLD = 1.4 # Absolute upper bound for L2 distance (strong match)
    RAG_DISTANCE_THRESHOLD_LOOSE = 1.65 # Loose upper bound for L2 distance (weak match)
    RAG_RELATIVE_MARGIN = 0.25   # Maximum distance allowed from the strongest match

    def retrieve(self, query, top_k=None, threshold=None, relative_margin=None):
        if not self.index or not self.documents:
            return []
            
        k = top_k if top_k is not None else self.RAG_TOP_K
        abs_threshold = threshold if threshold is not None else self.RAG_DISTANCE_THRESHOLD
        margin = relative_margin if relative_margin is not None else self.RAG_RELATIVE_MARGIN
            
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, k)
        
        candidates = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1 and dist < abs_threshold:
                candidates.append({
                    "document": self.documents[idx],
                    "distance": float(dist)
                })
                
        if not candidates:
            return []
            
        # Relative filtering
        best_distance = candidates[0]["distance"]
        final_results = []
        for cand in candidates:
            if cand["distance"] <= best_distance + margin:
                final_results.append(cand)
                
        return final_results

if __name__ == "__main__":
    print("Rebuilding RAG index...")
    rag = RAGService()
    rag.rebuild_index()
    print("Index rebuilt successfully.")
