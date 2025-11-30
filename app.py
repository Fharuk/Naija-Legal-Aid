import streamlit as st
import os

# --- PAGE CONFIG ---
# FIX: layout must be 'centered' or 'wide'. 'mobile' is invalid.
st.set_page_config(page_title="Naija Legal Aid", layout="centered")

# Internal Modules
from legal_agent_core import LegalAgent
from doc_generator import LegalDocBuilder

# --- SECURE INIT ---
def get_keys():
    gemini = os.environ.get("GEMINI_API_KEY")
    yarngpt = os.environ.get("YARNGPT_API_KEY")
    
    # Fallback to Streamlit Secrets
    if not gemini and "GEMINI_API_KEY" in st.secrets:
        gemini = st.secrets["GEMINI_API_KEY"]
    if not yarngpt and "YARNGPT_API_KEY" in st.secrets:
        yarngpt = st.secrets["YARNGPT_API_KEY"]
        
    return gemini, yarngpt

gemini_key, yarngpt_key = get_keys()

# UI Header
st.title("⚖️ Naija Legal Aid")
st.markdown("**Your Voice-First Legal Assistant**")

# Check for Keys
if not gemini_key or not yarngpt_key:
    st.error("System Offline. Missing API Keys.")
    st.info("Please set GEMINI_API_KEY and YARNGPT_API_KEY in your environment/secrets.")
    st.stop()

# Initialize Agent
try:
    agent = LegalAgent(gemini_key, yarngpt_key)
except Exception as e:
    st.error(f"Failed to initialize Agent: {e}")
    st.stop()

# --- INPUT SECTION ---
st.info("Wetin dey happen? Tell me make we solve am.")
user_input = st.text_area("Describe your issue (e.g. Landlord wahala):", height=100)

if st.button("Get Advice"):
    if user_input:
        with st.spinner("Consulting the Constitution..."):
            # 1. AI Analysis
            analysis = agent.analyze_case(user_input)
            
            if "error" in analysis:
                st.error(f"Analysis Failed: {analysis['error']}")
            else:
                # 2. Display Results
                st.subheader("Legal Breakdown")
                st.success(f"**Issue Identified:** {analysis.get('legal_issue')}")
                
                # Pidgin Advice
                st.markdown("### 🗣️ Counsel (Pidgin)")
                st.write(f"*{analysis.get('advice_pidgin')}*")
                
                # 3. Voice Generation (YarnGPT)
                with st.spinner("Generating Voice Note..."):
                    audio_path = agent.synthesize_voice(analysis.get('advice_pidgin'))
                    if audio_path:
                        st.audio(audio_path, format="audio/mp3", autoplay=True)
                    else:
                        st.warning("Audio unavailable. Check YarnGPT quota.")

                # 4. Document Generation
                st.markdown("---")
                st.subheader("📝 Action Plan")
                st.write("We have drafted a formal letter for you to print/send.")
                
                user_name = st.text_input("Enter your full name for the signature:", "Concerned Citizen")
                
                if analysis.get('letter_data'):
                    doc_buffer = LegalDocBuilder.generate_letter(user_name, analysis['letter_data'])
                    
                    st.download_button(
                        label="Download Formal Letter (.docx)",
                        data=doc_buffer,
                        file_name="legal_letter.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
    else:
        st.warning("Abeg write something first.")