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
    output_dir.mkdir(exist_ok=True)
    
    # Load configuration
    config_file = input_dir / "config.json"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {}
    
    persona = config.get("persona", "General Researcher")
    job_to_be_done = config.get("job_to_be_done", "Extract relevant information")
    
    # Get all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))[:5]  # Limit to 5 PDFs
    print(f"Found {len(pdf_files)} PDF files to process")
    
    if not pdf_files:
        print("No PDF files found!")
        return
    
    # Process all PDFs
    all_sections = []
    processed_docs = []
    start_time = time.time()
    
    for pdf_file in pdf_files:
        print(f"Processing {pdf_file.name}...")
        
        # Parse PDF
        parser = PDFParser()
        document_data = parser.parse(pdf_file)
        
        if not document_data["pages"]:
            print(f"No content extracted from {pdf_file.name}")
            continue
        
        # Extract sections
        extractor = SectionExtractor()
        sections = extractor.extract_sections(document_data)
        
        # Add document metadata
        for section in sections:
            section["document_name"] = pdf_file.name
            section["document_title"] = document_data["title"]
        
        all_sections.extend(sections)
        processed_docs.append(pdf_file.name)
        print(f"✓ Extracted {len(sections)} sections from {pdf_file.name}")
    
    print(f"Total sections extracted across all PDFs: {len(all_sections)}")
    
    if not all_sections:
        print("No sections extracted from any PDF!")
        return
    
    # Match sections to persona
    print("Matching sections to persona...")
    matcher = PersonaMatcher()
    relevant_sections = matcher.match_sections(all_sections, persona, job_to_be_done)
    
    print(f"Found {len(relevant_sections)} relevant sections")
    
    # Format output
    formatter = OutputFormatter()
    output_data = formatter.format_output(processed_docs, persona, job_to_be_done, relevant_sections)
    
    # Save output with error handling
    try:
        output_file = output_dir / "extracted_sections.json"
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write with explicit encoding and error handling
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        # Verify file was written
        if output_file.exists() and output_file.stat().st_size > 0:
            print(f"✅ Output successfully saved to {output_file}")
            print(f"📄 File size: {output_file.stat().st_size} bytes")
        else:
            print(f"❌ Output file creation failed!")
            
    except Exception as e:
        print(f"❌ Error saving output: {str(e)}")
        
        # Fallback - save to current directory
        try:
            with open("extracted_sections.json", 'w') as f:
                json.dump(output_data, f, indent=2)
            print("✅ Saved to current directory as fallback")
        except Exception as e2:
            print(f"❌ Fallback save also failed: {str(e2)}")
    
    total_time = time.time() - start_time
    print(f"Processing completed in {total_time:.2f} seconds")

if __name__ == "__main__":
    main()
