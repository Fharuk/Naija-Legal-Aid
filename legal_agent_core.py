import google.generativeai as genai
import json
import logging
import os
import tempfile
from gtts import gTTS

logger = logging.getLogger(__name__)

class LegalAgent:
    """
    Orchestrates Legal Reasoning (Gemini) and Voice Synthesis (gTTS).
    """
    def __init__(self, gemini_key: str, yarngpt_key: str = None):
        if not gemini_key:
            raise ValueError("API Key for Gemini is required.")
        
        genai.configure(api_key=gemini_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')

    def analyze_case(self, user_input: str):
        """
        Analyzes the legal situation and extracts formal details.
        """
        prompt = f"""
        You are a Senior Nigerian Legal Consultant. The user is facing a legal issue: "{user_input}"
        
        Context: Apply Nigerian Law strictly based on the user's jurisdiction.
        
        Tasks:
        1. Identify the specific legal issue.
        2. CITE THE LAW: Quote the specific Act, Section, or Law that applies (e.g., "Section 7 of Lagos Tenancy Law 2011").
        3. Draft a short advice in Nigerian Pidgin English (max 50 words).
        4. Extract data for a formal letter (Recipient, Address). Use "Unknown" if missing.
        5. Draft the body of a formal legal letter in Standard English.
        
        Output JSON:
        {{
            "legal_issue": "string",
            "relevant_law": "string (The specific citation)",
            "advice_pidgin": "string",
            "letter_data": {{
                "recipient_type": "Landlord/Police/Employer",
                "formal_body": "string"
            }}
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.replace('```json', '').replace('```', '')
            return json.loads(clean_text)
        except Exception as e:
            logger.error(f"Gemini Error: {e}")
            return {"error": str(e)}

    def synthesize_voice(self, text: str):
        """
        Converts text to speech using gTTS.
        """
        try:
            # Attempting 'en-ng' (Nigerian English) if available, else standard 'en'
            try:
                tts = gTTS(text=text, lang='en', tld='com.ng', slow=False)
            except:
                tts = gTTS(text=text, lang='en', slow=False)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tts.save(tmp.name)
                return tmp.name
        except Exception as e:
            logger.error(f"Voice Synthesis Failed: {e}")
            return None