import fitz
from typing import Dict, List

class PDFParser:
    def parse(self, pdf_path: str) -> Dict:
        """Parse PDF and extract all readable text."""
        doc = fitz.open(pdf_path)
        pages_data = []
        
        # Process up to 20 pages for speed while getting enough content
        total_pages = min(len(doc), 20)
        
        for page_num in range(total_pages):
            page = doc[page_num]
            
            # Extract all text from the page
            text = page.get_text()
            
            if len(text.strip()) > 50:  # Only include pages with substantial content
                pages_data.append({
                    "page_num": page_num + 1,
                    "text": text.strip()
                })
        
        doc.close()
        
        # Extract title from first page
        title = "Document"
        if pages_data and pages_data[0]["text"]:
            # Use first meaningful line as title
            first_lines = pages_data[0]["text"].split('\n')[:3]
            for line in first_lines:
                if len(line.strip()) > 10 and len(line.strip()) < 100:
                    title = line.strip()
                    break
        
        return {
            "title": title,
            "pages": pages_data,
            "total_pages": len(pages_data)
        }
