import json
from datetime import datetime
from typing import List, Dict

class OutputFormatter:
    def format_output(self, document_metadata: List[Dict], persona: str, 
                     job_to_be_done: str, sections: List[Dict]) -> Dict:
        """Format output according to required JSON schema."""
        
        output = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "persona": persona,
                "job_to_be_done": job_to_be_done,
                "processed_documents": document_metadata,
                "total_sections_extracted": len(sections),
                "processing_version": "1.0"
            },
            "extracted_sections": []
        }
        
        for section in sections:
            formatted_section = {
                "section_title": section["title"],
                "document_name": section.get("document_name", "Unknown"),
                "document_title": section.get("document_title", "Unknown"),
                "page_number": section["page"],
                "heading_level": section["level"],
                "importance_rank": section.get("importance_rank", 0),
                "relevance_score": round(section.get("relevance_score", 0.0), 4),
                "content_preview": section["content"][:200] + "..." if len(section["content"]) > 200 else section["content"],
                "subsections": []
            }
            
            # Format subsections
            for subsection in section.get("subsections", []):
                formatted_subsection = {
                    "summary": subsection.get("summary", ""),
                    "key_content": subsection.get("content", ""),
                    "references": subsection.get("references", []),
                    "relevance_score": round(subsection.get("relevance_score", 0.0), 4)
                }
                formatted_section["subsections"].append(formatted_subsection)
            
            output["extracted_sections"].append(formatted_section)
        
        return output
