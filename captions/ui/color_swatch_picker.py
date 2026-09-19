"""Wiederverwendbarer Farbkreis-Picker (Grid aus Farbkreisen statt Standard-Colorpicker).

Nutzt Streamlits eingebautes Verhalten, wonach jedes geschlüsselte Widget (key=...)
automatisch eine CSS-Klasse "st-key-<key>" auf seinem Wrapper-Element bekommt. Damit
lässt sich jeder Button direkt und zuverlässig per CSS ansprechen - ganz ohne
Positions-/Sibling-Selektoren, die sich zwischen Streamlit-Versionen verschieben
können (siehe vorherige Version dieser Datei für den fragileren Ansatz).
"""
import streamlit as st

PALETTE_COLORS = [
    "#000000", "#FFFFFF", "#E53935", "#FB8C00",
    "#FDD835", "#43A047", "#1E88E5", "#8E24AA",
]

_SWATCH_SIZE_PX = 22


def _swatch_css(button_key: str, color: str, selected: bool) -> str:
    """CSS-Regel für einen einzelnen Swatch-Button, adressiert über seine
    automatisch von Streamlit vergebene .st-key-<button_key>-Klasse."""
    ring = (
        "box-shadow: 0 0 0 2px #0E1117, 0 0 0 4px #7C5CFF !important;"
        if selected else ""
    )
    return (
        f'.st-key-{button_key} button {{'
        f'background-color: {color} !important;'
        f'border: 1px solid rgba(255,255,255,0.25) !important;'
        f'width: {_SWATCH_SIZE_PX}px !important;'
        f'height: {_SWATCH_SIZE_PX}px !important;'
        f'min-height: {_SWATCH_SIZE_PX}px !important;'
        f'min-width: {_SWATCH_SIZE_PX}px !important;'
        f'aspect-ratio: 1 / 1 !important;'
        f'padding: 0 !important;'
        f'border-radius: 50% !important;'
        f'margin: 2px auto !important;'
        f'{ring}'
        f'}}'
    )


def _custom_color_css(widget_key: str, color: str) -> str:
    return (
        f".st-key-{widget_key} input {{"
        f"background-color: {color} !important;"
        f"border-color: {color} !important;"
        f"}}"
        f".st-key-{widget_key} button {{"
        f"background-color: {color} !important;"
        f"}}"
    )


def color_swatch_picker(label: str, key: str, default: str = "#FFFFFF") -> str:
    """Zeigt ein Farbkreis-Raster (kräftige Farben + Pastelltöne) plus ein Feld
    für eine eigene Farbe. Gibt den aktuell gewählten Hex-Wert (#RRGGBB) zurück.

    Nutzung als Ersatz für st.color_picker(...):
        primary_color = color_swatch_picker("Textfarbe", key="primary_color", default="#FFFFFF")
    """
    if key not in st.session_state:
        st.session_state[key] = default.upper()
    current = st.session_state[key]

    css_rules = []

    st.markdown(
        f'<div class="color-picker-label"><span>{label}</span>'
        '<span class="color-picker-help" title="Für eigene Farbe auf das Farbfeld klicken">?</span></div>',
        unsafe_allow_html=True,
    )

    custom_placeholder = st.empty()

    # Zweite Zeile: acht Farben nebeneinander.
    palette_columns = st.columns(len(PALETTE_COLORS))
    for i, color in enumerate(PALETTE_COLORS):
        button_key = f"{key}_v3_p{i}"
        with palette_columns[i]:
            if st.button(" ", key=button_key):
                st.session_state[key] = color
                st.session_state.pop(f"{key}_custom_v3", None)

    current = st.session_state[key]
    custom_widget_key = f"{key}_custom_v3_{current.lstrip('#').lower()}"
    with custom_placeholder.container():
        custom_col = st.container()
        with custom_col:
            custom = st.color_picker(
                "eigene Farbe", value=current,
                key=custom_widget_key, label_visibility="collapsed",
            )
    if custom.upper() != st.session_state[key]:
        st.session_state[key] = custom.upper()
    css_rules = [
        _swatch_css(f"{key}_v3_p{i}", color, current == color)
        for i, color in enumerate(PALETTE_COLORS)
    ]
    css_rules.append(_custom_color_css(custom_widget_key, current))

    # Alle Swatch-Regeln in EINEM <style>-Block injizieren. Reihenfolge im DOM
    # spielt hier keine Rolle mehr, da über Klassen statt Position adressiert wird.
    st.markdown(f"<style>{''.join(css_rules)}</style>", unsafe_allow_html=True)

    return st.session_state[key]