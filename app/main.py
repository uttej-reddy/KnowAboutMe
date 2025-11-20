from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from pathlib import Path
from typing import List

from app.core.config import settings
from app.models.portfolio import (
    PortfolioData,
    QuestionRequest,
    QuestionResponse,
    TechStack,
    Experience,
    Project,
    Education
)
from app.services.document_parser import DocumentParser
from app.services.rag_service import rag_service

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Portfolio with RAG"
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Initialize services
doc_parser = DocumentParser()

# Sample portfolio data (replace with your actual data)
PORTFOLIO_DATA = PortfolioData(
    name="Your Name",
    title="Software Engineer | Full Stack Developer",
    bio="Passionate developer with experience in building scalable applications.",
    email="your.email@example.com",
    github="https://github.com/yourusername",
    linkedin="https://linkedin.com/in/yourusername",
    tech_stack=[
        TechStack(name="Python", category="Language", proficiency="Expert", years_experience=5),
        TechStack(name="FastAPI", category="Framework", proficiency="Expert", years_experience=3),
        TechStack(name="React", category="Framework", proficiency="Intermediate", years_experience=2),
    ],
    experiences=[],
    projects=[],
    education=[]
)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render home page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "portfolio": PORTFOLIO_DATA}
    )


@app.get("/api/portfolio")
async def get_portfolio():
    """Get portfolio data"""
    return PORTFOLIO_DATA




@app.post("/api/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about the portfolio using RAG

    Example questions:
    - What experience do you have with Python?
    - What projects have you worked on?
    - Tell me about your education
    """
    try:
        result = rag_service.answer_question(request.question)
        return QuestionResponse(
            answer=result["answer"],
            sources=result.get("sources", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@app.get("/api/search")
async def search_documents(query: str, limit: int = 5):
    """Search through uploaded documents"""
    try:
        results = rag_service.search(query, k=limit)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")


@app.delete("/api/clear-documents")
async def clear_documents():
    """Clear all uploaded documents from RAG system"""
    try:
        rag_service.clear_vectorstore()
        return {"message": "All documents cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing documents: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
