# CampusGuide

A production-ready, hallucination-safe Retrieval-Augmented Generation (RAG) system for ICFAI University that answers questions strictly using official documents.

## Overview

CampusGuide is a Streamlit-based RAG application designed for high-risk academic governance domains where accuracy and traceability are critical. The system prevents hallucinations by grounding all responses in official ICFAI University documents and provides explicit source citations.

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

### Hallucination Prevention Strategy

- **Retrieval Gate**: Minimum similarity threshold and supporting chunks required
- **Context-Only Generation**: System prompts enforce no external knowledge
- **Grounding Validation**: Every answer sentence verified against retrieved context
- **Refusal Response**: Standardized message when information unavailable

### Source Traceability

- Document name and page number citations
- Relevant text excerpts
- Human-readable source information
- No technical jargon in user interface

## Features

- **Role-Based Access**: Different document access based on user role
- **Document Versioning**: Newer documents override older ones
- **Incremental Updates**: Add new PDFs without full retraining
- **Robust PDF Processing**: Handles tables, OCR fallback, page mapping
- **Session Management**: Chat history with configurable limits

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd CampusGuide
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

4. Add PDF documents to `data/raw/` directory

5. Run the application:
```bash
streamlit run app.py
```

## Configuration

All configuration is centralized in `config/config.py`:

- LLM settings (model, temperature)
- Embedding parameters
- Retrieval thresholds
- Document processing options
- UI settings

## Project Structure

```
CampusGuide/
├── app.py                 # Main Streamlit application
├── config/
│   └── config.py         # Centralized configuration
├── data/
│   ├── raw/              # Raw PDF documents
│   └── processed/        # Processed data and vector store
├── ingestion/
│   ├── document_loader.py # PDF loading with OCR
│   ├── text_cleaner.py   # Text preprocessing
│   └── text_splitter.py  # Document chunking
├── embeddings/
│   ├── embedder.py       # OpenAI embeddings
│   └── vector_store.py   # FAISS vector storage
├── retriever/
│   └── retriever.py      # Semantic retrieval
├── llm/
│   ├── prompt_templates.py # Prompt engineering
│   └── answer_generator.py # LLM integration
├── validation/
│   ├── safety_checker.py # Retrieval confidence
│   └── grounding_validator.py # Answer validation
├── ui/
│   ├── sidebar.py        # Role selection UI
│   └── chat_ui.py        # Chat interface
├── utils/
│   ├── logger.py         # Logging utilities
│   └── helpers.py        # Helper functions
├── evaluation/
│   └── test_queries.json # Golden Q&A dataset
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── .env                 # Environment variables
```

## Usage

1. **Document Ingestion**: Place PDF files in `data/raw/`
2. **Role Selection**: Choose your role from the sidebar
3. **Ask Questions**: Use natural language queries
4. **Review Sources**: Expand sources section for citations

## System Limitations

- Responses limited to provided documents only
- No external knowledge or assumptions
- Requires high-quality PDF text extraction
- Performance depends on document volume and complexity

## Security Considerations

- No hardcoded secrets (all via .env)
- Input validation and sanitization
- Role-based access control
- Audit logging for all queries

## Evaluation

Run evaluation against the golden dataset:

```python
from evaluation.test_queries.json import evaluate_system
results = evaluate_system()
```

## Contributing

1. Follow the established code structure
2. Add type hints and docstrings
3. Update tests for new features
4. Ensure hallucination prevention measures

## License

[Add appropriate license information]