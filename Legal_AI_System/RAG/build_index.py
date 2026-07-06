import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

BASE_PATH = "legal_data"
SAVE_PATH = "rag_index"

print("🔄 Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Model loaded\n")

os.makedirs(SAVE_PATH, exist_ok=True)

all_documents = []
json_count = 0

print("🚀 Extracting legal data...\n")

# ---------------------------------
# LOOP THROUGH STAGE2 CATEGORY FOLDERS
# ---------------------------------

for stage2_category in os.listdir(BASE_PATH):

    category_path = os.path.join(BASE_PATH, stage2_category)

    if not os.path.isdir(category_path):
        continue

    print(f"📂 Processing Stage2 Category: {stage2_category}")

    for root, dirs, files in os.walk(category_path):

        for file in files:

            if file.endswith(".json"):

                json_count += 1
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:

                        data = json.load(f)

                        for item in data:

                            document = {

                                # SAVE ONLY STAGE2 CATEGORY
                                "stage2_category": stage2_category,

                                "act": item.get("act", ""),
                                "section": item.get("section_number", ""),
                                "title": item.get("title", ""),
                                "description": item.get("description", "")
                            }

                            all_documents.append(document)

                except Exception as e:
                    print(f"⚠ Error reading {file_path}: {e}")

print("\n📄 Total JSON files:", json_count)
print("📑 Total legal sections:", len(all_documents))


# ---------------------------------
# SAVE MERGED JSON
# ---------------------------------

merged_path = os.path.join(SAVE_PATH, "merged_legal_docs.json")

with open(merged_path, "w", encoding="utf-8") as f:
    json.dump(all_documents, f, ensure_ascii=False, indent=2)

print("✅ Merged JSON saved")


# ---------------------------------
# CREATE EMBEDDINGS
# ---------------------------------

print("\n🔄 Creating embeddings...")

texts = [
    f"Act: {d['act']} Section: {d['section']} Title: {d['title']} Provision: {d['description']}"
    for d in all_documents
]

embeddings = model.encode(texts, show_progress_bar=True)

embeddings = np.array(embeddings).astype("float32")

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)
index.add(embeddings)


# ---------------------------------
# SAVE FAISS INDEX
# ---------------------------------

index_path = os.path.join(SAVE_PATH, "legal_index.faiss")

faiss.write_index(index, index_path)

print("✅ FAISS index saved")

print("\n🎉 SINGLE RAG INDEX CREATED SUCCESSFULLY!")

print("\nStored fields:")
print("✔ stage2_category")
print("✔ act")
print("✔ section")
print("✔ title")
print("✔ description")