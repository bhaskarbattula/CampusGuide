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

        return role
