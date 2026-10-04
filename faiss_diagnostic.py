import json
import faiss
from pathlib import Path
from sentence_transformers import SentenceTransformer

def diagnose():
    print("==================================================")
    print("FAISS DIAGNOSTIC")
    
    data_dir = Path("data")
    index_path = data_dir / "faiss_index" / "index.faiss"
    docs_path = data_dir / "faiss_index" / "documents.json"
    
    if not index_path.exists() or not docs_path.exists():
        print("FAISS index not found.")
        return
        
    index = faiss.read_index(str(index_path))
    with open(docs_path, 'r', encoding='utf-8') as f:
        docs = json.load(f)
        
    print(f"Total FAISS vectors: {index.ntotal}")
    print(f"Total metadata records: {len(docs)}")
    
    dehydration_exists = any("dehydrat" in str(d).lower() for d in docs)
    print(f"Dehydration exists in metadata: {dehydration_exists}")
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    queries = ["dehydration", "What is dehydration?", "What are common symptoms of dehydration?"]
    
    for q in queries:
        print(f"\nQuery: '{q}'")
        emb = model.encode([q], convert_to_numpy=True)
        distances, indices = index.search(emb, 5)
        for d, i in zip(distances[0], indices[0]):
            if i != -1:
                print(f"  Distance: {d:.4f} -> Intent: {docs[i]['intent']}")

if __name__ == "__main__":
    diagnose()
