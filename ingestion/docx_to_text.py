import sys
from pathlib import Path
from typing import List, Dict, Any
from docx import Document

# Add workspace root to sys.path to enable importing config
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.Config import CHUNK_SIZE, CHUNK_OVERLAP
from file_extracter import Extractor

class DOCXExtractor(Extractor):

    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract(self, path: Path) -> List[Dict[str, Any]]:
        doc = Document(str(path))
        full_text = "\n".join([para.text.strip() for para in doc.paragraphs if para.text.strip()])
        chunks = self.chunk_text(full_text, chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)

        data = []
        for i, chunk in enumerate(chunks):
            data.append({
                "text": chunk,
                "chunk_index": i + 1,
                "page_no": None,
                "file_name": path.name,
                "file_type": "docx"
            })

        return data


if __name__ == '__main__':
    doc = DOCXExtractor()
    file_path = Path(r"E:\PROJECT py\Final Year Project\source\lions.docx")
    content = doc.extract(file_path)
    if content:
        for c in content[:3]:
            print(f"Chunk {c['chunk_index']}: {repr(c['text'])}")