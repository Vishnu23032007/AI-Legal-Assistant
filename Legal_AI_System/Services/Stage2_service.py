# Services/Stage2_service.py

import os
from transformers import pipeline
from typing import Dict, List

# -----------------------------
# 1️⃣ Load Legal Classifier
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLASSIFIER_PATH = os.path.join(
    BASE_DIR,
    "Models",
    "Stage2_legal_classifier_model",
    "legal_classifier_model"
)

classifier = pipeline(
    "text-classification",
    model=CLASSIFIER_PATH,
    tokenizer=CLASSIFIER_PATH,
    return_token_type_ids=False
)

# -----------------------------
# 2️⃣ Stage 2 Prediction (Classification Only)
# -----------------------------
def stage2_predict(text: str, confidence_gap: float = 0.2) -> Dict:
    """
    Stage 2 Legal Domain Classification

    Args:
        text (str): Legal query
        confidence_gap (float): Allow multiple classes if scores are close

    Returns:
        dict:
        {
            "stage": "stage2",
            "top_category": str,
            "confidence": float,           # ✅ Top category confidence
            "all_categories": [(label, score)],
        }
    """
    try:
        results = classifier(text, top_k=None)

        # Ensure consistent format
        if isinstance(results[0], dict):
            results = results
        else:
            results = results[0]

        # Sort by confidence descending
        results = sorted(results, key=lambda x: x["score"], reverse=True)

        top_score = results[0]["score"]

        # Multi-label logic: keep categories close to top_score
        filtered = [
            (item["label"], round(item["score"], 4))
            for item in results
            if (top_score - item["score"]) <= confidence_gap
        ]

        return {
            "stage": "stage2",
            "top_category": filtered[0][0],
            "confidence": round(filtered[0][1], 4),  # ✅ Top category confidence
            "all_categories": filtered
        }

    except Exception as e:
        return {
            "stage": "stage2",
            "top_category": "ERROR",
            "confidence": 0.0,
            "all_categories": [],
            "error": str(e)
        }