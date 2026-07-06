import time
import sys
from datetime import datetime
from openai import OpenAI, RateLimitError
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

# ----------------------------
# Step 1: Input Collection
# ----------------------------
print("--- CRYSTAL CLEAR GOVT COMPLAINT GENERATOR ---")
u_name = input("Your Full Name: ")
u_address = input("Your Full Address: ")
u_district = input("District Name: ")
u_recipient = input("Recipient (e.g., District Collector): ")
u_dept = input("Department (e.g., TNEB / Police): ")
u_subject = input("Subject: ")
u_scenario = input("Describe the issue simply: ")

user_data = {
    "name": u_name,
    "address": u_address,
    "district": u_district,
    "recipient": u_recipient,
    "dept": u_dept,
    "subject": u_subject,
    "details": u_scenario
}

# ----------------------------
# Step 2: Client Setup
# ----------------------------
api_key = ""
client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

# ----------------------------
# Step 3: Prompt for "Crystal Clear" Content
# ----------------------------
# This prompt is specifically designed to stop the AI from writing long stories.
prompt = f"""
Draft a formal English complaint letter that is extremely brief and clear. 

Issue: {user_data['details']}

STRICT FORMATTING RULES:
1. Start with a brief 'Respected Sir/Madam'.
2. Use a short 1-sentence introduction.
3. Use BULLET POINTS to list the key facts/grievances.
4. End with a 1-sentence specific request for action.
5. NO long paragraphs. Keep it under 150 words total.
"""

def generate_letter(prompt):
    try:
        print("\nDrafting concise complaint...")
        response = client.chat.completions.create(
            model="google/gemma-3-4b-it:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2 # Lower temperature for more direct, less creative text
        )
        return response.choices[0].message.content
    except RateLimitError:
        print("Rate limit hit. Wait a moment.")
        sys.exit()

letter_body = generate_letter(prompt)

# ----------------------------
# Step 4: PDF Generation (Same layout, cleaner text)
# ----------------------------
pdf_file = f"Clear_Complaint_{user_data['dept'].replace(' ', '_')}.pdf"
c = canvas.Canvas(pdf_file, pagesize=A4)
width, height = A4
margin = 60
y_coord = height - 60
line_h = 16

def draw_text(text, x, y, font="Helvetica", size=11, bold=False):
    f = f"{font}-Bold" if bold else font
    c.setFont(f, size)
    lines = simpleSplit(text, f, size, width - (2 * margin))
    for line in lines:
        c.drawString(x, y, line)
        y -= line_h
    return y

# Header
c.setFont("Helvetica-Bold", 14)
c.drawCentredString(width/2, y_coord, "OFFICIAL GRIEVANCE PETITION")
y_coord -= 40

# Date/Place
c.setFont("Helvetica", 11)
c.drawString(margin, y_coord, f"Place: {user_data['district']}")
c.drawString(width - 150, y_coord, f"Date: {datetime.now().strftime('%d-%m-%Y')}")
y_coord -= 30

# From/To
y_coord = draw_text("FROM:", margin, y_coord, bold=True)
y_coord = draw_text(f"{user_data['name']}\n{user_data['address']}", margin, y_coord)
y_coord -= 15
y_coord = draw_text("TO:", margin, y_coord, bold=True)
y_coord = draw_text(f"{user_data['recipient']},\n{user_data['dept']},\n{user_data['district']} District.", margin, y_coord)
y_coord -= 30

# Subject (Underlined)
y_coord = draw_text(f"SUB: {user_data['subject'].upper()}", margin, y_coord, bold=True)
c.setLineWidth(1)
c.line(margin, y_coord + 12, width - margin, y_coord + 12)
y_coord -= 20

# Letter Body (The "Crystal Clear" part)
for p in letter_body.split('\n'):
    if p.strip():
        y_coord = draw_text(p.strip(), margin, y_coord)
        y_coord -= 6 # Tighter spacing for bullet points
    if y_coord < 150:
        c.showPage()
        y_coord = height - 60

# Signature Box
y_coord -= 40
c.setFont("Helvetica-Bold", 11)
c.drawString(width - 220, y_coord, "Yours faithfully,")
y_coord -= 60
c.rect(width - 230, y_coord, 170, 70) 
c.setFont("Helvetica", 8)
c.drawString(width - 220, y_coord + 5, "Signature / Thumb Impression")
y_coord -= 20
c.setFont("Helvetica-Bold", 11)
c.drawString(width - 220, y_coord, f"({user_data['name']})")

c.save()
print(f"\n✅ SUCCESS! Crystal clear PDF saved as: {pdf_file}")