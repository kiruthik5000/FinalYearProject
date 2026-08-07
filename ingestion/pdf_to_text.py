import sys
from pathlib import Path
from typing import List, Dict, Any
import pdfplumber

from config.Config import CHUNK_SIZE, CHUNK_OVERLAP, PDF_HEADER_MARGIN, PDF_FOOTER_MARGIN
from file_extracter import Extractor

class PDFExtractor(Extractor):

    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP, header_margin: int = PDF_HEADER_MARGIN, footer_margin: int = PDF_FOOTER_MARGIN):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.header_margin = header_margin
        self.footer_margin = footer_margin

    def extract(self, path: Path) -> List[Dict[str, Any]]:
        """ Extracts text from PDF using pdfplumber and chunks it."""
        print(f"  Opening PDF with pdfplumber: {path}")
        full_text_list = []
        try:
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
            
            chunked_data = []
            for i, chunk in enumerate(chunks):
                chunked_data.append({
                    "text": chunk['text'],
                    "chunk_index": i + 1,
                    "page_no": chunk['page_no'],
                    "file_name": path.name,
                    "file_type": "pdf"
                })
            print(f"    Created {len(chunked_data)} chunks.")
            return chunked_data
        except Exception as e:
            print(f"    Error extracting from {path}: {e}")
            return []

if __name__ == '__main__':
    pdf = PDFExtractor()
    file_path = Path(r"E:\PROJECT py\Final Year Project\source\lion-quick-guide.pdf")
    chunks = pdf.extract(file_path)
    if chunks:
        print(chunks[0])