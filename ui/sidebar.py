import streamlit as st
import os
from config.config import Config


class Sidebar:
    def __init__(self):
        self.config = Config()

    def render(self) -> str:
        """
        Render the sidebar with role selection and information.

        Returns:
            Selected role
        """
        with st.sidebar:
            st.title("🎓 CampusGuide")
            st.markdown("---")

            # Role selection
            st.subheader("Select Your Role")
            role = st.selectbox(
                "Your role determines which documents you can access:",
                options=self.config.ALLOWED_ROLES,
                index=0,
                help="Different roles have access to different types of documents",
            )

            st.markdown("---")

            # File upload section
            st.subheader("📁 Upload Documents")
            uploaded_file = st.file_uploader(
                "Upload PDF or TXT files",
                type=["pdf", "txt"],
                help="Upload university documents to expand the knowledge base"
            )
            
            if uploaded_file is not None:
                self._handle_file_upload(uploaded_file)

            # Current documents
            st.subheader("📚 Current Documents")
            raw_dir = self.config.DATA_RAW_PATH
            if os.path.exists(raw_dir):
                files = [f for f in os.listdir(raw_dir) if f.lower().endswith(('.pdf', '.txt'))]
                if files:
                    for file in files:
                        st.write(f"• {file}")
                else:
                    st.write("*No documents uploaded yet*")
            else:
                st.write("*No documents uploaded yet*")

            st.markdown("---")

            # Information section
            st.subheader("ℹ️ About")
            st.markdown("""
            **CampusGuide** answers questions using official ICFAI University documents only.

            **Features:**
            - Document-grounded responses
            - Role-based access control
            - Source traceability
            - Hallucination prevention

            **Important:** Responses are based solely on uploaded documents.
            """)

            # Stats section (if available)
            if "retrieval_stats" in st.session_state:
                st.markdown("---")
                st.subheader("📊 System Stats")
                stats = st.session_state["retrieval_stats"]
                st.metric("Total Documents", stats.get("total_chunks", 0))
                st.metric("Vector Store Size", stats.get("index_size", 0))

            # Footer
            st.markdown("---")
            st.markdown("*Built with safety and accuracy in mind*")

        return role or "student"  # Default to student if None

    def _handle_file_upload(self, uploaded_file):
        """
        Handle file upload and re-ingestion.
        
        Args:
            uploaded_file: Streamlit uploaded file object
        """
        import tempfile
        import shutil
        
        # Create raw directory if it doesn't exist
        raw_dir = self.config.DATA_RAW_PATH
        os.makedirs(raw_dir, exist_ok=True)
        
        # Save uploaded file
        file_path = os.path.join(raw_dir, uploaded_file.name)
        
        # Check if file already exists
        if os.path.exists(file_path):
            st.warning(f"File '{uploaded_file.name}' already exists. It will be overwritten.")
        
        # Save the file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"✅ Uploaded {uploaded_file.name}")
        
        # Trigger re-ingestion
        if st.button("🔄 Re-ingest Documents", key="reingest"):
            with st.spinner("Re-ingesting documents..."):
                # Import here to avoid circular imports
                from app import CampusGuideApp
                app = CampusGuideApp()
                app.ingest_documents()
                st.success("✅ Documents re-ingested successfully!")
                st.rerun()
