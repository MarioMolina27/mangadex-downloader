import requests

from core.config import USER_AGENT

# Sesión compartida por la API y la descarga de imágenes
session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})
