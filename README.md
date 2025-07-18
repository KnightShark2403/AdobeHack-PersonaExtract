# AdobeHack-PersonaExtract
# PersonaExtract: Intelligent Persona-Driven PDF Insights Engine

## Overview

PersonaExtract is an intelligent system that extracts personalized sections and insights from multiple PDF documents based on user personas and specific job-to-be-done requirements.

## Features

- **Dynamic Persona Matching**: No hardcoded keywords - adapts to any persona and job description
- **Semantic Understanding**: Uses lightweight sentence transformers for contextual relevance
- **Multi-Document Processing**: Handles 3-10 related PDFs simultaneously
- **Structured Output**: Generates JSON with sections, subsections, and relevance rankings
- **Performance Optimized**: Processes 3-5 documents in under 60 seconds

## Technical Specifications

- **CPU Only**: No GPU requirements
- **Memory Efficient**: Models under 1GB total size
- **Offline Processing**: No internet connectivity required
- **Multilingual Support**: Handles various languages and document formats

## Usage

1. Place PDF files in the `input/` directory
2. Create a `config.json` file with persona and job definition:

