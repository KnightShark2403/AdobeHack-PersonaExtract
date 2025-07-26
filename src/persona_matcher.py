from typing import List, Dict
from collections import Counter
import re

class PersonaMatcher:
    def __init__(self):
        """Lightweight keyword-based matcher."""
        print("Using fast keyword-based persona matching...")
    
    def match_sections(self, sections: List[Dict], persona: str, job_to_be_done: str) -> List[Dict]:
        """Match sections using dynamic keyword extraction with generous scoring."""
        if not sections:
            return []
        
        # Extract keywords from persona and job
        query_text = f"{persona} {job_to_be_done}".lower()
        query_words = re.findall(r'\b[a-zA-Z]{3,}\b', query_text)
        
        # Remove only the most common stopwords
        basic_stopwords = {'the', 'and', 'for', 'with', 'this', 'that'}
        query_keywords = [word for word in query_words if word not in basic_stopwords]
        
        print(f"Matching against keywords: {query_keywords[:5]}")
        
        scored_sections = []
        
        for section in sections:
            # Create searchable text
            section_text = f"{section['title']} {section['content']}".lower()
            section_words = re.findall(r'\b[a-zA-Z]{3,}\b', section_text)
            
            # Calculate score with multiple matching strategies
            score = 0
            
            # 1. Exact keyword matches
            for keyword in query_keywords:
                if keyword in section_words:
                    score += 2
            
            # 2. Partial word matches
            for keyword in query_keywords:
                for word in section_words:
                    if keyword in word or word in keyword:
                        score += 0.5
            
            # 3. Title bonus
            for keyword in query_keywords:
                if keyword in section['title'].lower():
                    score += 3
            
            # 4. Content density bonus (more content = potentially more relevant)
            if len(section['content']) > 300:
                score += 1
            
            # 5. Ensure every section gets at least a small base score
            score += 0.1
            
            section_copy = section.copy()
            section_copy["relevance_score"] = score
            scored_sections.append(section_copy)
        
        # Sort by relevance score
        scored_sections.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Take top sections but ensure we have at least 3
        top_sections = scored_sections[:max(5, min(len(scored_sections), 3))]
        
        # Assign importance ranks
        for i, section in enumerate(top_sections):
            section["importance_rank"] = i + 1
        
        print(f"Persona matching completed in 0.00 seconds")
        print(f"Found {len(top_sections)} relevant sections")
        
        return top_sections
