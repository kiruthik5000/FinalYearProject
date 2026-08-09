import logging
from pathlib import Path
from typing import List, Dict, Any
from markdown_it import MarkdownIt

from config.Config import CHUNK_SIZE, CHUNK_OVERLAP
from file_extracter import Extractor

logger = logging.getLogger(__name__)


class MarkDownExtractor(Extractor):

    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.md = MarkdownIt()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract(self, path: Path) -> List[Dict[str, Any]]:
        """
        Extracts content from a markdown file, splits it into chunks, and returns list of dictionaries.
        """
        try:
            content = path.read_text(encoding="utf-8")
            all_tokens = [token.content for token in self.md.parse(content) if token.content]
            full_text = "\n".join(all_tokens)
            chunks = self.chunk_text(full_text, chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
            chunked_data = self.build_chunk_dicts(chunks, file_name=path.name, file_type="md")
            logger.info(f"Created {len(chunked_data)} markdown chunks from {path.name}")
            return chunked_data
        except Exception as e:
            logger.error(f"Error extracting Markdown file ({path.name}): {e}", exc_info=True)
            return []


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    md = MarkDownExtractor()
    file_path = Path("source/lions.md")
    if file_path.exists():
        print(md.extract(file_path))
