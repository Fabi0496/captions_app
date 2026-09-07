"""Whisper-Transkription mit Wort-Zeitstempeln."""
import os
import tempfile

import whisper


def transcribe_video(file_bytes: bytes, model_size: str, progress_callback=None):
    """Transkribiert die Videodatei und gibt eine flache Liste von Wort-Dicts zurück."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_in:
        tmp_in.write(file_bytes)
        input_path = tmp_in.name

    try:
        if progress_callback:
            progress_callback(5, "Whisper-Modell wird geladen...")
        model = whisper.load_model(model_size)
        if progress_callback:
            progress_callback(25, "Audio wird analysiert...")
        result = model.transcribe(input_path, verbose=True, word_timestamps=True)

        all_words = []
        segments = result["segments"]
        total_segments = max(len(segments), 1)
        for index, seg in enumerate(segments, start=1):
            for w in seg.get("words", []):
                all_words.append({
                    "start": w["start"],
                    "end": w["end"],
                    "word": w["word"].strip(),
                })
            if progress_callback:
                progress_callback(
                    25 + int(index / total_segments * 70),
                    f"Zeitstempel werden verarbeitet ({index}/{total_segments})",
                )
        if progress_callback:
            progress_callback(100, "Transkription gleich abgeschlossen...")
        return all_words
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
