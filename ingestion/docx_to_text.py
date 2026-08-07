import logging
from pathlib import Path
from typing import List, Dict, Any
from docx import Document

from config.Config import CHUNK_SIZE, CHUNK_OVERLAP
from file_extracter import Extractor

logger = logging.getLogger(__name__)


class DOCXExtractor(Extractor):

    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract(self, path: Path) -> List[Dict[str, Any]]:
        """Extracts text from DOCX file and chunks it."""
        try:
            doc = Document(str(path))
            full_text = "\n".join([para.text.strip() for para in doc.paragraphs if para.text.strip()])
            chunks = self.chunk_text(full_text, chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
            return self.build_chunk_dicts(chunks, file_name=path.name, file_type="docx")
        except Exception as e:
            logger.error(f"Error extracting DOCX file ({path.name}): {e}", exc_info=True)
            return []


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    doc = DOCXExtractor()
    file_path = Path("source/lions.docx")
    if file_path.exists():
        content = doc.extract(file_path)
        if content:
            print(f"Total chunks: {len(content)}")