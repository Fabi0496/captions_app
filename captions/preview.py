"""Live-Vorschau: Frame-Extraktion aus dem Original-Video + animiertes Style-Beispiel."""
import os
import subprocess
import tempfile

import streamlit as st
from PIL import Image, ImageDraw

from .config import (
    FFMPEG_BIN, FFPROBE_BIN, SAMPLE_WORD_POOL, FONT_FILE_PATHS, PREVIEW_FPS,
    PREVIEW_MAX_DURATION,
)
from .ass_builder import build_ass_header, build_ass_events, build_word_groups


def generate_sample_words(count: int):
    """Erzeugt count Beispielwörter mit fortlaufenden Zeitstempeln für die Vorschau."""
    words = []
    t = 0.0
    for i in range(count):
        w = SAMPLE_WORD_POOL[i % len(SAMPLE_WORD_POOL)]
        words.append({"word": f" {w}", "start": t, "end": t + 0.35})
        t += 0.4
    return words, t


@st.cache_data(show_spinner=False)
def create_default_preview_frame() -> bytes:
    """Erzeugt einen neutralen Hintergrund für die sofort verfügbare Startvorschau."""
    image = Image.new("RGB", (1280, 720), "#141c2f")
    draw = ImageDraw.Draw(image)
    for y in range(image.height):
        blend = y / max(image.height - 1, 1)
        color = (
            int(24 - 10 * blend),
            int(37 - 16 * blend),
            int(74 - 24 * blend),
        )
        draw.line((0, y, image.width, y), fill=color)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_out:
        image.save(tmp_out, format="PNG")
        frame_path = tmp_out.name
    try:
        with open(frame_path, "rb") as frame_file:
            return frame_file.read()
    finally:
        os.remove(frame_path)


@st.cache_data(show_spinner=False)
def extract_preview_frame(video_bytes: bytes, cache_key: str) -> bytes:
    """Extrahiert ein Frame aus der Videomitte (gecached pro Video-Hash)."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_in:
        tmp_in.write(video_bytes)
        in_path = tmp_in.name

    frame_path = in_path.replace(".mp4", "_frame.png")
    probe = subprocess.run(
        [FFPROBE_BIN, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", in_path],
        capture_output=True, text=True,
    )
    try:
        duration = float(probe.stdout.strip())
    except ValueError:
        duration = 1.0
    seek_time = max(0.1, duration / 2)

    subprocess.run(
        [FFMPEG_BIN, "-y", "-ss", str(seek_time), "-i", in_path, "-frames:v", "1", frame_path],
        capture_output=True,
    )
    with open(frame_path, "rb") as f:
        frame_bytes = f.read()
    os.remove(in_path)
    os.remove(frame_path)
    return frame_bytes


@st.cache_data(show_spinner=False)
def create_display_video(video_bytes: bytes, cache_key: str) -> bytes:
    """Erzeugt eine kleine Anzeigeversion, damit große Uploads den Browser nicht überlasten."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_in:
        tmp_in.write(video_bytes)
        in_path = tmp_in.name

    out_path = in_path.replace(".mp4", "_display.mp4")
    try:
        result = subprocess.run(
            [
                FFMPEG_BIN, "-y", "-i", in_path,
                "-vf", "scale='min(360,iw)':-2",
                "-c:v", "libx264", "-preset", "ultrafast", "-tune", "fastdecode",
                "-crf", "35", "-threads", "0", "-pix_fmt", "yuv420p", "-an",
                "-movflags", "+faststart",
                out_path,
            ],
            capture_output=True, text=True,
        )
        if result.returncode != 0 or not os.path.exists(out_path):
            raise RuntimeError(f"FFmpeg konnte die Anzeigeversion nicht erstellen: {result.stderr}")
        with open(out_path, "rb") as f:
            return f.read()
    finally:
        for path in (in_path, out_path):
            if os.path.exists(path):
                os.remove(path)


@st.cache_data(show_spinner=False)
def render_animated_preview(frame_bytes, group_size, font_name, font_size, primary_color,
                          highlight_color, outline_color, pos_y_percent, animation_style,
                          card_opacity_percent, card_bg_color, card_text_color,
                          card_corner_radius_percent, preview_words=None):
    """Brennt den aktuellen Style mit Transkripttext auf ein kurzes Vorschauvideo."""
    work_dir = tempfile.mkdtemp()
    frame_path = os.path.join(work_dir, "frame.png")
    with open(frame_path, "wb") as f:
        f.write(frame_bytes)

    probe = subprocess.run(
        [FFPROBE_BIN, "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", frame_path],
        capture_output=True, text=True,
    )
    if probe.returncode != 0 or not probe.stdout.strip():
        return None
    try:
        w, h = map(int, probe.stdout.strip().split("x"))
    except ValueError:
        return None

    if preview_words is None:
        preview_words = generate_sample_words(len(SAMPLE_WORD_POOL))[0]
    else:
        preview_words = [
            {**word, "end": min(float(word["end"]), PREVIEW_MAX_DURATION)}
            for word in preview_words
            if float(word["start"]) < PREVIEW_MAX_DURATION
        ]
    last_end = max((word["end"] for word in preview_words), default=0.0)
    total_duration = min(
        max(last_end + 0.8, 1.0),
        PREVIEW_MAX_DURATION,
    )

    ass_content = (
        build_ass_header(w, h, font_name, font_size, primary_color, outline_color, pos_y_percent)
        + build_ass_events(
            build_word_groups(preview_words, group_size), animation_style, w, h,
            primary_color, highlight_color, pos_y_percent,
            card_opacity_percent, font_size, FONT_FILE_PATHS.get(font_name),
            card_bg_color, card_text_color, card_corner_radius_percent,
        )
    )

    ass_path = os.path.join(work_dir, "style.ass")
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content)

    out_path = os.path.join(work_dir, "preview.mp4")
    result = subprocess.run(
        [
            FFMPEG_BIN, "-y", "-loop", "1", "-i", "frame.png",
            "-t", str(total_duration), "-vf",
            "ass=style.ass",
            "-r", str(PREVIEW_FPS), "-an",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            "preview.mp4",
        ],
        capture_output=True, text=True, cwd=work_dir,
    )

    output_bytes = None
    if result.returncode == 0 and os.path.exists(out_path):
        with open(out_path, "rb") as f:
            output_bytes = f.read()

    for p in [frame_path, ass_path, out_path]:
        if os.path.exists(p):
            os.remove(p)
    os.rmdir(work_dir)
    return output_bytes
