"""Fragment 1: Schrift-/Animations-Einstellungen, Live-Vorschau und Originalvideo."""
import streamlit as st

from ..config import FONT_OPTIONS, FONT_FILE_PATHS, ANIMATION_STYLES, VIDEO_WIDTH
from ..preview import extract_preview_frame, render_animated_preview


@st.fragment
def style_fragment():
    control_col, preview_col = st.columns([1.0, 1.5])

    with control_col:
        st.subheader("Einstellungen")
        words_per_group = st.slider(
            "Wörter pro Untertitel-Zeile", min_value=1, max_value=10, value=4,
            help="Wird zusätzlich bei Satzende automatisch abgebrochen."
        )
        font_choice = st.selectbox("Schriftart", list(FONT_OPTIONS.keys()), index=0)
        font_name = FONT_OPTIONS[font_choice]
        font_size = st.slider("Schriftgröße", 20, 150, 110)
        primary_color = st.color_picker("Textfarbe", "#FFFFFF")
        highlight_color = st.color_picker("Highlight-Farbe (Karaoke)", "#00FF00")
        outline_color = st.color_picker("Konturfarbe", "#000000")
        pos_y_percent = st.slider("Vertikale Position (% von unten)", 5, 90, 20)

        st.subheader("Animation")
        animation_style = st.selectbox("Animations-Stil", ANIMATION_STYLES, index=0)

        card_opacity_percent = 88
        card_bg_color = "#FFFFFF"
        card_text_color = "#000000"
        card_corner_radius_percent = 90
        if animation_style == "Paper Sheer (weiße Karte)":
            card_opacity_percent = st.slider(
                "Kartentransparenz (%)", min_value=0, max_value=100, value=0,
                help="0% = voll deckend, 100% = vollständig durchsichtig"
            )
            card_bg_color = st.color_picker("Kartenfarbe", "#FFFFFF")
            card_text_color = st.color_picker("Textfarbe auf Karte", "#000000")
            card_corner_radius_percent = st.slider(
                "Eckenrundung (%)", min_value=0, max_value=100, value=90,
                help="0 = eckig, 100 = maximal rund"
            )

    st.session_state["style_params"] = dict(
        words_per_group=words_per_group, font_name=font_name, font_size=font_size,
        primary_color=primary_color, highlight_color=highlight_color,
        outline_color=outline_color, pos_y_percent=pos_y_percent, animation_style=animation_style,
        card_opacity_percent=card_opacity_percent, card_bg_color=card_bg_color,
        card_text_color=card_text_color, card_corner_radius_percent=card_corner_radius_percent,
        font_file=FONT_FILE_PATHS.get(font_name),
    )

    with preview_col:
        preview_left, preview_right = st.columns(2)

        with preview_left:
            st.markdown(
                "<h3 style='text-align:center; width:100%;'>Style-Vorschau</h3>",
                unsafe_allow_html=True,
            )
            video_left, video_col, video_right = st.columns([1, 3, 1])
            with video_col, st.container(width=VIDEO_WIDTH):
                if st.session_state["file_bytes"] is None:
                    st.markdown(
                        """
                        <div style='display:flex;align-items:center;justify-content:center;height:280px;border:1px solid rgba(255,255,255,0.12);border-radius:14px;background:linear-gradient(135deg,#141c2f,#0f1729);color:#cbd5e1;font-size:15px;'>
                            Vorschau-Schablone<br><span style='font-size:12px;color:#8aa0c8;'>Video wird hier eingebettet</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    with st.spinner("Vorschau wird erstellt..."):
                        base_frame = extract_preview_frame(
                            st.session_state["file_bytes"], st.session_state["file_hash"]
                        )
                        preview_video = render_animated_preview(
                            base_frame, words_per_group, font_name, font_size,
                            primary_color, highlight_color, outline_color, pos_y_percent,
                            animation_style, card_opacity_percent, card_bg_color,
                            card_text_color, card_corner_radius_percent
                        )
                    if preview_video:
                        st.video(preview_video, width=VIDEO_WIDTH, loop=True, autoplay=True, muted=True)
                        st.caption(f"Beispiel mit {words_per_group} Wort(en) pro Untertitel-Zeile")
                    else:
                        st.warning("Vorschau konnte nicht erstellt werden.")

        with preview_right:
            st.markdown(
                "<h3 style='text-align:center; width:100%;'>Originalvideo</h3>",
                unsafe_allow_html=True,
            )
            video_left, video_col, video_right = st.columns([1, 3, 1])
            with video_col, st.container(width=VIDEO_WIDTH):
                if st.session_state["file_bytes"] is None:
                    st.markdown(
                        """
                        <div style='display:flex;align-items:center;justify-content:center;height:280px;border:1px solid rgba(255,255,255,0.12);border-radius:14px;background:linear-gradient(135deg,#121a2d,#0d1525);color:#b8c2d8;font-size:15px;'>
                            Originalvideo-Schablone<br><span style='font-size:12px;color:#8aa0c8;'>Hier erscheint dein Video nach dem Upload</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.video(st.session_state["file_bytes"], width=VIDEO_WIDTH)
