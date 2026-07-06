import os
from openai import OpenAI
import json

class LegalAIAgent:
    def __init__(self, chatbot_pipeline, complaint_generator, judgment_service, translator, advocate_service):
        self.chatbot = chatbot_pipeline
        self.complaint = complaint_generator
        self.judgment = judgment_service
        self.translator = translator
        self.advocate_service = advocate_service
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY", "your-api-key-here")
        )
    
    def process_unified(self, user_message, user_profile, language="en"):
        """Process scenario and return all three outputs: guidance, judgments, complaint, advocates"""
        
        if language == "ta":
            user_message = self.translator.tamil_to_english(user_message)
        
        # 1. Get legal guidance (center)
        guidance_result = self.chatbot(user_message)
        guidance = guidance_result.get("stage3", {}).get("response", "")
        
        # 2. Get similar judgments (left)
        judgments = self.judgment.find_similar_cases(user_message, top_n=3)
        
        # 3. Generate complaint letter (right)
        from ai_complaint_generator import auto_generate_complaint_with_profile, detect_scenario_from_text, save_letter_as_pdf
        import os
        
        scenario_type = detect_scenario_from_text(user_message)
        complaint_letter = auto_generate_complaint_with_profile(user_message, user_profile, scenario_type)
        
        # Save PDF
        pdf_path = os.path.join(os.path.dirname(__file__), "agent_complaint.pdf")
        save_letter_as_pdf(complaint_letter, pdf_path, "english")
        
        # 4. Get matching advocates based on user district
        advocates = []
        if user_profile.get('district'):
            advocates = self.advocate_service.match_advocates(
                user_profile['district'],
                user_message,
                limit=3
            )
        
        # Translate if needed
        if language == "ta":
            guidance = self.translator.english_to_tamil(guidance)
            complaint_letter = self.translator.english_to_tamil(complaint_letter)
        
        return {
            "status": "success",
            "guidance": guidance,
            "judgments": judgments,
            "complaint_letter": complaint_letter,
            "advocates": advocates,
            "scenario_type": scenario_type
        }
    
    def reset(self):
        pass
