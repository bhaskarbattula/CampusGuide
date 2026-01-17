from typing import List, Dict, Any, Tuple, Optional
from config.config import Config


class TextSplitter:
    def __init__(self):
        self.config = Config()

    def split_text(
        self, text: str, chunk_size: Optional[int] = None, overlap: Optional[int] = None
    ) -> List[str]:
        """
        Split text into chunks with overlap.

        Args:
            text: Text to split
            chunk_size: Size of each chunk (default from config)
            overlap: Overlap between chunks (default from config)

        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or self.config.CHUNK_SIZE
        overlap = overlap or self.config.CHUNK_OVERLAP

        if not text or chunk_size <= 0:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # If we're not at the end, try to find a good break point
            if end < len(text):
                # Look for sentence endings near the end
                sentence_endings = [". ", "! ", "? ", "\n\n"]
                break_point = end

                for ending in sentence_endings:
                    pos = text.rfind(ending, start, end)
                    if pos != -1 and pos > start + chunk_size // 2:
                        break_point = pos + len(ending)
                        break

                chunk = text[start:break_point].strip()
            else:
                chunk = text[start:].strip()

            if chunk:
                chunks.append(chunk)

            # Move start position with overlap
            start = max(start + 1, end - overlap)

        return chunks

    def split_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split a document into chunks with metadata preservation.

        Args:
            document: Document dict with 'text', 'pages', 'metadata'

        Returns:
            List of chunk dictionaries with metadata
        """
        text = document["text"]
        pages = document.get("pages", [])
        metadata = document.get("metadata", {})

        chunks = self.split_text(text)

        chunk_docs = []
        for i, chunk in enumerate(chunks):
            # Find which pages this chunk spans
            chunk_pages = self._find_chunk_pages(chunk, pages)

            chunk_doc = {
                "chunk_id": f"{metadata.get('filename', 'unknown')}_chunk_{i}",
                "text": chunk,
                "pages": chunk_pages,
                "metadata": {
                    **metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "start_page": chunk_pages[0] if chunk_pages else None,
                    "end_page": chunk_pages[-1] if chunk_pages else None,
                },
            }
            chunk_docs.append(chunk_doc)

        return chunk_docs

    def _find_chunk_pages(self, chunk: str, pages: List[Tuple[int, str]]) -> List[int]:
        """
        Find which pages a chunk appears on.

        Args:
            chunk: Text chunk
            pages: List of (page_num, page_text) tuples

        Returns:
            List of page numbers the chunk spans
        """
        chunk_pages = []
        chunk_lower = chunk.lower()

        for page_num, page_text in pages:
            if page_text.lower() in chunk_lower or any(
                word in page_text.lower() for word in chunk_lower.split()[:5]
            ):
                # More sophisticated check: check if significant portion of chunk is in page
                page_words = set(page_text.lower().split())
                chunk_words = set(chunk_lower.split())
                overlap = len(page_words.intersection(chunk_words))
                if overlap > len(chunk_words) * 0.3:  # 30% overlap
                    chunk_pages.append(page_num)

        return sorted(list(set(chunk_pages)))
