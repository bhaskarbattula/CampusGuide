import streamlit as st
import os
from typing import Dict, Any

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

        # RAG components
        self.document_loader = DocumentLoader()
        self.text_cleaner = TextCleaner()
        self.text_splitter = TextSplitter()
        self.embedder = Embedder()
        self.vector_store = VectorStore()
        self.retriever = Retriever()
        self.answer_generator = AnswerGenerator()
        self.safety_checker = SafetyChecker()
        self.grounding_validator = GroundingValidator()

        self._initialize_system()

    # ---------------- INITIALIZATION ---------------- #

    def _initialize_system(self):
        logger.info("Initializing CampusGuide system...")

        if self.vector_store.load():
            st.session_state["system_ready"] = True
            logger.info("Vector store loaded")
        else:
            raw_dir = self.config.DATA_RAW_PATH
            pdfs_exist = os.path.exists(raw_dir) and any(
                f.lower().endswith(".pdf") for f in os.listdir(raw_dir)
            )

            if pdfs_exist:
                logger.info("No vector store found. Auto-ingesting PDFs...")
                self.ingest_documents()
                st.session_state["system_ready"] = True
            else:
                st.session_state["system_ready"] = False

        st.session_state["retrieval_stats"] = self.retriever.get_retrieval_stats()

    # ---------------- INGESTION ---------------- #

    def ingest_documents(self):
        raw_dir = self.config.DATA_RAW_PATH
        logger.info("Starting document ingestion...")

        documents = self.document_loader.load_multiple_pdfs(raw_dir)
        if not documents:
            logger.warning("No documents found")
            return

        all_chunks = []
        for doc in documents:
            doc["text"] = self.text_cleaner.clean_text(doc["text"])
            all_chunks.extend(self.text_splitter.split_document(doc))

        embedded_chunks = self.embedder.embed_chunks(all_chunks)
        self.vector_store.add_chunks(embedded_chunks)
        self.vector_store.save()

        st.session_state["system_ready"] = True

        logger.info(
            f"Ingested {len(documents)} documents with {len(all_chunks)} chunks"
        )

    # ---------------- QUERY PIPELINE ---------------- #

    def process_query(self, query: str, role: str) -> Dict[str, Any]:
        logger.info(f"Processing query: {query}")

        retrieval_result = self.retriever.retrieve(query, role)
        safety = self.safety_checker.check_retrieval_safety(retrieval_result)

        # ❌ Retrieval confidence failure
        if not safety["safe"]:
            return self._refusal_response()

        chunks = retrieval_result["chunks"]
        answer = self.answer_generator.generate_answer(query, chunks)

        # ❌ LLM refusal
        if self._is_refusal(answer):
            return self._refusal_response()

        # ❌ Grounding failure
        grounding = self.grounding_validator.validate_answer_grounding(
            answer, chunks, query
        )
        if not grounding["valid"]:
            return self._refusal_response()

        # ✅ Valid answer
        return {
            "answer": answer,
            "sources": self._prepare_sources(chunks),
        }

    # ---------------- HELPERS ---------------- #

    def _is_refusal(self, answer: str) -> bool:
        refusal_markers = [
            "not available in the provided documents",
            "do not explicitly",
            "cannot provide an answer",
        ]
        return any(marker in answer.lower() for marker in refusal_markers)

    def _refusal_response(self) -> Dict[str, Any]:
        return {
            "answer": (
                "The internship guidelines do not explicitly list the documents students "
                "must carry during placement induction. To avoid assumptions, the system "
                "cannot provide an answer based on the available documents."
            ),
            "sources": [],
            "source_note": (
                "No sections in the provided documents explicitly mention this information."
            ),
        }

    def _prepare_sources(self, chunks: list) -> list:
        sources, seen = [], set()

        for chunk in chunks:
            meta = chunk.get("metadata", {})
            key = (meta.get("filename"), tuple(chunk.get("pages", [])))
            if key in seen:
                continue

            sources.append(
                {
                    "filename": meta.get("filename", "Unknown"),
                    "pages": sorted(chunk.get("pages", [])),
                    "excerpt": chunk["text"][:300],
                }
            )
            seen.add(key)

        return sources

    # ---------------- UI ---------------- #

    def run(self):
        st.set_page_config(
            page_title="CampusGuide - ICFAI University Assistant",
            page_icon="🎓",
            layout="wide",
        )

        role = self.sidebar.render()

        if not st.session_state.get("system_ready"):
            st.error("No documents available. Please add PDFs to data/raw/")
            return

        self.chat_ui.set_query_callback(self.process_query)
        self.chat_ui.render_chat_interface(role)


def main():
    CampusGuideApp().run()


if __name__ == "__main__":
    main()

