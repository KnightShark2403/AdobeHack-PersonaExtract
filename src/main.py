import os
import json
import time
from pathlib import Path
from pdf_parser import PDFParser
from section_extractor import SectionExtractor
from persona_matcher import PersonaMatcher
from output_formatter import OutputFormatter

def main():
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    
    # Initialize components
    pdf_parser = PDFParser()
    section_extractor = SectionExtractor()
    persona_matcher = PersonaMatcher()
    output_formatter = OutputFormatter()
    
    # Load configuration from config.json
    config_file = input_dir / "config.json"
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Extract persona and job info from config structure
        if "challenge_info" in config:
            persona_info = config.get("persona", {})
            job_info = config.get("job_to_be_done", {})
            persona = persona_info.get("role", "General Researcher")
            job_to_be_done = job_info.get("task", "Extract relevant information")
            documents_list = config.get("documents", [])
        else:
            # Fallback for simple config format
            persona = config.get("persona", "General Researcher")
            job_to_be_done = config.get("job_to_be_done", "Extract relevant information")
            documents_list = []
    else:
        persona = "General Researcher"
        job_to_be_done = "Extract relevant information"
        documents_list = []
    
    # Process all PDFs
    pdf_files = list(input_dir.glob("*.pdf"))
    all_sections = []
    processed_documents = []
    
    start_time = time.time()
    
    for pdf_file in pdf_files:
        try:
            print(f"Processing {pdf_file.name}...")
            
            # Parse PDF
            document_data = pdf_parser.parse(pdf_file)
            
            # Extract sections
            sections = section_extractor.extract_sections(document_data)
            
            # Add document metadata to each section
            for section in sections:
                section["document_name"] = pdf_file.name
                section["document_title"] = document_data["title"]
            
            all_sections.extend(sections)
            processed_documents.append(pdf_file.name)
            
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {str(e)}")
    
    # Match sections to persona
    relevant_sections = persona_matcher.match_sections(
        all_sections, persona, job_to_be_done
    )
    
    # Format output according to expected schema
    output_data = output_formatter.format_output(
        processed_documents, persona, job_to_be_done, relevant_sections
    )
    
    # Save output
    output_file = output_dir / "extracted_sections.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    processing_time = time.time() - start_time
    print(f"Processed {len(pdf_files)} documents in {processing_time:.2f} seconds")
    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    main()
