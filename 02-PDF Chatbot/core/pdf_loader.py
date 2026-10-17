
import fitz
from pathlib import Path

from core.utils import clean_text

class PDFLoader:

    def __init__(self, pdf_path):
        self.pdf_path = Path(pdf_path)

    def extract_text(self):
        document = fitz.open(self.pdf_path)

        pages = []

        for page in document:
            text = page.get_text()
            pages.append(clean_text(text))
        document.close()
        return pages

    def page_count(self):
        document= fitz.open(self.pdf_path)
        total= len(document)
        document.close()
        return total
