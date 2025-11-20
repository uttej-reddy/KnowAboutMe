# Portfolio Project - Session Summary

**Date**: 2025-11-16
**Project**: AI-Powered Portfolio with RAG (Retrieval Augmented Generation)
**Location**: D:\Projects\Portfolio

---

## Session Overview

This session focused on setting up and configuring an AI-powered portfolio website with document-based Q&A capabilities, removing insecure upload features, and enhancing answer generation with web search.

---

## Key Accomplishments

### 1. **Initial Setup & Analysis**
- Created comprehensive CLAUDE.md documentation for the project
- Analyzed codebase structure and architecture
- Identified Python version compatibility issues (3.7.5 → 3.11.9 required)

### 2. **Python Environment Upgrade**
- **Problem**: Python 3.7.5 was incompatible with modern FastAPI, Pydantic v2, and LangChain
- **Solution**: Upgraded to Python 3.11.9
- **Steps**:
  - Downloaded Python 3.11.9 installer
  - Removed old virtual environment
  - Created new venv with Python 3.11
  - Updated all dependencies

### 3. **Dependency Resolution**
Fixed multiple dependency and import errors:

#### Error 1: Missing langchain-community
```bash
pip install langchain-community
```

#### Error 2: Pydantic v2 Migration
**File**: `app/core/config.py`
```python
# Changed from:
from pydantic import BaseSettings
# To:
from pydantic_settings import BaseSettings
```

#### Error 3: LangChain Import Paths
**File**: `app/services/rag_service.py`
```python
# Updated imports for LangChain 1.0:
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
```

#### Error 4: Missing Path Import
Added `from pathlib import Path` to `rag_service.py`

### 4. **Security Enhancement - Removed Upload Feature**

**Why**: Public file upload is a security risk - anyone could upload files to the server.

**Changes Made**:

#### Frontend (HTML)
**File**: `app/templates/index.html`
- Removed upload UI section (lines 128-134)
- Updated messaging to remove upload references
- Changed from "Upload your resume first" to "Ask questions about my experience"

#### Frontend (JavaScript)
**File**: `app/static/js/main.js`
- Removed `uploadResume()` function
- Removed `showStatus()` function
- Kept only question-asking functionality

#### Backend
**File**: `app/main.py`
- Removed `/api/upload-resume` endpoint entirely
- Removed File and UploadFile imports

### 5. **Document Loading from Local Directory**

**Configuration**: `app/core/config.py`
```python
DOCUMENTS_DIR: str = "./data/documents"
```

**Implementation**: `app/services/rag_service.py`
- Created `_load_local_documents()` method
- Automatically scans `./data/documents/` on server startup
- Supports: PDF, DOCX, DOC, TXT files
- Parses and indexes all documents into ChromaDB
- Creates directory if it doesn't exist

**Your Documents**:
- Located in: `D:\Projects\Portfolio\data\documents\`
- Currently loaded:
  - UTTEJ_THOOMPALLY.pdf
  - UTTEJ_THOOMPALLY - Architect.docx
- Total: 12 chunks indexed

### 6. **Enhanced Answer Generation with Web Search**

**Problem**: Answers were only based on resume documents, lacking broader context.

**Solution**: Integrated web search to complement resume data.

**Implementation**: `app/services/rag_service.py`

#### New Methods Added:

1. **`_extract_keywords(text, top_n=5)`**
   - Extracts important keywords from resume context
   - Filters out common words (the, and, is, etc.)
   - Returns top N unique keywords

2. **`_search_web(query)`**
   - Searches DuckDuckGo (no API key required)
   - Extracts text snippets from results
   - Returns up to 500 characters of relevant content

3. **Updated `answer_question()`**
   ```python
   Flow:
   1. Search resume documents in ChromaDB
   2. Extract keywords from found context
   3. Combine keywords + question for web search
   4. Merge resume context + web results
   5. Return comprehensive answer
   ```

**Dependencies Added**: `requests` library

---

## Current Architecture

### Tech Stack
- **Backend**: FastAPI (Python 3.11.9)
- **Vector Database**: ChromaDB with persistence
- **Embeddings**: HuggingFace (sentence-transformers/all-MiniLM-L6-v2)
- **Text Processing**: LangChain (v1.0.7)
- **Document Parsing**: PyPDF2, python-docx, pdfplumber
- **Web Search**: DuckDuckGo HTML (via requests)
- **Frontend**: Jinja2 templates, vanilla JavaScript

### Data Flow

```
User Question
    ↓
[Frontend] main.js:askQuestion()
    ↓ POST /api/ask
[Backend] main.py:ask_question()
    ↓
[RAG Service] rag_service.py:answer_question()
    ↓
┌─────────────────────────────────────────┐
│ 1. Search Resume (ChromaDB)             │
│    → Vector similarity search           │
│    → Returns top 2 relevant chunks      │
├─────────────────────────────────────────┤
│ 2. Extract Keywords                     │
│    → Filter common words                │
│    → Get top 3 keywords                 │
├─────────────────────────────────────────┤
│ 3. Web Search (DuckDuckGo)              │
│    → Query: keywords + question         │
│    → Extract search snippets            │
├─────────────────────────────────────────┤
│ 4. Combine Results                      │
│    → Resume context (300 chars)         │
│    → Web results (500 chars)            │
└─────────────────────────────────────────┘
    ↓
Return: {answer, sources}
    ↓
