import re
import numpy as np
from typing import List, Dict
from collections import Counter
from sentence_transformers import SentenceTransformer
import math

class PersonaMatcher:
    def __init__(self):
        # Load lightweight sentence transformer
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except:
            self.model = None
            print("Warning: Using keyword-based matching only")
    
    def match_sections(self, sections: List[Dict], persona: str, job_to_be_done: str) -> List[Dict]:
        """Match sections to persona and job requirements."""
        if not sections:
            return []
        
        # Extract dynamic keywords
        persona_keywords = self._extract_dynamic_keywords(persona, job_to_be_done)
        
        scored_sections = []
        
        for section in sections:
            # Calculate relevance score
            if self.model:
                semantic_score = self._calculate_semantic_similarity(section, persona, job_to_be_done)
                keyword_score = self._calculate_keyword_relevance(section, persona_keywords)
                relevance_score = (0.7 * semantic_score) + (0.3 * keyword_score)
            else:
                relevance_score = self._calculate_keyword_relevance(section, persona_keywords)
            
            section_copy = section.copy()
            section_copy["relevance_score"] = relevance_score
            
            # Process and score subsections
            scored_subsections = []
            for subsection in section.get("subsections", []):
                subsection_score = self._calculate_subsection_relevance(
                    subsection, persona_keywords
                )
                subsection_copy = subsection.copy()
                subsection_copy["relevance_score"] = subsection_score
                scored_subsections.append(subsection_copy)
            
            # Keep top 2 subsections per section
            section_copy["subsections"] = sorted(
                scored_subsections, 
                key=lambda x: x["relevance_score"], 
                reverse=True
            )[:2]
            
            scored_sections.append(section_copy)
        
        # Sort by relevance and assign ranks
        scored_sections.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Keep top 5 sections and assign importance ranks
        top_sections = scored_sections[:5]
        for i, section in enumerate(top_sections):
            section["importance_rank"] = i + 1
        
        return top_sections
    
    def _extract_dynamic_keywords(self, persona: str, job_to_be_done: str) -> List[str]:
        """Extract keywords dynamically from persona and job description."""
        combined_text = f"{persona} {job_to_be_done}".lower()
        
        # Extract meaningful terms
        words = re.findall(r'\b[a-zA-Z]{3,}\b', combined_text)
        
        # Remove common stopwords
        stopwords = {
            'the', 'and', 'for', 'with', 'this', 'that', 'who', 'what', 'where', 
            'when', 'why', 'how', 'are', 'was', 'were', 'been', 'have', 'has',
            'will', 'would', 'could', 'should', 'can', 'may', 'must', 'need'
        }
        
        keywords = [word for word in words if word not in stopwords and len(word) > 2]
        
        return list(set(keywords))
    
    def _calculate_semantic_similarity(self, section: Dict, persona: str, job_to_be_done: str) -> float:
        """Calculate semantic similarity using sentence transformer."""
        if not self.model:
            return 0.0
        
        try:
            query_text = f"{persona} {job_to_be_done}"
            query_embedding = self.model.encode(query_text)
            
            section_text = f"{section['title']} {section['content'][:500]}"
            section_embedding = self.model.encode(section_text)
            
            similarity = np.dot(query_embedding, section_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(section_embedding)
            )
            
            return max(0.0, similarity)
        except:
            return 0.0
    
    def _calculate_keyword_relevance(self, section: Dict, keywords: List[str]) -> float:
        """Calculate relevance based on keyword matching."""
        text = (section["title"] + " " + section["content"]).lower()
        text_words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        word_freq = Counter(text_words)
        
        score = 0.0
        
        for keyword in keywords:
            # Exact match bonus
            score += word_freq.get(keyword, 0) * 2.0
            
            # Partial match bonus
            for word in text_words:
                if keyword in word or word in keyword:
                    score += 0.5
                    
            # Title match bonus
            if keyword in section["title"].lower():
                score += 3.0
        
        # Normalize by content length
        content_length = len(text_words)
        if content_length > 0:
            score = score / math.log(content_length + 1)
        
        return score
    
    def _calculate_subsection_relevance(self, subsection: Dict, keywords: List[str]) -> float:
        """Calculate relevance score for subsections."""
        text = subsection["content"].lower()
        text_words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        word_freq = Counter(text_words)
        
        score = 0.0
        
        for keyword in keywords:
            score += word_freq.get(keyword, 0) * 1.5
            
            for word in text_words:
                if keyword in word or word in keyword:
                    score += 0.3
        
        content_length = len(text_words)
        if content_length > 0:
            score = score / math.log(content_length + 1)
        
        return score
