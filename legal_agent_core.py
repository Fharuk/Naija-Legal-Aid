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
    Orchestrates Legal Reasoning (Gemini) and Voice Synthesis (YarnGPT + gTTS Fallback).
    """
    def __init__(self, gemini_key: str, yarngpt_key: str = None):
        if not gemini_key:
            raise ValueError("API Key for Gemini is required.")
        
        genai.configure(api_key=gemini_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        
        self.yarngpt_key = yarngpt_key
        # CORRECTED ENDPOINT from user documentation
        self.yarngpt_url = "https://yarngpt.ai/api/v1/tts" 

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
            clean_text = response.text.replace('```json', '').replace('```', '')
            return json.loads(clean_text)
        except Exception as e:
            logger.error(f"Gemini Error: {e}")
            return {"error": str(e)}

    def synthesize_voice(self, text: str):
        """
        Converts text to speech.
        Strategy: Try YarnGPT (Nigerian Accent) -> Fail -> Fallback to gTTS.
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
                    "voice": "Idera", # Using a valid voice from docs
                    "response_format": "mp3"
                }
                
                response = requests.post(self.yarngpt_url, json=payload, headers=headers, stream=True)
                
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                        for chunk in response.iter_content(chunk_size=8192):
                            tmp.write(chunk)
                        audio_path = tmp.name
                        logger.info("YarnGPT Synthesis Successful")
                else:
                    logger.warning(f"YarnGPT Failed ({response.status_code}): {response.text}")
            
            except Exception as e:
                logger.warning(f"YarnGPT Connection Failed: {e}")

        # 2. Fallback to gTTS if YarnGPT failed
        if not audio_path:
            logger.info("Falling back to gTTS...")
            try:
                tts = gTTS(text=text, lang='en', slow=False)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    tts.save(tmp.name)
                    audio_path = tmp.name
            except Exception as e:
                logger.error(f"gTTS Failed: {e}")
                return None

        return audio_path