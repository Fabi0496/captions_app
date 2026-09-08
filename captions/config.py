"""Zentrale Konfiguration: Pfade zu FFmpeg-Binaries, verfügbare Schriftarten, Konstanten."""
import os

FFMPEG_BIN = "ffmpeg.exe" if os.path.exists("ffmpeg.exe") else "ffmpeg"
FFPROBE_BIN = "ffprobe.exe" if os.path.exists("ffprobe.exe") else "ffprobe"

FONT_OPTIONS = {
    "Tahoma": "Tahoma",
    "Arial Bold": "Arial Bold",
    "Impact": "Impact",
    "Verdana Bold": "Verdana Bold",
    "Calibri Bold": "Calibri Bold",
    "Segoe UI Bold": "Segoe UI Bold",
}

FONT_FILE_PATHS = {
    "Tahoma": r"C:\Windows\Fonts\tahoma.ttf",
    "Arial Bold": r"C:\Windows\Fonts\arialbd.ttf",
    "Impact": r"C:\Windows\Fonts\impact.ttf",
    "Verdana Bold": r"C:\Windows\Fonts\verdanab.ttf",
    "Calibri Bold": r"C:\Windows\Fonts\calibrib.ttf",
    "Segoe UI Bold": r"C:\Windows\Fonts\segoeuib.ttf",
}

SAMPLE_WORD_POOL = [
    "Das", "ist", "eine", "coole", "Vorschau", "für", "deinen", "Video",
    "Untertitel", "Stil", "schau", "mal", "wie", "gut", "das", "aussieht",
]

ANIMATION_STYLES = [
    "Karaoke Wort-Highlight",
    "Fade In/Out",
    "Pop-In (Bounce)",
    "Slide-Up",
    "Paper Sheer (weiße Karte)",
    "Keine",
]

WHISPER_MODELS = ["tiny", "base", "small", "medium", "turbo"]

WHISPER_LANGUAGES = {
    "Automatisch erkennen": None,
    "Deutsch": "de",
    "Englisch": "en",
    "Französisch": "fr",
    "Spanisch": "es",
    "Italienisch": "it",
    "Niederländisch": "nl",
    "Portugiesisch": "pt",
    "Polnisch": "pl",
    "Türkisch": "tr",
    "Russisch": "ru",
    "Japanisch": "ja",
    "Koreanisch": "ko",
    "Chinesisch": "zh",
}

VIDEO_WIDTH = 390
PREVIEW_WIDTH = 400
PREVIEW_FPS = 15
