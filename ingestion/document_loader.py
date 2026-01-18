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

    def load_document(self, file_path: str) -> Dict[str, Any]:
        """
        Load document and extract text. Supports PDF and image files.
        For PDFs: extract text with OCR fallback.
        For images: use OCR directly.

        Args:
            file_path: Path to the document file

        Returns:
            Dict containing:
            - 'text': Full extracted text
            - 'pages': List of (page_num, page_text) tuples
            - 'metadata': Document metadata
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_ext = os.path.splitext(file_path)[1].lower()

        # Handle different file types
        if file_ext == ".pdf":
            return self._load_pdf_file(file_path)
        elif file_ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"]:
            return self._load_image_file(file_path)
        else:
            raise ValueError(
                f"Unsupported file type: {file_ext}. Supported: PDF, PNG, JPG, JPEG, BMP, TIFF, TIF"
            )

    def _load_pdf_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load PDF document and extract text with page mapping.
        Falls back to OCR if text extraction fails.

        Args:
            file_path: Path to the PDF file

        Returns:
            Dict containing extracted data
        """
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
            "file_type": "pdf",
        }

        return {"text": full_text.strip(), "pages": text_pages, "metadata": metadata}

    def _load_image_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load image file and extract text using OCR.

        Args:
            file_path: Path to the image file

        Returns:
            Dict containing extracted data
        """
        try:
            # Load image
            image = Image.open(file_path)

            # Perform OCR
            text = pytesseract.image_to_string(image)

            # Clean up the text - remove any non-text artifacts
            text = text.strip()
            # Remove common OCR errors and image-related text
            text = self._clean_ocr_text(text)

            if not text or len(text) < 10:  # Require minimum text length
                raise ValueError(
                    f"Insufficient text extracted from image {file_path}. OCR may have failed."
                )

            # Validate that we have actual readable text
            if not self._is_valid_text(text):
                raise ValueError(
                    f"Extracted text from {file_path} appears to be invalid or contains image artifacts."
                )

            # Create page structure (single page for images)
            text_pages = [(1, text)]

            metadata = {
                "filename": os.path.basename(file_path),
                "upload_date": os.path.getmtime(file_path),
                "file_size": os.path.getsize(file_path),
                "pages": 1,
                "file_type": os.path.splitext(file_path)[1].lower()[
                    1:
                ],  # 'png', 'jpg', etc.
            }

            return {"text": text, "pages": text_pages, "metadata": metadata}

        except Exception as e:
            error_msg = f"Error loading image {file_path}: {str(e)}. Image files may not contain readable text or OCR failed."
            print(error_msg)
            raise RuntimeError(error_msg)

    def _clean_ocr_text(self, text: str) -> str:
        """
        Clean OCR text by removing common artifacts and invalid characters.

        Args:
            text: Raw OCR text

        Returns:
            Cleaned text
        """
        import re

        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove lines that look like file paths or image metadata
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            # Skip lines that look like file paths, URLs, or metadata
            if (
                line.startswith("/")
                or line.startswith("http")
                or "screenshot" in line.lower()
                or line.lower().startswith("image")
                or len(line) < 3
            ):  # Skip very short lines
                continue
            cleaned_lines.append(line)

        return "\n".join(cleaned_lines).strip()

    def _is_valid_text(self, text: str) -> bool:
        """
        Check if the extracted text appears to be valid readable content.

        Args:
            text: Text to validate

        Returns:
            True if text appears valid
        """
        # Check for minimum word count
        words = text.split()
        if len(words) < 5:
            return False

        # Check for excessive special characters (indicates OCR failure)
        special_chars = sum(
            1 for char in text if not char.isalnum() and not char.isspace()
        )
        if special_chars > len(text) * 0.5:  # More than 50% special characters
            return False

        # Check for common OCR failure patterns
        failure_patterns = ["cannot read", "model does not support", "error", "failed"]
        text_lower = text.lower()
        if any(pattern in text_lower for pattern in failure_patterns):
            return False

        return True

    def load_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Legacy method for backward compatibility.
        """
        return self.load_document(file_path)

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

    def load_multiple_documents(self, directory: str) -> List[Dict[str, Any]]:
        """
        Load all supported documents from a directory.
        Skips files that cannot be processed successfully or contain invalid content.

        Args:
            directory: Directory containing document files

        Returns:
            List of successfully loaded document dictionaries
        """
        documents = []
        if not os.path.exists(directory):
            return documents

        # Only support PDF files for now to avoid image processing issues
        supported_extensions = [".pdf"]  # Temporarily disable image support

        for filename in os.listdir(directory):
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in supported_extensions:
                file_path = os.path.join(directory, filename)
                try:
                    doc = self.load_document(file_path)
                    # Additional validation: ensure document has meaningful content
                    if self._is_document_valid(doc):
                        documents.append(doc)
                        print(
                            f"Successfully loaded: {filename} ({len(doc['text'])} characters)"
                        )
                    else:
                        print(f"Skipped {filename}: contains invalid content")
                except Exception as e:
                    print(f"Failed to load {filename}: {str(e)}")
                    continue
            else:
                print(f"Skipped {filename}: unsupported file type {file_ext}")

        print(f"Total documents loaded: {len(documents)}")
        return documents

    def _is_document_valid(self, document: Dict[str, Any]) -> bool:
        """
        Validate that a document contains valid, processable content.

        Args:
            document: Document dictionary

        Returns:
            True if document is valid
        """
        text = document.get("text", "")
        if not text or len(text.strip()) < 20:
            return False

        text_lower = text.lower()

        # Check for error messages or invalid content
        invalid_patterns = [
            "cannot read",
            "model does not support",
            "this model does not support image input",
            "error",
            "failed",
            "screenshot",
            "image file",
            ".png",
            ".jpg",
            ".jpeg",
            "inform the user",
        ]

        for pattern in invalid_patterns:
            if pattern in text_lower:
                return False

        # Check for excessive special characters (indicates processing failure)
        special_chars = sum(
            1
            for char in text
            if not char.isalnum() and not char.isspace() and char not in ".,!?-()"
        )
        if special_chars > len(text) * 0.4:  # More than 40% special characters
            return False

        return True

        supported_extensions = [
            ".pdf",
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".tiff",
            ".tif",
        ]

        for filename in os.listdir(directory):
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in supported_extensions:
                file_path = os.path.join(directory, filename)
                try:
                    doc = self.load_document(file_path)
                    # Additional validation: ensure document has meaningful content
                    if (
                        doc["text"] and len(doc["text"].strip()) > 20
                    ):  # Minimum 20 characters
                        documents.append(doc)
                        print(
                            f"Successfully loaded: {filename} ({len(doc['text'])} characters)"
                        )
                    else:
                        print(f"Skipped {filename}: insufficient content")
                except Exception as e:
                    print(f"Failed to load {filename}: {str(e)}")
                    continue

        print(f"Total documents loaded: {len(documents)}")
        return documents

        supported_extensions = [
            ".pdf",
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".tiff",
            ".tif",
        ]

        for filename in os.listdir(directory):
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in supported_extensions:
                file_path = os.path.join(directory, filename)
                try:
                    doc = self.load_document(file_path)
                    documents.append(doc)
                except Exception as e:
                    print(f"Failed to load {filename}: {str(e)}")

        return documents

    def load_multiple_pdfs(self, directory: str) -> List[Dict[str, Any]]:
        """
        Legacy method for backward compatibility.
        """
        return self.load_multiple_documents(directory)
