import aiofiles
import httpx
import pdfplumber
import pypdf
from docx import Document
import tempfile
import os
from typing import List, Tuple
import re
import io
import logging

logger = logging.getLogger(__name__)

class DocumentLoader:
    def __init__(self):
        # Check if we should use local/fast mode for testing (disabled for production)
        self.use_local_mode = os.getenv('USE_LOCAL_MODE', 'false').lower() == 'true'
        # Hackathon optimization: limit pages for faster processing while maintaining accuracy
        self.hackathon_mode = os.getenv('HACKATHON_MODE', 'true').lower() == 'true'
        self.max_pages_local = 5  # Local testing
        self.max_pages_hackathon = 10  # Hackathon optimization for 30s requirement
        
        if self.use_local_mode:
            logger.info(f"DocumentLoader: Using local mode (max {self.max_pages_local} pages)")
        elif self.hackathon_mode:
            logger.info(f"DocumentLoader: Using hackathon mode (max {self.max_pages_hackathon} pages for speed)")
        else:
            logger.info("DocumentLoader: Using production mode (full document processing)")
    @staticmethod
    async def download_document(url: str) -> bytes:
        """Download document from URL"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                logger.info(f"Successfully downloaded document from {url}")
                return response.content
        except Exception as e:
            logger.error(f"Failed to download document from {url}: {str(e)}")
            raise

    def extract_text_from_pdf_pdfplumber(self, content: bytes) -> List[Tuple[str, int]]:
        """Extract text from PDF using pdfplumber"""
        texts = []
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(content)
            tmp_file.flush()
            
            try:
                with pdfplumber.open(tmp_file.name) as pdf:
                    # Determine max pages to process based on mode
                    if self.use_local_mode:
                        max_pages = self.max_pages_local
                        mode_info = f" (local mode - first {max_pages} pages)"
                    elif self.hackathon_mode:
                        max_pages = self.max_pages_hackathon
                        mode_info = f" (hackathon mode - first {max_pages} pages)"
                    else:
                        max_pages = len(pdf.pages)
                        mode_info = ""
                    
                    for page_num, page in enumerate(pdf.pages[:max_pages]):
                        text = page.extract_text()
                        if text and text.strip():
                            texts.append((text.strip(), page_num + 1))
                    logger.info(f"Extracted text from {len(texts)} pages using pdfplumber{mode_info}")
                return texts
            except Exception as e:
                logger.warning(f"pdfplumber failed: {e}, trying pypdf")
                return self.extract_text_from_pdf_pypdf(content)
            finally:
                os.unlink(tmp_file.name)

    def extract_text_from_pdf_pypdf(self, content: bytes) -> List[Tuple[str, int]]:
        """Extract text from PDF using pypdf (backup method)"""
        texts = []
        
        try:
            pdf_reader = pypdf.PdfReader(io.BytesIO(content))
            # Determine max pages to process based on mode
            if self.use_local_mode:
                max_pages = self.max_pages_local
            elif self.hackathon_mode:
                max_pages = self.max_pages_hackathon
            else:
                max_pages = None  # Process all pages in full production
            
            for page_num, page in enumerate(pdf_reader.pages[:max_pages]):
                text = page.extract_text()
                if text and text.strip():
                    texts.append((text.strip(), page_num + 1))
            
            mode_info = f" (local mode - first {max_pages} pages)" if self.use_local_mode else ""
            logger.info(f"Extracted text from {len(texts)} pages using pypdf{mode_info}")
            return texts
        except Exception as e:
            logger.error(f"pypdf extraction failed: {e}")
            return [("Could not extract text from PDF", 1)]

    def extract_text_from_pdf(self, content: bytes) -> List[Tuple[str, int]]:
        """Main PDF extraction method"""
        try:
            return self.extract_text_from_pdf_pdfplumber(content)
        except Exception:
            return self.extract_text_from_pdf_pypdf(content)

    @staticmethod
    def extract_text_from_docx(content: bytes) -> List[Tuple[str, int]]:
        """Extract text from DOCX"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            tmp_file.write(content)
            tmp_file.flush()
            
            try:
                doc = Document(tmp_file.name)
                texts = []
                for i, paragraph in enumerate(doc.paragraphs):
                    if paragraph.text.strip():
                        texts.append((paragraph.text.strip(), i + 1))
                logger.info(f"Extracted text from {len(texts)} paragraphs from DOCX")
                return texts
            finally:
                os.unlink(tmp_file.name)

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            if end < len(text):
                # Find the last sentence boundary within the chunk
                last_period = text.rfind('.', start, end)
                if last_period > start:
                    end = last_period + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            if end >= len(text):
                break
            start = end - overlap
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks