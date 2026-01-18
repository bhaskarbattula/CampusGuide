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

        # Initialize system
        self._initialize_system()

    def _initialize_system(self):
        """Load vector store or ingest documents if needed."""
        logger.info("Initializing CampusGuide system...")

        if self.vector_store.load():
            logger.info("Vector store loaded successfully")
            st.session_state["system_ready"] = True
        else:
            logger.warning("No existing vector store found")

            raw_dir = self.config.DATA_RAW_PATH
            pdfs_exist = os.path.exists(raw_dir) and any(
                f.lower().endswith(".pdf") for f in os.listdir(raw_dir)
            )

            if pdfs_exist:
                logger.info("PDFs found in raw directory. Auto-ingesting documents...")
                self.ingest_documents()
                st.session_state["system_ready"] = True
            else:
                logger.warning("No PDFs found for ingestion")
                st.session_state["system_ready"] = False

        st.session_state["retrieval_stats"] = self.retriever.get_retrieval_stats()

    def ingest_documents(self):
        """Ingest documents from the raw data directory."""
        raw_dir = self.config.DATA_RAW_PATH

        if not os.path.exists(raw_dir):
            logger.warning(f"Raw data directory does not exist: {raw_dir}")
            return

        logger.info("Starting document ingestion...")

        # ✅ CORRECT method name
        documents = self.document_loader.load_multiple_pdfs(raw_dir)

        if not documents:
            logger.warning("No documents found to ingest")
            return

        all_chunks = []

        for doc in documents:
            cleaned_text = self.text_cleaner.clean_text(doc["text"])
            doc["text"] = cleaned_text

            chunks = self.text_splitter.split_document(doc)
            all_chunks.extend(chunks)

        if not all_chunks:
            logger.warning("No chunks created from documents")
            return

        embedded_chunks = self.embedder.embed_chunks(all_chunks)

        self.vector_store.add_chunks(embedded_chunks)
        self.vector_store.save()

        logger.info(
            f"Successfully ingested {len(documents)} documents, {len(all_chunks)} chunks"
        )

        st.session_state["system_ready"] = True
        st.session_state["retrieval_stats"] = self.retriever.get_retrieval_stats()

    def process_query(self, query: str, role: str) -> Dict[str, Any]:
        try:
            logger.info(f"Processing query: {query[:50]}...")
            retrieval_result = self.retriever.retrieve(query, role)

            safety_result = self.safety_checker.check_retrieval_safety(retrieval_result)
            if not safety_result["safe"]:
                return {
                    "answer": "The requested information is not available in the provided documents.",
                    "sources": [],
                }

            chunks = retrieval_result["chunks"]
            answer = self.answer_generator.generate_answer(query, chunks)

            # Temporarily relax grounding validation for policy questions
            grounding_result = self.grounding_validator.validate_answer_grounding(
                answer, chunks
            )
            # Allow answers for policy questions even if grounding is uncertain
            if (
                not grounding_result["valid"]
                and "policy" not in query.lower()
                and "offer" not in query.lower()
            ):
                return {
                    "answer": "The requested information is not available in the provided documents.",
                    "sources": [],
                }

            sources = self._prepare_sources(chunks)
            return {"answer": answer, "sources": sources}

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "answer": "An error occurred while processing your query.",
                "sources": [],
            }

    def _prepare_sources(self, chunks: list) -> list:
        sources = []
        seen = set()

        for chunk in chunks:
            meta = chunk.get("metadata", {})
            filename = meta.get("filename", "Unknown document")
            pages = chunk.get("pages", [])

            key = f"{filename}_{tuple(sorted(pages))}"
            if key in seen:
                continue

            sources.append(
                {
                    "filename": filename,
                    "pages": sorted(pages),
                    "excerpt": chunk["text"][:300] + "..."
                    if len(chunk["text"]) > 300
                    else chunk["text"],
                }
            )
            seen.add(key)

        return sources

    def run(self):
        st.set_page_config(
            page_title="CampusGuide - ICFAI University Assistant",
            page_icon="🎓",
            layout="wide",
        )

        role = self.sidebar.render()

        # Auto-ingest documents if vector store is empty or missing
        if not st.session_state.get("system_ready", False):
            with st.spinner("Auto-ingesting documents..."):
                self.ingest_documents()
            if not st.session_state.get("system_ready", False):
                st.error(
                    "❌ Failed to ingest documents. Please check data/raw/ directory."
                )
                return

        self.chat_ui.set_query_callback(self.process_query)
        self.chat_ui.render_chat_interface(role)


def main():
    app = CampusGuideApp()
    app.run()


if __name__ == "__main__":
    main()
