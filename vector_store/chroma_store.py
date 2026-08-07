import chromadb
from typing import List, Dict, Any
from config.Config import CHROMA_DB_DIR, COLLECTION_NAME

class ChromaStore:
    def __init__(self):
        """Initializes the ChromaDB persistent client and gets/creates the collection."""
        # Ensure the storage directory exists
        CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
        
        # Initialize persistent client
        self.client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
        
        # Get or create the collection
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)

    def store_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Stores document chunks in the ChromaDB collection.
        Expects a list of dictionaries with structure:
        {
            'text': str,
            'file_name': str,
            'file_type': str,
            'chunk_index': int
        }
        """
        if not chunks:
            print("No chunks to store.")
            return

        documents = []
        metadatas = []
        ids = []

        for idx, chunk in enumerate(chunks):
            text = chunk.get("text", "")
            if not text.strip():
                continue
            
            documents.append(text)
            metadatas.append({
                "file_name": chunk.get("file_name", "unknown"),
                "file_type": chunk.get("file_type", "unknown"),
                "chunk_index": chunk.get("chunk_index", idx),
                "page_no": chunk.get("page_no", None)
            })
            # Generate a unique ID using file name and chunk index
            safe_file_name = chunk.get("file_name", "unknown").replace(" ", "_")
            ids.append(f"{safe_file_name}_chunk_{chunk.get('chunk_index', idx)}")

        if documents:
            print(f"Storing {len(documents)} chunks in ChromaDB...")
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print("Storage successful!")

    def query(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Queries the ChromaDB collection and returns matching documents and metadata.
        """
        print(f"Querying ChromaDB for: '{query_text}' (limit: {n_results})...")
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results

    def file_is_in_db(self, file_name: str) -> bool:
        results = self.collection.get(where={"file_name": file_name})
        return len(results) > 0