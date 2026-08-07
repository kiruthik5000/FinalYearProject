import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


class Extractor:

    def chunk_text(self, text: str, chunk_size: int = 100, chunk_overlap: int = 20) -> List[str]:
        """Splits a single text string using LangChain's RecursiveCharacterTextSplitter measured by word count."""
        if not text or not text.strip():
            return []

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=lambda x: len(x.split()),
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        return splitter.split_text(text)

    def chunk_text_with_pages(self, pages: List[Dict[str, Any]], chunk_size: int = 100, chunk_overlap: int = 20) -> List[Dict[str, Any]]:
        """
        Splits a list of page dicts [{"text": str, "page_no": int}] and preserves the page number.
        """
        from langchain_core.documents import Document as LC_Document

        lc_docs = [
            LC_Document(page_content=page["text"], metadata={"page_no": page.get("page_no", 1)})
            for page in pages if page.get("text")
        ]

        if not lc_docs:
            return []

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=lambda x: len(x.split()),
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        split_docs = splitter.split_documents(lc_docs)
        return [
            {"text": doc.page_content, "page_no": doc.metadata["page_no"]}
            for doc in split_docs
        ]

    def build_chunk_dicts(
        self,
        chunks: List[Any],
        file_name: str,
        file_type: str,
        chunk_size: int = 100,
        chunk_overlap: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Helper method to format raw string chunks or page dicts into standard database chunk dictionaries.
        """
        formatted = []
        for i, item in enumerate(chunks):
            if isinstance(item, dict):
                text = item.get("text", "")
                page_no = item.get("page_no")
            else:
                text = str(item)
                page_no = None

            if text.strip():
                formatted.append({
                    "text": text,
                    "chunk_index": i + 1,
                    "page_no": page_no,
                    "file_name": file_name,
                    "file_type": file_type
                })
        return formatted

    def extract_text(self, path: Path) -> List[Dict[str, Any]]:
        """Extracts and chunks plain text files."""
        try:
            text = path.read_text(encoding="utf-8")
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            full_text = " ".join(lines)
            chunks = self.chunk_text(full_text)
            chunked_data = self.build_chunk_dicts(chunks, file_name=path.name, file_type="txt")
            logger.info(f"Created {len(chunked_data)} chunks from {path.name}")
            return chunked_data
        except Exception as e:
            logger.error(f"Failed to extract text from file {path.name}: {e}", exc_info=True)
            return []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ext = Extractor()
    sample_path = Path("source/lions.txt")
    if sample_path.exists():
        data = ext.extract_text(sample_path)
        if data:
            print(data[0])
