import re
from typing import List, Tuple


class TextCleaner:
    def __init__(self):
        # Common header/footer patterns for academic documents
        self.header_patterns = [
            r"^.*Page \d+.*$",  # Page numbers
            r"^.*ICFAI University.*$",  # University headers
            r"^.*Student Information System.*$",  # SIS headers
            r"^.*Academic Regulations.*$",  # Regulation headers
            r"^.*Effective Date:.*$",  # Date headers
        ]

        self.footer_patterns = [
            r"^.*© \d{4} ICFAI.*$",  # Copyright footers
            r"^.*Confidential.*$",  # Confidentiality notices
            r"^.*Page \d+ of \d+.*$",  # Page X of Y
        ]

    def clean_text(self, text: str) -> str:
        """
        Clean the extracted text by removing headers, footers, and normalizing.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip lines that match header/footer patterns
            if self._is_header_or_footer(line):
                continue

            # Clean the line
            line = self._clean_line(line)
            if line:
                cleaned_lines.append(line)

        # Join lines and normalize spacing
        cleaned_text = "\n".join(cleaned_lines)
        cleaned_text = self._normalize_spacing(cleaned_text)

        return cleaned_text

    def clean_pages(self, pages: List[Tuple[int, str]]) -> List[Tuple[int, str]]:
        """
        Clean text for each page separately.

        Args:
            pages: List of (page_num, page_text) tuples

        Returns:
            List of cleaned (page_num, cleaned_text) tuples
        """
        cleaned_pages = []
        for page_num, page_text in pages:
            cleaned_text = self.clean_text(page_text)
            if cleaned_text.strip():
                cleaned_pages.append((page_num, cleaned_text))

        return cleaned_pages

    def _is_header_or_footer(self, line: str) -> bool:
        """
        Check if a line matches header or footer patterns.

        Args:
            line: Text line to check

        Returns:
            True if line is header/footer
        """
        line_lower = line.lower()

        # Check header patterns
        for pattern in self.header_patterns:
            if re.match(pattern, line_lower, re.IGNORECASE):
                return True

        # Check footer patterns
        for pattern in self.footer_patterns:
            if re.match(pattern, line_lower, re.IGNORECASE):
                return True

        # Check for very short lines that are likely headers/footers
        if len(line.strip()) < 20 and not any(char.islower() for char in line):
            return True

        return False

    def _clean_line(self, line: str) -> str:
        """
        Clean individual line content.

        Args:
            line: Text line to clean

        Returns:
            Cleaned line
        """
        # Remove excessive whitespace
        line = re.sub(r"\s+", " ", line)

        # Remove page numbers in middle of line
        line = re.sub(r"\s*Page \d+\s*", " ", line)

        # Remove trailing/leading punctuation that might be artifacts
        line = line.strip(".,;:- ")

        return line.strip()

    def _normalize_spacing(self, text: str) -> str:
        """
        Normalize spacing in the text.

        Args:
            text: Text to normalize

        Returns:
            Normalized text
        """
        # Replace multiple newlines with double newline (paragraph breaks)
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

        # Remove excessive spaces
        text = re.sub(r" +", " ", text)

        # Ensure single space after punctuation
        text = re.sub(r"([.!?])\s*([A-Z])", r"\1 \2", text)

        return text.strip()
