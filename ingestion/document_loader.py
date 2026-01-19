import os
from typing import Dict, List, Any


class DocumentLoader:
    def __init__(self):
        from config.config import Config

        self.config = Config()

    def load_document(self, file_path: str) -> Dict[str, Any]:
        """
        Load TXT document and extract text.

        Args:
            file_path: Path to the TXT file

        Returns:
            Dict containing:
            - 'text': Full extracted text
            - 'pages': List of (page_num, page_text) tuples
            - 'metadata': Document metadata
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        if ext != ".txt":
            raise ValueError("Only .txt files are supported")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                text = f.read()

        text_pages = [(1, text)]
        metadata = {
            "filename": os.path.basename(file_path),
            "upload_date": os.path.getmtime(file_path),
            "file_size": os.path.getsize(file_path),
            "pages": 1,
            "file_type": "txt",
        }

        return {"text": text.strip(), "pages": text_pages, "metadata": metadata}

    def load_multiple_documents(self, directory: str) -> List[Dict[str, Any]]:
        """
        Load all TXT documents from a directory.
        """
        documents = []
        if not os.path.exists(directory):
            return documents

        for filename in os.listdir(directory):
            if filename.lower().endswith(".txt"):
                file_path = os.path.join(directory, filename)
                try:
                    doc = self.load_document(file_path)
                    documents.append(doc)
                    print(f"Successfully loaded: {filename}")
                except Exception as e:
                    print(f"Failed to load {filename}: {str(e)}")

        print(f"Total documents loaded: {len(documents)}")
        return documents

    def load_multiple_pdfs(self, directory: str) -> List[Dict[str, Any]]:
        """
        Legacy method for backward compatibility.
        """
        return self.load_multiple_documents(directory)
