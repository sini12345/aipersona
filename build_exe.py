"""
Bygger .exe fil til Windows-distribution.

Kør på en Windows-maskine:
    pip install pyinstaller
    python build_exe.py

Resultatet ligger i dist/PersonaTraening/
"""

import PyInstaller.__main__
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    "launcher.py",
    "--name=PersonaTraening",
    "--onedir",
    "--noconsole",
    # Inkluder data-filer
    f"--add-data=templates{os.pathsep}templates",
    f"--add-data=personas{os.pathsep}personas",
    f"--add-data=theories{os.pathsep}theories",
    # Inkluder Python-moduler
    "--hidden-import=web",
    "--hidden-import=persona_engine",
    "--hidden-import=flask",
    "--hidden-import=jinja2.ext",
    # Ryd op
    "--clean",
    "--noconfirm",
])

print("\n" + "=" * 50)
print("  FÆRDIG!")
print("  .exe ligger i: dist/PersonaTraening/")
print("  Kopiér hele mappen til dine kollegaer.")
print("  De dobbeltklikker på PersonaTraening.exe")
print("=" * 50)
