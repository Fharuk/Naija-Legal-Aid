import streamlit as st
import os

# --- PAGE CONFIG MUST BE FIRST ---
st.set_page_config(page_title="Naija Legal Aid", layout="mobile")

# Internal Modules (Import after page config to be safe)
from legal_agent_core import LegalAgent
from doc_generator import LegalDocBuilder

# Secure Init
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

if not gemini_key or not yarngpt_key:
    st.error("System Offline. Missing API Keys.")
    st.info("Ensure GEMINI_API_KEY and YARNGPT_API_KEY are set.")
    st.stop()

# Initialize Agent
agent = LegalAgent(gemini_key, yarngpt_key)

# Input Section
st.info("Talk to me. Wetin dey happen? (e.g., Landlord wahala, Police harassment)")
user_input = st.text_area("Describe your issue here:", height=100)

if st.button("Get Legal Advice"):
    if user_input:
        with st.spinner("Consulting the Constitution..."):
            # 1. AI Analysis
            analysis = agent.analyze_case(user_input)
            
            if "error" in analysis:
                st.error(f"Analysis Failed: {analysis['error']}")
            else:
                # 2. Display Advice
                st.subheader("Legal Advice")
                st.success(f"**Issue:** {analysis.get('legal_issue')}")
                st.write(f"🗣️ **Counsel:** {analysis.get('advice_pidgin')}")
                
                # 3. Voice Synthesis (YarnGPT)
                with st.spinner("Generating Voice Note..."):
                    audio_path = agent.synthesize_voice(analysis.get('advice_pidgin'))
                    if audio_path:
                        st.audio(audio_path, format="audio/mp3", autoplay=True)
                    else:
                        st.warning("Voice synthesis unavailable (Check YarnGPT Key/Quota).")

                # 4. Document Generation
                st.markdown("---")
                st.subheader("Action Plan")
                st.write("We have drafted a formal letter for you. Download below.")
                
                user_name = st.text_input("Your Full Name (for the letter signature)", "Concerned Citizen")
                
                if analysis.get('letter_data'):
                    doc_buffer = LegalDocBuilder.generate_letter(user_name, analysis['letter_data'])
                    
                    st.download_button(
                        label="📄 Download Formal Letter (.docx)",
                        data=doc_buffer,
                        file_name="legal_letter.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
    else:
        st.warning("Abeg write something first.")