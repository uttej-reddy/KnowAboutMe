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

    def _extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """Extract important keywords from text"""
        # Simple keyword extraction - filter common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                       'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                       'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                       'could', 'should', 'may', 'might', 'can', 'i', 'you', 'he', 'she',
                       'it', 'we', 'they', 'what', 'when', 'where', 'who', 'how', 'why'}

        words = text.lower().split()
        keywords = [w.strip('.,!?;:()[]{}') for w in words
                   if w.lower() not in common_words and len(w) > 3]

        # Return unique keywords
        return list(dict.fromkeys(keywords))[:top_n]

    def _search_web(self, query: str) -> str:
        """Search the web using DuckDuckGo"""
        try:
            # Use DuckDuckGo HTML search (no API key required)
            url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code == 200:
                # Extract text snippets from results (basic parsing)
                text = response.text
                # Simple extraction - get first few hundred characters of relevant content
                start = text.find('result__snippet')
                if start != -1:
                    snippet_text = text[start:start+1000]
                    # Clean HTML tags (very basic)
                    import re
                    clean_text = re.sub('<[^<]+?>', '', snippet_text)
                    return clean_text[:500]

            return ""
        except Exception as e:
            print(f"Web search error: {e}")
            return ""

    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a question using RAG + Web Search

        Args:
            question: User's question

        Returns:
            Dictionary with answer and sources
        """
        answer_parts = []
        sources = []

        # Get relevant documents from resume
        if self.vectorstore is not None:
            relevant_docs = self.search(question, k=2)

            if relevant_docs:
                context = "\n".join([doc["content"] for doc in relevant_docs])
                sources.extend([doc["source"] for doc in relevant_docs])

                # Extract keywords from resume context
                keywords = self._extract_keywords(context, top_n=3)

                answer_parts.append(f"Based on my resume:\n{context[:300]}")

                # Search web with resume keywords + question
                if keywords:
                    search_query = f"{' '.join(keywords)} {question}"
                    web_results = self._search_web(search_query)

                    if web_results:
                        answer_parts.append(f"\n\nAdditional context from web search:\n{web_results}")
                        sources.append("Web Search")

        if not answer_parts:
            # No resume data, try web search with question only
            web_results = self._search_web(question)
            if web_results:
                answer_parts.append(f"Based on web search:\n{web_results}")
                sources.append("Web Search")
            else:
                return {
                    "answer": "I couldn't find relevant information to answer that question. Please ensure documents are placed in the ./data/documents/ directory.",
                    "sources": []
                }

        return {
            "answer": "\n".join(answer_parts),
            "sources": list(set(sources))
        }

    def clear_vectorstore(self):
        """Clear all documents from vector store"""
        if os.path.exists(settings.CHROMA_PERSIST_DIRECTORY):
            import shutil
            shutil.rmtree(settings.CHROMA_PERSIST_DIRECTORY)
            self.vectorstore = None
            print("Vectorstore cleared")


# Global instance
rag_service = SimpleRAG()
