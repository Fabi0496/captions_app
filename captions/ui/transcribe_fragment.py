"""Fragment 2: Whisper-Transkription starten und Wort-für-Wort-Text korrigieren."""
import pandas as pd
import streamlit as st

from ..config import WHISPER_LANGUAGES, WHISPER_MODELS
from ..rendering import build_ass_content
from ..transcription import transcribe_video


@st.fragment
def transcribe_fragment():
    st.markdown('<div class="step-kicker">02 / Find the rhythm</div>', unsafe_allow_html=True)
    st.subheader("Transcription")
    whisper_model_size = st.selectbox("Whisper-Modell", WHISPER_MODELS, index=3)
    language_label = st.selectbox(
        "Sprache der Audiospur",
        list(WHISPER_LANGUAGES),
        help=(
            "Wenn die Sprache feststeht, kann Whisper die automatische "
            "Spracherkennung überspringen."
        ),
    )
    language = WHISPER_LANGUAGES[language_label]

    if st.button("Video transkribieren"):
        progress = st.progress(0, text="Whisper wird gestartet...")

        def update_progress(value, message):
            progress.progress(value, text=message)

        all_words = transcribe_video(
            st.session_state["file_bytes"],
            whisper_model_size,
            language=language,
            progress_callback=update_progress,
        )
        progress.empty()

        st.session_state["transcribed_words"] = all_words
        st.session_state["transcribed_file_hash"] = st.session_state["file_hash"]
        st.session_state["correction_completed"] = False
        st.rerun()

    if st.session_state["transcribed_words"] is not None:
        st.subheader("Fine-tune your words")
        st.caption(
            "Wörter/Zeiten direkt in der Tabelle anpassen. Über die Auswahl darunter "
            "kannst du eine Zeile teilen (Zeit wird halbiert) oder löschen."
        )

        words_df = pd.DataFrame(st.session_state["transcribed_words"])
        edited_df = st.data_editor(
            words_df,
            column_config={
                "start": st.column_config.NumberColumn("Start (s)", format="%.2f", step=0.05),
                "end": st.column_config.NumberColumn("Ende (s)", format="%.2f", step=0.05),
                "word": st.column_config.TextColumn("Wort", width="large"),
            },
            hide_index=True, num_rows="fixed", use_container_width=True,
            key=f"word_editor_{st.session_state['file_hash']}",
        )
        st.session_state["transcribed_words"] = edited_df.to_dict("records")
        current_words = st.session_state["transcribed_words"]

        st.markdown("**Zeile teilen oder löschen**")
        row_options = [
            f"{i}: [{w['start']:.2f}s - {w['end']:.2f}s] {w['word']}"
            for i, w in enumerate(current_words)
        ]
        col_select, col_split, col_delete = st.columns([3, 1, 1])

        with col_select:
            selected_label = st.selectbox(
                "Zeile auswählen", row_options, label_visibility="collapsed",
                key=f"row_select_{st.session_state['file_hash']}"
            )
        selected_idx = int(selected_label.split(":")[0])

        with col_split:
            if st.button("Zeile teilen", use_container_width=True):
                row = current_words[selected_idx]
                mid = (row["start"] + row["end"]) / 2
                first_half = {"start": row["start"], "end": mid, "word": row["word"]}
                second_half = {"start": mid, "end": row["end"], "word": ""}
                st.session_state["transcribed_words"] = (
                    current_words[:selected_idx] + [first_half, second_half]
                    + current_words[selected_idx + 1:]
                )
                st.rerun(scope="fragment")

        with col_delete:
            if st.button("Zeile löschen", use_container_width=True):
                st.session_state["transcribed_words"] = (
                    current_words[:selected_idx] + current_words[selected_idx + 1:]
                )
                st.rerun(scope="fragment")

        if st.button("Fertig Korrigiert", type="primary", use_container_width=True):
            st.session_state["correction_completed"] = True
            st.rerun()

        ass_content = build_ass_content(
            st.session_state["file_bytes"],
            current_words,
            st.session_state["style_params"],
        )
        st.download_button(
            "ASS-Datei herunterladen",
            data=ass_content,
            file_name="untertitel.ass",
            mime="text/plain",
            use_container_width=True,
        )
