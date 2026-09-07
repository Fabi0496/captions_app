"""Aufbau des ASS-Untertitel-Inhalts: Style-Header, Wortgruppierung, Animations-Events."""
from .utils import hex_to_ass_color, percent_to_ass_alpha, format_ass_time
from .ass_drawing import measure_text_width, build_rounded_rect_path_topleft


def build_ass_header(video_w, video_h, font_name, font_size, primary_color,
                    outline_color, pos_y_percent) -> str:
    """Erzeugt den [Script Info]/[V4+ Styles]/[Events]-Header der ASS-Datei."""
    primary = hex_to_ass_color(primary_color)
    outline = hex_to_ass_color(outline_color)
    margin_v = int(video_h * (pos_y_percent / 100))

    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_w}
PlayResY: {video_h}
ScaledBorderAndShadow: yes
WrapStyle: 2
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{primary},{primary},{outline},&H99000000,-1,0,0,0,100,100,0,0,1,2,2,2,20,20,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def build_word_groups(all_words, group_size):
    """Gruppiert eine flache Liste von Wort-Dicts (start, end, word) zu je group_size Wörtern."""
    groups = []
    current = []
    for w in all_words:
        current.append(w)
        text = w["word"].strip()
        if text.endswith((".", "!", "?")) or len(current) >= group_size:
            groups.append(current)
            current = []
    if current:
        groups.append(current)
    return groups


def build_ass_events(groups, style, video_w, video_h, primary_color, highlight_color,
                    pos_y_percent, card_opacity_percent=88, font_size=110, font_file=None,
                    card_bg_color="#FFFFFF", card_text_color="#000000",
                    card_corner_radius_percent=90) -> str:
    """Erzeugt die Dialogue-Zeilen für den gewählten Animations-Stil."""
    lines = []
    highlight = hex_to_ass_color(highlight_color)
    primary = hex_to_ass_color(primary_color)
    margin_v = int(video_h * (pos_y_percent / 100))

    target_x = video_w // 2
    target_y = video_h - margin_v
    start_y = target_y + int(video_h * 0.08)

    for group in groups:
        group_start = group[0]["start"]
        group_end = group[-1]["end"]
        start_ts = format_ass_time(group_start)
        end_ts = format_ass_time(group_end)

        if style == "Karaoke Wort-Highlight":
            for idx, w in enumerate(group):
                start = format_ass_time(w["start"])
                end = (format_ass_time(group[idx + 1]["start"])
                       if idx + 1 < len(group) else format_ass_time(group_end))
                parts = []
                for j, w2 in enumerate(group):
                    word_text = w2["word"].strip()
                    if j == idx:
                        parts.append(f"{{\\c{highlight}&}}{word_text}{{\\c{primary}&}}")
                    else:
                        parts.append(word_text)
                text = " ".join(parts)
                lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

        elif style == "Fade In/Out":
            plain_text = " ".join(w["word"].strip() for w in group)
            text = "{\\fad(200,200)}" + plain_text
            lines.append(f"Dialogue: 0,{start_ts},{end_ts},Default,,0,0,0,,{text}")

        elif style == "Pop-In (Bounce)":
            plain_text = " ".join(w["word"].strip() for w in group)
            text = ("{\\fscx60\\fscy60\\t(0,150,\\fscx110\\fscy110)"
                    "\\t(150,250,\\fscx100\\fscy100)}") + plain_text
            lines.append(f"Dialogue: 0,{start_ts},{end_ts},Default,,0,0,0,,{text}")

        elif style == "Slide-Up":
            plain_text = " ".join(w["word"].strip() for w in group)
            text = f"{{\\move({target_x},{start_y},{target_x},{target_y},0,200)}}" + plain_text
            lines.append(f"Dialogue: 0,{start_ts},{end_ts},Default,,0,0,0,,{text}")

        elif style == "Paper Sheer (weiße Karte)":
            plain_text = " ".join(w["word"].strip() for w in group)

            if font_file:
                text_w = measure_text_width(plain_text, font_file, font_size)
            else:
                text_w = int(len(plain_text) * font_size * 0.58)

            padding_x = font_size * 0.55
            padding_y = font_size * 0.40
            half_w = (text_w / 2) + padding_x
            half_h = (font_size / 2) + padding_y
            corner_radius = half_h * (card_corner_radius_percent / 100)

            card_w = half_w * 2
            card_h = half_h * 2
            card_path = build_rounded_rect_path_topleft(card_w, card_h, corner_radius)
            alpha_hex = percent_to_ass_alpha(card_opacity_percent)
            card_bg = hex_to_ass_color(card_bg_color)
            card_text_col = hex_to_ass_color(card_text_color)

            card_pos_x = target_x - half_w
            card_pos_y = target_y - half_h

            card_drawing = (
                f"{{\\an7\\pos({card_pos_x:.0f},{card_pos_y:.0f})"
                f"\\1c{card_bg}&\\1a&H{alpha_hex}&\\bord0\\shad0\\fad(150,150)\\p1}}"
                f"{card_path}{{\\p0}}"
            )
            lines.append(f"Dialogue: 0,{start_ts},{end_ts},Default,,0,0,0,,{card_drawing}")

            text_line = (
                f"{{\\an5\\pos({target_x},{target_y})\\c{card_text_col}&"
                f"\\bord0\\shad0\\fad(150,150)}}{plain_text}"
            )
            lines.append(f"Dialogue: 1,{start_ts},{end_ts},Default,,0,0,0,,{text_line}")

        else:
            plain_text = " ".join(w["word"].strip() for w in group)
            lines.append(f"Dialogue: 0,{start_ts},{end_ts},Default,,0,0,0,,{plain_text}")

    return "\n".join(lines)
