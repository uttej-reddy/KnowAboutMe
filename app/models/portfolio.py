from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class TechStack(BaseModel):
    """Technology stack item"""
    name: str
    category: str  # e.g., "Language", "Framework", "Database", "Tool"
    proficiency: str  # e.g., "Expert", "Intermediate", "Beginner"
    years_experience: Optional[int] = None


class Experience(BaseModel):
    """Work experience entry"""
    company: str
    position: str
    start_date: date
    end_date: Optional[date] = None
    description: str
    technologies: List[str]
    achievements: Optional[List[str]] = None


class Project(BaseModel):
    """Project entry"""
    name: str
    description: str
    technologies: List[str]
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    image_url: Optional[str] = None


class Education(BaseModel):
    """Education entry"""
    institution: str
    degree: str
    field_of_study: str
    start_date: date
    end_date: Optional[date] = None
    gpa: Optional[float] = None


class PortfolioData(BaseModel):
    """Complete portfolio data"""
    name: str
    title: str
    bio: str
    email: str
    github: Optional[str] = None
    linkedin: Optional[str] = None
    tech_stack: List[TechStack]
    experiences: List[Experience]
    projects: List[Project]
    education: List[Education]


class QuestionRequest(BaseModel):
    """Request model for RAG questions"""
    question: str


class QuestionResponse(BaseModel):
    """Response model for RAG answers"""
    answer: str
    sources: Optional[List[str]] = None
