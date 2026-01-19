import streamlit as st
import os
import hashlib
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

        raw_dir = self.config.DATA_RAW_PATH
        supported_files_exist = os.path.exists(raw_dir) and any(
            f.lower().endswith(tuple(self.config.SUPPORTED_EXTENSIONS))
            for f in os.listdir(raw_dir)
        )

        if self.vector_store.load():
            if supported_files_exist:
                st.session_state["system_ready"] = True
                logger.info("Vector store loaded with existing documents")
            else:
                logger.info("No documents in raw folder, clearing old vector store")
                self.vector_store.clear()
                st.session_state["system_ready"] = False
        else:
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
            logger.info("No files uploaded")
            return False

        logger.info(f"Supported extensions: {self.config.SUPPORTED_EXTENSIONS}")
        logger.info(f"Processing {len(uploaded_files)} uploaded files")
        raw_dir = self.config.DATA_RAW_PATH
        os.makedirs(raw_dir, exist_ok=True)

        # Compute hashes of existing files for duplicate check
        existing_hashes = {}
        if os.path.exists(raw_dir):
            for filename in os.listdir(raw_dir):
                if filename.lower().endswith(tuple(self.config.SUPPORTED_EXTENSIONS)):
                    filepath = os.path.join(raw_dir, filename)
                    try:
                        with open(filepath, "rb") as f:
                            existing_hashes[hashlib.md5(f.read()).hexdigest()] = (
                                filename
                            )
                    except Exception:
                        pass  # Skip if can't read

        saved_files = []
        for uploaded_file in uploaded_files:
            logger.info(f"Processing file: {uploaded_file.name}")
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            logger.info(f"File extension: {file_ext}")

            if file_ext not in self.config.SUPPORTED_EXTENSIONS:
                logger.warning(
                    f"Skipping {uploaded_file.name}: unsupported extension {file_ext}"
                )
                continue

            # Check for duplicate content
            file_hash = hashlib.md5(uploaded_file.getbuffer()).hexdigest()
            if file_hash in existing_hashes:
                logger.info(
                    f"Skipped duplicate file: {uploaded_file.name} (matches {existing_hashes[file_hash]})"
                )
                continue

            base_name = os.path.splitext(uploaded_file.name)[0]
            ext = file_ext
            counter = 0
            file_path = os.path.join(raw_dir, uploaded_file.name)

            while os.path.exists(file_path):
                counter += 1
                file_path = os.path.join(raw_dir, f"{base_name}_{counter}{ext}")

            try:
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                saved_files.append(file_path)
                existing_hashes[file_hash] = os.path.basename(
                    file_path
                )  # Update for future checks
                logger.info(f"Saved uploaded file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to save file {uploaded_file.name}: {e}")
                continue

            base_name = os.path.splitext(uploaded_file.name)[0]
            ext = file_ext
            counter = 0
            file_path = os.path.join(raw_dir, uploaded_file.name)

            while os.path.exists(file_path):
                counter += 1
                file_path = os.path.join(raw_dir, f"{base_name}_{counter}{ext}")

            try:
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                saved_files.append(file_path)
                logger.info(f"Saved uploaded file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to save file {uploaded_file.name}: {e}")
                continue

        if saved_files:
            logger.info(f"Saved files: {[os.path.basename(f) for f in saved_files]}")
            # Trigger full ingestion to rebuild vector store with all files
            logger.info(
                f"Uploaded {len(saved_files)} files, rebuilding knowledge base..."
            )
            try:
                self.ingest_documents()
                return True
            except Exception as e:
                logger.error(f"Failed to ingest documents after upload: {e}")
                return False

        logger.warning("No files were successfully saved")
        return False

        raw_dir = self.config.DATA_RAW_PATH
        os.makedirs(raw_dir, exist_ok=True)

        saved_files = []
        for uploaded_file in uploaded_files:
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            if file_ext not in self.config.SUPPORTED_EXTENSIONS:
                continue

            base_name = os.path.splitext(uploaded_file.name)[0]
            ext = file_ext
            counter = 0
            file_path = os.path.join(raw_dir, uploaded_file.name)

            while os.path.exists(file_path):
                counter += 1
                file_path = os.path.join(raw_dir, f"{base_name}_{counter}{ext}")

            try:
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                saved_files.append(file_path)
                logger.info(f"Saved uploaded file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to save file {uploaded_file.name}: {e}")
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

        logger.info(
            f"Loaded documents: {[d['metadata']['filename'] for d in documents]}"
        )

        all_chunks = []
        for doc in documents:
            doc["text"] = self.text_cleaner.clean_text(doc["text"])
            chunks = self.text_splitter.split_document(doc)
            all_chunks.extend(chunks)
            logger.info(
                f"Created {len(chunks)} chunks for {doc['metadata']['filename']}"
            )

        logger.info(f"Total chunks created: {len(all_chunks)}")

        # Fit the embedder on all chunk texts first
        chunk_texts = [chunk["text"] for chunk in all_chunks]
        self.embedder.fit_on_texts(chunk_texts)

        # Then embed the chunks
        embedded_chunks = self.embedder.embed_chunks(all_chunks)
        self.vector_store.add_chunks(embedded_chunks)
        self.vector_store.save()

        logger.info(f"Vector store saved with {len(embedded_chunks)} embedded chunks")

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
            logger.warning("Retrieval safety failed")
            return self._refusal_response()

        chunks = retrieval_result["chunks"]
        logger.info(
            f"Retrieved {len(chunks)} chunks from: {[c.get('metadata', {}).get('filename', 'unknown') for c in chunks]}"
        )
        logger.info(
            f"Total context length: {sum(len(c['text']) for c in chunks)} chars"
        )

        answer = self.answer_generator.generate_answer(query, chunks)
        logger.info(f"Generated answer: {answer[:200]}...")
        logger.info(f"Is refusal: {self._is_refusal(answer)}")

        # ❌ LLM refusal
        if self._is_refusal(answer):
            logger.warning("LLM generated refusal")
            return self._refusal_response()

        # ❌ Grounding failure
        grounding = self.grounding_validator.validate_answer_grounding(
            answer, chunks, query
        )
        logger.info(
            f"Grounding valid: {grounding['valid']}, score: {grounding.get('grounding_score', 'N/A')}"
        )
        if not grounding["valid"]:
            logger.warning("Grounding validation failed")
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
            raw_dir = self.config.DATA_RAW_PATH
            if os.path.exists(raw_dir) and any(
                f.lower().endswith(tuple(self.config.SUPPORTED_EXTENSIONS))
                for f in os.listdir(raw_dir)
            ):
                with st.spinner("Loading documents..."):
                    self.ingest_documents()
                if not st.session_state.get("system_ready"):
                    st.error("❌ Failed to load documents.")
                    return
            else:
                st.info("📤 Please upload .txt files to build the knowledge base.")
                # Don't return, allow upload

        role = self.sidebar.render()
        self.chat_ui.set_query_callback(self.process_query)
        self.chat_ui.render_chat_interface(role)


def main():
    CampusGuideApp().run()


if __name__ == "__main__":
    main()
