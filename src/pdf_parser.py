import fitz  # PyMuPDF
import re
from typing import Dict, List
import locale

class PDFParser:
    def __init__(self):
        # Multilingual text patterns
        self.text_patterns = {
            'latin': re.compile(r'[a-zA-ZÀ-ÿ]+'),
            'cyrillic': re.compile(r'[а-яё]+', re.IGNORECASE),
            'arabic': re.compile(r'[\u0600-\u06FF]+'),
            'chinese': re.compile(r'[\u4e00-\u9fff]+'),
            'japanese': re.compile(r'[\u3040-\u309f\u30a0-\u30ff]+'),
            'korean': re.compile(r'[\uac00-\ud7af]+'),
            'hindi': re.compile(r'[\u0900-\u097F]+'),
            'thai': re.compile(r'[\u0e00-\u0e7f]+'),
            'vietnamese': re.compile(r'[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]+', re.IGNORECASE)
        }
        
        # Language-specific stopwords for better text detection
        self.stopwords = {
            'english': {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'},
            'spanish': {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te'},
            'french': {'le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir', 'que', 'pour'},
            'german': {'der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich', 'des', 'auf'},
            'italian': {'il', 'di', 'che', 'e', 'la', 'per', 'un', 'in', 'con', 'non', 'da', 'su'},
            'portuguese': {'o', 'de', 'a', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com'},
            'russian': {'в', 'и', 'не', 'на', 'я', 'быть', 'тот', 'а', 'за', 'к', 'до', 'из'},
            'arabic': {'في', 'من', 'إلى', 'على', 'هذا', 'التي', 'كان', 'لم', 'قد', 'كل', 'ما', 'أن'},
            'chinese': {'的', '了', '和', '是', '就', '都', '而', '及', '与', '则', '等', '在'},
            'japanese': {'の', 'に', 'は', 'を', 'た', 'が', 'で', 'て', 'と', 'し', 'れ', 'さ'},
            'korean': {'이', '가', '은', '는', '을', '를', '의', '에', '로', '와', '과', '도'},
            'hindi': {'का', 'एक', 'की', 'को', 'है', 'में', 'से', 'के', 'पर', 'और', 'या', 'हो'}
        }
    
    def detect_language(self, text: str) -> List[str]:
        """Detect languages present in the text."""
        detected_languages = []
        text_lower = text.lower()
        
        # Check for language patterns
        for lang, pattern in self.text_patterns.items():
            if pattern.search(text):
                detected_languages.append(lang)
        
        # Check for language-specific stopwords
        for lang, stopwords in self.stopwords.items():
            word_matches = sum(1 for word in stopwords if word in text_lower)
            if word_matches >= 2:  # At least 2 stopwords found
                detected_languages.append(lang)
        
        return list(set(detected_languages)) if detected_languages else ['english']
    
    def parse(self, pdf_path: str) -> Dict:
        """Parse PDF with multilingual support."""
        try:
            doc = fitz.open(pdf_path)
            total_pages = min(len(doc), 50)  # Adobe requirement
            pages_data = []
            detected_languages = set()
            
            for page_num in range(total_pages):
                page = doc[page_num]
                
                # Extract text blocks with multilingual handling
                text_blocks = self._extract_multilingual_blocks(page, page_num + 1)
                
                if text_blocks:
                    pages_data.append({
                        "page_num": page_num + 1,
                        "blocks": text_blocks
                    })
                    
                    # Detect languages in this page
                    page_text = ' '.join([block['text'] for block in text_blocks])
                    page_languages = self.detect_language(page_text)
                    detected_languages.update(page_languages)
            
            doc.close()
            
            return {
                "title": self._extract_multilingual_title(pages_data),
                "pages": pages_data,
                "total_pages": len(pages_data),
                "detected_languages": list(detected_languages)
            }
            
        except Exception as e:
            print(f"Error parsing PDF {pdf_path}: {str(e)}")
            return {"title": "Error", "pages": [], "total_pages": 0, "detected_languages": []}
    
    def _extract_multilingual_blocks(self, page, page_num: int) -> List[Dict]:
        """Extract text blocks with proper multilingual character handling."""
        text_blocks = []
        
        # Use dict extraction for better formatting info
        page_dict = page.get_text("dict")
        
        for block in page_dict.get("blocks", []):
            if "lines" not in block:
                continue
                
            for line in block["lines"]:
                line_text = ""
                font_info = {"size": 12, "flags": 0}
                
                for span in line["spans"]:
                    text = span.get("text", "").strip()
                    if text:
                        # Handle different encodings properly
                        try:
                            # Ensure proper Unicode handling
                            text = text.encode('utf-8').decode('utf-8')
                            line_text += text + " "
                            font_info["size"] = span.get("size", 12)
                            font_info["flags"] = span.get("flags", 0)
                        except UnicodeError:
                            # Skip problematic characters
                            continue
                
                if line_text.strip() and len(line_text.strip()) > 1:
                    text_blocks.append({
                        "text": line_text.strip(),
                        "page": page_num,
                        "bbox": block.get("bbox", [0, 0, 0, 0]),
                        "font_size": font_info["size"],
                        "font_flags": font_info["flags"],
                        "languages": self.detect_language(line_text.strip())
                    })
        
        return text_blocks
    
    def _extract_multilingual_title(self, pages_data: List[Dict]) -> str:
        """Extract title with multilingual support."""
        if not pages_data or not pages_data[0]["blocks"]:
            return "Untitled Document"
        
        # Find text with largest font size (likely title)
        first_page_blocks = pages_data[0]["blocks"]
        if not first_page_blocks:
            return "Untitled Document"
        
        max_font_size = max(block["font_size"] for block in first_page_blocks)
        
        for block in first_page_blocks:
            if block["font_size"] == max_font_size:
                text = block["text"].strip()
                if 5 <= len(text) <= 200:
                    return text
        
        # Fallback to first meaningful text
        for block in first_page_blocks:
            text = block["text"].strip()
            if 5 <= len(text) <= 200:
                return text
        
        return "Untitled Document"
