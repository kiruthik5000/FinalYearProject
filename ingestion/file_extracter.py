from typing import List, Dict
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter

class Extractor:

    def chunk_text(self, text: str, chunk_size: int = 100, chunk_overlap: int = 20) -> List[str]:
        """Splits a single text string using LangChain's RecursiveCharacterTextSplitter measured by word count."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=lambda x: len(x.split()),
            separators=[
                "\n\n",   # paragraph
                "\n",     # line
                ". ",     # sentence
                " ",      # word
                ""
            ]
        )
        return splitter.split_text(text)

    def chunk_text_with_pages(self, pages: List[Dict], chunk_size: int = 100, chunk_overlap: int = 20) -> List[Dict]:
        """
        Splits a list of page dicts [{"text": str, "page_no": int}] and preserves the page number.
        Measured by word count.
        """
        from langchain_core.documents import Document as LC_Document
        
        lc_docs = []
        for page in pages:
            lc_docs.append(LC_Document(
                page_content=page["text"],
                metadata={"page_no": page.get("page_no", 1)}
            ))

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=lambda x: len(x.split()),
            separators=[
                "\n\n",   # paragraph
                "\n",     # line
                ". ",     # sentence
                " ",      # word
                ""
            ]
        )
        
        split_docs = splitter.split_documents(lc_docs)
        
        chunks = []
        for doc in split_docs:
            chunks.append({
                "text": doc.page_content,
                "page_no": doc.metadata["page_no"]
            })
            
        return chunks


    def extract_text(self, path: Path) -> List[str]:

        try:
            try:
                text = path.read_text(encoding='utf-8')
            except Exception as e:
                print(f"Error Loading the txt file {path.name}: {e}")

            lines = text.splitlines()
            total_lines = []
            for line in lines:
                if line:
                    total_lines.append(line.strip())
            full_text = " ".join(total_lines)
            chunks = self.chunk_text(full_text)

            chunked_data = []

            for i, chunk in enumerate(chunks):
                chunked_data.append({
                    "text": chunk,
                    "chunk_index": i + 1,
                    "page_no": None,
                    "file_name": path.name,
                    "file_type": "txt"
                })

            print(f" Created {len(chunked_data)} chunks.")
            return chunked_data

        except Exception as e:
            print(f"Cannot Extract data from the text file {path.name} {e}")


if __name__ == '__main__':
    ext = Extractor()
    path = Path(r'E:\PROJECT py\Final Year Project\source\lions.txt')

    data = ext.extract_text(path)
    print(data[0])
