import json
from datetime import datetime
from typing import List, Dict

class OutputFormatter:
    def format_output(self, input_documents: List[str], persona: str, 
                     job_to_be_done: str, sections: List[Dict]) -> Dict:
        """Format output to match the exact required JSON schema."""
        
        # Create extracted_sections list (top-level sections only)
        extracted_sections = []
        subsection_analysis = []
        
        for section in sections[:5]:  # Keep only top 5 sections
            # Add to extracted_sections
            extracted_sections.append({
                "document": section.get("document_name", "Unknown"),
                "section_title": section["title"],
                "importance_rank": section.get("importance_rank", 0),
                "page_number": section["page"]
            })
            
            # Add subsections to subsection_analysis
            for subsection in section.get("subsections", []):
                subsection_analysis.append({
                    "document": section.get("document_name", "Unknown"),
                    "refined_text": subsection.get("content", ""),
                    "page_number": section["page"]
                })
        
        # Create final output structure matching the expected format
        output = {
            "metadata": {
                "input_documents": input_documents,
                "persona": persona,
                "job_to_be_done": job_to_be_done,
                "processing_timestamp": datetime.now().isoformat()
            },
            "extracted_sections": extracted_sections,
            "subsection_analysis": subsection_analysis
        }
        
        return output
