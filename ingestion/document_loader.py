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

        return self._load_text_file(file_path)

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

            if not full_text:
                raise ValueError("Text file contains no readable content")

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

        text_lower = text.lower()
        return not any(p in text_lower for p in bad_patterns)
