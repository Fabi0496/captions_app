"""Finales Video-Rendering: ASS-Untertitel per FFmpeg fest ins Video einbrennen."""
import os
import subprocess
import tempfile
import time

from .config import FFMPEG_BIN, FFPROBE_BIN
from .ass_builder import build_ass_header, build_ass_events, build_word_groups


def _remove_file(path: str) -> None:
    """Entfernt eine temporär gesperrte Datei unter Windows mit kurzen Wiederholungen."""
    for attempt in range(5):
        if not os.path.exists(path):
            return
        try:
            os.remove(path)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.2)


def build_ass_content(file_bytes: bytes, corrected_words: list, style_params: dict) -> str:
    """Erzeugt die ASS-Datei ohne das Video zu rendern."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_in:
        tmp_in.write(file_bytes)
        input_path = tmp_in.name

    try:
        probe = subprocess.run(
            [FFPROBE_BIN, "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", input_path],
            capture_output=True, text=True, check=True,
        )
        video_w, video_h = map(int, probe.stdout.strip().split("x"))
        sp = style_params
        groups = build_word_groups(corrected_words, sp["words_per_group"])
        return (
            build_ass_header(video_w, video_h, sp["font_name"], sp["font_size"],
                             sp["primary_color"], sp["outline_color"], sp["pos_y_percent"])
            + build_ass_events(
                groups, sp["animation_style"], video_w, video_h,
                sp["primary_color"], sp["highlight_color"], sp["pos_y_percent"],
                sp["card_opacity_percent"], sp["font_size"], sp["font_file"],
                sp["card_bg_color"], sp["card_text_color"], sp["card_corner_radius_percent"],
            )
        )
    finally:
        _remove_file(input_path)


def render_final_video(file_bytes: bytes, corrected_words: list, style_params: dict, use_qsv: bool,
                      progress_callback=None):
    """Rendert das finale Video mit eingebrannten Untertiteln."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_in:
        tmp_in.write(file_bytes)
        input_path = tmp_in.name

    output_path = input_path.replace(".mp4", "_output.mp4")
    ass_path = os.path.join(os.path.dirname(input_path), "untertitel_render.ass")
    sp = style_params
    process = None

    try:
        probe = subprocess.run(
            [FFPROBE_BIN, "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", input_path],
            capture_output=True, text=True,
        )
        video_w, video_h = map(int, probe.stdout.strip().split("x"))

        duration_probe = subprocess.run(
            [FFPROBE_BIN, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", input_path],
            capture_output=True, text=True, check=True,
        )
        duration = max(float(duration_probe.stdout.strip()), 0.01)

        groups = build_word_groups(corrected_words, sp["words_per_group"])
        ass_content = (
            build_ass_header(video_w, video_h, sp["font_name"], sp["font_size"],
                             sp["primary_color"], sp["outline_color"], sp["pos_y_percent"])
            + build_ass_events(
                groups, sp["animation_style"], video_w, video_h,
                sp["primary_color"], sp["highlight_color"], sp["pos_y_percent"],
                sp["card_opacity_percent"], sp["font_size"], sp["font_file"],
                sp["card_bg_color"], sp["card_text_color"], sp["card_corner_radius_percent"],
            )
        )

        work_dir = os.path.dirname(input_path)
        input_filename = os.path.basename(input_path)
        ass_filename = "untertitel_render.ass"
        output_filename = os.path.basename(output_path)

        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(ass_content)

        if use_qsv:
            cmd = [FFMPEG_BIN, "-y", "-i", input_filename, "-vf", f"ass={ass_filename}",
                   "-c:v", "h264_qsv", "-c:a", "aac", output_filename]
        else:
            cmd = [FFMPEG_BIN, "-y", "-i", input_filename, "-vf", f"ass={ass_filename}",
                   "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", output_filename]

        cmd[1:1] = ["-progress", "pipe:1", "-nostats", "-loglevel", "error"]
        if progress_callback:
            progress_callback(5, "FFmpeg rendert das Video...")

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=work_dir,
        )
        progress_output = []
        assert process.stdout is not None
        for line in process.stdout:
            line = line.strip()
            if line.startswith("out_time_ms="):
                raw_elapsed = line.split("=", 1)[1]
                if raw_elapsed == "N/A":
                    continue
                try:
                    elapsed = int(raw_elapsed) / 1_000_000
                except ValueError:
                    progress_output.append(line)
                    continue
                if progress_callback:
                    percent = min(99, 5 + int((elapsed / duration) * 94))
                    progress_callback(percent, f"Rendering läuft... {min(99, int((elapsed / duration) * 100))} %")
            elif line:
                progress_output.append(line)
        stderr = process.stderr.read() if process.stderr else ""
        return_code = process.wait()

        if return_code != 0 and use_qsv:
            fallback_cmd = [
                FFMPEG_BIN, "-y", "-i", input_filename, "-vf", f"ass={ass_filename}",
                "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", output_filename,
            ]
            fallback_cmd[1:1] = ["-progress", "pipe:1", "-nostats", "-loglevel", "error"]
            if progress_callback:
                progress_callback(5, "QSV nicht verfügbar – CPU-Rendering wird verwendet...")
            fallback = subprocess.run(
                fallback_cmd, cwd=work_dir, capture_output=True, text=True,
            )
            return_code = fallback.returncode
            stderr = fallback.stderr
            progress_output = [fallback.stdout] if fallback.stdout else progress_output

        if return_code != 0:
            return {"success": False, "video_bytes": None, "ass_content": ass_content,
                    "error": (stderr or "\n".join(progress_output))[-2000:]}

        with open(output_path, "rb") as f:
            video_bytes_result = f.read()

        if progress_callback:
            progress_callback(100, "Rendering abgeschlossen")
        return {"success": True, "video_bytes": video_bytes_result,
                "ass_content": ass_content, "error": None}

    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        _remove_file(input_path)
        _remove_file(output_path)
        _remove_file(ass_path)
