"""Whisper-Transkription mit Wort-Zeitstempeln."""
import os
import queue
import re
import subprocess
import tempfile
import threading
from contextlib import redirect_stdout

import whisper

from .config import FFPROBE_BIN


TIMESTAMP_PATTERN = re.compile(r"\[(\d+):(\d+(?:\.\d+)?)\s+-->\s+")


class _OutputQueue:
    def __init__(self, output_queue):
        self.output_queue = output_queue

    def write(self, text):
        if text:
            self.output_queue.put(text)
        return len(text)

    def flush(self):
        pass


def transcribe_video(
    file_bytes: bytes,
    model_size: str,
    progress_callback=None,
    language: str | None = None,
):
    """Transkribiert die Videodatei und gibt eine flache Liste von Wort-Dicts zurück."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_in:
        tmp_in.write(file_bytes)
        input_path = tmp_in.name

    try:
        duration_probe = subprocess.run(
            [
                FFPROBE_BIN, "-v", "error",
                "-show_entries", "format=duration",
                "-of", "csv=p=0", input_path,
            ],
            capture_output=True, text=True,
        )
        try:
            video_duration = max(float(duration_probe.stdout.strip()), 0.01)
        except ValueError:
            video_duration = None

        if progress_callback:
            progress_callback(5, "Whisper-Modell wird geladen...")
        model = whisper.load_model(model_size)
        if progress_callback:
            progress_callback(25, "Audio wird analysiert...")
        output_queue = queue.Queue()
        result_holder = {}

        def transcribe_worker():
            try:
                with redirect_stdout(_OutputQueue(output_queue)):
                    result_holder["result"] = model.transcribe(
                        input_path,
                        verbose=True,
                        word_timestamps=True,
                        language=language,
                    )
            except Exception as error:
                result_holder["error"] = error

        worker = threading.Thread(target=transcribe_worker)
        worker.start()
        while worker.is_alive():
            try:
                output = output_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            for match in TIMESTAMP_PATTERN.finditer(output):
                timestamp = int(match.group(1)) * 60 + float(match.group(2))
                if progress_callback and video_duration is not None:
                    progress = 25 + int(min(timestamp / video_duration, 1.0) * 70)
                    progress_callback(
                        progress,
                        f"Video erkannt bis {timestamp:.1f} / {video_duration:.1f} Sekunden",
                    )
        worker.join()
        while not output_queue.empty():
            output = output_queue.get_nowait()
            for match in TIMESTAMP_PATTERN.finditer(output):
                timestamp = int(match.group(1)) * 60 + float(match.group(2))
                if progress_callback and video_duration is not None:
                    progress = 25 + int(min(timestamp / video_duration, 1.0) * 70)
                    progress_callback(
                        progress,
                        f"Video erkannt bis {timestamp:.1f} / {video_duration:.1f} Sekunden",
                    )
        if "error" in result_holder:
            raise result_holder["error"]
        result = result_holder["result"]

        all_words = []
        segments = result["segments"]
        total_segments = max(len(segments), 1)
        last_timestamp = 0.0
        for index, seg in enumerate(segments, start=1):
            for w in seg.get("words", []):
                all_words.append({
                    "start": w["start"],
                    "end": w["end"],
                    "word": w["word"].strip(),
                })
            last_timestamp = max(last_timestamp, float(seg.get("end", last_timestamp)))
            if progress_callback:
                if video_duration is not None:
                    progress = 25 + int(min(last_timestamp / video_duration, 1.0) * 70)
                    progress_message = (
                        f"Video erkannt bis {last_timestamp:.1f} / "
                        f"{video_duration:.1f} Sekunden"
                    )
                else:
                    progress = 25 + int(index / total_segments * 70)
                    progress_message = f"Zeitstempel werden verarbeitet ({index}/{total_segments})"
                progress_callback(
                    progress,
                    progress_message,
                )
        if progress_callback:
            progress_callback(100, "Transkription gleich abgeschlossen...")
        return all_words
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
