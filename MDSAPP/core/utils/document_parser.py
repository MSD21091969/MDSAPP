# MDSAPP/core/utils/document_parser.py

import fitz  # PyMuPDF
import docx
from typing import Protocol
import logging # Added logging import

logger = logging.getLogger(__name__) # Added logger

class Parser(Protocol):
    """Protocol for document parsers."""
    def parse(self, file_path: str) -> str:
        ... # Ellipsis is valid here

class DocumentParser:
    """A utility to extract text from various document types."""

    def parse(self, file_path: str) -> str:
        """
        Parses a document based on its file extension.

        Args:
            file_path: The path to the document file.

        Returns:
            The extracted text content as a single string.
        
        Raises:
            ValueError: If the file type is not supported.
        """
        if file_path.lower().endswith(".pdf"):
            return self._parse_pdf(file_path)
        elif file_path.lower().endswith(".docx"):
            return self._parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type for file: {file_path}")

    def _parse_pdf(self, file_path: str) -> str:
        """Extracts text from a PDF document."""
        text = ""
        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {e}") # Changed print to logger.error
            return ""
        return text

    def _parse_docx(self, file_path: str) -> str:
        """Extracts text from a DOCX document."""
        try:
            doc = docx.Document(file_path)
            full_text = [para.text for para in doc.paragraphs]
            return "\n".join(full_text)
        except Exception as e:
            logger.error(f"Error parsing DOCX {file_path}: {e}") # Changed print to logger.error
            return ""
