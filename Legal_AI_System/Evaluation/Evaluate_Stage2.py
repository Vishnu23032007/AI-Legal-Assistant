from transformers import pipeline
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "Models", "Stage2_legal_classifier_model", "legal_classifier_model")

classifier = pipeline(
    "text-classification",
    model=model_path,
    tokenizer=model_path,
    local_files_only=True
)

print("Model loaded successfully")
def predict_query(text, confidence_threshold=0.6, gap_threshold = 0.20):

    output = classifier(text, top_k=None)

    # Handle both possible return structures safely
    if isinstance(output[0], dict):
        results = output
    else:
        results = output[0]

    # If only one label returned (strict single-label model)
    if isinstance(results, dict):
        return [(results["label"], round(results["score"], 4))]

    # Sort all labels by score
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    top_score = results[0]["score"]

    # Case 1: Low confidence
    if top_score < confidence_threshold:
        return [("Uncertain", round(top_score, 4))]

    # Case 2: Multi-class if scores are close
    multi_labels = []

    for item in results:
        if (top_score - item["score"]) < gap_threshold:
            multi_labels.append(
                (item["label"], round(item["score"], 4))
            )

    return multi_labels


# ---------------- TEST ----------------

text = """when i riding in a bike without helmet, police ask to pay a fine?
"""
predictions = predict_query(text)

print("\nPredictions:")
for label, confidence in predictions:
    print(f"{label}  -->  {confidence}")