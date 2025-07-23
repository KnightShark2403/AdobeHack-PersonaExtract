import os
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from pdf_parser import PDFParser
from section_extractor import SectionExtractor
from persona_matcher import PersonaMatcher
from output_formatter import OutputFormatter

def process_single_pdf(pdf_path, config_data):
    """Process a single PDF file with better error handling."""
    try:
        pdf_parser = PDFParser()
        section_extractor = SectionExtractor()
        
        print(f"Processing {pdf_path.name}...")
        
        # Parse PDF with better error handling
        document_data = pdf_parser.parse(str(pdf_path))
        
        if not document_data or not document_data.get("pages"):
            print(f"Warning: No content extracted from {pdf_path.name}")
            return None
        
        # Extract sections
        sections = section_extractor.extract_sections(document_data)
        
        # Add document metadata
        for section in sections:
            section["document_name"] = pdf_path.name
            section["document_title"] = document_data["title"]
        
        return {
            "pdf_name": pdf_path.name,
            "sections": sections,
            "success": True
        }
        
    except Exception as e:
        print(f"Error processing {pdf_path.name}: {str(e)}")
        return None

def main():
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Ensure directories exist
    output_dir.mkdir(exist_ok=True)
    
    # Load configuration
    config_file = input_dir / "config.json"
    config = {}
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    # Extract persona and job
    persona = config.get("persona", "General Researcher")
    job_to_be_done = config.get("job_to_be_done", "Extract relevant information")
    
    # Get ALL PDF files with proper filtering
    pdf_files = []
    for file_path in input_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() == '.pdf':
            # Check if file is readable
            try:
                if file_path.stat().st_size > 0:  # Not empty
                    pdf_files.append(file_path)
                else:
                    print(f"Skipping empty file: {file_path.name}")
            except Exception as e:
                print(f"Cannot access file {file_path.name}: {e}")
    
    print(f"Found {len(pdf_files)} PDF files to process:")
    for pdf in pdf_files:
        print(f"  - {pdf.name} ({pdf.stat().st_size} bytes)")
    
    if not pdf_files:
        print("ERROR: No valid PDF files found!")
        return
    
    all_sections = []
    processed_documents = []
    start_time = time.time()
    
    # Process PDFs with ThreadPoolExecutor (faster than ProcessPoolExecutor for I/O)
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all jobs
        future_to_pdf = {
            executor.submit(process_single_pdf, pdf_path, config): pdf_path 
            for pdf_path in pdf_files
        }
        
        # Collect results
        for future in as_completed(future_to_pdf):
            pdf_path = future_to_pdf[future]
            try:
                result = future.result(timeout=30)  # 30 second timeout per PDF
                if result and result["success"]:
                    all_sections.extend(result["sections"])
                    processed_documents.append(result["pdf_name"])
                    print(f"✓ Successfully processed: {result['pdf_name']}")
                else:
                    print(f"✗ Failed to process: {pdf_path.name}")
            except Exception as e:
                print(f"✗ Exception processing {pdf_path.name}: {str(e)}")
    
    print(f"Successfully processed {len(processed_documents)} out of {len(pdf_files)} PDFs")
    
    if not all_sections:
        print("ERROR: No sections extracted from any PDF!")
        return
    
    # Continue with persona matching...
    persona_matcher = PersonaMatcher()
    relevant_sections = persona_matcher.match_sections(all_sections, persona, job_to_be_done)
    
    # Format and save output
    output_formatter = OutputFormatter()
    output_data = output_formatter.format_output(processed_documents, persona, job_to_be_done, relevant_sections)
    
    output_file = output_dir / "extracted_sections.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    total_time = time.time() - start_time
    print(f"Total processing time: {total_time:.2f} seconds")
    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    main()
