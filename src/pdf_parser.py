import fitz  # PyMuPDF
import re
from typing import Dict, List, Tuple

class PDFParser:
    def __init__(self):
        pass
    
    def parse(self, pdf_path: str) -> Dict:
        """Parse PDF and extract text with structure information."""
        doc = fitz.open(pdf_path)
        pages_data = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extract text blocks with formatting info
            blocks = page.get_text("dict")
            text_blocks = []
            
            for block in blocks["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        font_info = {"size": 12, "flags": 0}
                        
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text:
                                line_text += text + " "
                                font_info["size"] = span["size"]
                                font_info["flags"] = span["flags"]
                                
                        if line_text.strip():
                            text_blocks.append({
                                "text": line_text.strip(),
                                "page": page_num + 1,
                                "bbox": block["bbox"],
                                "font_size": font_info["size"],
                                "font_flags": font_info["flags"]
                            })
            
            pages_data.append({
                "page_num": page_num + 1,
                "blocks": text_blocks
            })
        
        doc.close()
        
        return {
            "title": self._extract_title(pages_data),
            "pages": pages_data,
            "total_pages": len(pages_data)
        }
    
    def _extract_title(self, pages_data: List[Dict]) -> str:
        """Extract document title from first page."""
        if not pages_data or not pages_data[0]["blocks"]:
            return "Untitled Document"
        
        # Find the largest font size on first page
        first_page_blocks = pages_data[0]["blocks"]
        max_font_size = max(block["font_size"] for block in first_page_blocks)
        
        # Use text with largest font size as title
        for block in first_page_blocks:
            if block["font_size"] == max_font_size:
                text = block["text"].strip()
                if 5 < len(text) < 200:  # Reasonable title length
                    return text
        
        return "Untitled Document"
