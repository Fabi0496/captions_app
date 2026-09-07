"""Kleine Hilfsfunktionen: Dateinamen bereinigen, Farb-/Zeit-Konvertierungen für ASS."""
import re


def hex_to_ass_color(hex_color: str) -> str:
    """Wandelt #RRGGBB in ASS-Farbformat &HBBGGRR& um."""
    value = hex_color.strip().lstrip("#")
    if len(value) != 6:
        value = "FFFFFF"
    r, g, b = value[0:2], value[2:4], value[4:6]
    return f"&H{int(b, 16):02X}{int(g, 16):02X}{int(r, 16):02X}&"


def percent_to_ass_alpha(percent: int) -> str:
    """Wandelt Prozent in ASS-Alpha-Hex um: 0 = sichtbar, 255 = unsichtbar."""
    percent = max(0, min(100, int(percent)))
    alpha = int((percent / 100) * 255)
    return f"{alpha:02X}"


def format_ass_time(seconds: float) -> str:
    """Formatiert Sekunden im ASS-Zeitformat H:MM:SS.cc."""
    total_ms = int(round(seconds * 100))
    hours, remainder = divmod(total_ms, 360000)
    minutes, remainder = divmod(remainder, 6000)
    secs, centis = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def sanitize_filename(value: str, fallback: str) -> str:
    """Bereinigt Dateinamen für Dateiendungen und Sonderzeichen."""
    clean = re.sub(r"[^A-Za-z0-9_\- ]+", "", (value or fallback)).strip()
    return clean or fallback
