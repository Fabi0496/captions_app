"""Fragment 3: Finales Rendering, Ergebnisanzeige und Dateinamen-Export."""
import streamlit as st

from ..config import VIDEO_WIDTH
from ..rendering import render_final_video
from ..utils import sanitize_filename


@st.fragment
def render_fragment():
    if st.session_state["correction_completed"]:
        st.markdown('<div class="step-kicker">04 / Make it real</div>', unsafe_allow_html=True)
        st.subheader("Render your final video")

        if st.button("Animierte Untertitel erstellen"):
            progress = st.progress(0, text="Rendering wird vorbereitet...")

            def update_progress(value, message):
                progress.progress(value, text=message)

            result = render_final_video(
                st.session_state["file_bytes"],
                st.session_state["transcribed_words"],
                st.session_state["style_params"],
                progress_callback=update_progress,
            )
            progress.empty()

            if not result["success"]:
                st.session_state["render_error"] = result["error"]
                st.session_state["render_result"] = None
            else:
                st.session_state["render_result"] = {
                    "video_bytes": result["video_bytes"],
                    "ass_content": result["ass_content"],
                }
                st.session_state["render_error"] = None

    if st.session_state.get("render_error"):
        st.error("FFmpeg-Fehler:")
        st.code(st.session_state["render_error"])

    if st.session_state["render_result"] is not None:
        st.success("Fertig! Hier ist dein Video mit animierten Untertiteln:")
        with st.container(horizontal_alignment="center"):
            st.video(st.session_state["render_result"]["video_bytes"], width=VIDEO_WIDTH)

        col1, col2 = st.columns(2)
        with col1:
            mp4_filename_input = st.text_input("Videoname (Export)", value="video_animiert")
            final_mp4_name = sanitize_filename(mp4_filename_input, "video_animiert") + ".mp4"
            st.download_button(
                f"Video herunterladen ({final_mp4_name})",
                st.session_state["render_result"]["video_bytes"],
                file_name=final_mp4_name, mime="video/mp4",
            )
        with col2:
            ass_filename_input = st.text_input("Untertitelname (Export)", value="untertitel")
            final_ass_name = sanitize_filename(ass_filename_input, "untertitel") + ".ass"
            st.download_button(
                f"ASS-Datei herunterladen ({final_ass_name})",
                st.session_state["render_result"]["ass_content"],
                file_name=final_ass_name, mime="text/plain",
            )
