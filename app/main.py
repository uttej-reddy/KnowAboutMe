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

# Portfolio data from resume
PORTFOLIO_DATA = PortfolioData(
    name="Uttej Reddy Thoompally",
    title="Sr Software Engineer | Cloud Platform Architect",
    bio="",
    email="uttej.thoompally@gmail.com",
    github="https://github.com/uttej-t",
    linkedin="https://www.linkedin.com/in/uttej-t/",
    tech_stack=[
        TechStack(name="Java", category="Language", proficiency="Expert", years_experience=10),
        TechStack(name="C#", category="Language", proficiency="Expert", years_experience=8),
        TechStack(name="Python", category="Language", proficiency="Expert", years_experience=7),
        TechStack(name="Scala", category="Language", proficiency="Advanced", years_experience=4),
        TechStack(name="SQL", category="Language", proficiency="Expert", years_experience=10),
        TechStack(name="JavaScript", category="Language", proficiency="Advanced", years_experience=6),
        TechStack(name="Azure", category="Cloud Platform", proficiency="Expert", years_experience=5),
        TechStack(name="AWS", category="Cloud Platform", proficiency="Expert", years_experience=7),
        TechStack(name="Docker", category="DevOps", proficiency="Expert", years_experience=6),
        TechStack(name="Kubernetes", category="DevOps", proficiency="Advanced", years_experience=4),
        TechStack(name="Kafka", category="Streaming", proficiency="Expert", years_experience=5),
        TechStack(name="Spark", category="Big Data", proficiency="Expert", years_experience=5),
        TechStack(name="Terraform", category="Infrastructure", proficiency="Advanced", years_experience=3),
        TechStack(name="Grafana", category="Monitoring", proficiency="Advanced", years_experience=4),
        TechStack(name="Spring Boot", category="Framework", proficiency="Expert", years_experience=8),
        TechStack(name=".NET Core", category="Framework", proficiency="Expert", years_experience=6),
        TechStack(name="ReactJS", category="Framework", proficiency="Intermediate", years_experience=3),
        TechStack(name="Cosmos DB", category="Database", proficiency="Advanced", years_experience=4),
        TechStack(name="Redis", category="Database", proficiency="Expert", years_experience=5),
        TechStack(name="PostgreSQL", category="Database", proficiency="Expert", years_experience=8),
        TechStack(name="MongoDB", category="Database", proficiency="Advanced", years_experience=6),
    ],
    experiences=[
        Experience(
            company="",
            position="",
            location="",
            start_date="",
            end_date="",
            description="Experienced software engineer with 10+ years of expertise in designing and building scalable backend services and platform infrastructure on Azure and AWS in Agile environments using Java, C#, Python, Kafka and Spark. Specialized in resilient distributed systems, microservices, cloud engineering, data engineering, data architecture, and cloud-native architecture with experience across automotive and e-commerce domains.",
            technologies=[],
            responsibilities=[]
        )
    ],
    projects=[
        Project(
            name="Vehicle Telemetry Data Platform",
            description="Designed and built end-to-end data platform for processing petabytes of vehicle telemetry data with real-time streaming and batch processing capabilities",
            technologies=["Azure", "Databricks", "Kafka", "Spark", "Delta Lake", "Unity Catalog"],
            github_url="",
            live_url="",
            highlights=[
                "Processing petabytes of vehicle data in real-time",
                "40% reduction in latency through optimized Kafka/Spark pipelines",
                "20% cost reduction through Redis optimization"
            ]
        ),
        Project(
            name="Buy Online Pick Up Instore (BOPIS)",
            description="Built complete guest experience for BOPIS feature on lululemon.com, enabling customers to purchase online and pick up in physical stores",
            technologies=["Java", "Oracle ATG", "AWS", "JavaScript"],
            github_url="",
            live_url="",
            highlights=[
                "8-14% boost in store sales",
                "Increased foot traffic to physical stores",
                "Seamless integration with existing e-commerce platform"
            ]
        ),
        Project(
            name="Cloud Migration - Oracle to AWS",
            description="Led migration of Oracle ATG applications from Oracle Managed Cloud to AWS infrastructure",
            technologies=["AWS", "Oracle ATG", "Java"],
            github_url="",
            live_url="",
            highlights=[
                "Lift-and-shift approach for minimal disruption",
                "Improved infrastructure flexibility and control",
                "Enhanced scaling capabilities"
            ]
        )
    ],
    education=[
        Education(
            institution="University of Houston - Clear Lake",
            degree="Master of Science",
            field="Management Information Systems",
            graduation_date="December 2013",
            gpa="",
            achievements=[]
        ),
        Education(
            institution="Birla Institute of Technology and Science - Pilani, India",
            degree="Bachelor of Science",
            field="Information Systems",
            graduation_date="May 2012",
            gpa="",
            achievements=[]
        )
    ]
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
