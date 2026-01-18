import streamlit as st
from typing import List, Dict, Any
from config.config import Config


class ChatUI:
    def __init__(self):
        self.config = Config()
        self.query_callback = None

    def set_query_callback(self, callback):
        """Set the callback function for processing queries."""
        self.query_callback = callback

    def render_chat_interface(self, role: str):
        """
        Render the main chat interface.

        Args:
            role: Selected user role
        """
        st.title("💬 Ask CampusGuide")
        st.markdown(f"*Role: {role.title()}*")

        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Display chat history
        self._display_chat_history()

        # Chat input
        self._render_chat_input(role)

    def _display_chat_history(self):
        """Display the conversation history."""
        for message in st.session_state.chat_history[-self.config.MAX_CHAT_HISTORY :]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                # Display sources if available
                if "sources" in message and message["sources"]:
                    self._display_sources(message["sources"])

    def _render_chat_input(self, role: str):
        """Render the chat input area."""
        if prompt := st.chat_input("Ask a question about ICFAI University policies..."):
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": prompt})

            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("Searching documents..."):
                    # This will be handled by the main app
                    response_data = self._get_response(prompt, role)

                    st.markdown(response_data["answer"])

                    if response_data.get("sources"):
                        self._display_sources(response_data["sources"])

                    # Add to history
                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": response_data["answer"],
                            "sources": response_data.get("sources", []),
                        }
                    )

    def _get_response(self, prompt: str, role: str) -> Dict[str, Any]:
        """
        Get response from the RAG system via callback.

        Args:
            prompt: User query
            role: User role

        Returns:
            Response data with answer and sources
        """
        if self.query_callback:
            return self.query_callback(prompt, role)
        else:
            return {
                "answer": "System not initialized. Please check your configuration.",
                "sources": [],
            }

    def _display_sources(self, sources: List[Dict[str, Any]]):
        """
        Display source citations.

        Args:
            sources: List of source information
        """
        with st.expander("📚 Sources", expanded=False):
            for i, source in enumerate(sources, 1):
                st.markdown(f"**Source {i}:** {source.get('filename', 'Unknown')}")
                if "pages" in source and source["pages"]:
                    st.markdown(f"*Pages: {', '.join(map(str, source['pages']))}*")
                if "excerpt" in source:
                    st.markdown(f"```\n{source['excerpt'][:200]}...\n```")
                st.markdown("---")

    def display_error(self, error_message: str):
        """
        Display an error message.

        Args:
            error_message: Error message to display
        """
        st.error(f"❌ {error_message}")

    def display_warning(self, warning_message: str):
        """
        Display a warning message.

        Args:
            warning_message: Warning message to display
        """
        st.warning(f"⚠️ {warning_message}")

    def display_success(self, success_message: str):
        """
        Display a success message.

        Args:
            success_message: Success message to display
        """
        st.success(f"✅ {success_message}")
