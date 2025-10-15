from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.utils.file_handler import FileHandler
from app.config import get_settings

settings = get_settings()

class DocumentProcessor:
    def __init__(self):
        self.file_handler = FileHandler()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )
    
    async def process_document(self, file_path: str, filename: str) -> tuple[str, int, list]:
        """
        Process document: extract text, validate, and chunk
        Returns: (text, page_count, chunks)
        """
        # Extract text based on file type
        if filename.lower().endswith('.pdf'):
            text, page_count = self.file_handler.extract_text_from_pdf(file_path)
        elif filename.lower().endswith('.docx'):
            text, page_count = self.file_handler.extract_text_from_docx(file_path)
        elif filename.lower().endswith('.txt'):
            text, page_count = self.file_handler.extract_text_from_txt(file_path)
        else:
            raise ValueError("Unsupported file format")
        
        # Validate page count
        if page_count > settings.max_pages_per_doc:
            raise ValueError(f"Document exceeds maximum page limit of {settings.max_pages_per_doc}")
        
        # Chunk the text
        chunks = self.text_splitter.split_text(text)
        
        return text, page_count, chunks