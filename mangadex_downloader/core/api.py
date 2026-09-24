import time

import requests

from core.config import API_URL
from core.http import session


def api_get(endpoint, params=None):
    url = API_URL + endpoint
    for attempt in range(5):
        try:
            response = session.get(url, params=params, timeout=30)
            if response.status_code == 429:
                time.sleep(int(response.headers.get("Retry-After", "5")))
                continue
            if response.status_code >= 500:
                time.sleep(2 ** attempt)
                continue
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[API Error] Intento {attempt + 1}: {e}")
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("No se pudo contactar con MangaDex.")


def search_manga(title):
    endpoint = "/manga"
    params = {
        "title": title,
        "limit": 100,
        "includes[]": "cover_art",
        # Incluimos erotica y pornographic para no filtrar mangas maduros/seinen
        "contentRating[]": ["safe", "suggestive", "erotica", "pornographic"],
        # Ordenamos por relevancia para que la obra principal salga primero
        "order[relevance]": "desc",
    }

    print("\n" + "=" * 60)
    print("[DEBUG PASO 1] Petición API enviada:")
    print(f"  -> URL / Endpoint : {API_URL}{endpoint}")
    print(f"  -> Parámetros     : {params}")
    print("=" * 60)

    data = api_get(endpoint, params)

    results = []
    for idx, item in enumerate(data.get("data", []), start=1):
        manga_id = item.get("id")
        titles = item.get("attributes", {}).get("title", {})
        display_title = (
            titles.get("en")
            or titles.get("ja-ro")
            or next(iter(titles.values()), "Sin título")
        )
        print(f"  [{idx:02d}] ID : {manga_id} | Título : {display_title}")
        results.append({
            "id": manga_id,
            "title": display_title,
            "attributes": item.get("attributes", {}),
        })
    return results


def get_chapters(manga_id, language):
    print(f"[Paso 2] Obteniendo lista de capítulos (Idioma: {language})...")
    chapters = []
    offset = 0
    while True:
        params = {
            "translatedLanguage[]": [language],
            "limit": 100,
            "offset": offset,
            "order[volume]": "asc",
            "order[chapter]": "asc",
        }
        data = api_get(f"/manga/{manga_id}/feed", params)
        batch = data.get("data", [])
        chapters.extend(batch)
        offset += len(batch)
        if not batch or offset >= data.get("total", 0):
            break
        time.sleep(0.2)
    print(f"[Paso 2] Total de capítulos obtenidos: {len(chapters)}")
    return chapters


def get_page_urls(chapter_id):
    data = api_get(f"/at-home/server/{chapter_id}")
    base, ch = data["baseUrl"], data["chapter"]
    return [f"{base}/data/{ch['hash']}/{page}" for page in ch["data"]]
