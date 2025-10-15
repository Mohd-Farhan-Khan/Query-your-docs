import os
from typing import BinaryIO
from PyPDF2 import PdfReader
from docx import Document
import uuid

class FileHandler:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> tuple[str, int]:
        """Extract text from PDF and return (text, page_count)"""
        reader = PdfReader(file_path)
        page_count = len(reader.pages)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text, page_count
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> tuple[str, int]:
        """Extract text from DOCX and return (text, page_count)"""
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        # Rough estimate: 500 words per page
        word_count = len(text.split())
        page_count = max(1, word_count // 500)
        return text, page_count
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> tuple[str, int]:
        """Extract text from TXT and return (text, page_count)"""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        word_count = len(text.split())
        page_count = max(1, word_count // 500)
        return text, page_count
    
    @staticmethod
    def save_upload_file(file: BinaryIO, filename: str) -> str:
        """Save uploaded file and return file path"""
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(filename)[1]
        new_filename = f"{file_id}{file_extension}"
        file_path = os.path.join(upload_dir, new_filename)
        
        with open(file_path, "wb") as f:
            content = file.read()
            f.write(content)
        
        return file_path