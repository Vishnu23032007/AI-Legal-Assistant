import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load JSON
with open("data_updated.json", "r", encoding="utf-8") as f:
    data = json.load(f)

documents = []
metadata = []

# Convert JSON to text documents
for item in data:
    text = f"""
    Category: {item['stage2_category']}
    Act: {item['act']}
    Section: {item['section']}
    Description: {item.get('description','')}
    """
    
    documents.append(text)
    metadata.append(item)

# Generate embeddings
embeddings = model.encode(documents)

# Convert to numpy
embeddings = np.array(embeddings).astype("float32")

# Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)

# Add vectors
index.add(embeddings)

# Save FAISS index
faiss.write_index(index, "legal_faiss_index.bin")

# Save metadata
with open("metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=4)

print("FAISS index created successfully!")