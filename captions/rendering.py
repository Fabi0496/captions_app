"""Finales Video-Rendering: ASS-Untertitel per FFmpeg fest ins Video einbrennen."""
import os
import subprocess
import tempfile

from .config import FFMPEG_BIN, FFPROBE_BIN
from .ass_builder import build_ass_header, build_ass_events, build_word_groups


def render_final_video(file_bytes: bytes, corrected_words: list, style_params: dict, use_qsv: bool,
                      progress_callback=None):
    """Rendert das finale Video mit eingebrannten Untertiteln."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_in:
        tmp_in.write(file_bytes)
        input_path = tmp_in.name

    output_path = input_path.replace(".mp4", "_output.mp4")
    sp = style_params

    try:
        groups = build_word_groups(corrected_words, sp["words_per_group"])

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

        ass_path = os.path.join(work_dir, ass_filename)
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
                elapsed = int(line.split("=", 1)[1]) / 1_000_000
                if progress_callback:
                    percent = min(99, 5 + int((elapsed / duration) * 94))
                    progress_callback(percent, f"Rendering läuft... {min(99, int((elapsed / duration) * 100))} %")
            elif line:
                progress_output.append(line)
        stderr = process.stderr.read() if process.stderr else ""
        return_code = process.wait()

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
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
