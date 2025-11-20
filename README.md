# AI-Powered Portfolio with RAG

A modern portfolio website built with FastAPI, featuring AI-powered Q&A using Retrieval Augmented Generation (RAG). Upload your resume and let visitors ask questions about your experience, skills, and projects!

## Features

- **FastAPI Backend**: Modern, fast Python web framework
- **RAG-Powered Q&A**: Upload resumes/documents and answer questions intelligently
- **Document Parsing**: Supports PDF, DOCX, and TXT formats
- **Vector Database**: ChromaDB for efficient document retrieval
- **Responsive Design**: Mobile-friendly interface
- **No API Keys Required**: Uses open-source embeddings (can be upgraded to use OpenAI/Anthropic)

## Tech Stack

**Backend:**
- FastAPI
- LangChain
- ChromaDB (Vector Database)
- Sentence Transformers (Embeddings)
- PyPDF2 & pdfplumber (Document Parsing)

**Frontend:**
- HTML5, CSS3, JavaScript
- Jinja2 Templates

## Installation

### Prerequisites

- Python 3.7 or higher
- pip

### Setup Steps

1. **Create a virtual environment**
   ```bash
   cd D:\Projects\Portfolio
   py -m venv venv
   ```

2. **Activate the virtual environment**

   On Windows:
   ```bash
   venv\Scripts\activate
   ```

   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file** (optional)
   ```bash
   copy .env.example .env
   ```

   Edit `.env` if you want to use OpenAI or Anthropic API for better responses.

## Usage

### 1. Start the Server

```bash
py -m uvicorn app.main:app --reload
```

The server will start at: `http://localhost:8000`

### 2. Upload Your Resume

1. Open your browser and navigate to `http://localhost:8000`
2. Scroll to the "Ask AI About Me" section
3. Click "Choose File" and select your resume (PDF, DOCX, or TXT)
4. Click "Upload"
5. Wait for processing (this will parse your resume and create embeddings)

### 3. Ask Questions

Once your resume is uploaded, you can ask questions like:
- "What programming languages do you know?"
- "Tell me about your work experience"
- "What projects have you worked on?"
- "What is your educational background?"

The AI will search through your resume and provide relevant answers!

## Customization

### Update Portfolio Data

Edit `app/main.py` and update the `PORTFOLIO_DATA` object:

```python
PORTFOLIO_DATA = PortfolioData(
    name="Your Name",
    title="Your Title",
    bio="Your bio",
    email="your.email@example.com",
    github="https://github.com/yourusername",
    linkedin="https://linkedin.com/in/yourusername",
    tech_stack=[
        TechStack(
            name="Python",
            category="Language",
            proficiency="Expert",
            years_experience=5
        ),
        # Add more...
    ],
    experiences=[],
    projects=[],
    education=[]
)
```

### Styling

Edit `app/static/css/style.css` to customize colors, fonts, and layout.

### Advanced: Use GPT/Claude for Better Answers

1. Get an API key from OpenAI or Anthropic
2. Add it to your `.env` file:
   ```
   OPENAI_API_KEY=your_key_here
   ```
3. Update `app/services/rag_service.py` to use the LLM for generating answers

## API Endpoints

- `GET /` - Home page
- `GET /api/portfolio` - Get portfolio data (JSON)
- `POST /api/upload-resume` - Upload resume document
- `POST /api/ask` - Ask a question about the portfolio
- `GET /api/search?query=...` - Search documents
- `DELETE /api/clear-documents` - Clear all uploaded documents
- `GET /health` - Health check

## Project Structure

```
Portfolio/
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Configuration
│   ├── models/           # Pydantic models
│   ├── services/         # Business logic
│   │   ├── document_parser.py
│   │   └── rag_service.py
│   ├── static/           # CSS, JS, images
│   │   ├── css/
│   │   └── js/
│   ├── templates/        # HTML templates
│   └── main.py           # FastAPI app
├── data/
│   └── resumes/          # Uploaded resumes
├── chroma_db/            # Vector database (auto-created)
├── requirements.txt
├── .env.example
└── README.md
```

## Deployment

### Deploy to Railway/Render

1. Create a `runtime.txt`:
   ```
   python-3.10.0
   ```

2. Create a `Procfile`:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

3. Push to GitHub and connect to Railway/Render

### Deploy to Vercel (with serverless)

Use Vercel's Python runtime or containerize the app.

## Troubleshooting

**Issue: ModuleNotFoundError**
- Make sure your virtual environment is activated
- Run `pip install -r requirements.txt` again

**Issue: Document parsing fails**
- Check file format (must be PDF, DOCX, or TXT)
- Ensure file is not corrupted

**Issue: RAG not working**
- Upload a document first
- Check ChromaDB directory was created
- Look at server logs for errors

## Next Steps

1. Add more personal information to `PORTFOLIO_DATA`
2. Upload your actual resume
3. Add project images to `app/static/images/`
4. Customize the styling
5. Add authentication if needed
6. Deploy to production

## Contributing

Feel free to fork this project and customize it for your needs!

## License

MIT
