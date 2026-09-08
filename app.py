"""Haupt-Einstiegspunkt: streamlit run app.py"""
import hashlib

import streamlit as st  # pyright: ignore[reportMissingImports]

from captions.ui.style_fragment import style_fragment
from captions.ui.transcribe_fragment import transcribe_fragment
from captions.ui.render_fragment import render_fragment

st.set_page_config(
    page_title="Animierte Untertitel",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --app-bg: #0b1020;
        --panel-bg: #131b2f;
        --panel-border: #263554;
        --muted: #9aa9c7;
        --accent: #7c5cff;
        --accent-2: #20d9c4;
    }
    .stApp {
        background: radial-gradient(circle at 15% 0%, #18254a 0%, var(--app-bg) 42%);
        color: #f4f7ff;
    }
    [data-testid="stHeader"] { background: rgba(11, 16, 32, 0.86); }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #10182b 0%, #0c1222 100%);
        border-right: 1px solid var(--panel-border);
    }
    [data-testid="stFileUploader"], [data-testid="stExpander"] {
        background: rgba(19, 27, 47, 0.76);
        border: 1px solid var(--panel-border);
        border-radius: 14px;
    }
    .hero {
        padding: .75rem 1.25rem;
        margin-bottom: .75rem;
        border: 1px solid var(--panel-border);
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(124, 92, 255, .22), rgba(32, 217, 196, .08));
        box-shadow: 0 18px 50px rgba(0, 0, 0, .24);
    }
    .hero h1 { margin: 0; letter-spacing: -0.03em; }
    .hero p { margin: .35rem 0 0; color: var(--muted); }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent), #5b8cff);
        border: 0;
    }
    </style>
    <div class="hero">
        <h1>Captionizer</h1>
        <p>Transkribieren, stylen und Untertitel direkt als ASS in dein Video rendern.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

for key, default in [
    ("render_result", None), ("render_error", None),
    ("transcribed_words", None), ("transcribed_file_hash", None),
    ("file_bytes", None), ("file_hash", None),
    ("preview_video", None), ("preview_signature", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

uploaded_file = st.file_uploader("Video hochladen (MP4)", type=["mp4"])

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    file_hash = hashlib.md5(file_bytes).hexdigest()

    if st.session_state["file_hash"] != file_hash:
        st.session_state["file_bytes"] = file_bytes
        st.session_state["file_hash"] = file_hash
        st.session_state["preview_video"] = None
        st.session_state["preview_signature"] = None
        st.session_state["transcribed_words"] = None
        st.session_state["transcribed_file_hash"] = None
        st.session_state["render_result"] = None
        st.session_state["render_error"] = None

    style_fragment()
    transcribe_fragment()
    render_fragment()
else:
    style_fragment()
