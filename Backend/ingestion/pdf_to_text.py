import logging
from pathlib import Path
from typing import List, Dict, Any
import pdfplumber

from config.Config import CHUNK_SIZE, CHUNK_OVERLAP, PDF_HEADER_MARGIN, PDF_FOOTER_MARGIN
from file_extracter import Extractor

logger = logging.getLogger(__name__)


class PDFExtractor(Extractor):

    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP, header_margin: int = PDF_HEADER_MARGIN, footer_margin: int = PDF_FOOTER_MARGIN):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.header_margin = header_margin
        self.footer_margin = footer_margin

    def extract(self, path: Path) -> List[Dict[str, Any]]:
        """Extracts text from PDF using pdfplumber and chunks it."""
        try:
            logger.info(f"Opening PDF file: {path}")
            full_text_list = []
            with pdfplumber.open(path) as pdf:
                for page_no, page in enumerate(pdf.pages):
                    crop_box = (0, self.header_margin, page.width, page.height - self.footer_margin)
                    cropped_page = page.crop(bbox=crop_box)
                    text = cropped_page.extract_text(x_tolerance=2, layout=True)
                    if text:
                        full_text_list.append({
                            "text": text.strip(),
                            "page_no": page_no + 1
                        })

            chunks = self.chunk_text_with_pages(full_text_list, chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
            chunked_data = self.build_chunk_dicts(chunks, file_name=path.name, file_type="pdf")
            logger.info(f"Created {len(chunked_data)} PDF chunks from {path.name}")
            return chunked_data
        except Exception as e:
            logger.error(f"Error extracting PDF file ({path.name}): {e}", exc_info=True)
            return []


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    pdf = PDFExtractor()
    file_path = Path("source/lion-quick-guide.pdf")
    if file_path.exists():
        chunks = pdf.extract(file_path)
        if chunks:
            print(chunks[0])