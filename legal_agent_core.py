import google.generativeai as genai
import requests
import json
import logging
import os
import tempfile

logger = logging.getLogger(__name__)

class LegalAgent:
    """
    Orchestrates Legal Reasoning (Gemini) and Voice Synthesis (YarnGPT).
    """
    def __init__(self, gemini_key: str, yarngpt_key: str):
        if not gemini_key or not yarngpt_key:
            raise ValueError("API Keys for Gemini and YarnGPT are required.")
        
        genai.configure(api_key=gemini_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.yarngpt_key = yarngpt_key
        # Standard endpoint assumption - Verify against specific YarnGPT docs if 404 occurs
        self.yarngpt_url = "https://api.yarngpt.ai/v1/synthesize" 

    def analyze_case(self, user_input: str):
        """
        1. Analyzes the legal situation using Nigerian Law context.
        2. Extracts entities for the document.
        3. Drafts a simplified explanation in Pidgin.
        """
        prompt = f"""
        You are a Nigerian Legal Assistant. The user is facing a legal issue: "{user_input}"
        
        Context: Apply Nigerian Law (e.g., Lagos Tenancy Law 2011, Police Act 2020).
        
        Tasks:
        1. Identify the legal issue (e.g., Unlawful Eviction, Harassment).
        2. Draft a short, comforting advice in Nigerian Pidgin English (max 50 words).
        3. Extract entities for a formal letter: Recipient (Landlord/Police), Address, Date. Use "Unknown" if not provided.
        4. Draft the body of a formal legal letter in Standard English.
        
        Output JSON:
        {{
            "legal_issue": "string",
            "advice_pidgin": "string",
            "letter_data": {{
                "recipient_type": "Landlord/Police/Employer",
                "formal_body": "string (The main paragraphs of the letter)"
            }}
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text.strip('`json \n'))
        except Exception as e:
            logger.error(f"Gemini Error: {e}")
            return {"error": str(e)}

    def synthesize_voice(self, text: str):
        """
        Converts text to Nigerian-accented speech using YarnGPT.
        """
        headers = {
            "Authorization": f"Bearer {self.yarngpt_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "voice_id": "Mary", 
            "speed": 1.0
        }
        
        try:
            response = requests.post(self.yarngpt_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                # Save audio to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    tmp.write(response.content)
                    return tmp.name
            else:
                logger.error(f"YarnGPT Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Voice Synthesis Failed: {e}")
            return None