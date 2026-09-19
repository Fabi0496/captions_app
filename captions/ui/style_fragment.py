"""Fragment 1: Schrift-/Animations-Einstellungen, Live-Vorschau und Originalvideo."""
import streamlit as st
from .color_swatch_picker import color_swatch_picker
from ..config import FONT_OPTIONS, FONT_FILE_PATHS, ANIMATION_STYLES, PREVIEW_WIDTH
from ..preview import extract_preview_frame, render_animated_preview


@st.fragment
def style_fragment():
    control_col, preview_col = st.columns([1.0, 1.5])

    with control_col:
        st.markdown('<div class="step-kicker">03 / Shape the mood</div>', unsafe_allow_html=True)
        st.subheader("Style settings")
        animation_style = st.selectbox(
            "Animationsstil", ANIMATION_STYLES,
            index=ANIMATION_STYLES.index("Paper Sheer (weiße Karte)"),
        )

        words_per_group = st.slider(
            "Wörter pro Untertitel-Zeile", min_value=1, max_value=10, value=2,
            help="Wird zusätzlich bei Satzende automatisch abgebrochen."
        )
        font_choice = st.selectbox("Schriftart", list(FONT_OPTIONS.keys()), index=0)
        font_name = FONT_OPTIONS[font_choice]
        font_size = st.slider("Schriftgröße", 20, 150, 110)
        primary_color = "#FFFFFF"
        highlight_color = "#00FF00"
        outline_color = "#000000"
        pos_y_percent = 20
        card_bg_color = "#FFFFFF"
        card_text_color = "#000000"
        card_opacity_percent = 88
        card_corner_radius_percent = 90

        if animation_style.startswith("Paper Sheer"):
            card_opacity_percent = st.slider(
                "Kartentransparenz (%)", min_value=0, max_value=100, value=0,
                help="0% = voll deckend, 100% = vollständig durchsichtig"
            )
            card_bg_color = color_swatch_picker(
                "Kartenfarbe", key="card_bg_color", default="#FFFFFF"
            )
            card_text_color = color_swatch_picker(
                "Textfarbe auf Karte", key="card_text_color", default="#000000"
            )
            card_corner_radius_percent = st.slider(
                "Eckenrundung (%)", min_value=0, max_value=100, value=90,
                help="0 = eckig, 100 = maximal rund"
            )
            pos_y_percent = st.slider(
                "Vertikale Position (% von unten)", 5, 90, 20,
                help="Legt fest, wie hoch die Untertitelkarte im Video erscheint."
            )
        else:
            primary_color = color_swatch_picker(
                "Textfarbe", key="primary_color", default="#FFFFFF"
            )
            highlight_color = color_swatch_picker(
                "Highlight-Farbe (Karaoke)", key="highlight_color", default="#00FF00"
            )
            outline_color = color_swatch_picker(
                "Konturfarbe", key="outline_color", default="#000000"
            )
            pos_y_percent = st.slider("Vertikale Position (% von unten)", 5, 90, 20)

    st.session_state["style_params"] = dict(
        words_per_group=words_per_group, font_name=font_name, font_size=font_size,
        primary_color=primary_color, highlight_color=highlight_color,
        outline_color=outline_color, pos_y_percent=pos_y_percent, animation_style=animation_style,
        card_opacity_percent=card_opacity_percent, card_bg_color=card_bg_color,
        card_text_color=card_text_color, card_corner_radius_percent=card_corner_radius_percent,
        font_file=FONT_FILE_PATHS.get(font_name),
    )

    with preview_col:
        st.markdown(
            "<div class='section-kicker' style='text-align:center;'>Live canvas</div><h3 style='text-align:center; width:100%;'>Style preview</h3>",
            unsafe_allow_html=True,
        )
        if st.session_state["transcribed_words"] is not None:
            current_words = st.session_state["transcribed_words"]
            preview_signature = (
                st.session_state["file_hash"], words_per_group, font_name, font_size,
                primary_color, highlight_color, outline_color, pos_y_percent,
                animation_style, card_opacity_percent, card_bg_color,
                card_text_color, card_corner_radius_percent,
                tuple((word["word"], word["start"], word["end"]) for word in current_words),
            )
            preview_placeholder = st.empty()
            caption_placeholder = st.empty()
            if st.session_state["preview_signature"] != preview_signature:
                existing_preview = st.session_state.get("preview_video")
                if existing_preview:
                    with preview_placeholder.container(horizontal_alignment="center"):
                        st.video(existing_preview, width=PREVIEW_WIDTH, loop=True, autoplay=True, muted=True)
                else:
                    with preview_placeholder.container(horizontal_alignment="center"):
                        st.markdown(
                            f"<div style='height:{PREVIEW_WIDTH}px;'></div>",
                            unsafe_allow_html=True,
                        )
                with st.spinner("Animierte Vorschau wird aktualisiert...", show_time=True):
                    base_frame = extract_preview_frame(
                        st.session_state["file_bytes"], st.session_state["file_hash"]
                    )
                    st.session_state["preview_video"] = render_animated_preview(
                        base_frame, words_per_group, font_name, font_size,
                        primary_color, highlight_color, outline_color, pos_y_percent,
                        animation_style, card_opacity_percent, card_bg_color,
                        card_text_color, card_corner_radius_percent, current_words
                    )
                st.session_state["preview_signature"] = preview_signature
            preview_video = st.session_state["preview_video"]
            if preview_video:
                with preview_placeholder.container(horizontal_alignment="center"):
                    st.video(preview_video, width=PREVIEW_WIDTH, loop=True, autoplay=True, muted=True)
                caption_placeholder.markdown(
                    f"<div class='preview-caption'>Echte Untertitelvorschau mit {words_per_group} Wort(en) pro Zeile · Videobild ist nur ein Screenshot zur Ausrichtung</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.warning("Vorschau konnte nicht erstellt werden.")
