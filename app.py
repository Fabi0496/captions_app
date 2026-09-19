"""Haupt-Einstiegspunkt: streamlit run app.py"""
import hashlib

import streamlit as st  # pyright: ignore[reportMissingImports]

from captions.ui.style_fragment import style_fragment
from captions.ui.transcribe_fragment import transcribe_fragment
from captions.ui.render_fragment import render_fragment
from captions.preview import create_default_preview_frame, render_animated_preview

st.set_page_config(
    page_title="Animierte Untertitel",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Die Startvorschau wird einmal pro Host-Prozess vorgeneriert. Dadurch ist
# direkt nach dem Öffnen bereits ein Beispiel sichtbar.
if "default_preview_video" not in st.session_state:
    with st.spinner("Animierte Startvorschau wird geladen...", show_time=True):
        st.session_state["default_preview_video"] = render_animated_preview(
            create_default_preview_frame(),
            2,
            "Tahoma",
            110,
            "#FFFFFF",
            "#00FF00",
            "#000000",
            20,
            "Paper Sheer (weiße Karte)",
            0,
            "#FFFFFF",
            "#000000",
            90,
        )

st.markdown(
    """
    <style>
    :root {
        --ink: #20211e;
        --paper: #f5f1e8;
        --paper-deep: #ebe4d5;
        --panel: #fffdf8;
        --line: #d8d0c1;
        --muted: #6c6b63;
        --coral: #ed684a;
        --lime: #d7e75f;
        --blue: #c8d9ee;
    }
    html, body, [class*="css"] { font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
    .stApp {
        background:
            radial-gradient(circle at 92% 2%, rgba(237, 104, 74, .12), transparent 26rem),
            radial-gradient(circle at 3% 38%, rgba(200, 217, 238, .42), transparent 24rem),
            var(--paper);
        color: var(--ink);
    }
    [data-testid="stHeader"] { background: rgba(245, 241, 232, .88); }
    [data-testid="stToolbar"] { visibility: hidden; }
    [data-testid="stSidebar"] { background: var(--paper-deep); border-right: 1px solid var(--line); }
    [data-testid="stAppViewContainer"] > .main {
        background-image: linear-gradient(rgba(32, 33, 30, .025) 1px, transparent 1px);
        background-size: 100% 8px;
    }
    .block-container { max-width: 1320px; padding: 3.5rem 4rem 5rem; }
    .brand-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
    .brand { color: var(--ink); font-size: .78rem; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; }
    .brand-mark { display: inline-flex; width: 1.75rem; height: 1.75rem; margin-right: .55rem; align-items: center; justify-content: center; background: var(--coral); border-radius: 50%; color: white; }
    .brand-note { color: var(--muted); font-size: .75rem; letter-spacing: .08em; text-transform: uppercase; }
    .hero {
        position: relative; overflow: hidden; padding: 2.75rem 3rem 2.6rem;
        margin-bottom: 1.25rem; border: 1px solid var(--ink); border-radius: 2px;
        background: var(--panel); box-shadow: 10px 10px 0 var(--lime);
    }
    .hero:after { content: "✦"; position: absolute; right: 2.5rem; top: 1.4rem; color: var(--coral); font-size: 4.5rem; line-height: 1; transform: rotate(12deg); }
    .hero-kicker { color: var(--coral); font-size: .72rem; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; }
    .hero h1 { max-width: 760px; margin: .65rem 0 .5rem; color: var(--ink); font-size: clamp(2.6rem, 6vw, 5.4rem); font-weight: 800; letter-spacing: -.075em; line-height: .9; }
    .hero p { max-width: 620px; margin: .9rem 0 0; color: var(--muted); font-size: 1.05rem; line-height: 1.55; }
    .upload-card { padding: 1.15rem 1.35rem .5rem; margin: 2.4rem 0 1.8rem; border: 1px dashed var(--ink); background: rgba(255, 253, 248, .7); }
    .upload-card-label { margin-bottom: .5rem; color: var(--ink); font-size: .78rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
    [data-testid="stFileUploader"] { background: transparent; border: 0; }
    [data-testid="stFileUploaderDropzone"] { min-height: 5.5rem; border: 1px dashed var(--line); border-radius: 0; background: var(--paper); }
    [data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stFileUploaderDropzoneInstructions"] *,
    [data-testid="stFileUploaderDropzone"] small,
    [data-testid="stFileUploaderDropzone"] span { color: var(--muted) !important; }
    [data-testid="stFileUploaderDropzone"] button {
        border: 1px solid var(--ink); border-radius: 0; background: var(--paper); color: var(--ink);
    }
    [data-testid="stFileUploaderDropzone"] button:hover {
        border-color: var(--ink); background: var(--ink); color: white;
    }
    [data-testid="stExpander"] { border: 1px solid var(--line); border-radius: 2px; background: var(--panel); }
    [data-testid="stVerticalBlockBorderWrapper"] { border-color: var(--line); border-radius: 2px; background: rgba(255, 253, 248, .62); }
    h2, h3 { color: var(--ink) !important; letter-spacing: -.04em; }
    h3 { font-size: 1.3rem !important; }
    .section-kicker { margin: 1.7rem 0 .35rem; color: var(--coral); font-size: .7rem; font-weight: 800; letter-spacing: .15em; text-transform: uppercase; }
    .preview-caption { text-align: center; color: var(--muted); font-size: .78rem; letter-spacing: .02em; }
    [data-testid="stProgress"] {
        padding: .35rem .55rem .45rem;
        border: 1px solid var(--line);
        border-radius: 0;
        background: #ffffff;
    }
    [data-testid="stProgress"] [role="progressbar"] {
        height: .55rem;
        overflow: hidden;
        border-radius: 999px;
        background: #ffffff !important;
    }
    [data-testid="stProgress"] [role="progressbar"] > div {
        border-radius: 999px;
        background: var(--coral) !important;
    }
    [data-testid="stProgress"] label,
    [data-testid="stProgress"] p {
        color: var(--muted) !important;
        font-size: .78rem;
    }
    [data-testid="stSpinner"] > div > div {
        border-top-color: var(--coral) !important;
        border-right-color: var(--coral) !important;
    }
    [data-testid="stSpinner"] { justify-content: center; text-align: center; }
    [data-testid="stSpinner"] > div { margin: 0 auto; }
    div.stButton > button, div.stDownloadButton > button {
        min-height: 2.7rem; border: 1px solid var(--ink); border-radius: 0;
        background: var(--ink); color: var(--paper); font-weight: 700;
        transition: transform .15s ease, box-shadow .15s ease;
    }
    div.stButton > button *,
    div.stDownloadButton > button * { color: inherit !important; }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        border-color: var(--ink); background: var(--ink); color: white;
        transform: translate(-2px, -2px); box-shadow: 4px 4px 0 var(--coral);
    }
    div.stButton > button[kind="primary"] { background: var(--coral); color: white; }
    div.stButton > button[kind="primary"] * { color: white !important; }
    input, textarea, [data-baseweb="select"] > div {
        border-radius: 0 !important; border-color: var(--line) !important;
        background: var(--panel) !important; color: var(--ink) !important;
    }
    [data-baseweb="select"] input,
    [data-baseweb="select"] [class*="singleValue"],
    [data-baseweb="select"] [class*="placeholder"],
    [data-baseweb="select"] svg { color: var(--ink) !important; fill: var(--ink) !important; }
    [role="listbox"], [role="option"] { background: var(--panel) !important; color: var(--ink) !important; }
    [role="option"]:hover { background: var(--paper-deep) !important; }
    [data-testid="stSlider"] [role="slider"] { background: var(--coral) !important; border-color: var(--coral) !important; }
    [data-testid="stSlider"] [data-baseweb="slider"] > div > div { background: var(--coral) !important; }
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span,
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] small { color: var(--ink) !important; }
    .color-picker-label, .color-picker-label span {
        color: #20211e !important;
        opacity: 1 !important;
    }
    .color-picker-label { display: flex; align-items: center; gap: 6px; margin: 0 0 4px; font-size: .875rem; line-height: 1.25rem; }
    .color-picker-help {
        display: inline-flex; align-items: center; justify-content: center;
        width: 14px; height: 14px; border: 1px solid var(--muted); border-radius: 50%;
        color: var(--muted) !important; font-size: .65rem; cursor: help;
    }
    [data-testid="stDataEditor"] { border: 1px solid var(--line); }
    label, [data-testid="stMarkdownContainer"] p { color: var(--ink); }
    .footer-note { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--line); color: var(--muted); font-size: .75rem; }
    </style>
    <div class="brand-row">
        <div class="brand"><span class="brand-mark">C</span> Captionizer studio</div>
        <div class="brand-note">turn sound into motion</div>
    </div>
    <div class="hero">
        <div class="hero-kicker">Video captioning, reimagined</div>
        <h1>Give every word a little more life.</h1>
        <p>Transkribiere, style und rendere animierte Untertitel direkt in dein Video – schnell, präzise und mit deinem eigenen Look.</p>
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

st.markdown(
    '<div class="upload-card"><div class="upload-card-label">01 / Start with a video</div>',
    unsafe_allow_html=True,
)
uploaded_file = st.file_uploader("Video hochladen (MP4)", type=["mp4"])
st.markdown("</div>", unsafe_allow_html=True)

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

st.markdown(
    '<div class="footer-note">Captionizer studio · Designed for creators who care about the details.</div>',
    unsafe_allow_html=True,
)
