import sys
from pathlib import Path

# Add workspace root and ingestion directory to sys.path to enable imports
base_path = Path(__file__).resolve().parent
sys.path.append(str(base_path))
sys.path.append(str(base_path / "ingestion"))

from ingestion.load_from_source import load_data
from vector_store.chroma_store import ChromaStore

def main():
    print("Starting data ingestion process...")
    chunks = load_data()
    print(f"\nIngestion complete! Extracted {len(chunks)} text chunks.")
    
    if not chunks:
        print("No chunks extracted. Please place supported files (PDF, DOCX, MD) in the 'source' directory.")
        return

    # Initialize ChromaStore and store chunks
    db = ChromaStore()
    if not Path("./chroma_db").is_dir():
        db.store_chunks(chunks)
    
    # Query Retrieval Demo
    print("\n--- ChromaDB Query Retrieval System ---")
    query_text = input("\nEnter a search query to retrieve relevant document chunks: ").strip()
    if not query_text:
        # Default query if user inputs nothing
        query_text = "project details"
        print(f"No query entered. Using default query: '{query_text}'")
        
    results = db.query(query_text, n_results=3)
    
    print("\nSearch Results:")
    if results and "documents" in results and results["documents"]:
        docs = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results.get("distances", [[]])[0]
        
        for i, (doc, meta) in enumerate(zip(docs, metadatas)):
            dist = f" (Distance: {distances[i]:.4f})" if i < len(distances) else ""
            print(f"\n[{i+1}] File: {meta.get('file_name')} | Chunk: {meta.get('chunk_index')}{dist}")
            print(f"Content: {doc[:300]}...")
    else:
        print("No results found.")

if __name__ == "__main__":
    main()

