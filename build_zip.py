"""
Erstellt eine ZIP-Datei des kompletten Projekts (für Backup oder Weitergabe).

Nutzung:
    python build_zip.py

Die ZIP-Datei wird im übergeordneten Ordner als "<projektname>.zip" abgelegt,
z.B. bei einem Projektordner "captions_app" -> "captions_app.zip" eine Ebene
darüber. Beim Entpacken entsteht wieder derselbe Ordnername.

Ausgeschlossen werden automatisch: __pycache__, .git, virtuelle Umgebungen
(venv/.venv) und kompilierte .pyc-Dateien.
"""
import os
import zipfile
from pathlib import Path

EXCLUDE_DIR_NAMES = {"__pycache__", ".git", ".venv", "venv"}
EXCLUDE_FILE_SUFFIXES = {".pyc"}


def should_skip_dir(dirname: str) -> bool:
    return dirname in EXCLUDE_DIR_NAMES


def should_skip_file(filename: str) -> bool:
    return any(filename.endswith(suffix) for suffix in EXCLUDE_FILE_SUFFIXES)


def build_zip():
    project_root = Path(__file__).resolve().parent
    zip_name = f"{project_root.name}.zip"
    zip_path = project_root.parent / zip_name

    file_count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for current_dir, dirnames, filenames in os.walk(project_root):
            # Unerwünschte Unterordner von der Traversierung ausschließen
            dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]

            for filename in filenames:
                if should_skip_file(filename):
                    continue
                if filename == zip_name:
                    continue  # eigene Ausgabedatei nicht mit einpacken

                file_path = Path(current_dir) / filename
                # Pfad relativ zum übergeordneten Ordner, damit im ZIP
                # ein Top-Level-Ordner mit dem Projektnamen entsteht
                arcname = file_path.relative_to(project_root.parent)
                zf.write(file_path, arcname)
                file_count += 1

    print(f"Fertig: {file_count} Dateien gepackt.")
    print(f"ZIP-Datei erstellt: {zip_path}")


if __name__ == "__main__":
    build_zip()