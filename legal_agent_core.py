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
        # Updated to Gemini 2.5 Flash Preview
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        self.yarngpt_key = yarngpt_key
        # Note: Verify this endpoint in your YarnGPT dashboard documentation
        self.yarngpt_url = "https://api.yarngpt.ai/v1/synthesize" 

    def analyze_case(self, user_input: str):
        """
        Analyzes the legal situation and extracts formal details.
        """
        prompt = f"""
        You are a Nigerian Legal Assistant. The user is facing a legal issue: "{user_input}"
        
        Context: Apply Nigerian Law (e.g., Lagos Tenancy Law 2011, Police Act 2020, Labour Act).
        
        Tasks:
        1. Identify the specific legal issue.
        2. Draft a short advice in Nigerian Pidgin English (max 50 words).
        3. Extract data for a formal letter (Recipient, Address). Use "Unknown" if missing.
        4. Draft the body of a formal legal letter in Standard English.
        
        Output JSON:
        {{
            "legal_issue": "string",
            "advice_pidgin": "string",
            "letter_data": {{
                "recipient_type": "Landlord/Police/Employer",
                "formal_body": "string"
            }}
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # robust cleanup for markdown formatting
            clean_text = response.text.replace('```json', '').replace('```', '')
            return json.loads(clean_text)
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
        
        # Ensure you use a valid voice_id from your YarnGPT account
        payload = {
            "text": text,
            "voice_id": "funke", 
            "speed": 1.0
        }
        
        try:
            response = requests.post(self.yarngpt_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    tmp.write(response.content)
                    return tmp.name
            else:
                logger.error(f"YarnGPT Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Voice Synthesis Failed: {e}")
            return None