import re
from typing import List, Dict

class SectionExtractor:
    def extract_sections(self, document_data: Dict) -> List[Dict]:
        """Extract sections with generous thresholds to ensure content is found."""
        if not document_data.get("pages"):
            return []
        
        sections = []
        
        for page_data in document_data["pages"]:
            text = page_data["text"]
            
            # Try multiple splitting methods to ensure we get content
            
            # Method 1: Split by double newlines (paragraphs)
            paragraphs = re.split(r'\n\s*\n', text)
            
            # Method 2: Split by single newlines if paragraphs are too few
            if len(paragraphs) < 3:
                paragraphs = text.split('\n')
            
            # Method 3: Split by sentences if still too few
            if len(paragraphs) < 3:
                paragraphs = re.split(r'[.!?]+', text)
            
            for para in paragraphs:
                para = para.strip()
                
                # Very generous content threshold
                if len(para) > 30:  # At least 30 characters
                    # Extract title from first line or first few words
                    lines = para.split('\n')
                    title = lines[0] if lines[0] else para[:50]
                    
                    # Clean title
                    title = re.sub(r'\s+', ' ', title.strip())[:100]
                    
                    sections.append({
                        "title": title,
                        "page": page_data["page_num"],
                        "content": para[:800],  # Keep substantial content
                        "subsections": self._create_simple_subsections(para)
                    })
        
        # Ensure we have at least some sections
        if not sections and document_data["pages"]:
            # Fallback: create sections from each page
            for page_data in document_data["pages"]:
                if len(page_data["text"]) > 100:
                    sections.append({
                        "title": f"Page {page_data['page_num']} Content",
                        "page": page_data["page_num"],
                        "content": page_data["text"][:800],
                        "subsections": []
                    })
        
        print(f"Extracted {len(sections)} sections from document")
        return sections[:20]  # Return up to 20 sections
    
    def _create_simple_subsections(self, content: str) -> List[Dict]:
        """Create simple subsections if content is long enough."""
        if len(content) < 200:
            return []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if len(sentences) <= 2:
            return []
        
        # Create 1-2 subsections
        mid_point = len(sentences) // 2
        
        subsections = []
        
        # First subsection
        first_half = '. '.join(sentences[:mid_point]) + '.'
        if len(first_half) > 50:
            subsections.append({
                "content": first_half[:400],
                "summary": sentences[0][:150] + "..." if len(sentences[0]) > 150 else sentences[0],
                "references": []
            })
        
        # Second subsection
        if len(sentences) > mid_point:
            second_half = '. '.join(sentences[mid_point:]) + '.'
            if len(second_half) > 50:
                subsections.append({
                    "content": second_half[:400],
                    "summary": sentences[mid_point][:150] + "..." if len(sentences[mid_point]) > 150 else sentences[mid_point],
                    "references": []
                })
        
        return subsections
