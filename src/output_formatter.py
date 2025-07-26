import json
from datetime import datetime
from typing import List, Dict

class OutputFormatter:
    def format_output(self, input_documents: List[str], persona: str, 
                     job_to_be_done: str, sections: List[Dict]) -> Dict:
        """Debug version to see what sections are being formatted."""
        
        print(f"🔍 Output formatter received {len(sections)} sections")
        for i, section in enumerate(sections[:3]):
            print(f"🔍 Section {i+1}: '{section.get('title', 'NO TITLE')}'")
        
        extracted_sections = []
        subsection_analysis = []
        
        # Force create output even if sections are empty
        if not sections:
            print("🔍 No sections provided - creating placeholder")
            extracted_sections = [{
                "document": "Unknown",
                "section_title": "No relevant sections found",
                "importance_rank": 1,
                "page_number": 1
            }]
        else:
            for section in sections:
                extracted_sections.append({
                    "document": section.get("document_name", "Unknown"),
                    "section_title": section.get("title", "Untitled"),
                    "importance_rank": section.get("importance_rank", 0),
                    "page_number": section.get("page", 1)
                })
                
                # Add subsections
                for subsection in section.get("subsections", []):
                    subsection_analysis.append({
                        "document": section.get("document_name", "Unknown"),
                        "refined_text": subsection.get("content", ""),
                        "page_number": section.get("page", 1),
                        "references": subsection.get("references", []),
                        "summary": subsection.get("summary", "")
                    })
        
        output = {
            "metadata": {
                "input_documents": input_documents,
                "persona": persona,
                "job_to_be_done": job_to_be_done,
                "processing_timestamp": datetime.now().isoformat(),
                "total_sections_extracted": len(extracted_sections),
                "total_subsections_analyzed": len(subsection_analysis)
            },
            "extracted_sections": extracted_sections,
            "subsection_analysis": subsection_analysis
        }
        
        print(f"🔍 Final output has {len(output['extracted_sections'])} extracted sections")
        return output
