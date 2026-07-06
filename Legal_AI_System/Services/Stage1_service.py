import os
from transformers import pipeline
from typing import Dict

# -----------------------------
# 1️⃣ Label Mapping
# -----------------------------
print("Stage1 model loaded successfully")

LABEL_MAP = {
    "LABEL_0": "ILLEGAL_REQUEST",
    "LABEL_1": "LEGAL_REQUEST",
    "LABEL_2": "OUT_OF_SCOPE",
    0: "ILLEGAL_REQUEST",
    1: "LEGAL_REQUEST",
    2: "OUT_OF_SCOPE"
}

# -----------------------------
# 2️⃣ Load Model (Load Once)
# -----------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(
    BASE_DIR,
    "Models",
    "Stage1_intent_model",
    "stage1_model"
)

classifier = pipeline(
    "text-classification",
    model=MODEL_PATH,
    tokenizer=MODEL_PATH,
    
)


# -----------------------------
# 3️⃣ Prediction Function
# -----------------------------

def stage1_predict(text: str, confidence_threshold: float = 0.0) -> Dict:
    """
    Stage 1 Intent Classification

    Args:
        text (str): User input
        confidence_threshold (float): Minimum confidence threshold

    Returns:
        dict:
        {
            "stage": "stage1",
            "label": "LEGAL_REQUEST" | "ILLEGAL_REQUEST" | "OUT_OF_SCOPE",
            "confidence": float
        }
    """

    try:
        result = classifier(text)[0]

        raw_label = result["label"]
        score = round(result["score"], 4)

        label = LABEL_MAP.get(raw_label, raw_label)

        if score < confidence_threshold:
            label = "OUT_OF_SCOPE"

        return {
            "stage": "stage1",
            "label": label,
            "confidence": score
        }

    except Exception as e:
        return {
            "stage": "stage1",
            "label": "ERROR",
            "confidence": 0.0,
            "error": str(e)
        }