# Naija-Legal-Aid

⚖️ Naija Legal Aid: Voice-First AI Legal Assistant

Naija Legal Aid is an AI-powered civic tech application designed to democratize access to legal information in Nigeria. It bridges the gap between complex legal statutes and the everyday citizen by providing simplified advice in Pidgin English, synthesized audio guidance, and automated formal document generation.

🔗 Live Demo: https://naija-legal-aid-bnwwrslbvyi8rmtpnsqhye.streamlit.app

🚀 Key Features

1. Voice-First Accessibility

Problem: Many Nigerians are intimidated by text-heavy legal jargon.

Solution: The app speaks back to the user. It uses a Hybrid Voice Engine that attempts to use YarnGPT (for authentic Nigerian accents) and seamlessly falls back to gTTS (Google Text-to-Speech) if the primary service is unavailable, ensuring 100% uptime for audio guidance.

2. Context-Aware Legal Reasoning

Intelligence: Powered by Google Gemini 2.5 Flash, the system analyzes user queries (e.g., "Landlord lock my shop") against specific Nigerian statutes.

Jurisdiction Logic: A sidebar selector allows users to specify their location (Lagos, Abuja, Kano, etc.), enabling the AI to cite the correct local laws (e.g., Lagos Tenancy Law 2011 vs. Recovery of Premises Act).

Citation Engine: The AI is prompted to explicitly cite the relevant section of the law to build trust and authority.

3. Automated Action (Document Generator)

Problem: Knowing your rights is one thing; enforcing them is another.

Solution: The app features a Local Document Engine (python-docx) that automatically drafts a formal, professionally formatted Letter of Demand or Petition based on the user's specific situation. This file is generated instantly in-memory, requiring no external cloud storage dependencies.

4. Safety & Compliance

Disclaimer Protocol: A mandatory disclaimer acts as a guardrail, clarifying that the AI provides legal information, not legal advice, protecting both the user and the developer.

Chat History: The interface maintains a conversational context, allowing users to ask follow-up questions without losing the thread of the legal issue.

🛠️ Technical Architecture

Tech Stack

Frontend: Streamlit (Python)

AI Core: Google Gemini 2.5 Flash (via google-generativeai)

Voice Synthesis: Hybrid (YarnGPT API + gTTS Library)

Document Engine: python-docx

Deployment: Streamlit Community Cloud

Application Flow

Input: User selects Jurisdiction and types/speaks a query.

Analysis: Gemini processes the query + jurisdiction context to extract:

The Legal Issue

Specific Citation

Pidgin Advice

Formal Letter Metadata

Synthesis:

Text advice is displayed.

Audio is generated (YarnGPT/gTTS).

Word Document is compiled (.docx).

Output: User listens to advice and downloads the formal letter.

💻 Installation & Local Setup

Prerequisites

Python 3.10+

Google Gemini API Key

(Optional) YarnGPT API Key

Step 1: Clone Repository

git clone [https://github.com/Fharuk/naija-legal-aid.git](https://github.com/Fharuk/naija-legal-aid.git)
cd naija-legal-aid


Step 2: Install Dependencies

pip install -r requirements.txt


Step 3: Configure Credentials

Create a .env file or export your keys:

export GEMINI_API_KEY="your_api_key_here"
# Optional
export YARNGPT_API_KEY="your_yarngpt_key_here"


Step 4: Run Application

streamlit run app.py


🛡️ Disclaimer

This tool is for informational purposes only. It is not a substitute for professional legal counsel from a qualified Barrister and Solicitor of the Supreme Court of Nigeria.

Built with ❤️ for a more just Nigeria.