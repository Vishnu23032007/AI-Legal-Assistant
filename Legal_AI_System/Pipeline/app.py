from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys

from ai_complaint_generator import generate_complaint_pdf
from ai_complaint_generator import global_state

# ---------------------------------
# Fix Import Path
# ---------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

sys.path.append(PROJECT_ROOT)

from main_pipeline import run_pipeline, conversation_history
from Services.translation_service import TranslationService
from Services.judgment_service import JudgmentService
from Services.user_service import UserService
from Services.advocate_service import AdvocateService
from agent_controller import LegalAIAgent

# ---------------------------------
# Initialize Services
# ---------------------------------
translator = TranslationService()
judgment_service = JudgmentService()
user_service = UserService()
advocate_service = AdvocateService()
agent = LegalAIAgent(run_pipeline, generate_complaint_pdf, judgment_service, translator, advocate_service)

# ---------------------------------
# Create Flask App
# ---------------------------------
app = Flask(__name__)
CORS(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# ---------------------------------
# 🔐 Authentication Endpoints
# ---------------------------------
@app.route("/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    data = request.json
    result = user_service.register(
        email=data.get("email"),
        password=data.get("password"),
        name=data.get("name"),
        phone=data.get("phone"),
        address=data.get("address"),
        district=data.get("district")
    )
    return jsonify(result)

@app.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    data = request.json
    result = user_service.login(
        email=data.get("email"),
        password=data.get("password")
    )
    return jsonify(result)

# ---------------------------------
# 🤖 AI AGENT ENDPOINT (Unified)
# ---------------------------------
@app.route("/agent", methods=["POST", "OPTIONS"])
def ai_agent():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    data = request.json
    user_message = data.get("message")
    user_email = data.get("email")
    language = data.get("language", "en")

    if not user_message or not user_email:
        return jsonify({"error": "Message and email are required"}), 400

    try:
        # Get user profile
        user_profile = user_service.get_user_profile(user_email)
        if not user_profile:
            return jsonify({"error": "User not found"}), 404
        
        # Process unified request
        result = agent.process_unified(user_message, user_profile, language)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/agent/reset", methods=["POST", "OPTIONS"])
def reset_agent():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    agent.reset()
    return jsonify({"message": "Agent reset successful"})


# ---------------------------------
# 1️⃣ Chatbot Endpoint
# ---------------------------------
@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.json

    user_text = data.get("message")
    selected_language = data.get("language", "en")

    if not user_text:
        return jsonify({"error": "Message is required"}), 400

    # 🔹 Tamil → English
    if selected_language == "ta":
        user_text = translator.tamil_to_english(user_text)

    # 🔹 Run Legal AI Pipeline
    result = run_pipeline(user_text)

    # 🔹 Translate AI response → Tamil
    if selected_language == "ta":
        if "stage3" in result and "response" in result["stage3"]:
            result["stage3"]["response"] = translator.english_to_tamil(
                result["stage3"]["response"]
            )

    return jsonify(result)


# ---------------------------------
# 2️⃣ Clear Conversation Memory
# ---------------------------------
@app.route("/new_conversation", methods=["POST"])
def new_conversation():

    global conversation_history

    conversation_history.clear()

    return jsonify({
        "message": "Conversation reset successful"
    })


# ---------------------------------
# 3️⃣ Complaint Generator Endpoint
# ---------------------------------
@app.route("/complaint", methods=["POST"])
def complaint():

    data = request.json

    user_text = data.get("message")
    selected_language = data.get("language", "en")
    user_email = data.get("email")

    if not user_text:
        return jsonify({"error": "Message is required"}), 400

    # Get user profile if email provided
    user_profile = None
    if user_email:
        user_profile = user_service.get_user_profile(user_email)

    # 🔹 Translate Tamil → English (AI works internally in English)
    if selected_language == "ta":
        user_text = translator.tamil_to_english(user_text)

    output_file = "generated_complaint.pdf"

    # 🔹 Pass user profile to complaint generator
    result = generate_complaint_pdf(
        user_message=user_text,
        output_path=output_file,
        language=selected_language,
        user_profile=user_profile
    )

    # ------------------------------
    # CASE 1 : PDF Generated
    # ------------------------------
    if result["status"] == "success":

        return send_file(
            output_file,
            as_attachment=True,
            download_name="complaint.pdf",
            mimetype="application/pdf"
        )

    # ------------------------------
    # CASE 2 : Continue conversation
    # ------------------------------
    elif result["status"] == "incomplete":

        message = result["message"]

        # Translate follow-up message
        if selected_language == "ta":
            message = translator.english_to_tamil(message)

        return jsonify({
            "status": "continue",
            "message": message
        })

    # ------------------------------
    # CASE 3 : Error
    # ------------------------------
    else:

        return jsonify(result), 500


# ---------------------------------
# 4️⃣ Judgment Retrieval Endpoint
# ---------------------------------
@app.route("/judgment", methods=["POST"])
def judgment():
    data = request.json
    query = data.get("query")
    top_n = data.get("top_n", 5)

    if not query:
        return jsonify({"error": "Query is required"}), 400

    try:
        similar_cases = judgment_service.find_similar_cases(query, top_n=top_n)
        return jsonify({
            "status": "success",
            "query": query,
            "total_results": len(similar_cases),
            "cases": similar_cases
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ---------------------------------
# 5️⃣ Generate PDF Endpoint
# ---------------------------------
@app.route("/generate_pdf", methods=["POST", "OPTIONS"])
def generate_pdf_endpoint():
    if request.method == "OPTIONS":
        return jsonify({}), 200
        
    data = request.json
    text = data.get("text")
    language = data.get("language", "en")
    
    if not text:
        return jsonify({"error": "Text is required"}), 400
        
    from ai_complaint_generator import save_letter_as_pdf
    output_file = "downloaded_complaint.pdf"
    success = save_letter_as_pdf(text, output_file, "tamil" if language == "ta" else "english")
    
    if success:
        return send_file(
            output_file,
            as_attachment=True,
            download_name="complaint_letter.pdf",
            mimetype="application/pdf"
        )
    return jsonify({"error": "Failed to generate PDF"}), 500

# ---------------------------------
# Run Server
# ---------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False) 