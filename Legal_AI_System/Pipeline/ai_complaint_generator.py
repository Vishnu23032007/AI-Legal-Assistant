#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime
from openai import OpenAI

# ================= PDF IMPORTS =================
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# Tamil Font
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# =====================================================================
# CONFIGURATION
# =====================================================================

API_KEY = os.getenv("OPENROUTER_API_KEY", "your-api-key-here")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY
)

MODEL = "meta-llama/llama-3.3-70b-instruct"

# =====================================================================
# COMPLAINT TEMPLATES
# =====================================================================

COMPLAINT_TEMPLATES = {
    "consumer": """
From:
[Full Name]
[Full Address]
[Phone Number]
[Email]

Date: {date}

To:
The District Consumer Forum
[District Name]
[Location]

Subject: Consumer Complaint regarding [Product/Service Issue]

Respected Sir/Madam,

I am writing to file a formal consumer complaint under the Consumer Protection Act, 2019.

Details of Purchase/Service:
- Date of Purchase/Service: [Date]
- Invoice/Bill Number: [Number]
- Amount Paid: Rs. [Amount]
- Seller/Service Provider: [Name and Address]

Nature of Complaint:
[Detailed description of defect/deficiency in goods or services]

Correspondence Made:
[Details of complaints made to seller/service provider and their response]

Relief Sought:
1. [Specific relief - refund/replacement/compensation]
2. Compensation for mental agony and harassment: Rs. [Amount]
3. Litigation costs

I request your urgent intervention in this matter.

Thanking you.

Yours faithfully,
[Full Name]

Enclosures:
1. Copy of bill/invoice
2. Correspondence records
3. Supporting documents
""",
    
    "police": """
From:
[Full Name]
[Full Address]
[Phone Number]

Date: {date}

To:
The Station House Officer
[Police Station Name]
[Location]

Subject: Complaint regarding [Nature of Offense]

Respected Sir/Madam,

I wish to lodge a formal complaint regarding the following incident:

Incident Details:
- Date and Time: [Date and Time]
- Place of Occurrence: [Exact Location]
- Nature of Offense: [Brief description]

Detailed Account:
[Comprehensive description of the incident, sequence of events, and persons involved]

Suspect/Accused Details (if known):
- Name: [Name]
- Address: [Address]
- Identifying features: [Description]

Witnesses:
1. [Name and Contact]
2. [Name and Contact]

I request you to register an FIR and take immediate action against the accused.

Yours faithfully,
[Full Name]

Enclosures:
1. Medical certificate (if applicable)
2. Evidence/photographs
3. Witness statements
""",
    
    "civil": """
From:
[Full Name]
[Full Address]
[Phone Number]

Date: {date}

To:
[Authority/Person Name]
[Designation]
[Address]

Subject: Legal Notice regarding [Matter]

Dear Sir/Madam,

Under instructions from my client, I am writing this legal notice regarding the following matter:

Background:
[Brief background of the relationship/transaction/agreement]

Grievance:
[Detailed description of the breach/violation/dispute]

Legal Position:
[Relevant legal provisions and rights violated]

Demand:
You are hereby called upon to:
1. [Specific action demanded]
2. [Compensation/damages if applicable]
3. [Timeline for compliance]

This notice is without prejudice to my client's rights and remedies available under law.

Failure to comply within [X days] will compel my client to initiate appropriate legal proceedings without further notice.

Yours faithfully,
[Full Name]
""",
    
    "workplace": """
From:
[Full Name]
[Employee ID]
[Department]
[Contact Number]

Date: {date}

To:
The HR Manager / Grievance Officer
[Company Name]
[Address]

Subject: Formal Complaint regarding [Issue]

Dear Sir/Madam,

I am writing to formally lodge a complaint regarding the following workplace issue:

Employee Details:
- Name: [Full Name]
- Designation: [Position]
- Department: [Department]
- Date of Joining: [Date]

Nature of Complaint:
[Detailed description of harassment/discrimination/unfair treatment/wage dispute]

Incidents:
1. Date: [Date] - [Description]
2. Date: [Date] - [Description]

Impact:
[How this has affected work performance and well-being]

Previous Attempts to Resolve:
[Any informal complaints or discussions]

Relief Sought:
1. [Specific action requested]
2. [Compensation if applicable]
3. [Preventive measures]

I request immediate investigation and appropriate action as per company policy and labour laws.

Yours sincerely,
[Full Name]
""",
    
    "property": """
From:
[Full Name]
[Full Address]
[Phone Number]

Date: {date}

To:
[Recipient Name]
[Designation]
[Address]

Subject: Complaint regarding Property Dispute - [Property Details]

Respected Sir/Madam,

I am writing regarding a property dispute concerning:

Property Details:
- Address: [Complete Address]
- Survey/Plot Number: [Number]
- Area: [Measurement]
- Document Reference: [Registration/Sale Deed Number]

Ownership Details:
[How ownership was acquired - purchase/inheritance/gift]

Nature of Dispute:
[Detailed description of encroachment/illegal possession/title dispute]

Legal Rights:
[Reference to sale deed/title documents/court orders]

Relief Sought:
1. [Eviction/removal of encroachment/declaration of title]
2. [Compensation for illegal occupation]
3. [Injunction against further interference]

I request your immediate intervention to protect my legal rights over the property.

Yours faithfully,
[Full Name]

Enclosures:
1. Copy of title documents
2. Survey/measurement records
3. Photographs/evidence
""",
    
    "cyber": """
From:
[Full Name]
[Full Address]
[Phone Number]
[Email]

Date: {date}

To:
The Cyber Crime Cell
[Police Station/Department]
[Location]

Subject: Complaint regarding Cyber Crime - [Nature of Crime]

Respected Sir/Madam,

I wish to report a cyber crime incident:

Incident Details:
- Date and Time: [Date and Time]
- Type of Crime: [Hacking/Phishing/Online Fraud/Identity Theft/Cyberbullying]
- Platform/Website: [Details]

Account of Incident:
[Detailed description of how the crime occurred]

Financial Loss (if any):
- Amount: Rs. [Amount]
- Transaction Details: [Bank/UPI/Card details]

Suspect Information (if available):
- Username/Profile: [Details]
- Contact: [Phone/Email/Social Media]
- IP Address/URL: [If known]

Evidence Preserved:
1. Screenshots
2. Transaction records
3. Communication logs
4. URLs/links

I request immediate action to trace and apprehend the culprits and recover the lost amount.

Yours faithfully,
[Full Name]

Enclosures:
1. Screenshots of fraud
2. Bank statements
3. Communication records
""",
    
    "general": """
From:
[Full Name]
[Full Address]
[Phone Number]

Date: {date}

To:
[Authority Designation]
[Office Name]
[Location]

Subject: [One-line subject]

Respected Sir/Madam,

[Paragraph 1 – Purpose and introduction]

[Paragraph 2 – Incident details with date, time, and location]

[Paragraph 3 – Additional facts and circumstances]

[Paragraph 4 – Impact and consequences]

Relief Sought:
1. [Specific relief requested]
2. [Additional remedies]
3. [Compensation if applicable]

I request your urgent attention and appropriate action in this matter.

Thanking you.

Yours faithfully,
[Full Name]
"""
}

