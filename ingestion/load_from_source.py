from typing import List, Dict, Any

from config.Config import SOURCE_DIR
from pdf_to_text import PDFExtractor
from docx_to_text import DOCXExtractor
from markdown_to_text import MarkDownExtractor

def load_data() -> List[Dict[str, Any]]:
    """Loads and extracts chunks from all supported files in the source directory."""
    extractors = {
        ".pdf": PDFExtractor(),
        ".docx": DOCXExtractor(),
        ".doc": DOCXExtractor(),
        ".md": MarkDownExtractor()
    }

    source = []

    try:
        if not SOURCE_DIR.exists():
            print(f"Source directory does not exist: {SOURCE_DIR}")
            return source

        for file in SOURCE_DIR.iterdir():
            if file.is_file():
                ext = file.suffix.lower()
                extractor = extractors.get(ext)
                if extractor:
                    print(f"Processing file: {file.name} using {extractor.__class__.__name__}")
                    data = extractor.extract(file)
                    source.extend(data)
                else:
                    print(f"Unsupported file format: {file.name}")
    except Exception as e:
        print(f"Cannot extract data from the source: {e}")

    return source

if __name__ == '__main__':
    all_chunks = load_data()
    print(f"\nTotal extracted chunks: {len(all_chunks)}")
    if all_chunks:
        print("First chunk sample:", all_chunks[0])
