# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered portfolio website built with FastAPI that features a RAG (Retrieval Augmented Generation) system. Users can upload resumes/documents and visitors can ask natural language questions about the portfolio owner's experience, skills, and projects.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment (Windows)
py -m venv venv
venv\Scripts\activate

# Create and activate virtual environment (macOS/Linux)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Start development server with auto-reload
py -m uvicorn app.main:app --reload

# Start production server
py -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The application runs at `http://localhost:8000`

### Database and Storage
- ChromaDB vector store is created automatically at `./chroma_db` on application startup
- **Documents are loaded from `./data/documents/` on startup** - Place your PDF, DOCX, or TXT files there
- To reset the RAG system, delete the `./chroma_db` directory and restart the server

## Architecture

### Core Components

**FastAPI Application ([app/main.py](app/main.py))**
- Main entry point defining all API routes
- Contains `PORTFOLIO_DATA` object that stores static portfolio information (name, title, bio, tech stack, experiences, projects, education)
- Instantiates services and templates
- All endpoints are defined here (no separate API router modules despite the empty `app/api/` directory)

**RAG Service ([app/services/rag_service.py](app/services/rag_service.py))**
- Singleton instance (`rag_service`) that handles document retrieval and question answering
- Uses HuggingFace embeddings (`sentence-transformers/all-MiniLM-L6-v2`) for vector representation
- ChromaDB as vector store with persistence
- Text chunking with 1000 character chunks and 200 character overlap
- **Important**: Currently returns basic context snippets without LLM-based answer generation

**Document Parser ([app/services/document_parser.py](app/services/document_parser.py))**
- Supports PDF (via pdfplumber with PyPDF2 fallback), DOCX, and TXT formats
- Static methods for each format, unified interface via `parse_document()`

**Configuration ([app/core/config.py](app/core/config.py))**
- Pydantic Settings for environment-based configuration
- Loads from `.env` file if present
- API keys (OpenAI, Anthropic) are optional and not currently used in code

**Data Models ([app/models/portfolio.py](app/models/portfolio.py))**
- Pydantic models defining the portfolio data structure
- Key models: `PortfolioData`, `TechStack`, `Experience`, `Project`, `Education`
- Request/Response models: `QuestionRequest`, `QuestionResponse`

### Data Flow

1. **Document Loading (Startup)**: Server starts → RAG service scans `./data/documents/` → DocumentParser extracts text → Chunks text → ChromaDB stores embeddings
2. **Question Answering**: Question → RAG service searches ChromaDB → Returns top-k relevant chunks → Basic answer construction (no LLM currently)
3. **Portfolio Display**: Jinja2 renders `index.html` template with `PORTFOLIO_DATA` object

### Key Design Decisions

- **No API Router Separation**: Despite having an `app/api/` directory, all routes are defined directly in `main.py`
- **No Upload Endpoint**: Documents are loaded from local filesystem only for security. No public upload functionality.
- **Embedding Model**: Uses local HuggingFace model to avoid API dependencies
- **Answer Generation**: Currently returns raw context snippets. To upgrade to LLM-based answers, modify `answer_question()` in `rag_service.py` to use OpenAI or Anthropic APIs
- **Vector Store Persistence**: ChromaDB persists to disk, so documents survive server restarts
- **Document Loading**: On startup, the RAG service automatically scans `./data/documents/` and indexes all PDF, DOCX, and TXT files

## Customization Guide

### Adding Your Documents

**Place your resume, CV, or portfolio documents in `./data/documents/`**

Supported formats:
- PDF (.pdf)
- Microsoft Word (.docx, .doc)
- Plain text (.txt)

The application will automatically:
1. Scan this directory on startup
2. Parse all supported documents
3. Index them in ChromaDB for Q&A

To refresh the index after adding new documents, restart the server.

### Updating Portfolio Information

Edit the `PORTFOLIO_DATA` object in [app/main.py](app/main.py) (lines 40-55). This is the primary source of static portfolio data.

Example:
```python
PORTFOLIO_DATA = PortfolioData(
    name="Your Name",
    title="Your Title",
    bio="Your bio...",
    email="your.email@example.com",
    github="https://github.com/username",
    linkedin="https://linkedin.com/in/username",
    tech_stack=[...],
    experiences=[...],
    projects=[...],
    education=[...]
)
```

### Upgrading to LLM-Based Answers

To use OpenAI or Anthropic for better answer generation:

1. Add API key to `.env` file:
   ```
   OPENAI_API_KEY=sk-...
   ```

2. Modify `answer_question()` in [app/services/rag_service.py](app/services/rag_service.py) to call the LLM API with the retrieved context as prompt context

3. The configuration already loads the API keys via [app/core/config.py](app/core/config.py)

## API Endpoints

- `GET /` - Home page (Jinja2 template)
- `GET /api/portfolio` - Get portfolio data (JSON)
- `POST /api/ask` - Ask question via RAG
- `GET /api/search?query=...` - Search documents
- `DELETE /api/clear-documents` - Clear vector store
- `GET /health` - Health check

**Note:** The upload endpoint has been removed for security. Documents are loaded from `./data/documents/` on startup only.

## File Structure Notes

- `app/api/` exists but is currently unused (all routes in `main.py`)
- `app/static/` contains CSS, JS, and images for frontend
- `app/templates/` contains Jinja2 HTML templates
- `data/documents/` **← Place your PDF, DOCX, or TXT files here**
- `chroma_db/` is auto-created for vector store persistence