# =====================================================================
# AUTO-GENERATE COMPLAINT WITH USER PROFILE
# =====================================================================

def detect_scenario_from_text(text):
    """Quick scenario detection from text"""
    full_text = text.lower()
    
    if any(word in full_text for word in ["product", "defective", "refund", "warranty", "seller", "purchase", "consumer"]):
        return "consumer"
    elif any(word in full_text for word in ["theft", "stolen", "assault", "fir", "police", "crime", "robbery"]):
        return "police"
    elif any(word in full_text for word in ["workplace", "employer", "salary", "harassment", "office"]):
        return "workplace"
    elif any(word in full_text for word in ["property", "land", "encroachment", "possession", "tenant"]):
        return "property"
    elif any(word in full_text for word in ["cyber", "hacking", "phishing", "online fraud", "upi", "scam"]):
        return "cyber"
    elif any(word in full_text for word in ["contract", "agreement", "breach", "dispute"]):
        return "civil"
    
    return "general"

def auto_generate_complaint_with_profile(scenario_text, user_profile, scenario_type):
    """Generate complaint letter automatically using user profile"""
    current_date = datetime.now().strftime("%d/%m/%Y")
    
    prompt = f"""Generate a professional legal complaint letter in Indian format.

User Details (USE THESE EXACTLY):
- Name: {user_profile.get('name')}
- Address: {user_profile.get('address')}
- Phone: {user_profile.get('phone')}
- Email: {user_profile.get('email')}

Scenario Type: {scenario_type}
User's Complaint: {scenario_text}

Date: {current_date}

Generate a complete formal complaint letter following this structure:

From:
{user_profile.get('name')}
{user_profile.get('address')}
{user_profile.get('phone')}

Date: {current_date}

To:
[Appropriate Authority based on scenario]
[Office Name]
[Location]

Subject: [Appropriate subject based on complaint]

Respected Sir/Madam,

[Write 3-4 paragraphs describing the complaint professionally]

Relief Sought:
[List appropriate relief]

Thanking you.

Yours faithfully,
{user_profile.get('name')}

Generate ONLY the letter, no explanations."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=800
    )

    return response.choices[0].message.content.strip()

# =====================================================================
# SCENARIO DETECTION
# =====================================================================

def detect_scenario(conversation_history):
    """
    Analyze conversation to detect the type of complaint scenario
    """
    full_text = " ".join([msg["content"].lower() for msg in conversation_history if msg["role"] == "user"])
    
    # Consumer-related keywords
    if any(word in full_text for word in ["product", "defective", "refund", "warranty", "seller", "purchase", "consumer", "service deficiency"]):
        return "consumer"
    
    # Police/Criminal keywords
    elif any(word in full_text for word in ["theft", "stolen", "assault", "fir", "police", "crime", "robbery", "violence", "threat"]):
        return "police"
    
    # Workplace keywords
    elif any(word in full_text for word in ["workplace", "employer", "salary", "harassment", "discrimination", "termination", "office", "boss", "colleague"]):
        return "workplace"
    
    # Property keywords
    elif any(word in full_text for word in ["property", "land", "encroachment", "possession", "eviction", "tenant", "landlord", "plot", "house"]):
        return "property"
    
    # Cyber crime keywords
    elif any(word in full_text for word in ["cyber", "hacking", "phishing", "online fraud", "upi", "account hacked", "scam", "fake website"]):
        return "cyber"
    
    # Civil dispute keywords
    elif any(word in full_text for word in ["contract", "agreement", "breach", "legal notice", "dispute", "damages", "compensation"]):
        return "civil"
    
    return "general"

# =====================================================================
# DYNAMIC SYSTEM PROMPT WITH REAL DATE
# =====================================================================

def get_system_prompt(scenario="general", user_profile=None):
    current_date = datetime.now().strftime("%d/%m/%Y")
    template = COMPLAINT_TEMPLATES.get(scenario, COMPLAINT_TEMPLATES["general"])
    
    # Build user info section
    user_info_instruction = ""
    if user_profile:
        user_info_instruction = f"""
