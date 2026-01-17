# CampusGuide

A production-ready, hallucination-safe Retrieval-Augmented Generation (RAG) system for ICFAI University that answers questions strictly using official documents.

---

## Overview

CampusGuide is a Streamlit-based RAG application designed for high-risk academic governance domains where accuracy and traceability are critical.  
The system prevents hallucinations by grounding all responses in official ICFAI University documents and provides explicit source citations.

---

## Architecture

### RAG Pipeline

1. **Document Ingestion**
   - PDF loading with OCR fallback
   - Text cleaning (header/footer removal)
   - Chunking with configurable overlap
   - Embedding generation

2. **Retrieval**
   - Semantic search using FAISS vector store
   - Role-based filtering (student, faculty, coordinator, parent)
   - Similarity threshold gating

3. **Generation**
   - Context-only LLM prompting
   - Low temperature for factual responses
   - OpenAI GPT models

4. **Validation**
   - Retrieval confidence gating
   - Post-generation grounding verification
   - Sentence-level validation

---

## Hallucination Prevention Strategy

- Retrieval Gate: Minimum similarity threshold and supporting chunks required
- Context-Only Generation: System prompts enforce no external knowledge
- Grounding Validation: Every answer sentence verified against retrieved context
- Refusal Response: Standardized message when information is unavailable

---

## Source Traceability

- Document name and page number citations
- Relevant text excerpts
- Human-readable source information
- No technical jargon in user interface

---

## Features

- Role-Based Access: Different document access based on user role
- Document Versioning: Newer documents override older ones
- Incremental Updates: Add new PDFs without full retraining
- Robust PDF Processing: Handles tables, OCR fallback, page mapping
- Session Management: Chat history with configurable limits

---

## Installation

1. Clone the repository:
   git clone https://gitlab.com/campusguide/campusguide-website.git  
   cd CampusGuide

2. Install dependencies:
   pip install -r requirements.txt

3. Set up environment variables:
   cp .env.example .env  
   Edit `.env` and add your OpenAI API key

4. Add official documents:
   Place PDF files inside `data/raw/`

5. Run the application:
   streamlit run app.py

---

## Configuration

All configuration is centralized in `config/config.py`, including:
- LLM model and temperature
- Embedding parameters
- Retrieval thresholds
- Document processing options
- UI settings

---

## Project Structure

CampusGuide/
├── app.py  
├── config/  
│   └── config.py  
├── data/  
│   ├── raw/  
│   └── processed/  
├── ingestion/  
│   ├── document_loader.py  
│   ├── text_cleaner.py  
│   └── text_splitter.py  
├── embeddings/  
│   ├── embedder.py  
│   └── vector_store.py  
├── retriever/  
│   └── retriever.py  
├── llm/  
│   ├── prompt_templates.py  
│   └── answer_generator.py  
├── validation/  
│   ├── safety_checker.py  
│   └── grounding_validator.py  
├── ui/  
│   ├── sidebar.py  
│   └── chat_ui.py  
├── utils/  
│   ├── logger.py  
│   └── helpers.py  
├── evaluation/  
│   └── test_queries.json  
├── requirements.txt  
├── README.md  
└── .env  

---

## Usage

1. Place PDF files in `data/raw/`
2. Select user role (student / faculty / coordinator / parent)
3. Ask questions in natural language
4. Review cited sources for verification

---

## System Limitations

- Answers strictly limited to provided documents
- No external or assumed knowledge
- Requires high-quality PDF extraction
- Performance depends on document volume

---

## Security Considerations

- No hardcoded secrets
- Environment-based configuration
- Role-based access control
- Audit logging for all queries

---

## Evaluation

Run evaluation using the golden dataset:
from evaluation.test_queries import evaluate_system  
results = evaluate_system()

---

## Contributing

1. Follow existing folder structure
2. Add type hints and docstrings
3. Update evaluation data for new features
4. Maintain hallucination prevention guarantees

---

## License

To be added.
