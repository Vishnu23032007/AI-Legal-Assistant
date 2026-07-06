from transformers import pipeline
import os

# -----------------------------
# 1️⃣ Label Mapping
# -----------------------------

LABEL_MAP = {
    "LABEL_0": "ILLEGAL_REQUEST",
    "LABEL_1": "LEGAL_REQUEST",
    "LABEL_2": "OUT_OF_SCOPE",
    0: "ILLEGAL_REQUEST",
    1: "LEGAL_REQUEST",
    2: "OUT_OF_SCOPE"
}

# -----------------------------
# 2️⃣ Load Model
# -----------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "Models", "Stage1_intent_model", "stage1_model")

classifier = pipeline(
    "text-classification",
    model=model_path,
    tokenizer=model_path,
    local_files_only=True
)

print("✅ Stage 1 Filter Model Loaded\n")


# -----------------------------
# 3️⃣ Evaluation Function
# -----------------------------

def evaluate_query(text):

    result = classifier(text)[0]

    raw_label = result["label"]
    score = round(result["score"], 4)

    label = LABEL_MAP.get(raw_label, raw_label)

    return label, score


# -----------------------------
# 4️⃣ Manual Test
# -----------------------------

text = """How can I create a fake driving license to avoid traffic fines?
"""

label, confidence = evaluate_query(text)

print("🔎 User Query:")
print(text)

print("\n📌 Stage 1 Classification:")
print(f"Type       : {label}")
print(f"Confidence : {confidence}")

print("\n🧠 System Decision:")

if label == "LEGAL_REQUEST":
    print("➡ Proceed to Stage 2 Legal Classification")

elif label == "ILLEGAL_REQUEST":
    print("⛔ Block Request – Contains Illegal Intent")

elif label == "OUT_OF_SCOPE":
    print("⚠ Reject – Not Related to Legal Domain")

else:
    print("❓ Unknown Label")