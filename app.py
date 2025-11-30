import streamlit as st
import os

#  PAGE CONFIG 
st.set_page_config(page_title="Naija Legal Aid", layout="centered")

# Internal Modules
from legal_agent_core import LegalAgent
from doc_generator import LegalDocBuilder

#  SECURE INIT 
def get_keys():
    gemini = os.environ.get("GEMINI_API_KEY")
    yarngpt = os.environ.get("YARNGPT_API_KEY")
    
    if not gemini and "GEMINI_API_KEY" in st.secrets:
        gemini = st.secrets["GEMINI_API_KEY"]
    if not yarngpt and "YARNGPT_API_KEY" in st.secrets:
        yarngpt = st.secrets["YARNGPT_API_KEY"]
        
    return gemini, yarngpt

gemini_key, yarngpt_key = get_keys()

#  SESSION STATE 
if "messages" not in st.session_state:
    st.session_state.messages = []
if "jurisdiction" not in st.session_state:
    st.session_state.jurisdiction = "Lagos"

# UI Header
st.title("⚖️ Naija Legal Aid")
st.markdown("**Your Voice-First Legal Assistant**")

#  1. DISCLAIMER 
with st.expander("🚨 IMPORTANT DISCLAIMER - READ BEFORE USE", expanded=True):
    st.error("""
    **THIS IS NOT A LAWYER.** This AI tool provides **legal information**, NOT legal advice. 
    It is based on Nigerian statutes but may hallucinate or be outdated.
    
    * Do not rely on this for court cases.
    * Always consult a qualified Barrister for critical issues.
    * By using this tool, you accept that the developers are not liable for any actions taken.
    """)

# Check for Keys
if not gemini_key:
    st.error("System Offline. Missing Gemini API Key.")
    st.stop()

# Initialize Agent
try:
    agent = LegalAgent(gemini_key, yarngpt_key)
except Exception as e:
    st.error(f"Failed to initialize Agent: {e}")
    st.stop()

#  2. SETTINGS & DEBUG SIDEBAR 
st.sidebar.header("Settings")
jurisdiction = st.sidebar.selectbox(
    "Select Your Location (State)",
    ["Lagos", "Abuja (FCT)", "Kano", "Rivers", "Oyo", "General (Federal Law)"],
    index=0
)
st.session_state.jurisdiction = jurisdiction

st.sidebar.markdown("---")
st.sidebar.subheader("🔌 Connectivity Test")
if st.sidebar.button("Test YarnGPT Connection"):
    with st.sidebar.status("Checking YarnGPT..."):
        status, msg = agent.test_yarngpt_connection()
        if status:
            st.sidebar.success(f"Online: {msg}")
        else:
            st.sidebar.error(f"Offline: {msg}")

#  3. CHAT HISTORY 
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "audio_path" in message:
            st.audio(message["audio_path"], format="audio/mp3")
        if "doc_data" in message:
            st.download_button(
                label="📄 Download Formal Letter",
                data=message["doc_data"],
                file_name="legal_letter.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"dl_{message['id']}"
            )

# React to user input
if prompt := st.chat_input("Wetin dey happen? (e.g. My landlord lock my shop)"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner(f"Consulting {jurisdiction} Laws..."):
        full_context_prompt = f"Jurisdiction: {jurisdiction}. User Query: {prompt}"
        analysis = agent.analyze_case(full_context_prompt)
        
        if "error" in analysis:
            response_text = f"❌ Error: {analysis['error']}"
            st.chat_message("assistant").markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
        else:
            legal_issue = analysis.get('legal_issue', 'Unknown Issue')
            relevant_law = analysis.get('relevant_law', 'General Legal Principles')
            advice = analysis.get('advice_pidgin', 'No advice generated.')
            
            # Displaying the specific citation as requested
            response_md = f"**Issue:** {legal_issue}\n\n**⚖️ Citation:** *{relevant_law}*\n\n**Counsel:** {advice}"
            
            with st.chat_message("assistant"):
                st.markdown(response_md)
                
                audio_path = agent.synthesize_voice(advice)
                if audio_path:
                    st.audio(audio_path, format="audio/mp3", autoplay=True)
                
                doc_buffer = None
                if analysis.get('letter_data'):
                    doc_buffer = LegalDocBuilder.generate_letter("Concerned Citizen", analysis['letter_data'])
                    st.download_button(
                        label="📄 Download Formal Letter",
                        data=doc_buffer,
                        file_name="legal_letter.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

            msg_data = {
                "role": "assistant", 
                "content": response_md,
                "id": len(st.session_state.messages)
            }
            if audio_path:
                msg_data["audio_path"] = audio_path
            if doc_buffer:
                msg_data["doc_data"] = doc_buffer
                
            st.session_state.messages.append(msg_data)