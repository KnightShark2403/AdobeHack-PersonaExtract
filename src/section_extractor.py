import re
from typing import List, Dict
from collections import Counter

class SectionExtractor:
    def __init__(self):
        self.min_heading_length = 3
        self.max_heading_length = 200
    
    def extract_sections(self, document_data: Dict) -> List[Dict]:
        """Extract sections from parsed document data."""
        sections = []
        current_section = None
        
        for page_data in document_data["pages"]:
            for block in page_data["blocks"]:
                text = block["text"].strip()
                
                # Check if this is a heading
                if self._is_heading(block, page_data["blocks"]):
                    # Save previous section if exists
                    if current_section and current_section["content"].strip():
                        sections.append(current_section)
                    
                    # Start new section
                    current_section = {
                        "title": text,
                        "page": block["page"],
                        "level": self._determine_heading_level(block, page_data["blocks"]),
                        "content": "",
                        "subsections": []
                    }
                else:
                    # Add content to current section
                    if current_section:
                        current_section["content"] += text + " "
                    else:
                        # Create a default section for content without heading
                        current_section = {
                            "title": "Document Content",
                            "page": block["page"],
                            "level": 1,
                            "content": text + " ",
                            "subsections": []
                        }
        
        # Add the last section
        if current_section and current_section["content"].strip():
            sections.append(current_section)
        
        # Extract subsections for each section
        for section in sections:
            section["subsections"] = self._extract_subsections(section["content"])
        
        return sections
    
    def _is_heading(self, block: Dict, all_blocks: List[Dict]) -> bool:
        """Determine if a text block is a heading using dynamic analysis."""
        text = block["text"].strip()
        
        # Skip if text is too short or too long
        if len(text) < self.min_heading_length or len(text) > self.max_heading_length:
            return False
        
        # Calculate average font size of page
        font_sizes = [b["font_size"] for b in all_blocks if b["font_size"] > 0]
        if not font_sizes:
            return False
        
        avg_font_size = sum(font_sizes) / len(font_sizes)
        
        # Heading if font size is significantly larger than average
        if block["font_size"] > avg_font_size * 1.2:
            return True
        
        # Check if text has heading-like patterns
        heading_patterns = [
            r'^\d+\.?\s+\w+',  # Numbered sections
            r'^[IVX]+\.?\s+\w+',  # Roman numerals
            r'^[A-Z][a-z]*\s*:',  # Title case with colon
            r'^[A-Z\s]{3,}$',  # All caps short text
        ]
        
        for pattern in heading_patterns:
            if re.match(pattern, text):
                return True
        
        # Check if text ends with colon (common in headings)
        if text.endswith(':') and len(text.split()) <= 8:
            return True
        
        # Check if text is standalone and short
        if len(text.split()) <= 10 and block["font_flags"] & 16:  # Bold flag
            return True
        
        return False
    
    def _determine_heading_level(self, block: Dict, all_blocks: List[Dict]) -> int:
        """Determine heading level dynamically based on font size."""
        font_sizes = [b["font_size"] for b in all_blocks if b["font_size"] > 0]
        if not font_sizes:
            return 1
        
        # Sort font sizes to determine levels
        unique_sizes = sorted(set(font_sizes), reverse=True)
        
        # Assign levels based on font size ranking
        for i, size in enumerate(unique_sizes[:3]):
            if block["font_size"] == size:
                return i + 1
        
        return 3  # Default to H3 for smaller fonts
    
    def _extract_subsections(self, content: str) -> List[Dict]:
        """Extract subsections from section content."""
        if not content.strip():
            return []
        
        # Split content into sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 3:
            return [{
                "content": content.strip(),
                "summary": self._create_summary(content.strip()),
                "references": self._extract_references(content)
            }]
        
        # Group sentences into subsections
        subsections = []
        current_subsection = []
        
        for sentence in sentences:
            current_subsection.append(sentence)
            
            # Create subsection every 3-5 sentences
            if len(current_subsection) >= 4:
                subsection_text = '. '.join(current_subsection) + '.'
                subsections.append({
                    "content": subsection_text,
                    "summary": self._create_summary(subsection_text),
                    "references": self._extract_references(subsection_text)
                })
                current_subsection = []
        
        # Add remaining sentences
        if current_subsection:
            subsection_text = '. '.join(current_subsection) + '.'
            subsections.append({
                "content": subsection_text,
                "summary": self._create_summary(subsection_text),
                "references": self._extract_references(subsection_text)
            })
        
        return subsections
    
    def _create_summary(self, text: str) -> str:
        """Create extractive summary of text."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 2:
            return text
        
        # Simple extractive: first sentence + longest sentence
        first_sentence = sentences[0]
        longest_sentence = max(sentences, key=len)
        
        if first_sentence == longest_sentence:
            return first_sentence + "."
        else:
            return first_sentence + ". " + longest_sentence + "."
    
    def _extract_references(self, text: str) -> List[str]:
        """Extract references to figures, tables, etc."""
        references = []
        
        # Common reference patterns
        ref_patterns = [
            r'Figure\s+\d+',
            r'Table\s+\d+',
            r'Section\s+\d+',
            r'Chapter\s+\d+',
            r'Equation\s+\d+',
            r'\[\d+\]',  # Citation numbers
        ]
        
        for pattern in ref_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            references.extend(matches)
        
        return list(set(references))  # Remove duplicates
