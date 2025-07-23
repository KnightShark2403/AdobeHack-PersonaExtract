import re
from typing import List, Dict
from collections import Counter

class SectionExtractor:
    def __init__(self):
        # Multilingual heading patterns
        self.heading_patterns = {
            'numbered': re.compile(r'^\d+\.?\d*\.?\s+\w+'),
            'roman': re.compile(r'^[IVX]+\.?\s+\w+'),
            'letters': re.compile(r'^[A-Z]\.?\s+\w+'),
            'title_colon': re.compile(r'^[A-Z][^.!?]*:$'),
            'all_caps': re.compile(r'^[A-Z\s]{3,}$'),
            'bold_short': re.compile(r'^\w+(\s+\w+){0,5}$')  # Short bold text
        }
        
        # Common section keywords in multiple languages
        self.section_keywords = {
            'english': ['introduction', 'abstract', 'summary', 'conclusion', 'methodology', 'results', 
                       'discussion', 'background', 'literature', 'analysis', 'findings', 'references'],
            'spanish': ['introducción', 'resumen', 'conclusión', 'metodología', 'resultados', 
                       'discusión', 'antecedentes', 'análisis', 'referencias'],
            'french': ['introduction', 'résumé', 'conclusion', 'méthodologie', 'résultats', 
                      'discussion', 'contexte', 'analyse', 'références'],
            'german': ['einleitung', 'zusammenfassung', 'schlussfolgerung', 'methodik', 'ergebnisse', 
                      'diskussion', 'hintergrund', 'analyse', 'literatur'],
            'italian': ['introduzione', 'riassunto', 'conclusione', 'metodologia', 'risultati', 
                       'discussione', 'contesto', 'analisi', 'riferimenti'],
            'portuguese': ['introdução', 'resumo', 'conclusão', 'metodologia', 'resultados', 
                          'discussão', 'contexto', 'análise', 'referências']
        }
    
    def extract_sections(self, document_data: Dict) -> List[Dict]:
        """Enhanced section extraction with better quality."""
        if not document_data.get("pages"):
            return []
        
        sections = []
        current_section = None
        
        # Get document languages for better processing
        doc_languages = document_data.get("detected_languages", ['english'])
        
        for page_data in document_data["pages"]:
            for block in page_data["blocks"]:
                text = block["text"].strip()
                
                if len(text) < 3:
                    continue
                
                # Enhanced heading detection
                if self._is_quality_heading(block, page_data["blocks"], doc_languages):
                    # Save previous section if it has substantial content
                    if current_section and len(current_section["content"].strip()) > 50:
                        current_section["subsections"] = self._extract_quality_subsections(
                            current_section["content"], doc_languages
                        )
                        sections.append(current_section)
                    
                    # Start new section
                    current_section = {
                        "title": self._clean_heading_text(text),
                        "page": block["page"],
                        "level": self._determine_heading_level(block, page_data["blocks"]),
                        "content": "",
                        "subsections": [],
                        "languages": block.get("languages", doc_languages)
                    }
                else:
                    # Add content to current section
                    if current_section:
                        current_section["content"] += text + " "
                    else:
                        # Create default section for orphaned content
                        current_section = {
                            "title": "Document Content",
                            "page": block["page"],
                            "level": 1,
                            "content": text + " ",
                            "subsections": [],
                            "languages": block.get("languages", doc_languages)
                        }
        
        # Add final section
        if current_section and len(current_section["content"].strip()) > 50:
            current_section["subsections"] = self._extract_quality_subsections(
                current_section["content"], current_section.get("languages", doc_languages)
            )
            sections.append(current_section)
        
        # Filter out low-quality sections
        quality_sections = []
        for section in sections:
            if self._is_quality_section(section):
                quality_sections.append(section)
        
        return quality_sections
    
    def _is_quality_heading(self, block: Dict, all_blocks: List[Dict], languages: List[str]) -> bool:
        """Enhanced heading detection with quality checks."""
        text = block["text"].strip()
        
        # Basic length check
        if not (3 <= len(text) <= 200):
            return False
        
        # Check heading patterns
        for pattern_name, pattern in self.heading_patterns.items():
            if pattern.match(text):
                return True
        
        # Check if it's a known section keyword
        text_lower = text.lower()
        for lang in languages:
            if lang in self.section_keywords:
                for keyword in self.section_keywords[lang]:
                    if keyword in text_lower and len(text.split()) <= 8:
                        return True
        
        # Font-based detection
        if all_blocks:
            avg_font_size = sum(b["font_size"] for b in all_blocks) / len(all_blocks)
            if block["font_size"] > avg_font_size * 1.3:  # Significantly larger
                return True
            
            # Bold text that's reasonably short
            if (block["font_flags"] & 16) and len(text.split()) <= 10:
                return True
        
        return False
    
    def _clean_heading_text(self, text: str) -> str:
        """Clean and normalize heading text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove trailing punctuation except meaningful ones
        text = re.sub(r'[^\w\s:.-]$', '', text)
        
        return text[:150]  # Limit length
    
    def _determine_heading_level(self, block: Dict, all_blocks: List[Dict]) -> int:
        """Determine heading level based on multiple factors."""
        text = block["text"].strip()
        
        # Pattern-based level detection
        if re.match(r'^\d+\.?\s+', text):  # 1. Main heading
            return 1
        elif re.match(r'^\d+\.\d+\.?\s+', text):  # 1.1 Sub heading
            return 2
        elif re.match(r'^\d+\.\d+\.\d+\.?\s+', text):  # 1.1.1 Sub-sub heading
            return 3
        
        # Font size based detection
        if all_blocks:
            font_sizes = sorted(set(b["font_size"] for b in all_blocks), reverse=True)
            for i, size in enumerate(font_sizes[:3]):
                if block["font_size"] == size:
                    return i + 1
        
        return 2  # Default to H2
    
    def _extract_quality_subsections(self, content: str, languages: List[str]) -> List[Dict]:
        """Extract meaningful subsections with quality control."""
        if len(content.strip()) < 100:
            return []
        
        # Split into meaningful chunks
        sentences = self._split_into_sentences(content, languages)
        
        if len(sentences) <= 3:
            return [{
                "content": content.strip()[:800],  # Limit length
                "summary": self._create_quality_summary(sentences),
                "references": self._extract_references(content),
                "key_terms": self._extract_key_terms(content, languages)
            }]
        
        # Create subsections
        subsections = []
        chunk_size = max(3, len(sentences) // 4)  # Aim for 4 subsections max
        
        for i in range(0, len(sentences), chunk_size):
            chunk = sentences[i:i + chunk_size]
            if chunk and len(' '.join(chunk)) > 50:  # Minimum content threshold
                subsection_text = ' '.join(chunk)
                subsections.append({
                    "content": subsection_text[:800],
                    "summary": self._create_quality_summary(chunk),
                    "references": self._extract_references(subsection_text),
                    "key_terms": self._extract_key_terms(subsection_text, languages)
                })
                
                if len(subsections) >= 3:  # Limit for performance
                    break
        
        return subsections
    
    def _split_into_sentences(self, text: str, languages: List[str]) -> List[str]:
        """Split text into sentences considering multiple languages."""
        # Enhanced sentence splitting for multiple languages
        sentence_endings = r'[.!?。！？।۔]'
        sentences = re.split(sentence_endings, text)
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Minimum sentence length
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _create_quality_summary(self, sentences: List[str]) -> str:
        """Create a high-quality summary from sentences."""
        if not sentences:
            return ""
        
        if len(sentences) == 1:
            return sentences[0][:200] + "..."
        
        # Select most informative sentences
        # First sentence (often introduces topic)
        summary_parts = [sentences[0]]
        
        # Longest sentence (often has most detail)
        if len(sentences) > 1:
            longest = max(sentences[1:], key=len)
            if longest != sentences[0]:
                summary_parts.append(longest)
        
        summary = ' '.join(summary_parts)
        return summary[:300] + "..." if len(summary) > 300 else summary
    
    def _extract_references(self, text: str) -> List[str]:
        """Extract references with better accuracy."""
        references = []
        
        ref_patterns = [
            r'(?i)figure\s+\d+(?:\.\d+)?',
            r'(?i)table\s+\d+(?:\.\d+)?',
            r'(?i)section\s+\d+(?:\.\d+)?',
            r'(?i)chapter\s+\d+',
            r'(?i)equation\s+\d+',
            r'\[\d+\]',  # Citation numbers
            r'\(\d+\)',  # Citation numbers in parentheses
        ]
        
        for pattern in ref_patterns:
            matches = re.findall(pattern, text)
            references.extend(matches[:5])  # Limit to prevent noise
        
        return list(set(references))[:8]  # Remove duplicates, limit total
    
    def _extract_key_terms(self, text: str, languages: List[str]) -> List[str]:
        """Extract key terms/concepts from text."""
        # Simple keyword extraction
        words = re.findall(r'\b[A-Za-z]{4,}\b', text.lower())
        
        # Remove common stopwords
        all_stopwords = set()
        for lang in languages:
            if lang in ['english', 'spanish', 'french', 'german', 'italian', 'portuguese']:
                # Basic stopwords for these languages
                common_stops = {'this', 'that', 'with', 'from', 'they', 'were', 'been', 'have', 'will', 'said'}
                all_stopwords.update(common_stops)
        
        filtered_words = [word for word in words if word not in all_stopwords]
        
        # Count frequency and return top terms
        word_freq = Counter(filtered_words)
        return [word for word, count in word_freq.most_common(10) if count > 1]
    
    def _is_quality_section(self, section: Dict) -> bool:
        """Check if section meets quality standards."""
        # Must have substantial content
        if len(section["content"].strip()) < 50:
            return False
        
        # Title should be meaningful
        title = section["title"].strip()
        if len(title) < 3 or title.lower() in ['document content', 'untitled']:
            return len(section["content"].strip()) > 200  # Allow if content is substantial
        
        # Should have some structure (subsections or key terms)
        has_structure = (
            len(section.get("subsections", [])) > 0 or
            len(section["content"].split('.')) > 3  # Multiple sentences
        )
        
        return has_structure
