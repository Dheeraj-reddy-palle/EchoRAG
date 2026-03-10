import streamlit as st
import requests
import os

# Streamlit `requests` run on the server, not in the browser. 
# Inside a Docker container, the loopback address is 127.0.0.1
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="EchoRAG Assistant", page_icon="🗣️", layout="wide")

# -----------------------------------------------------------
# Custom CSS
# -----------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    /* Hide deploy, toolbar, header, footer */
    #MainMenu, header, footer {visibility: hidden;}
    .stDeployButton, [data-testid="stToolbar"],
    [data-testid="stDecoration"], [data-testid="stStatusWidget"] {display: none !important;}

    /* Title */
    .hero-title h1 {
        background: linear-gradient(90deg, #00d2ff, #7b2ff7, #ff6ec7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4rem !important;
        font-weight: 800 !important;
        text-align: center;
        margin-bottom: 0;
    }
    .hero-subtitle {
        text-align: center;
        color: #888;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #12102e 0%, #1a1a3e 100%) !important;
        border-right: 1px solid rgba(123,47,247,0.15);
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        background: none !important;
        -webkit-text-fill-color: #e8e8e8 !important;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #aaa !important;
    }
    
    /* Chat bubbles */
    .stChatMessage {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        border-radius: 18px !important;
        backdrop-filter: blur(12px);
        margin-bottom: 8px !important;
    }
    
    /* Chat input */
    .stChatInput > div {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(123,47,247,0.35) !important;
        border-radius: 24px !important;
    }
    .stChatInput textarea { color: #fff !important; }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #7b2ff7, #00d2ff) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(123,47,247,0.25) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(123,47,247,0.45) !important;
    }
    
    /* Delete buttons */
    .delete-btn button {
        background: linear-gradient(135deg, #ff4757, #ff6b81) !important;
        box-shadow: 0 4px 15px rgba(255,71,87,0.2) !important;
        font-size: 12px !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] > div {
        border: 2px dashed rgba(123,47,247,0.3) !important;
        border-radius: 14px !important;
        background: rgba(255,255,255,0.03) !important;
    }
    
    /* Spinner */
    .stSpinner > div { border-color: #7b2ff7 transparent transparent transparent !important; }
    .stSpinner > div > div { color: #b0b0ff !important; }
    
    /* Alerts */
    .stAlert {
        background: rgba(255,255,255,0.04) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }
    
    /* Text */
    .stMarkdown p, .stMarkdown li, .stMarkdown span { color: #d4d4d4 !important; }
    h1, h2, h3 { color: #e8e8e8 !important; }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(123,47,247,0.3); border-radius: 3px; }
    
    /* Selectbox & TextInput */
    .stSelectbox > div > div, .stTextInput > div > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(123,47,247,0.25) !important;
        border-radius: 10px !important;
        color: #e0e0e0 !important;
    }
    
    /* Voice transcription preview */
    .voice-preview {
        background: linear-gradient(135deg, rgba(0,210,255,0.08), rgba(123,47,247,0.08));
        border: 1px solid rgba(0,210,255,0.25);
        border-radius: 14px;
        padding: 14px 18px;
        margin: 8px 0;
        color: #e0e0e0;
        font-size: 15px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# Header
# -----------------------------------------------------------
st.markdown('<div class="hero-title"><h1>🗣️ EchoRAG</h1></div>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Your AI-powered voice & document assistant</p>', unsafe_allow_html=True)

# -----------------------------------------------------------
# Session State
# -----------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "voice_text" not in st.session_state:
    st.session_state.voice_text = None
if "current_project" not in st.session_state:
    st.session_state.current_project = None

# -----------------------------------------------------------
# Sidebar: Project Manager + Documents
# -----------------------------------------------------------
with st.sidebar:
    st.markdown("### 🧠 Projects")
    
    new_project = st.text_input("New project name", placeholder="e.g. Physics, Biology...")
    if st.button("Create Project", use_container_width=True):
        if new_project.strip():
            try:
                resp = requests.post(f"{API_URL}/projects/create?name={new_project.strip()}", timeout=5)
                if resp.status_code == 200:
                    st.session_state.current_project = new_project.strip().lower().replace(" ", "_").replace("-", "_")
                    st.rerun()
                else:
                    st.error("Failed to create project.")
            except Exception:
                st.error("Backend offline.")
        else:
            st.warning("Enter a project name.")
    
    st.markdown("---")
    
    # List projects
    try:
        proj_resp = requests.get(f"{API_URL}/projects", timeout=3)
        if proj_resp.status_code == 200:
            projects = proj_resp.json().get("projects", [])
            if projects:
                project_names = [p["name"] for p in projects]
                
                default_idx = 0
                if st.session_state.current_project in project_names:
                    default_idx = project_names.index(st.session_state.current_project)
                
                selected = st.selectbox("Select Project", project_names, index=default_idx)
                st.session_state.current_project = selected
                
                proj_info = next((p for p in projects if p["name"] == selected), None)
                if proj_info:
                    st.caption(f"{proj_info['chunks']} chunks indexed")
                
                st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
                if st.button(f"Delete '{selected}'", use_container_width=True, key="del_proj"):
                    requests.delete(f"{API_URL}/projects/{selected}")
                    st.session_state.current_project = None
                    st.session_state.messages = []
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.caption("No projects yet. Create one above!")
    except Exception:
        st.caption("Backend offline.")
    
    st.markdown("---")
    
    # Document Upload
    if st.session_state.current_project:
        st.markdown(f"### 📚 Documents in `{st.session_state.current_project}`")
        
        uploaded_files = st.file_uploader("Drop files here", type=["pdf", "txt"], accept_multiple_files=True, key="file_upload")
        
        if st.button("Process", use_container_width=True):
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    with st.spinner(f"Processing {uploaded_file.name}..."):
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/octet-stream")}
                        response = requests.post(f"{API_URL}/upload?project={st.session_state.current_project}", files=files)
                        if response.status_code == 200:
                            st.success(f"{uploaded_file.name} — {response.json().get('chunks_processed', 0)} chunks")
                        else:
                            st.error(f"Failed: {uploaded_file.name}")
                st.rerun()
            else:
                st.warning("Upload a file first.")
        
        # Show documents
        try:
            doc_resp = requests.get(f"{API_URL}/documents?project={st.session_state.current_project}", timeout=3)
            if doc_resp.status_code == 200:
                docs = doc_resp.json().get("documents", [])
                if docs:
                    for doc in docs:
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.markdown(f"**{doc['name']}**")
                            st.caption(f"{doc['chunks']} chunks")
                        with c2:
                            st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
                            if st.button("Remove", key=f"del_{doc['name']}"):
                                requests.delete(f"{API_URL}/documents/{doc['name']}?project={st.session_state.current_project}")
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
        except Exception:
            pass
    else:
        st.info("Create or select a project to start.")

# -----------------------------------------------------------
# Chat History
# -----------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------------------------------------
# Voice Input (mic right above the chat bar)
# -----------------------------------------------------------
audio_func = getattr(st, "audio_input", getattr(st, "experimental_audio_input", None))

if audio_func and st.session_state.voice_text is None:
    voice_audio = audio_func("🎙️ Click to record")
    
    if voice_audio:
        with st.spinner("Transcribing..."):
            files = {"audio_file": ("query.wav", voice_audio.getvalue(), "audio/wav")}
            try:
                resp = requests.post(f"{API_URL}/voice/transcribe", files=files)
                if resp.status_code == 200:
                    transcribed = resp.json().get("transcription", "").strip()
                    if transcribed:
                        st.session_state.voice_text = transcribed
                        st.rerun()
                    else:
                        st.warning("Could not hear any speech. Please try again.")
                else:
                    st.error("Transcription error.")
            except Exception as e:
                st.error(f"Transcription failed: {e}")

if st.session_state.voice_text:
    st.markdown(f'<div class="voice-preview">🗣️ You said: <strong>{st.session_state.voice_text}</strong></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Send", use_container_width=True, key="voice_send"):
            query = st.session_state.voice_text
            st.session_state.voice_text = None
            st.session_state.messages.append({"role": "user", "content": query})
            with st.spinner("Thinking..."):
                payload = {"query": query, "project": st.session_state.current_project}
                response = requests.post(f"{API_URL}/ask", json=payload)
                if response.status_code == 200:
                    answer = response.json().get("answer")
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.session_state.messages.append({"role": "assistant", "content": "Error generating answer."})
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True, key="voice_cancel"):
            st.session_state.voice_text = None
            st.rerun()

# -----------------------------------------------------------
# Text Input
# -----------------------------------------------------------
proj_label = st.session_state.current_project or "general"
text_query = st.chat_input(f"Ask about {proj_label}...")

if text_query:
    st.session_state.messages.append({"role": "user", "content": text_query})
    with st.chat_message("user"):
        st.markdown(text_query)
        
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            payload = {"query": text_query, "project": st.session_state.current_project}
            response = requests.post(f"{API_URL}/ask", json=payload)
            if response.status_code == 200:
                answer = response.json().get("answer")
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error("Error answering question.")
