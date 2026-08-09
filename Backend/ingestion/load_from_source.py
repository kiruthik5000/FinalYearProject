import sys
from pathlib import Path
from typing import List, Dict, Any

base_path = Path(__file__).resolve().parent.parent
if str(base_path) not in sys.path:
    sys.path.append(str(base_path))
if str(base_path / "ingestion") not in sys.path:
    sys.path.append(str(base_path / "ingestion"))

from config.Config import SOURCE_DIR
from pdf_to_text import PDFExtractor
from docx_to_text import DOCXExtractor
from markdown_to_text import MarkDownExtractor
from file_extracter import Extractor
from vector_store.chroma_store import ChromaStore


from website_extractor import WebSiteExtractor
from youtube_to_text import YouTubeExtractor


def extract_single_file(file_path: Path) -> List[Dict[str, Any]]:
    """Extracts chunks from a single supported file."""
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        return PDFExtractor().extract(file_path)
    elif ext in [".docx", ".doc"]:
        return DOCXExtractor().extract(file_path)
    elif ext == ".md":
        return MarkDownExtractor().extract(file_path)
    elif ext in [".txt", ".text"]:
        return Extractor().extract_text(file_path)
    return []


def extract_url(url: str) -> List[Dict[str, Any]]:
    """Extracts content chunks from YouTube or website URLs."""
    url_lower = url.lower()
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return YouTubeExtractor().extract(url)
    else:
        return WebSiteExtractor().extract(url)


def ingest_async(source: Path | str) -> None:
    """Unified asynchronous ingestion for files (Path) or URLs (str) into ChromaDB."""
    try:
        label = source.name if isinstance(source, Path) else str(source)
        print(f"Starting async ingestion for: {label}")
        chunks = extract_single_file(source) if isinstance(source, Path) else extract_url(label)
        if chunks:
            db = ChromaStore()
            db.store_chunks(chunks)
            print(f"Async ingestion complete: {len(chunks)} chunks stored for {label}")
        else:
            print(f"Async ingestion warning: No chunks extracted from {label}")
    except Exception as e:
        print(f"Async ingestion error processing {label}: {e}")


# Backwards compatibility aliases
ingest_file_async = ingest_async
ingest_url_async = ingest_async




def load_data() -> List[Dict[str, Any]]:
    """Loads and extracts chunks from all supported files in the source directory."""
    source = []

    try:
        if not SOURCE_DIR.exists():
            print(f"Source directory does not exist: {SOURCE_DIR}")
            return source

        for file in SOURCE_DIR.iterdir():
            if file.is_file():
                chunks = extract_single_file(file)
                if chunks:
                    source.extend(chunks)
                else:
                    print(f"Skipped or empty file: {file.name}")
    except Exception as e:
        print(f"Cannot extract data from the source: {e}")

    return source


if __name__ == '__main__':
    all_chunks = load_data()
    print(f"\nTotal extracted chunks: {len(all_chunks)}")
    if all_chunks:
        print("First chunk sample:", all_chunks[0])

