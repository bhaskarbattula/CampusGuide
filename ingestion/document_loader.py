import os
from typing import Dict, List, Any
from config.config import Config


class DocumentLoader:
    def __init__(self):
        self.config = Config()

    # ---------------- SINGLE DOCUMENT ---------------- #

    def load_document(self, file_path: str) -> Dict[str, Any]:
        """
        Load a supported document (.txt only).

        Returns:
            {
              "text": full text,
              "pages": list of line numbers,
              "metadata": metadata dict
            }
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        if ext != ".txt":
            raise ValueError("Only .txt files are supported")

<<<<<<< HEAD
        return self._load_text_file(file_path)
=======
        # Handle different file types
        if file_ext == ".pdf":
            return self._load_pdf_file(file_path)
        elif file_ext == ".txt":
            return self._load_txt_file(file_path)
        elif file_ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"]:
            return self._load_image_file(file_path)
        else:
            raise ValueError(
                f"Unsupported file type: {file_ext}. Supported: PDF, TXT, PNG, JPG, JPEG, BMP, TIFF, TIF"
            )
>>>>>>> bhaskar

    # ---------------- TXT LOADER ---------------- #

    def _load_text_file(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_lines = f.readlines()

            text_lines = []
            pages = []
            full_text = []

            for line_num, line in enumerate(raw_lines, start=1):
                line = line.strip()
                if line:
                    text_lines.append(line)
                    pages.append(line_num)
                    full_text.append(line)

<<<<<<< HEAD
            if not full_text:
                raise ValueError("Text file contains no readable content")
=======
    def _load_txt_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load TXT document and extract text.

        Args:
            file_path: Path to the TXT file

        Returns:
            Dict containing extracted data
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, "r", encoding="latin-1") as f:
                text = f.read()

        # For TXT files, treat as single page
        text_pages = [(1, text)]

        # Extract metadata
        metadata = {
            "filename": os.path.basename(file_path),
            "upload_date": os.path.getmtime(file_path),
            "file_size": os.path.getsize(file_path),
            "pages": 1,
            "file_type": "txt",
        }

        return {"text": text.strip(), "pages": text_pages, "metadata": metadata}

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
>>>>>>> bhaskar

            metadata = {
                "filename": os.path.basename(file_path),
                "file_type": "txt",
                "line_start": pages[0],
                "line_end": pages[-1],
                "total_lines": len(pages),
            }

            return {
                "text": "\n".join(full_text),
                "pages": pages,          # ✅ IMPORTANT FIX
                "metadata": metadata,
            }

        except UnicodeDecodeError:
            raise RuntimeError(
                f"Encoding error while reading {file_path}. Use UTF-8."
            )

    # ---------------- MULTIPLE DOCUMENTS ---------------- #

    def load_multiple_documents(self, directory: str) -> List[Dict[str, Any]]:
        documents = []

        if not os.path.exists(directory):
            return documents

<<<<<<< HEAD
=======
        # Only support configured file types
        supported_extensions = self.config.SUPPORTED_EXTENSIONS

>>>>>>> bhaskar
        for filename in os.listdir(directory):
            if filename.lower().endswith(".txt"):
                path = os.path.join(directory, filename)
                try:
                    doc = self.load_document(path)
                    if self._is_document_valid(doc):
                        documents.append(doc)
                        print(f"Loaded TXT: {filename}")
                except Exception as e:
                    print(f"Failed to load {filename}: {e}")

        print(f"Total documents loaded: {len(documents)}")
        return documents

    # ---------------- VALIDATION ---------------- #

    def _is_document_valid(self, document: Dict[str, Any]) -> bool:
        text = document.get("text", "")
        if len(text.strip()) < 50:
            return False

        bad_patterns = [
            "error",
            "cannot read",
            "failed",
            "image file",
            ".png",
            ".jpg",
        ]

<<<<<<< HEAD
        text_lower = text.lower()
        return not any(p in text_lower for p in bad_patterns)
=======
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

    def load_multiple_pdfs(self, directory: str) -> List[Dict[str, Any]]:
        """
        Legacy method for backward compatibility.
        """
        return self.load_multiple_documents(directory)
>>>>>>> bhaskar
