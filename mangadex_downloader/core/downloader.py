"""Orquestador: descarga las páginas de un tomo y genera EPUB/PDF."""
import time
from pathlib import Path

from core.api import get_page_urls
from core.chapters import chapter_label
from core.exporters import EpubBuilder, export_pdf
from core.images import download_image, normalize_image
from core.utils import safe_filename


def _collect_page_urls(chapters, progress_callback):
    all_pages = []
    for chapter in chapters:
        name = chapter_label(chapter)
        print(f"\n=> Obteniendo URLs de: {name}")
        progress_callback(0, 1, f"Buscando {name}...")
        all_pages.append((chapter, get_page_urls(chapter["id"])))
    return all_pages


def create_volume_files(manga_title, volume, chapters, language, output_base_dir,
                        export_epub, export_pdf_flag, progress_callback):
    safe_title = safe_filename(manga_title)
    safe_volume = safe_filename(volume)

    target_dir = Path(output_base_dir) / safe_title / f"Tomo {safe_volume}"
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== Procesando Tomo {volume} ===")
    print(f"Carpeta de salida: {target_dir}")

    epub_builder = None
    if export_epub:
        epub_builder = EpubBuilder(
            title=f"{manga_title} - Tomo {volume}",
            identifier=f"mangadex-{safe_title}-{safe_volume}",
            language=language,
        )

    all_pages = _collect_page_urls(chapters, progress_callback)
    total_pages = sum(len(urls) for _, urls in all_pages)
    downloaded_pages = 0
    images = []

    print(f"Total de páginas a procesar: {total_pages}")

    for chapter, urls in all_pages:
        chapter_name = chapter_label(chapter)
        if epub_builder:
            epub_builder.begin_chapter(chapter["id"], chapter_name)

        for page_index, url in enumerate(urls, start=1):
            print(f"  -> Descargando [Pág {page_index}/{len(urls)}]: {url.split('/')[-1]}")
            image_data = download_image(url)

            if not image_data:
                print("     [ERROR] Se ignoró la página por fallo de descarga.")
                downloaded_pages += 1
                continue

            try:
                final_data, extension, media_type = normalize_image(image_data)
            except Exception as e:
                print(f"     [ERROR] Fallo PIL: {e}")
                downloaded_pages += 1
                continue

            images.append(final_data)
            if epub_builder:
                epub_builder.add_page(page_index, final_data, extension, media_type)

            downloaded_pages += 1
            progress_callback(downloaded_pages, total_pages, f"Pág {page_index}/{len(urls)} de {chapter_name}")
            time.sleep(0.02)

    if not images:
        raise RuntimeError(f"No se pudieron obtener páginas para el Tomo {volume}.")

    base_name = f"{safe_title} - Tomo {safe_volume}"

    if epub_builder:
        print("=> Compilando EPUB...")
        epub_builder.save(target_dir / f"{base_name}.epub")

    if export_pdf_flag:
        print("=> Compilando PDF...")
        progress_callback(total_pages, total_pages, "Generando PDF...")
        export_pdf(images, target_dir / f"{base_name}.pdf")

    print(f"[ÉXITO] Tomo {volume} generado correctamente.")
    return target_dir
