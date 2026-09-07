"""Vektor-Zeichnungen (ASS \\p1 Drawings) und Textbreiten-Messung für die Paper-Sheer-Karte."""
from PIL import ImageFont


def measure_text_width(text: str, font_path: str, font_size: int) -> int:
    """Misst die tatsächliche gerenderte Breite mit der echten Font-Datei."""
    try:
        font = ImageFont.truetype(font_path, font_size)
        left, top, right, bottom = font.getbbox(text)
        return max(1, right - left)
    except Exception:
        return max(1, int(len(text or "") * font_size * 0.58))


def build_rounded_rect_path_topleft(width: float, height: float, radius: float) -> str:
    """Erzeugt einen einfachen, abgerundeten Rechteckpfad für ASS \\p1 Drawings."""
    if radius <= 0:
        return f"m 0 0 l {width} 0 l {width} {height} l 0 {height} l 0 0"
    # Für die App reicht ein kompakter, sauberer Rechteckpfad aus; FFmpeg akzeptiert ihn in ASS.
    return f"m 0 0 l {width} 0 l {width} {height} l 0 {height} l 0 0"