IMPORTANT - USER PROFILE IS ALREADY PROVIDED:
- Name: {user_profile.get('name')}
- Address: {user_profile.get('address')}
- Phone: {user_profile.get('phone')}
- Email: {user_profile.get('email')}

DO NOT ASK FOR NAME, ADDRESS, PHONE, OR EMAIL.
These details are already available. Use them directly in the letter.
ONLY ask for incident-specific details like date, location, description, etc.
"""
    
    return f"""
You are a professional legal drafting assistant specializing in Indian law.

Today's official date is: {current_date}

Detected Scenario: {scenario.upper()}
{user_info_instruction}
Your job:
1. ONLY ask for incident/case specific details (NOT personal details if profile provided).
2. Ask only 1-2 questions at a time.
3. Be specific to the type of complaint.
4. Do NOT generate letter until ALL incident details are collected.

For {scenario} complaints, collect ONLY:
{get_required_fields(scenario, user_profile)}

When generating FINAL LETTER:
- Output ONLY the letter.
- Start directly with "From:"
- Use Date: {current_date}
- Use the provided user profile details in the letter.
- Follow the template structure for {scenario} complaints.
- No explanations before or after.

Template Structure:
{template}
"""

def get_required_fields(scenario, user_profile=None):
    # Skip personal details if user profile exists
    if user_profile:
        fields = {
            "consumer": """- Purchase Date, Invoice Number, Amount
