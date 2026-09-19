# Video Auto-Captions Editor

Eine Streamlit-App, die aus einem hochgeladenen Video automatisch Untertitel
transkribiert (per OpenAI Whisper) und diese als animierte, individuell
gestylte Untertitel per FFmpeg/ASS direkt ins Video einbrennt.

## Funktionen

- Video-Upload (MP4)
- Transkription mit wählbarer Whisper-Modellgröße und Audiosprache
- Wort-für-Wort-Zeitstempel
- Gruppierung mehrerer Wörter pro Untertitel-Zeile, mit automatischem
  Zeilenumbruch bei Satzende
- Editierbare Wort-Tabelle inkl. Zeile teilen/löschen zur Textkorrektur
- Freie Auswahl von Schriftart, -größe, Farben, Position
- Animations-Stile: Karaoke-Highlight, Fade, Pop-In, Slide-Up, Paper Sheer
  (Karten-Style), oder keine Animation
- Animierte Live-Vorschau direkt in der App
- Style-Vorschau nach der Transkription mit echten Untertiteln aus dem eigenen
  Video (auf maximal 8 Sekunden begrenzt)
- Hardware-beschleunigtes Rendering über Intel Quick Sync (QSV), mit
  Fallback auf CPU-Encoding
- Frei wählbare Dateinamen für MP4- und ASS-Export

## Ordnerstruktur

```
captions_app/
├── app.py                          # Haupt-Einstiegspunkt (streamlit run app.py)
├── requirements.txt                # Python-Abhängigkeiten
├── README.md                       # Diese Datei
├── build_zip.py                    # Erstellt ein ZIP-Backup des Projekts
├── ffmpeg.exe                      # (optional, falls nicht im System-PATH)
├── ffprobe.exe                     # (optional, falls nicht im System-PATH)
├── .streamlit/
│   └── config.toml                 # Upload-Limit (z.B. 1000 MB)
└── captions/                       # Kernlogik-Package
    ├── __init__.py
    ├── config.py                   # FFmpeg-Pfade, Schriftarten, Konstanten
    ├── utils.py                    # Dateinamen-, Farb-, Zeit-Hilfsfunktionen
    ├── ass_drawing.py              # Vektor-Zeichnungen + Textbreiten-Messung
    ├── ass_builder.py              # ASS-Header, Wortgruppierung, Animations-Events
    ├── preview.py                  # Frame-Extraktion + animierte Live-Vorschau
    ├── transcription.py            # Whisper-Transkription
    ├── rendering.py                # Finales FFmpeg-Rendering
    └── ui/                         # Streamlit-Fragmente
        ├── __init__.py
        ├── style_fragment.py       # Schrift-/Animations-Sidebar + Vorschau
        ├── transcribe_fragment.py  # Transkription + Textkorrektur-Tabelle
        └── render_fragment.py      # Rendering-Button, Ergebnis, Downloads
```

## Voraussetzungen

### Python-Pakete

```bash
pip install -r requirements.txt
```

> `openai-whisper` installiert automatisch `torch` mit. Der erste Start
> lädt zusätzlich das gewählte Whisper-Modell herunter.

### FFmpeg (nicht über pip installierbar)

Benötigt `ffmpeg`/`ffprobe` mit `libass`-Unterstützung.

```powershell
winget install Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
```

**Empfohlen: FFmpeg dauerhaft in den System-PATH eintragen**, statt die
`.exe`-Dateien in den Projektordner zu kopieren. Neues PowerShell-Fenster
öffnen und ausführen:

```powershell
$ffmpegBinDir = Split-Path (Get-ChildItem -Path "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter "ffmpeg.exe" -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName)
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";$ffmpegBinDir", "User")
```

Danach das Terminal **komplett schließen und neu öffnen** (die PATH-Änderung
wirkt erst im nächsten Terminal-Fenster), dann testen:

```powershell
ffmpeg -version
ffprobe -version
```

Beide sollten Versionsinfos ausgeben. Ab dann findet die App FFmpeg über den
System-PATH und benötigt keine lokalen Kopien im Projektordner mehr.

**Alternative:** Falls du FFmpeg lieber lokal im Projektordner statt im
System-PATH halten willst, kannst du `ffmpeg.exe`/`ffprobe.exe` stattdessen
direkt dorthin kopieren — die App sucht automatisch zuerst dort, bevor sie
auf den System-PATH zurückfällt (siehe `captions/config.py`). In diesem Fall
sind die Binaries bereits über `.gitignore` von Git ausgeschlossen.

### Schriftarten

Die in `captions/config.py` unter `FONT_FILE_PATHS` hinterlegten `.ttf`-Pfade
müssen auf deinem System existieren. Passe die Pfade bei Bedarf an.

## Nutzung

```bash
streamlit run app.py
```

Im Browser (`http://localhost:8501`):

1. Video hochladen
2. Whisper-Modell und optional die Sprache der Audiospur wählen und
   **„Video transkribieren"** klicken
3. Text bei Bedarf in der Tabelle korrigieren (Wörter teilen/löschen)
4. Style einstellen und die Live-Vorschau mit den echten Untertiteln prüfen
5. **„Animierte Untertitel erstellen"** klicken
6. Fertiges Video bzw. `.ass`-Datei über die Download-Buttons speichern

## Projekt als ZIP sichern

Um jederzeit eine aktuelle ZIP-Kopie des gesamten Projekts zu erstellen
(z.B. nach eigenen Änderungen, für ein Backup oder zum Weitergeben):

```bash
python build_zip.py
```

Das legt eine `captions_app.zip` eine Ebene über dem Projektordner an.
`__pycache__`, `.git` und virtuelle Umgebungen werden automatisch
ausgeschlossen.

## Architektur-Hinweise

- Die UI nutzt `@st.fragment`, damit Parameteränderungen (z.B. Schriftgröße)
  nur den betroffenen Bereich neu laden, nicht die komplette Seite.
- `style_params` wird in `st.session_state` abgelegt und von `render_fragment`
  gelesen — so bleiben Style-Einstellungen und Rendering-Logik entkoppelt.
- Die Paper-Sheer-Karte nutzt ASS-Vektor-Zeichnungen (`\p1`) mit einem
  manuell berechneten Top-Left-Anker (`\an7`), da libass die automatische
  Zentrierung (`\an5`) bei reinen Formen ohne Text unzuverlässig behandelt.