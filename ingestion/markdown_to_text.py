import sys
from pathlib import Path
from typing import List, Dict, Any
from markdown_it import MarkdownIt

# Add workspace root to sys.path to enable importing config
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.Config import CHUNK_SIZE, CHUNK_OVERLAP
from file_extracter import Extractor

class MarkDownExtractor(Extractor):

    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.md = MarkdownIt()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract(self, path: Path) -> List[Dict[str, Any]]:
        """
        Extracts content from a markdown file, splits it into chunks, and returns list of dictionaries.
        """
        all_tokens = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            for token in self.md.parse(content):
                if token.content:
                    all_tokens.append(token.content)

            full_text = "\n".join(all_tokens)
            chunks = self.chunk_text(full_text, chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)

            chunked_data = []
            for i, chunk in enumerate(chunks):
                chunked_data.append({
                    "text": chunk,
                    "chunk_index": i + 1,
                    "page_no": None,
                    "file_name": path.name,
                    "file_type": "md"
                })

            print(f" Created {len(chunked_data)} chunks.")
            return chunked_data
        except Exception as e:
            print(f" Error extracting from file {path}: {e}")
            return []

if __name__ == '__main__':
    md = MarkDownExtractor()
    file_path = Path(r"E:\PROJECT py\Final Year Project\source\lions.md")
    print(md.extract(file_path))