- Seller/Service Provider Details
- Nature of Defect/Deficiency
- Previous Complaints Made
- Relief Sought""",
            
            "police": """- Incident Date, Time, Location
- Nature of Offense
- Detailed Account of Incident
- Suspect/Accused Details
- Witness Information""",
            
            "workplace": """- Employee ID, Department
- Designation, Date of Joining
- Nature of Complaint
- Specific Incidents with Dates
- Impact on Work
- Relief Sought""",
            
            "property": """- Property Address, Survey Number
- Ownership Documents
- Nature of Dispute
- Relief Sought""",
            
            "cyber": """- Incident Date, Time
- Type of Cyber Crime
- Platform/Website Details
- Financial Loss Details
- Suspect Information
- Evidence Available""",
            
            "civil": """- Background of Matter
- Nature of Grievance
- Legal Position
- Specific Demands
- Timeline for Compliance""",
            
            "general": """- Incident Date, Time, Location
- Detailed Description
- Relief Requested
- Authority Name & Designation"""
        }
    else:
        fields = {
            "consumer": """- Full Name, Address, Phone, Email
- Purchase Date, Invoice Number, Amount
- Seller/Service Provider Details
- Nature of Defect/Deficiency
- Previous Complaints Made
- Relief Sought""",
            
            "police": """- Full Name, Address, Phone
- Incident Date, Time, Location
- Nature of Offense
- Detailed Account of Incident
- Suspect/Accused Details
- Witness Information""",
            
            "workplace": """- Full Name, Employee ID, Department
- Designation, Date of Joining
- Nature of Complaint
- Specific Incidents with Dates
- Impact on Work
- Relief Sought""",
            
            "property": """- Full Name, Address, Phone
- Property Address, Survey Number
- Ownership Documents
- Nature of Dispute
- Relief Sought""",
            
            "cyber": """- Full Name, Address, Phone, Email
- Incident Date, Time
- Type of Cyber Crime
- Platform/Website Details
- Financial Loss Details
- Suspect Information
- Evidence Available""",
            
            "civil": """- Full Name, Address, Phone
- Background of Matter
- Nature of Grievance
- Legal Position
- Specific Demands
- Timeline for Compliance""",
            
            "general": """- Full Name, Address, Phone
- Incident Date, Time, Location
- Detailed Description
- Relief Requested
- Authority Name & Designation"""
        }
    
    return fields.get(scenario, fields["general"])

# =====================================================================
# STATE MANAGEMENT
# =====================================================================

class ConversationState:
    def __init__(self, user_profile=None):
        self.conversation_history = []
        self.language_selected = None
        self.final_letter = None
        self.detected_scenario = None
        self.user_profile = user_profile

    def add_message(self, role, content):
        self.conversation_history.append({
            "role": role,
            "content": content
        })


global_state = ConversationState()

# =====================================================================
# AI INTERACTION
# =====================================================================

def call_ai(state, user_message):

    state.add_message("user", user_message)
    
    # Detect scenario from conversation
    scenario = detect_scenario(state.conversation_history)
    
    # Build system message with user profile
    system_content = get_system_prompt(scenario, state.user_profile)
    
    # Add user profile context to first message if available
    if state.user_profile and len(state.conversation_history) == 1:
        profile_context = f"""[SYSTEM: User profile loaded - Name: {state.user_profile.get('name')}, Address: {state.user_profile.get('address')}, Phone: {state.user_profile.get('phone')}, Email: {state.user_profile.get('email')}. Use these in the letter. Do not ask for them.]"""
        state.conversation_history[0]["content"] = profile_context + "\n\n" + state.conversation_history[0]["content"]

    messages = [{"role": "system", "content": system_content}]
    messages.extend(state.conversation_history)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.2,
            max_tokens=700
        )

        ai_response = response.choices[0].message.content.strip()
        state.add_message("assistant", ai_response)

        return ai_response

    except Exception as e:
        return f"Error communicating with AI: {str(e)}"

# =====================================================================
# TRANSLATE LETTER TO TAMIL
# =====================================================================

def translate_to_tamil(text):

    prompt = f"""
Translate the following legal complaint letter into professional Tamil.

Keep the same structure.

{text}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a professional legal translator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()

# =====================================================================
# CLEAN LETTER
# =====================================================================

