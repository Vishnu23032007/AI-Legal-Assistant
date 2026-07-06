# Services/Stage3_service.py

import os
from openai import OpenAI
from typing import Dict, List, Tuple


class Stage3Service:

    def __init__(self):

        api_key = os.getenv("OPENROUTER_API_KEY", "your-api-key-here")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )

    # --------------------------------------------------
    # 1️⃣ Structured Legal Consultation System Prompt
    # --------------------------------------------------
    def _build_system_prompt(self) -> str:

        return """
You are a senior Indian advocate with 20+ years of courtroom experience.
Wherever you state a legal principle, explain how it applies specifically to the client's situation.

You are speaking DIRECTLY to the person asking the question.
Always respond strictly in English.

IMPORTANT TONE RULE:
- Always address the person as "you".
- Never refer to them as "the client".
- Do not use third-person narration.
- Speak like you are advising them personally in your office.

You MUST respond strictly in structured Markdown format.

Formatting Rules (MANDATORY):
- Use Markdown headings with ## for each section.
- Use bullet points under every section.
- Keep each bullet point clear and logically explained.
- Each bullet must contain 2–4 lines explaining the reasoning.
- Avoid unnecessary filler.
- Provide courtroom-level clarity.
- Explain WHY something is legally important.
- Do NOT write conversational filler.
- Do NOT give generic safety disclaimers.
- Do NOT mention that you are an AI.
- If necessary, include practical courtroom strategy insights.
- Mention tactical advantages and risks realistically.

The response MUST follow this exact structure:

## 1. Brief Understanding of the Situation
- ...

## 2. Legal Position
- ...

## 3. Relevant Legal Principles
- ...

## 4. Strengths in Your Case
- ...

## 5. Possible Weaknesses / Risks
- ...

## 6. Your Legal Rights
- ...

## 7. Strategic Next Steps (How to Approach)
- Start each point with action-oriented advice using "You should", "You can", or "You must".

## 8. Required Documents / Evidence
- ...

## 9. Important Risks / Limitation Issues
- ...

CRITICAL INSTRUCTION:
- You must rely primarily on the provided legal provisions.
- Do NOT invent section numbers.
- If no provision is relevant, state that clearly.

--------------------------------------
RAG INTEGRATION INSTRUCTIONS (MANDATORY)
--------------------------------------

You will be provided with a section titled "Relevant Legal Provisions".
These provisions are retrieved from a structured legal knowledge base.

You MUST follow these rules strictly:

1. Primary Source Rule:
   - Base reasoning primarily on retrieved provisions.

2. No Hallucination Rule:
   - Do NOT invent section numbers or statutes.

3. Application Rule:
   - Always connect law → facts → legal consequence.

4. Insufficient Retrieval Handling:
   - If provisions are insufficient, clearly state the limitation.

5. Conflict Handling:
   - Identify conflicts and explain court interpretation.

6. Structured Citation Style:
   - Refer descriptively to provisions.

7. No Blind Copying:
   - Summarize provisions instead of copying.

8. Practical Strategy Integration:
   - Suggest realistic courtroom strategies.

Failure to follow these rules is considered a critical reasoning error.
"""

    # --------------------------------------------------
    # 2️⃣ Clarification Prompt (NEW)
    # --------------------------------------------------
    def _build_clarification_prompt(self) -> str:

        return """
You are a senior Indian legal advisor.

The user's question is too vague or lacks sufficient factual detail
to determine the correct legal category.

Your task is NOT to give legal advice yet.

Instead, you must ask the user a few focused clarification questions
to better understand the situation.

Rules:
- Ask 3 to 5 precise questions.
- Questions must help identify the legal issue.
- Be professional and polite.
- Do not assume facts.
- Do not provide legal conclusions yet.

Format:

## I Need A Few More Details

- Question 1
- Question 2
- Question 3
- Question 4 (optional)
- Question 5 (optional)

Explain briefly why the information is needed.
"""

    # --------------------------------------------------
    # 3️⃣ Out-of-Scope Prompt
    # --------------------------------------------------
    def _build_general_prompt(self) -> str:

        return """
You are a responsible AI legal assistant.

If the request involves illegal activity:
- Refuse politely.

If the query is outside legal domain:
- Inform the user politely.

Keep tone professional.
"""

    # --------------------------------------------------
    # 4️⃣ Main Response Generator
    # --------------------------------------------------
    def generate_response(

        self,
        user_prompt: str,
        stage1_label: str,
        legal_category: str = None,
        retrieved_sections: List[dict] = None,
        conversation_history: List[Tuple[str, str]] = None,
        need_clarification: bool = False   # ⭐ NEW PARAMETER

    ) -> Dict:

        try:

            # ----------------------------------
            # Build Conversation History
            # ----------------------------------

            context_prompt = ""

            if conversation_history:

                for q, a in conversation_history[-3:]:

                    context_prompt += f"Client: {q}\nLawyer: {a}\n\n"

            full_user_prompt = context_prompt + f"Client: {user_prompt}\nLawyer:"

            # ----------------------------------
            # 🔥 CLARIFICATION MODE
            # ----------------------------------

            if need_clarification:

                system_prompt = self._build_clarification_prompt()
                user_message = full_user_prompt

            # ----------------------------------
            # LEGAL REQUEST
            # ----------------------------------

            elif stage1_label == "LEGAL_REQUEST":

                system_prompt = self._build_system_prompt()

                if retrieved_sections:

                    formatted_sections = []

                    for sec in retrieved_sections:

                        law = sec.get("law", "Unknown Law")
                        section = sec.get("section", "Unknown Section")
                        description = sec.get("description", "")

                        text = f"""
Law: {law}
Section: {section}

Description:
{description}
"""

                        formatted_sections.append(text)

                    rag_context = "\n\n-----------------------\n\n".join(formatted_sections)

                else:

                    rag_context = "No specific statutory provisions were retrieved."

                user_message = f"""
Legal Category: {legal_category}

Relevant Legal Provisions:
{rag_context}

Client Situation:
{full_user_prompt}

Please provide structured legal advice using the above provisions.
"""

            # ----------------------------------
            # OUT OF SCOPE
            # ----------------------------------

            else:

                system_prompt = self._build_general_prompt()
                user_message = full_user_prompt

            # ----------------------------------
            # LLM CALL
            # ----------------------------------

            response = self.client.chat.completions.create(

                model="meta-llama/llama-3.3-70b-instruct",

                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],

                temperature=0.6,
                max_tokens=1000

            )

            return {

                "stage": "stage3",
                "status": "success",
                "category": legal_category,
                "response": response.choices[0].message.content.strip()

            }

        except Exception as e:

            return {

                "stage": "stage3",
                "status": "error",
                "category": legal_category,
                "message": str(e)

            }