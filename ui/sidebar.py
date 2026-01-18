import streamlit as st
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
            st.subheader("📤 Upload Knowledge Files")
            uploaded_files = st.file_uploader(
                "Upload TXT files to add to knowledge base",
                type=["txt"],
                accept_multiple_files=True,
                help="Upload text files containing academic policies and guidelines",
            )

            if uploaded_files:
                # This will be handled in app.py
                st.session_state["uploaded_files"] = uploaded_files
                if st.button("Process Uploaded Files"):
                    st.rerun()

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
                vs_stats = stats.get("vector_store_stats", {})
                st.metric("Processed Chunks", vs_stats.get("total_chunks", 0))
                st.metric("Vector Store Size", vs_stats.get("index_size", 0))

            # Footer
            st.markdown("---")
            st.markdown("*Built with safety and accuracy in mind*")

        return role
