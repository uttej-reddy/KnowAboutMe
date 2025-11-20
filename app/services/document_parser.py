import PyPDF2
import pdfplumber
from pathlib import Path
from typing import Dict, List


class DocumentParser:
    """Parse resumes and documents to extract text"""

    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """
        Parse PDF document and extract text

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text content
        """
        text = ""

        try:
            # Try pdfplumber first (better for complex PDFs)
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumber failed: {e}, trying PyPDF2...")

            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e:
                print(f"PyPDF2 also failed: {e}")
                raise

        return text.strip()

    @staticmethod
    def parse_docx(file_path: str) -> str:
        """
        Parse DOCX document and extract text

        Args:
            file_path: Path to DOCX file

        Returns:
            Extracted text content
        """
        try:
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            print(f"Failed to parse DOCX: {e}")
            raise

    @staticmethod
    def parse_txt(file_path: str) -> str:
        """
        Parse text file

        Args:
            file_path: Path to text file

        Returns:
            File content
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()

    def parse_document(self, file_path: str) -> str:
        """
        Parse any supported document format

        Args:
            file_path: Path to document

        Returns:
            Extracted text
        """
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension == '.pdf':
            return self.parse_pdf(file_path)
        elif extension in ['.docx', '.doc']:
            return self.parse_docx(file_path)
        elif extension == '.txt':
            return self.parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")

    def parse_multiple_documents(self, file_paths: List[str]) -> Dict[str, str]:
        """
        Parse multiple documents

        Args:
            file_paths: List of file paths

        Returns:
            Dictionary mapping filename to extracted text
        """
        results = {}
        for file_path in file_paths:
            try:
                filename = Path(file_path).name
                results[filename] = self.parse_document(file_path)
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
                results[filename] = f"Error: {str(e)}"

        return results
