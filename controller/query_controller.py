import sys
from pathlib import Path
from typing import Set, List, Dict, Any

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from vector_store import ChromaStore


class QueryController:

    def __init__(self):
        self.db = ChromaStore()

    def get_files(self) -> Set[str]:
        """
        Retrieves all unique source file names currently stored in the database.
        """
        try:
            results = self.db.collection.get(include=["metadatas"])
            metadatas = results.get("metadatas", [])

            if not metadatas:
                return set()

            files = {
                metadata["file_name"]
                for metadata in metadatas
                if metadata and "file_name" in metadata
            }

            return files

        except Exception as e:
            print(f"Error fetching files from database: {e}")
            return set()

    def _get_result(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Queries the vector store for matching document chunks and returns formatted results.
        """
        try:
            if not query_text or not query_text.strip():
                return []

            raw_results = self.db.query(query_text, n_results=n_results)
            formatted_results = []

            if raw_results and "documents" in raw_results and raw_results["documents"]:
                docs = raw_results["documents"][0]
                metadatas = raw_results.get("metadatas", [[]])[0]
                distances = raw_results.get("distances", [[]])[0]
                ids = raw_results.get("ids", [[]])[0]

                for i, doc in enumerate(docs):
                    meta = metadatas[i] if i < len(metadatas) else {}
                    dist = distances[i] if i < len(distances) else None
                    doc_id = ids[i] if i < len(ids) else None

                    formatted_results.append({
                        "id": doc_id,
                        "content": doc,
                        "file_name": meta.get("file_name", "unknown"),
                        "file_type": meta.get("file_type", "unknown"),
                        "chunk_index": meta.get("chunk_index"),
                        "page_no": meta.get("page_no"),
                        "distance": dist
                    })

            return formatted_results

        except Exception as e:
            print(f"Error retrieving query results: {e}")
            return []

    def get_answer(self, query_text: str) -> Dict[str, Any]:

if __name__ == '__main__':
    q = QueryController()
    print("Files in DB:", q.get_files())
    print("Search Result Sample:", q.get_result("project details", n_results=2))