def clean_letter(text):
    if "From:" in text:
        return text[text.index("From:"):].strip()
    return text.strip()

# =====================================================================
# DETECT DOCUMENT TITLE
# =====================================================================

def detect_document_title(letter_text):

    text = letter_text.lower()

    if "petition" in text:
        return "PETITION"
    elif "complaint" in text:
        return "COMPLAINT"
    else:
        return "LEGAL REPRESENTATION"

# =====================================================================
# PDF GENERATION
# =====================================================================

def save_letter_as_pdf(letter_text, filename="legal_document.pdf", language="english"):
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.pagesizes import A4

        letter_text = clean_letter(letter_text)

        # Safety check
        if not letter_text or len(letter_text.strip()) < 30:
            print("PDF Error: Letter text empty")
            return False

        styles = getSampleStyleSheet()
        story = []

        # Title
        title = Paragraph("<b>COMPLAINT LETTER</b>", styles["Title"])
        story.append(title)
        story.append(Spacer(1, 20))

        # Body
        for line in letter_text.split("\n"):
            line = line.strip()

            if not line:
                story.append(Spacer(1, 6))
                continue

            paragraph = Paragraph(line, styles["Normal"])
            story.append(paragraph)
            story.append(Spacer(1, 8))

        doc = SimpleDocTemplate(filename, pagesize=A4)
        doc.build(story)

        print("PDF Generated:", filename)

        return True

    except Exception as e:
        print("PDF Error:", str(e))
        return False

# =====================================================================
# LETTER DETECTION
# =====================================================================

def detect_letter_in_response(response):

    if not response:
        return False

    return "From:" in response and "Subject:" in response

# =====================================================================
# MAIN FUNCTION CALLED BY FLASK
# =====================================================================

def generate_complaint_pdf(user_message, output_path="generated_complaint.pdf", language=None, user_profile=None):

    global global_state
    
    # Initialize state with user profile if provided and state is empty
    if user_profile and not global_state.user_profile:
        global_state.user_profile = user_profile

    # If language already asked
    if global_state.final_letter and global_state.language_selected is None:

        if user_message.lower() in ["1", "english"]:

            letter = global_state.final_letter
            language = "english"

        elif user_message.lower() in ["2", "tamil", "தமிழ்"]:

            letter = translate_to_tamil(global_state.final_letter)
            language = "tamil"

        else:

            return {
                "status": "incomplete",
                "message": "Please type 1 for English or 2 for Tamil."
            }

        success = save_letter_as_pdf(letter, output_path, language)

        if success:

            global_state = ConversationState()

            return {
                "status": "success",
                "pdf_path": output_path
            }

        return {
            "status": "error",
            "message": "PDF generation failed"
        }

    # Normal AI flow
    ai_response = call_ai(global_state, user_message)

    # If final letter detected
    if detect_letter_in_response(ai_response):

        global_state.final_letter = ai_response

        return {
            "status": "incomplete",
            "message": "Choose language for complaint letter:\n\n1️⃣ English\n2️⃣ தமிழ்"
        }

    return {
        "status": "incomplete",
        "message": ai_response
    }

# =====================================================================
# CLI INTERFACE
# =====================================================================

if __name__ == "__main__":
    print("="*60)
    print("⚖️  AI LEGAL COMPLAINT GENERATOR")
    print("="*60)
    print("\nSupported Complaint Types:")
    print("  • Consumer Complaints")
    print("  • Police/FIR Complaints")
    print("  • Workplace Issues")
    print("  • Property Disputes")
    print("  • Cyber Crime")
    print("  • Civil Disputes")
    print("\nType 'exit' to quit | 'new' to start over\n")
    print("="*60)

    while True:
        user_input = input("\n👤 You: ").strip()

        if user_input.lower() == "exit":
            print("\n👋 Goodbye!\n")
            break

        if user_input.lower() == "new":
            global_state = ConversationState()
            print("\n🔄 New conversation started.\n")
            continue

        if not user_input:
            print("⚠️  Please enter a message.")
            continue

        result = generate_complaint_pdf(user_input)

        if result["status"] == "success":
            print(f"\n✅ PDF Generated: {result['pdf_path']}\n")
            print("🔄 Starting new conversation...\n")
        else:
            print(f"\n🤖 Assistant: {result['message']}")