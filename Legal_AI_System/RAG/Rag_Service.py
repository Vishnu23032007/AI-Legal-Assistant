import os
import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer


# ----------------------------------
# Base Directory (RAG Folder Path)
# ----------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INDEX_PATH = os.path.join(BASE_DIR, "legal_faiss_index.bin")
METADATA_PATH = os.path.join(BASE_DIR, "metadata.json")


# ----------------------------------
# Load Embedding Model
# ----------------------------------
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")


# ----------------------------------
# Load FAISS Index
# ----------------------------------
print("Loading FAISS index...")

try:
    index = faiss.read_index(INDEX_PATH)
    print("FAISS index loaded successfully")
except Exception as e:
    print("Error loading FAISS index:", e)
    index = None


# ----------------------------------
# Load Metadata
# ----------------------------------
print("Loading metadata...")

try:
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    print("Metadata loaded successfully")
except Exception as e:
    print("Error loading metadata:", e)
    metadata = []


# ----------------------------------
# Retrieve Relevant Laws
# ----------------------------------
def retrieve_laws(query, category, top_k=2):

    try:

        if index is None:
            print("FAISS index not loaded")
            return []

        # Convert query to embedding
        query_embedding = model.encode([query]).astype("float32")

        # Search FAISS
        distances, indices = index.search(query_embedding, top_k)

        results = []

        for idx in indices[0]:

            if idx >= len(metadata):
                continue

            item = metadata[idx]

            # Filter using Stage2 predicted category
            if item.get("stage2_category") == category:
                results.append({
                    "law": item.get("act"),
                    "section": item.get("section"),
                    "description": item.get("description")
                })

        return results

    except Exception as e:

        print("RAG Retrieval Error:", e)
        return []