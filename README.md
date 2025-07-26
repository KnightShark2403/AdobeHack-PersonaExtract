# PersonaExtract: Intelligent Persona-Driven PDF Insights Engine

## Overview

PersonaExtract is a streamlined, high-performance system that extracts personalized sections and insights from multiple PDF documents based on user personas and specific job-to-be-done requirements. Built specifically for the Adobe India Hackathon Round 1B challenge.

## Key Features

- **🚀 Ultra-Fast Processing**: Completes in 10-15 seconds for 5 documents (well under Adobe's 60-second requirement)
- **🎯 Dynamic Persona Matching**: No hardcoded keywords - fully adaptive to any domain and persona
- **🌐 Multilingual Support**: Handles Japanese, English, and other languages with proper Unicode processing
- **⚡ Lightweight Architecture**: CPU-only processing with minimal dependencies
- **📊 Structured Output**: Adobe-compliant JSON format with metadata, sections, and subsection analysis
- **🔄 Generalizable Design**: Works across all domains without domain-specific assumptions

## Technical Specifications

- **Processing Time**: 10-15 seconds for 5 documents
- **Memory Usage**: <2GB RAM
- **Model Size**: No ML models required (streamlined keyword approach)
- **Platform**: CPU-only, no GPU dependencies
- **Docker Support**: Complete containerization for easy deployment
- **Input**: 3-10 PDF documents + persona configuration
- **Output**: Structured JSON with extracted sections and analysis

## Architecture

### Core Components

1. **PDF Parser** (`pdf_parser.py`): Fast text extraction with Unicode support
2. **Section Extractor** (`section_extractor.py`): Dynamic content segmentation
3. **Persona Matcher** (`persona_matcher.py`): Keyword-based relevance scoring
4. **Output Formatter** (`output_formatter.py`): Adobe-compliant JSON generation

### Processing Pipeline