[Frontend] Display formatted response
```

### File Structure
```
D:\Projects\Portfolio\
├── app/
│   ├── main.py                 # FastAPI routes
│   ├── core/
│   │   └── config.py          # Settings (Pydantic)
│   ├── models/
│   │   └── portfolio.py       # Data models
│   ├── services/
│   │   ├── rag_service.py     # RAG + Web Search
│   │   └── document_parser.py # PDF/DOCX/TXT parsing
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   │       └── main.js        # Frontend logic
│   └── templates/
│       └── index.html         # Main page
├── data/
│   └── documents/             # ← Place your documents here
│       ├── UTTEJ_THOOMPALLY.pdf
│       └── UTTEJ_THOOMPALLY - Architect.docx
├── chroma_db/                 # Vector store (auto-created)
├── venv/                      # Python 3.11.9 virtual env
├── requirements.txt
├── CLAUDE.md                  # Development guide
└── SESSION_SUMMARY.md         # This file
```

---

## Important Notes

### Current Limitations

1. **No LLM Integration** ⚠️
   - Currently returns **raw text chunks**, not intelligent answers
   - Just concatenates resume text + web snippets
   - No natural language generation
   - To add LLM: Integrate OpenAI or Anthropic API

2. **Web Search Quality**
   - Basic HTML parsing of DuckDuckGo results
   - May return incomplete or poorly formatted snippets
   - No ranking or relevance scoring

3. **Answer Quality**
   - Truncates at arbitrary character limits (300/500)
   - May cut off mid-sentence
   - No coherent synthesis of information

### Security Features ✅
- ✅ No public file upload
- ✅ Documents loaded from local filesystem only
- ✅ No API keys required (unless adding LLM)
- ✅ Sandboxed document directory

---

## How to Use

### Starting the Server
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows

# Start development server
py -m uvicorn app.main:app --reload

# Server runs at: http://localhost:8000
```

### Adding Documents
1. Place PDF, DOCX, or TXT files in: `D:\Projects\Portfolio\data\documents\`
2. Restart server (auto-reload will pick them up)
3. Documents are automatically indexed

### Resetting Vector Store
```bash
# Delete ChromaDB and restart
rmdir /s chroma_db
# Restart server to rebuild index
```

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Home page (HTML) |
| `/api/portfolio` | GET | Portfolio data (JSON) |
| `/api/ask` | POST | Ask question via RAG + Web Search |
| `/api/search` | GET | Search documents only |
| `/api/clear-documents` | DELETE | Clear vector store |
| `/health` | GET | Health check |

**Note**: `/api/upload-resume` endpoint was **removed** for security.

---

## Future Enhancements

### Recommended Next Steps

1. **Integrate LLM for Better Answers**
   ```python
   # Option 1: OpenAI
   import openai
   response = openai.ChatCompletion.create(...)

   # Option 2: Anthropic Claude
   import anthropic
   client = anthropic.Anthropic(api_key=...)
   ```

2. **Improve Web Search**
   - Use proper search API (Bing, Google Custom Search)
   - Better result parsing
   - Relevance ranking

3. **Add Caching**
   - Cache web search results
   - Cache common questions
   - Reduce API costs

4. **Enhanced Document Processing**
   - OCR for scanned PDFs
   - Better chunk boundary detection
   - Metadata extraction (dates, companies, etc.)

5. **Analytics**
   - Track popular questions
   - Monitor answer quality
   - A/B testing different prompts

---

## Configuration

### Environment Variables (.env)
```bash
# Optional - for LLM integration
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# App settings
DEBUG=True
```

### Key Settings (app/core/config.py)
```python
APP_NAME: str = "Portfolio"
CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
DOCUMENTS_DIR: str = "./data/documents"
```

---

## Troubleshooting

### Common Issues

1. **Server won't start**
   - Check Python version: `py --version` (should be 3.11+)
   - Reinstall dependencies: `pip install -r requirements.txt`

2. **Documents not loading**
   - Check file format (PDF, DOCX, TXT only)
   - Verify file path: `D:\Projects\Portfolio\data\documents\`
   - Check server logs for parsing errors

3. **Web search not working**
   - Check internet connection
   - DuckDuckGo may rate-limit requests
   - Check timeout settings (currently 5s)

4. **ChromaDB errors**
   - Delete `chroma_db/` folder and restart
   - Check disk space
   - Verify write permissions

---

## Key Learnings from Session

### What Works Well ✅
- Local document loading (secure and private)
- Vector similarity search (fast and accurate)
- Web search enhancement (broader context)
- Auto-reload during development

### What Needs Improvement ⚠️
- Answer quality (needs LLM integration)
- Web search result parsing (basic HTML scraping)
- No answer caching (repeated queries re-search web)
- Limited error handling

### Best Practices Applied
- Removed insecure upload endpoint
- Used environment-based configuration
- Persistent vector store (survives restarts)
- Comprehensive documentation (CLAUDE.md)

---

## Quick Reference Commands

```bash
# Environment
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Run Server
py -m uvicorn app.main:app --reload

# Production
py -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Reset Vector Store
rmdir /s chroma_db

# Add New Document
# Just copy to: data/documents/
# Then restart server
```

---

## Session Statistics

- **Time Spent**: Full session from setup to deployment
- **Files Modified**: 8
- **Files Created**: 3 (CLAUDE.md, SESSION_SUMMARY.md, data/documents/)
- **Dependencies Installed**: ~20 packages
- **Documents Indexed**: 2 (12 chunks total)
- **Lines of Code Changed**: ~200
- **Errors Fixed**: 4 major + several minor

---

## Contact & Resources

**Project Documentation**: `CLAUDE.md`
**Server**: http://localhost:8000
**Documents Location**: `D:\Projects\Portfolio\data\documents\`

For questions or issues, refer to this summary and CLAUDE.md.
