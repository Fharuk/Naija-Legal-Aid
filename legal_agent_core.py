import google.generativeai as genai
import requests
import json
import logging
import os
import tempfile
from gtts import gTTS

logger = logging.getLogger(__name__)

class LegalAgent:
    """
    Orchestrates Legal Reasoning (Gemini) and Voice Synthesis (YarnGPT + gTTS).
    """
    def __init__(self, gemini_key: str, yarngpt_key: str = None):
        if not gemini_key:
            raise ValueError("API Key for Gemini is required.")
        
        genai.configure(api_key=gemini_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        
        self.yarngpt_key = yarngpt_key
        self.yarngpt_url = "https://yarngpt.ai/api/v1/tts" 

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
            logger.error("Gemini Error: %s", e)
            return {"error": str(e)}

    def synthesize_voice(self, text: str):
        """
        Converts text to speech.
        Strategy: Try YarnGPT (Nigerian Accent) -> Fail -> Fallback to gTTS (Tweaked).
        """
        audio_path = None
        
        # 1. Try YarnGPT
        if self.yarngpt_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.yarngpt_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "text": text,
                    "voice": "Idera", 
                    "response_format": "mp3"
                }
                
                response = requests.post(self.yarngpt_url, json=payload, headers=headers, stream=True)
                
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                        for chunk in response.iter_content(chunk_size=8192):
                            tmp.write(chunk)
                        audio_path = tmp.name
                else:
                    logger.warning("YarnGPT Failed (%s): %s", response.status_code, response.text)
            
            except Exception as e:
                logger.warning("YarnGPT Connection Failed: %s", e)

        # 2. Fallback to gTTS if YarnGPT failed
        if not audio_path:
            logger.info("Falling back to gTTS...")
            try:
                # Attempt to use Nigerian English TLD if available, else standard
                # 'slow=False' makes it speak at normal conversational speed
                tts = gTTS(text=text, lang='en', tld='com.ng', slow=False)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    tts.save(tmp.name)
                    audio_path = tmp.name
            except Exception as e:
                logger.error("gTTS Failed: %s", e)
                return None

        return audio_path

    def test_yarngpt_connection(self):
        """Debug utility to check YarnGPT status."""
        if not self.yarngpt_key:
            return False, "No Key Provided"
        try:
            # Simple ping with minimal text
            headers = {"Authorization": f"Bearer {self.yarngpt_key}"}
            payload = {"text": "Test", "voice": "Idera"}
            response = requests.post(self.yarngpt_url, json=payload, headers=headers)
            if response.status_code == 200:
                return True, "Connected"
            return False, f"Error {response.status_code}"
        except Exception as e:
            return False, str(e)