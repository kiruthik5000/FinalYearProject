import logging
from typing import Set, List, Dict, Any

from vector_store.chroma_store import ChromaStore
from llm.open_router import Generator

logger = logging.getLogger(__name__)


class QueryController:

    def __init__(self):
        self.db = ChromaStore()
        self.generator = Generator()
        self.intent_dict = {
            "explanation": ["explain", "describe", "elaborate"],
            "comparison": ["compare", "difference between", "distinguish"],
            "procedure": ["how to", "how do", "how does"],
            "advantage_disadvantage": ["advantage" , "pros", "cons", "disadvantage"],
            "definition": ["what is", "define", "definition"],
            "summary": ["summarize", "summary of"]
        }
        self.retriver_dict = {
            "explanation": 8,
        }

    def get_files(self) -> Set[str]:
        """
        Retrieves all unique source file names currently stored in the database.
        """
        try:
            results = self.db.collection.get(include=["metadatas"])
            metadatas = results.get("metadatas", [])

            if not metadatas:
                return set()

            return {
                metadata["file_name"]
                for metadata in metadatas
                if metadata and "file_name" in metadata
            }

        except Exception as e:
            logger.error(f"Error fetching files from database: {e}", exc_info=True)
            return set()

    def _get_result(self, query_text: str, query_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Queries the vector store for matching document chunks and returns formatted results.
        """
        try:
            if not query_text or not query_text.strip():
                return []

            n_chunks = self.retriver_dict.get(query_analysis["intent"], 5)
            raw_results = self.db.query(query_text, n_results=n_chunks)
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
            logger.error(f"Error retrieving query results for '{query_text}': {e}", exc_info=True)
            return []

    def get_answer(self, query_text: str) -> Dict[str, Any]:
        """
        Retrieves matching chunks and refines the response using LLM.
        """
        try:
            query_analysis = self._query_analyzer(query_text)
            collected_data = self._get_result(query_text, query_analysis)

            if not collected_data:
                return {
                    "status": "failed",
                    "message": "No relevant document chunks found in database."
                }

            return self.generator.refine_with_llm(query_text, collected_data, query_analysis)

        except Exception as e:
            logger.error(f"Error generating answer for query '{query_text}': {e}", exc_info=True)
            return {
                "status": "failed",
                "message": str(e)
            }
    def _query_analyzer(self, query_text: str) -> Dict[str, Any]:
        """
        able to identify the nature of the query and advances the llm to be aware of the
        question so it can provide the output result more efficiently

        :param query_text:
        :returns:
        {
        "intent": ["comparison", "definition", "explanation", "procedure", "advantages_disadvantages", "summary"],
        "depth": ["concise", "moderate", "detailed"],
        "example": ["required", "not required"]
        }
        """

        intent = self._get_intent(query_text)

        depth = self._get_depth(intent)

        example = self._get_example(depth)

        return {
            "intent": intent,
            "depth": depth,
            "example": example
        }

    def _get_example(self, depth: str) -> str:
        if depth in ["detailed", "moderate"]:
            return "required"
        return "not required"

    def _get_depth(self, intent: str) -> str:
        if intent == "definition":
            return "consise"
        elif intent in ["comparision", "explanation"]:
            return "detailed"
        else:
            return "moderate"
    def _get_intent(self, query: str) -> str:

        for intent in self.intent_dict:
            for keys in self.intent_dict[intent]:
                if keys in query.lower():
                    return intent
        return "undefined"



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    q = QueryController()
    query = "Difference between good habits and bad habits"
    analysis = q._query_analyzer(query)
    print(analysis)
    res = q._get_result(query, analysis)
    print("--" * 50)
    print(res)
    print("--" * 50)
    print(q.get_answer(query))