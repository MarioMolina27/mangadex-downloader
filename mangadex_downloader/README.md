# MangaDex Downloader

Aplicación de escritorio con asistente paso a paso (Tkinter) para buscar una serie en [MangaDex](https://mangadex.org), elegir idioma y tomos, y exportarlos como **EPUB** y/o **PDF**.

## Características

- Búsqueda de series por título (incluye todas las clasificaciones de contenido).
- Selección de idioma de traducción: Español, Español (LATAM), English, Català, Français y Deutsch.
- Agrupación de capítulos por tomo, con selección múltiple de tomos.
- Exportación a EPUB (paginado fijo, con tabla de contenidos por capítulo) y/o PDF.
- Conversión automática de imágenes no compatibles (por ejemplo WebP) a JPEG.
- Reintentos ante errores de red y límites de la API.
- Registro de actividad en vivo dentro de la propia ventana y en la terminal.

## Requisitos

- Python 3.10 o superior
- Tkinter (viene con Python en Windows y macOS; en Linux: `sudo apt install python3-tk`)

## Instalación y uso

```bash
git clone <URL-DEL-REPOSITORIO>
cd mangadex_downloader

python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux / macOS: source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

### Flujo de la aplicación

1. **Buscar serie**: escribe el título y elige el resultado.
2. **Idioma y tomos**: selecciona el idioma, pulsa "Cargar / Recargar Tomos" y marca uno o varios tomos.
3. **Configuración**: elige la carpeta de destino y los formatos (EPUB, PDF o ambos).
4. **Descargar**: sigue el progreso y el registro de actividad.

Los archivos se guardan en `<carpeta elegida>/<Serie>/Tomo <N>/`.

Por defecto, la carpeta de destino es `output/` dentro del proyecto. Si usas el ejecutable, es `MangaDownloads` dentro de tu carpeta de usuario. En ambos casos puedes cambiarla en el paso 3.

## Estructura del proyecto

```
mangadex_downloader/
├── main.py                # punto de entrada
├── requirements.txt
├── core/                  # lógica, sin dependencias de Tkinter
│   ├── config.py          # URL de la API, idiomas, carpeta por defecto
│   ├── http.py            # sesión de requests compartida
│   ├── api.py             # llamadas a la API de MangaDex
│   ├── chapters.py        # ordenación, etiquetas y agrupación por tomo
│   ├── images.py          # descarga y normalización de imágenes
│   ├── exporters.py       # generación de EPUB y PDF
│   ├── downloader.py      # orquestador de la descarga de un tomo
│   └── utils.py
└── gui/
    ├── app.py             # ventana, cabecera y navegación
    ├── redirector.py      # duplica stdout en terminal y GUI
    └── steps/             # un módulo por cada paso del asistente
```

## Generar ejecutables

Se usa [PyInstaller](https://pyinstaller.org). No permite compilar para otro sistema operativo, así que cada ejecutable debe construirse en su propia plataforma.

```bash
pip install pyinstaller

# Windows y Linux (un solo archivo)
pyinstaller --onefile --windowed --name MangaDexDownloader main.py

# macOS (genera un .app)
pyinstaller --windowed --name MangaDexDownloader main.py
```

El resultado queda en `dist/`.

El repositorio incluye un workflow de GitHub Actions (`.github/workflows/build.yml`) que construye los tres a la vez. Se lanza al subir una etiqueta (`git tag v1.0 && git push --tags`) o manualmente desde la pestaña *Actions*, y deja los ejecutables como artefactos descargables.

Los ejecutables no están firmados, por lo que Windows (SmartScreen) y macOS (Gatekeeper) pueden mostrar un aviso la primera vez.
