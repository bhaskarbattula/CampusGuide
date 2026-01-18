import streamlit as st
import os
from typing import Dict, Any

# Import all components
from config.config import Config
from ingestion.document_loader import DocumentLoader
from ingestion.text_cleaner import TextCleaner
from ingestion.text_splitter import TextSplitter
from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore
from retriever.retriever import Retriever
from llm.answer_generator import AnswerGenerator
from validation.safety_checker import SafetyChecker
from validation.grounding_validator import GroundingValidator
from ui.sidebar import Sidebar
from ui.chat_ui import ChatUI
from utils.logger import logger
from utils.helpers import extract_document_metadata


class CampusGuideApp:
    def __init__(self):
        self.config = Config()
        self.sidebar = Sidebar()
        self.chat_ui = ChatUI()

        # Initialize RAG components
        self.document_loader = DocumentLoader()
        self.text_cleaner = TextCleaner()
        self.text_splitter = TextSplitter()
        self.embedder = Embedder()
        self.vector_store = VectorStore()
        self.retriever = Retriever()
        self.answer_generator = AnswerGenerator()
        self.safety_checker = SafetyChecker()
        self.grounding_validator = GroundingValidator()

        # Load vector store on startup
        self._initialize_system()

    def _initialize_system(self):
        """Initialize the system by loading existing vector store."""
        logger.info("Initializing CampusGuide system...")
        if self.vector_store.load():
            logger.info("Vector store loaded successfully")
            st.session_state["system_ready"] = True
        else:
            logger.warning("No existing vector store found")
            st.session_state["system_ready"] = False

        # Store retrieval stats in session
        st.session_state["retrieval_stats"] = self.retriever.get_retrieval_stats()

    def process_query(self, query: str, role: str) -> Dict[str, Any]:
        """
        Process a user query through the complete RAG pipeline.

        Args:
            query: User query
            role: User role

        Returns:
            Response with answer and sources
        """
        try:
            # Step 1: Retrieve relevant chunks
            logger.info(f"Processing query: {query[:50]}...")
            retrieval_result = self.retriever.retrieve(query, role)

            # Step 2: Safety check
            safety_result = self.safety_checker.check_retrieval_safety(retrieval_result)
            if not safety_result["safe"]:
                logger.warning(f"Safety check failed: {safety_result['reason']}")
                return {
                    "answer": "The requested information is not available in the provided documents.",
                    "sources": [],
                    "safety_issue": safety_result["reason"],
                }

            # Step 3: Generate answer
            chunks = retrieval_result["chunks"]
            answer = self.answer_generator.generate_answer(query, chunks)

            # Step 4: Grounding validation
            grounding_result = self.grounding_validator.validate_answer_grounding(
                answer, chunks
            )
            if not grounding_result["valid"]:
                logger.warning(
                    f"Grounding validation failed: {grounding_result['reason']}"
                )
                return {
                    "answer": "The requested information is not available in the provided documents.",
                    "sources": [],
                    "grounding_issue": grounding_result["reason"],
                }

            # Step 5: Prepare sources for display
            sources = self._prepare_sources(chunks)

            logger.info("Query processed successfully")
            return {"answer": answer, "sources": sources}

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "answer": "An error occurred while processing your query. Please try again.",
                "sources": [],
            }

    def _prepare_sources(self, chunks: list) -> list:
        """
        Prepare source information for display.

        Args:
            chunks: Retrieved chunks

        Returns:
            List of source dictionaries
        """
        sources = []
        seen_sources = set()

        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            filename = metadata.get("filename", "Unknown document")
            pages = chunk.get("pages", [])

            # Create unique source key
            source_key = f"{filename}_{'_'.join(map(str, sorted(pages)))}"

            if source_key not in seen_sources:
                sources.append(
                    {
                        "filename": filename,
                        "pages": sorted(pages),
                        "excerpt": chunk["text"][:300] + "..."
                        if len(chunk["text"]) > 300
                        else chunk["text"],
                    }
                )
                seen_sources.add(source_key)

        return sources

    def ingest_documents(self):
        """Ingest documents from the raw data directory."""
        raw_dir = self.config.DATA_RAW_PATH

        if not os.path.exists(raw_dir):
            logger.warning(f"Raw data directory does not exist: {raw_dir}")
            return

        logger.info("Starting document ingestion...")

        # Load documents
        documents = self.document_loader.load_multiple_pdfs(raw_dir)

        if not documents:
            logger.warning("No documents found to ingest")
            return

        all_chunks = []
        for doc in documents:
            # Clean text
            cleaned_doc = self.text_cleaner.clean_text(doc["text"])
            doc["text"] = cleaned_doc

            # Split into chunks
            chunks = self.text_splitter.split_document(doc)
            all_chunks.extend(chunks)

        # Generate embeddings
        embedded_chunks = self.embedder.embed_chunks(all_chunks)

        # Add to vector store
        self.vector_store.add_chunks(embedded_chunks)
        self.vector_store.save()

        logger.info(
            f"Successfully ingested {len(documents)} documents, {len(all_chunks)} chunks"
        )
        st.session_state["system_ready"] = True

        # Update stats
        st.session_state["retrieval_stats"] = self.retriever.get_retrieval_stats()

    def run(self):
        """Run the Streamlit application."""
        st.set_page_config(
            page_title="CampusGuide - ICFAI University Assistant",
            page_icon="🎓",
            layout="wide",
        )

        # Render sidebar and get role
        role = self.sidebar.render()

        # Main content
        if not st.session_state.get("system_ready", False):
            st.warning(
                "⚠️ No documents have been ingested yet. Please add PDF documents to the data/raw/ directory and restart the application."
            )
            if st.button("Ingest Documents"):
                with st.spinner("Ingesting documents..."):
                    self.ingest_documents()
                st.rerun()
            return

        # Set query callback
        self.chat_ui.set_query_callback(self.process_query)

        # Render chat interface
        self.chat_ui.render_chat_interface(role)

        # Handle chat input through session state
        if "pending_query" in st.session_state and st.session_state["pending_query"]:
            query = st.session_state["pending_query"]
            st.session_state["pending_query"] = None

            response = self.process_query(query, role)

            # Store response for UI
            st.session_state["last_response"] = response


def main():
    app = CampusGuideApp()
    app.run()


if __name__ == "__main__":
    main()
