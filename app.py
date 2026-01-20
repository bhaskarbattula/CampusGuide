import streamlit as st
import os
import streamlit as st
import torch
from typing import Dict, Any

# Force CPU device for all tensors
torch.set_default_device("cpu")

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
        # Set environment variables from Streamlit secrets if available
        if hasattr(st, "secrets"):
            os.environ["API_PROVIDER"] = st.secrets.get("API_PROVIDER", "groq")
            os.environ["OPENAI_API_KEY"] = st.secrets.get("OPENAI_API_KEY", "")
            os.environ["GROQ_API_KEY"] = st.secrets.get("GROQ_API_KEY", "")
            os.environ["API_KEY"] = st.secrets.get("API_KEY", "")
            os.environ["LLM_MODEL"] = st.secrets.get("LLM_MODEL", "")

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

            supported_files_exist = os.path.exists(raw_dir) and any(
                f.lower().endswith(tuple(self.config.SUPPORTED_EXTENSIONS))
                for f in os.listdir(raw_dir)
            )

            if supported_files_exist:
                logger.info(
                    "Documents found in raw directory. Auto-ingesting documents..."
                )
                self.ingest_documents()
                st.session_state["system_ready"] = True
            else:
                logger.warning("No supported documents found for ingestion")

                st.session_state["system_ready"] = False

        st.session_state["retrieval_stats"] = self.retriever.get_retrieval_stats()

    # ---------------- INGESTION ---------------- #

    def handle_file_uploads(self, uploaded_files):
        """Handle file uploads from Streamlit UI."""
        if not uploaded_files:
            return False

        raw_dir = self.config.DATA_RAW_PATH
        os.makedirs(raw_dir, exist_ok=True)

        saved_files = []
        for uploaded_file in uploaded_files:
            # Validate file type
            if not uploaded_file.name.lower().endswith(".txt"):
                continue

            # Create unique filename to avoid overwrites
            base_name = os.path.splitext(uploaded_file.name)[0]
            ext = ".txt"
            counter = 0
            file_path = os.path.join(raw_dir, uploaded_file.name)

            while os.path.exists(file_path):
                counter += 1
                file_path = os.path.join(raw_dir, f"{base_name}_{counter}{ext}")

            # Save file
            try:
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                saved_files.append(file_path)
                logger.info(f"Saved uploaded file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to save file {uploaded_file.name}: {e}")
                continue

        if saved_files:
            # Trigger full ingestion to rebuild vector store with all files
            logger.info(
                f"Uploaded {len(saved_files)} files, rebuilding knowledge base..."
            )
            self.ingest_documents()
            return True

        return False

    def ingest_documents(self):
        raw_dir = self.config.DATA_RAW_PATH

        # Ensure processed directory exists
        processed_dir = self.config.DATA_PROCESSED_PATH
        os.makedirs(processed_dir, exist_ok=True)

        logger.info("Starting document ingestion...")

        # Clear existing vector store to rebuild fresh
        self.vector_store.clear()
        logger.info("Cleared existing vector store for fresh rebuild")

        documents = self.document_loader.load_multiple_documents(raw_dir)
        if not documents:
            logger.warning("No documents found")
            return

        all_chunks = []
        for doc in documents:
            doc["text"] = self.text_cleaner.clean_text(doc["text"])
            all_chunks.extend(self.text_splitter.split_document(doc))

        # Fit the embedder on all chunk texts first
        chunk_texts = [chunk["text"] for chunk in all_chunks]
        self.embedder.fit_on_texts(chunk_texts)

        # Then embed the chunks
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

        # Handle file uploads first
        if "uploaded_files" in st.session_state and st.session_state["uploaded_files"]:
            with st.spinner("Processing uploaded files..."):
                success = self.handle_file_uploads(st.session_state["uploaded_files"])
                if success:
                    st.success("✅ Files uploaded and processed successfully!")
                    st.session_state["uploaded_files"] = []  # Clear after processing
                    st.rerun()  # Refresh to update stats
                else:
                    st.error("❌ Failed to process uploaded files.")

        # Auto-ingest documents if not ready (for initial load or restart)
        if not st.session_state.get("system_ready"):
            with st.spinner("Loading documents..."):
                self.ingest_documents()
            if not st.session_state.get("system_ready"):
                st.error(
                    "❌ Failed to load documents. Please add .txt files to data/raw/ and restart the application."
                )
                return

        role = self.sidebar.render()
        self.chat_ui.set_query_callback(self.process_query)
        self.chat_ui.render_chat_interface(role)


def main():
    CampusGuideApp().run()


if __name__ == "__main__":
    main()
