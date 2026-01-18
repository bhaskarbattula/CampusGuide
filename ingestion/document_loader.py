import os
from typing import Dict, List, Tuple, Any
import pdfplumber
import pytesseract
from PIL import Image
import io
import fitz  # PyMuPDF
from config.config import Config


class DocumentLoader:
    def __init__(self):
        self.config = Config()

    def load_pdf(self, file_path: str) -> Dict[str, any]:
        """
        Load PDF document and extract text with page mapping.
        Falls back to OCR if text extraction fails.

        Args:
            file_path: Path to the PDF file

        Returns:
            Dict containing:
            - 'text': Full extracted text
            - 'pages': List of (page_num, page_text) tuples
            - 'metadata': Document metadata
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        text_pages = []
        full_text = ""

        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_pages.append((page_num, page_text.strip()))
                        full_text += page_text + "\n"
                    else:
                        # Fallback to OCR if no text extracted
                        if self.config.OCR_FALLBACK:
                            ocr_text = self._ocr_page(page)
                            if ocr_text.strip():
                                text_pages.append((page_num, ocr_text.strip()))
                                full_text += ocr_text + "\n"
        except Exception as e:
            raise RuntimeError(f"Error loading PDF {file_path}: {str(e)}")

        metadata = {
            "filename": os.path.basename(file_path),
            "upload_date": os.path.getmtime(file_path),
            "file_size": os.path.getsize(file_path),
            "pages": len(text_pages),
        }

        return {"text": full_text.strip(), "pages": text_pages, "metadata": metadata}

    def _ocr_page(self, page) -> str:
        """
        Perform OCR on a PDF page.

        Args:
            page: pdfplumber page object

        Returns:
            Extracted text from OCR
        """
        try:
            # Convert page to image
            zoom = 2  # Higher resolution for better OCR
            matrix = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=matrix)
            img = Image.open(io.BytesIO(pix.tobytes()))

            # Perform OCR
            text = pytesseract.image_to_string(img)
            return text
        except Exception as e:
            print(f"OCR failed for page: {str(e)}")
            return ""

    def load_multiple_pdfs(self, directory: str) -> List[Dict[str, any]]:
        """
        Load all PDFs from a directory.

        Args:
            directory: Directory containing PDF files

        Returns:
            List of document dictionaries
        """
        documents = []
        if not os.path.exists(directory):
            return documents

        for filename in os.listdir(directory):
            if filename.lower().endswith(".pdf"):
                file_path = os.path.join(directory, filename)
                try:
                    doc = self.load_pdf(file_path)
                    documents.append(doc)
                except Exception as e:
                    print(f"Failed to load {filename}: {str(e)}")

        return documents
