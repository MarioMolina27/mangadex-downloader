"""Descarga y normalización de imágenes."""
import io
import time

from PIL import Image, ImageFile

from core.http import session

# Evitar errores con imágenes ligeramente truncadas o dañadas
ImageFile.LOAD_TRUNCATED_IMAGES = True


def download_image(url):
    """Devuelve los bytes de la imagen o None si falla tras 3 intentos."""
    for _ in range(3):
        try:
            response = session.get(url, timeout=30)
            if response.status_code != 200:
                print(f"      [!] HTTP {response.status_code} en {url}")
                time.sleep(2)
                continue

            content = response.content
            if not content or len(content) < 1024:
                print(f"      [!] Imagen muy pequeña o vacía ({len(content) if content else 0} bytes)")
                time.sleep(1)
                continue

            return content
        except Exception as e:
            print(f"      [!] Excepción {type(e).__name__}: {e}")
            time.sleep(2)
    return None


def normalize_image(image_data):
    """Devuelve (bytes, extensión, media_type) compatible con PDF/EPUB.

    Lanza excepción si PIL no puede abrir la imagen.
    """
    image = Image.open(io.BytesIO(image_data))
    image_format = (image.format or "desconocido").lower()

    if image_format not in ("jpeg", "jpg", "png"):
        print(f"     [CONVERSIÓN] {image_format.upper()} -> JPEG (Compatibilidad PDF/EPUB)")
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=95)
        return buffer.getvalue(), "jpg", "image/jpeg"

    extension = "jpg" if image_format in ("jpeg", "jpg") else "png"
    media_type = "image/jpeg" if extension == "jpg" else "image/png"
    return image_data, extension, media_type
