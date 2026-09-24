"""Generación de archivos EPUB y PDF."""
import img2pdf
from ebooklib import epub


class EpubBuilder:
    def __init__(self, title, identifier, language):
        self.language = language
        self.book = epub.EpubBook()
        self.book.set_identifier(identifier)
        self.book.set_title(title)
        self.book.set_language(language)
        self.book.add_metadata(None, "meta", "pre-paginated", {"property": "rendition:layout"})
        self.book.add_metadata(None, "meta", "portrait", {"property": "rendition:orientation"})

        self.spine = ["nav"]
        self.toc = []
        self._counter = 0
        self._chapter_id = None
        self._chapter_name = ""
        self._chapter_has_pages = False

    def begin_chapter(self, chapter_id, chapter_name):
        self._chapter_id = chapter_id
        self._chapter_name = chapter_name
        self._chapter_has_pages = False

    def add_page(self, page_index, image_data, extension, media_type):
        n = self._counter
        image_name = f"page_{n:06d}.{extension}"

        self.book.add_item(epub.EpubItem(
            uid=f"image_{n}",
            file_name=f"images/{image_name}",
            media_type=media_type,
            content=image_data,
        ))

        page = epub.EpubHtml(
            title=f"{self._chapter_name} - Pág {page_index}",
            file_name=f"page_{n:06d}.xhtml",
            lang=self.language,
        )
        page.content = (
            '<html><body style="margin:0;padding:0;background-color:#000;display:flex;'
            'justify-content:center;align-items:center;height:100vh;">'
            f'<img src="images/{image_name}" style="max-width:100%;max-height:100%;object-fit:contain;"/>'
            "</body></html>"
        )
        self.book.add_item(page)
        self.spine.append(page)

        if not self._chapter_has_pages:
            self.toc.append(epub.Link(page.file_name, self._chapter_name, f"chapter-{self._chapter_id}"))
            self._chapter_has_pages = True

        self._counter += 1

    def save(self, path):
        self.book.toc = tuple(self.toc)
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())
        self.book.spine = self.spine
        epub.write_epub(str(path), self.book)


def export_pdf(images, path):
    pdf_bytes = img2pdf.convert(images)
    with open(path, "wb") as f:
        f.write(pdf_bytes)
