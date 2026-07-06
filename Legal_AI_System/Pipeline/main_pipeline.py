# main_pipeline.py

import os
import sys
import json

# ---------------------------------
# 1️⃣ Fix Import Path
# ---------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from Services.Stage1_service import stage1_predict
from Services.Stage2_service import stage2_predict
from Services.Stage3_service import Stage3Service
from RAG.Rag_Service import retrieve_laws


# ---------------------------------
# 2️⃣ Initialize Services
# ---------------------------------
print("🔄 Initializing AI Legal System...\n")

try:
    stage3_service = Stage3Service()
    print("✅ All services initialized.\n")

except Exception as e:
    print("❌ Service initialization failed:", str(e))
    sys.exit(1)


# ---------------------------------
# 3️⃣ Session Memory
# ---------------------------------
conversation_history = []
MAX_HISTORY = 6

# Confidence threshold
CONFIDENCE_THRESHOLD = 0.2

# ---------------------------------
# ⭐ Clarification Control
# ---------------------------------
clarification_count = 0
MAX_CLARIFICATION = 3
last_unclear_query = None


# ---------------------------------
# 4️⃣ Main Pipeline
# ---------------------------------
def run_pipeline(text: str) -> dict:

    global conversation_history
    global clarification_count
    global last_unclear_query

    print("\n==============================")
    print("🧠 Running Legal AI Pipeline")
    print("==============================\n")

    # ---------------------------------
    # Combine previous unclear query
    # ---------------------------------
    if last_unclear_query:
        print("🔗 Combining previous unclear query with new input\n")
        text = last_unclear_query + " " + text
        last_unclear_query = None

    print(f"User Query: {text}\n")

    # ---------------------------------
    # Stage 1 - Intent Detection
    # ---------------------------------
    print("🔎 Stage1: Detecting intent...")

    stage1_result = stage1_predict(text)

    if stage1_result["label"] == "ERROR":
        return stage1_result

    stage1_label = stage1_result["label"]

    print(f"✅ Stage1 Intent: {stage1_label}\n")

    # ---------------------------------
    # Stage 2 - Legal Domain Detection
    # ---------------------------------
    stage2_result = None
    legal_category = None
    stage2_confidence = 0
    need_clarification = False

    if stage1_label == "LEGAL_REQUEST":

        print("📚 Stage2: Detecting legal domain...")

        stage2_result = stage2_predict(text)

        if stage2_result["top_category"] == "ERROR":
            return stage2_result

        legal_category = stage2_result["top_category"]

        stage2_confidence = stage2_result.get("confidence", 0)

        print(f"✅ Stage2 Category: {legal_category}")
        print(f"📊 Confidence Score: {stage2_confidence}\n")

        # ---------------------------------
        # ⭐ Confidence Check
        # ---------------------------------
        if stage2_confidence <= CONFIDENCE_THRESHOLD:

            clarification_count += 1
            last_unclear_query = text

            print(
                f"⚠️ Low confidence detected ({clarification_count}/{MAX_CLARIFICATION})\n"
            )

            if clarification_count < MAX_CLARIFICATION:

                legal_category = None
                need_clarification = True

                stage2_result[
                    "note"
                ] = "Low confidence classification. Clarification required."

            else:

                print(
                    "⚠️ Repeated low confidence detected. Providing general legal guidance.\n"
                )

                legal_category = None
                need_clarification = False

                stage2_result[
                    "note"
                ] = "Repeated low confidence. Providing general legal guidance."

                clarification_count = 0

        else:
            clarification_count = 0

    # ---------------------------------
    # RAG Retrieval
    # ---------------------------------
    retrieved_sections = []

    if legal_category:

        try:

            print("🔍 RAG: Searching Legal Knowledge Base...\n")

            retrieved_sections = retrieve_laws(
                query=text,
                category=legal_category,
                top_k=2
            )

            print(f"✅ Retrieved {len(retrieved_sections)} relevant legal sections\n")

        except Exception as e:

            print("❌ RAG Error:", str(e))
            retrieved_sections = []

    else:

        print("⚠️ Skipping RAG retrieval due to uncertain legal category.\n")

    # ---------------------------------
    # Stage 3 - LLM Response Generation
    # ---------------------------------
    print("🤖 Stage3: Generating AI Legal Response...\n")

    stage3_result = stage3_service.generate_response(
        user_prompt=text,
        stage1_label=stage1_label,
        legal_category=legal_category,
        retrieved_sections=retrieved_sections,
        conversation_history=conversation_history,
        need_clarification=need_clarification
    )

    # ---------------------------------
    # Safe Response Extraction
    # ---------------------------------
    response_text = stage3_result.get("response")

    if response_text is None:
        print("⚠️ Stage3 returned unexpected output:", stage3_result)
        response_text = "No response generated."

    # ---------------------------------
    # Update Conversation Memory
    # ---------------------------------
    conversation_history.append((text, response_text))

    if len(conversation_history) > MAX_HISTORY:
        conversation_history.pop(0)

    # ---------------------------------
    # Final Output
    # ---------------------------------
    output = {
        "stage1": stage1_result,
        "stage2": stage2_result,
        "stage3": stage3_result,
        "retrieved_sections": retrieved_sections
    }

    return output


# ---------------------------------
# 5️⃣ CLI Testing
# ---------------------------------
if __name__ == "__main__":

    print("⚖️ AI Legal Consultation System Started")
    print("Type 'exit' to quit")
    print("Type 'new' to start a new conversation\n")

    while True:

        user_input = input("> ").strip()

        if user_input.lower() == "exit":

            print("👋 Exiting system. Goodbye!")
            break

        if user_input.lower() in ["new", "start over"]:

            conversation_history.clear()
            clarification_count = 0
            last_unclear_query = None

            print("\n🆕 Memory cleared. New conversation started.\n")
            continue

        if not user_input:

            print("⚠️ Please enter a valid question.\n")
            continue

        print("\n⏳ Processing...\n")

        result = run_pipeline(user_input)

        print("\n📤 Final Pipeline Output:\n")

        print(
            json.dumps(
                result,
                indent=4,
                ensure_ascii=False
            )
        )
        print("\n" + "=" * 100 + "\n")