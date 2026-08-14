import io
from pathlib import Path
from pypdf import PdfReader, PdfWriter

class PDFController:

    def __init__(self):
        self.source_path = Path(__file__).resolve().parent.parent / "source"
        pass

    def get_pdf(self, pdf_name: str, start_page: int, no_of_pages: int=5):
        try:
            if pdf_name.split('.')[-1] != "pdf":
                raise Exception("Invalid file_name specified")
            if start_page < 1:
                raise Exception("Invalid page no")
            file_path = self.source_path / pdf_name
            reader = PdfReader(file_path)
            if start_page > len(reader.pages):
                raise Exception("Invalid page no")
            writer = PdfWriter()

            for p in range(start_page - 1, start_page + no_of_pages - 1):
                if p >= len(reader.pages):
                    break
                writer.add_page(reader.pages[p])

            output = io.BytesIO()
            writer.write(output)

            output.seek(0)

            return output
        except Exception as e:
            print(f"Error in retrieving pdf from source {e}")
            raise

if __name__ == '__main__':
    pdf = PDFController()

    io = pdf.get_pdf("lion-quick-guide.pdf", 1, 1)

    with open("test.pdf", "wb") as file:
        file.write(io.read())

