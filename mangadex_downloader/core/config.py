import sys
from pathlib import Path

API_URL = "https://api.mangadex.org"
USER_AGENT = "LocalMangaEpubPDF/1.6"

BASE_DIR = Path(__file__).resolve().parent.parent

if getattr(sys, "frozen", False):
    # Ejecutable de PyInstaller: __file__ apunta a una carpeta temporal
    # (o al interior del .app en macOS), así que guardamos en la carpeta del usuario.
    DEFAULT_OUTPUT_DIR = Path.home() / "MangaDownloads"
else:
    DEFAULT_OUTPUT_DIR = BASE_DIR / "output"

LANGUAGES = {
    "Español": "es",
    "Español (LATAM)": "es-la",
    "English": "en",
    "Català": "ca",
    "Français": "fr",
    "Deutsch": "de",
}
