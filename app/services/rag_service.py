from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from typing import Optional, List, Dict, Any
from app.core.config import settings
from pathlib import Path
import os
import requests
import json
from urllib.parse import quote
from openai import OpenAI


class SimpleRAG:
    """
    RAG (Retrieval Augmented Generation) service for portfolio Q&A

    This uses open-source models by default (no API keys required)
    Can be upgraded to use OpenAI/Anthropic for better responses
    """

    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vectorstore: Optional[Chroma] = None

        # Initialize OpenAI client if API key is available
        self.openai_client = None
        if settings.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                print("OpenAI client initialized successfully")
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
        else:
            print("No OpenAI API key found. Responses will use basic context extraction.")

        self._initialize_vectorstore()

    def _initialize_vectorstore(self):
        """Initialize or load existing vector store"""
        persist_directory = settings.CHROMA_PERSIST_DIRECTORY

        if os.path.exists(persist_directory):
            # Load existing vectorstore
            try:
                self.vectorstore = Chroma(
                    persist_directory=persist_directory,
                    embedding_function=self.embeddings
                )
                print(f"Loaded existing vectorstore from {persist_directory}")
            except Exception as e:
                print(f"Error loading vectorstore: {e}")
                self.vectorstore = None
        else:
            print("No existing vectorstore found. Will create on first document add.")

        # Load documents from local directory
        self._load_local_documents()

    def _load_local_documents(self):
        """Load documents from local documents directory"""
        from app.services.document_parser import DocumentParser

        documents_dir = settings.DOCUMENTS_DIR

        # Create directory if it doesn't exist
        if not os.path.exists(documents_dir):
            os.makedirs(documents_dir, exist_ok=True)
            print(f"Created documents directory: {documents_dir}")
            print(f"Place your PDF, DOCX, or TXT files in {documents_dir} to index them")
            return

        # Supported file extensions
        supported_extensions = {'.pdf', '.docx', '.doc', '.txt'}

        # Find all supported documents
        doc_files = []
        for ext in supported_extensions:
            doc_files.extend(Path(documents_dir).glob(f"*{ext}"))

        if not doc_files:
            print(f"No documents found in {documents_dir}")
            print(f"Place your PDF, DOCX, or TXT files there to index them")
            return

        # Parse and add documents
        parser = DocumentParser()
        documents = {}

        for file_path in doc_files:
            try:
                print(f"Loading document: {file_path.name}")
                text = parser.parse_document(str(file_path))
                documents[file_path.name] = text
            except Exception as e:
                print(f"Error loading {file_path.name}: {e}")

        if documents:
            self.add_documents(documents)
            print(f"Successfully loaded {len(documents)} document(s)")

    def add_documents(self, documents: Dict[str, str]):
        """
        Add documents to the vector store

        Args:
            documents: Dictionary mapping document names to their text content
        """
        all_texts = []
        metadatas = []

        for doc_name, content in documents.items():
            # Split document into chunks
            chunks = self.text_splitter.split_text(content)

            for i, chunk in enumerate(chunks):
                all_texts.append(chunk)
                metadatas.append({
                    "source": doc_name,
                    "chunk_id": i
                })

        if all_texts:
            if self.vectorstore is None:
                # Create new vectorstore
                self.vectorstore = Chroma.from_texts(
                    texts=all_texts,
                    embedding=self.embeddings,
                    metadatas=metadatas,
                    persist_directory=settings.CHROMA_PERSIST_DIRECTORY
                )
            else:
                # Add to existing vectorstore
                self.vectorstore.add_texts(
                    texts=all_texts,
                    metadatas=metadatas
                )

            self.vectorstore.persist()
            print(f"Added {len(all_texts)} chunks from {len(documents)} documents")

    def search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """
        Search for relevant documents

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of relevant document chunks with metadata
        """
        if self.vectorstore is None:
            return []

        results = self.vectorstore.similarity_search_with_score(query, k=k)

        return [
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "score": score
            }
            for doc, score in results
        ]


    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a question using RAG from uploaded documents with OpenAI

        Args:
            question: User's question

        Returns:
            Dictionary with answer and sources
        """
        if self.vectorstore is None:
            return {
                "answer": "No documents have been loaded yet. Please ensure your resume and documents are in the ./data/documents/ directory.",
                "sources": []
            }

        # Get relevant documents from resume
        relevant_docs = self.search(question, k=5)

        if not relevant_docs:
            return {
                "answer": "I couldn't find relevant information in the uploaded documents to answer that question. Try asking about experience, skills, education, or projects.",
                "sources": []
            }

        # Gather context from relevant chunks
        context_parts = []
        for doc in relevant_docs:
            context_parts.append(doc["content"])

        # Combine all relevant context
        full_context = "\n\n".join(context_parts)

        # Generate answer using OpenAI if available, otherwise use basic extraction
        if self.openai_client:
            answer = self._generate_openai_answer(question, full_context)
        else:
            answer = self._generate_basic_answer(question, full_context)

        return {
            "answer": answer,
            "sources": []  # Sources removed as per request
        }

    def _generate_openai_answer(self, question: str, context: str) -> str:
        """
        Generate a dynamic answer using OpenAI GPT

        Args:
            question: User's question
            context: Relevant context from documents

        Returns:
            Generated answer
        """
        try:
            # Create a prompt that instructs GPT to answer in first person
            system_prompt = """You are Uttej Reddy Thoompally, a Senior Software Engineer.
Answer questions about your professional background in first person using the provided context from your resume.
Be conversational, confident, and natural. Don't mention that you're looking at a resume or documents.
Keep answers concise (2-3 paragraphs max) but informative."""

            user_prompt = f"""Context from my resume:
{context}

Question: {question}

Please answer this question naturally in first person, as if you're speaking in an interview."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Using cost-effective model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Fallback to basic answer if OpenAI fails
            return self._generate_basic_answer(question, context)

    def _generate_basic_answer(self, question: str, context: str) -> str:
        """
        Generate a basic answer without OpenAI (fallback)

        Args:
            question: User's question
            context: Relevant context from documents

        Returns:
            Basic extracted answer
        """
        # Return context with minimal formatting
        answer = context[:1200]

        # Clean up if cut off mid-sentence
        if len(context) > 1200:
            last_period = answer.rfind('.')
            if last_period > 500:
                answer = answer[:last_period + 1]

        return answer

    def clear_vectorstore(self):
        """Clear all documents from vector store"""
        if os.path.exists(settings.CHROMA_PERSIST_DIRECTORY):
            import shutil
            shutil.rmtree(settings.CHROMA_PERSIST_DIRECTORY)
            self.vectorstore = None
            print("Vectorstore cleared")


# Global instance
rag_service = SimpleRAG()
