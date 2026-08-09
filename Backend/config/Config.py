from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = BASE_DIR / "source"

# Text Splitting / Chunking Configurations
CHUNK_SIZE = 100
CHUNK_OVERLAP = 20

# PDF Ingestion margin settings
PDF_HEADER_MARGIN = 50
PDF_FOOTER_MARGIN = 50

# ChromaDB Configurations
CHROMA_DB_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "document_chunks"
