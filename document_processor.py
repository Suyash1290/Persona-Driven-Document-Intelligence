import PyPDF2
import pdfplumber
import re
from typing import List, Dict, Any, Optional

class DocumentProcessor:
    """Handles PDF document processing and text extraction."""
    
    def __init__(self):
        self.min_section_length = 100  # Minimum characters for a valid section
    
    def extract_text_from_pdf(self, file_path: str, filename: str) -> Optional[Dict[str, Any]]:
        """Extract text from PDF using multiple methods for robustness."""
        try:
            # Try pdfplumber first (better for complex layouts)
            text_content = self._extract_with_pdfplumber(file_path)
            
            if not text_content:
                # Fallback to PyPDF2
                text_content = self._extract_with_pypdf2(file_path)
            
            if not text_content:
                print(f"Could not extract text from {filename}")
                return None
            
            return {
                "filename": filename,
                "file_path": file_path,
                "content": text_content,
                "page_count": len(text_content)
            }
        
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            return None
    
    def _extract_with_pdfplumber(self, file_path: str) -> List[str]:
        """Extract text using pdfplumber for better layout preservation."""
        pages = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        pages.append(text)
                    else:
                        pages.append("")
        except Exception:
            return []
        return pages
    
    def _extract_with_pypdf2(self, file_path: str) -> List[str]:
        """Fallback extraction using PyPDF2."""
        pages = []
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    pages.append(text if text else "")
        except Exception:
            return []
        return pages
    
    def extract_sections(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract meaningful sections from document pages."""
        sections = []
        filename = document["filename"]
        
        for page_num, page_text in enumerate(document["content"], 1):
            if not page_text.strip():
                continue
            
            # Split page into sections based on various delimiters
            page_sections = self._split_page_into_sections(page_text)
            
            for section_idx, section_text in enumerate(page_sections):
                if len(section_text.strip()) < self.min_section_length:
                    continue
                
                # Generate section title
                section_title = self._generate_section_title(section_text)
                
                section = {
                    "document_name": filename,
                    "page_number": page_num,
                    "section_title": section_title,
                    "content": section_text.strip(),
                    "content_preview": self._generate_preview(section_text),
                    "word_count": len(section_text.split()),
                    "section_id": f"{filename}_p{page_num}_s{section_idx}"
                }
                sections.append(section)
        
        return sections
    
    def _split_page_into_sections(self, page_text: str) -> List[str]:
        """Split page text into logical sections."""
        # Common section delimiters
        section_patterns = [
            r'\n\s*\d+\.\s+',  # Numbered sections (1. 2. 3.)
            r'\n\s*[A-Z][^.]{20,}\n',  # Title-like lines
            r'\n\s*[A-Z]{2,}[:\s]',  # ALL CAPS headers
            r'\n\s*\w+\s+\d+\s*\n',  # Chapter/Section numbers
            r'\n\s*#+\s+',  # Markdown-style headers
            r'\n\s*Introduction\s*\n',  # Common sections
            r'\n\s*Conclusion\s*\n',
            r'\n\s*Abstract\s*\n',
            r'\n\s*References\s*\n',
            r'\n\s*Methods\s*\n',
            r'\n\s*Results\s*\n',
        ]
        
        # Try to split by patterns
        for pattern in section_patterns:
            splits = re.split(pattern, page_text, flags=re.IGNORECASE)
            if len(splits) > 1:
                return [split.strip() for split in splits if split.strip()]
        
        # Fallback: split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\s*\n', page_text)
        if len(paragraphs) > 3:
            return [p.strip() for p in paragraphs if len(p.strip()) > 50]
        
        # Last resort: return the whole page as one section
        return [page_text]
    
    def _generate_section_title(self, section_text: str) -> str:
        """Generate a meaningful title for a section."""
        lines = section_text.strip().split('\n')
        
        # Look for a title-like first line
        first_line = lines[0].strip()
        
        # Check if first line looks like a title
        if (len(first_line) < 100 and 
            not first_line.endswith('.') and 
            len(first_line.split()) < 12):
            return first_line
        
        # Extract first sentence as title
        sentences = re.split(r'[.!?]+', section_text)
        if sentences:
            title = sentences[0].strip()
            if len(title) > 80:
                title = title[:80] + "..."
            return title
        
        # Fallback: use first 50 characters
        return section_text[:50].strip() + "..."
    
    def _generate_preview(self, text: str, max_length: int = 200) -> str:
        """Generate a preview of the section content."""
        # Remove extra whitespace
        clean_text = ' '.join(text.split())
        
        if len(clean_text) <= max_length:
            return clean_text
        
        # Find a good breaking point
        preview = clean_text[:max_length]
        last_space = preview.rfind(' ')
        if last_space > max_length * 0.8:
            preview = preview[:last_space]
        
        return preview + "..." 