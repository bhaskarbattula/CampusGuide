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

    # --------------------------------------------------
    # Main chat interface
    # --------------------------------------------------
    def render_chat_interface(self, role: str):
        st.title("💬 Ask CampusGuide")
        st.markdown(f"*Role: {role.title()}*")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        self._display_chat_history()
        self._render_chat_input(role)

    # --------------------------------------------------
    # Chat history
    # --------------------------------------------------
    def _display_chat_history(self):
        for message in st.session_state.chat_history[-self.config.MAX_CHAT_HISTORY :]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                if message.get("sources"):
                    self._display_sources(message["sources"])
                elif message.get("source_note"):
                    self._display_source_note(message["source_note"])

    # --------------------------------------------------
    # Chat input
    # --------------------------------------------------
    def _render_chat_input(self, role: str):
        if prompt := st.chat_input("Ask a question about ICFAI University policies..."):
            # Store user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Searching documents..."):
                    response = self._get_response(prompt, role)

                    # Display answer
                    st.markdown(response["answer"])

                    # Display sources OR refusal explanation
                    if response.get("sources"):
                        self._display_sources(response["sources"])
                    elif response.get("source_note"):
                        self._display_source_note(response["source_note"])

                    # Save assistant response
                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": response["answer"],
                            "sources": response.get("sources", []),
                            "source_note": response.get("source_note"),
                        }
                    )

    # --------------------------------------------------
    # Callback to backend
    # --------------------------------------------------
    def _get_response(self, prompt: str, role: str) -> Dict[str, Any]:
        if self.query_callback:
            return self.query_callback(prompt, role)

        return {
            "answer": "System not initialized. Please check configuration.",
            "sources": [],
        }

    # --------------------------------------------------
    # Document sources display
    # --------------------------------------------------
    def _display_sources(self, sources: List[Dict[str, Any]]):
        with st.expander("📚 Sources", expanded=False):
            for i, source in enumerate(sources, 1):
                filename = source.get("filename", "Unknown document")
                lines = source.get("lines", [])  # Changed from 'pages' to 'lines'
                excerpt = source.get("excerpt", "")

                st.markdown(f"**Source {i}: {filename}**")

                if lines:
                    st.markdown(f"*Lines: {', '.join(map(str, lines))}*")

                if excerpt:
                    st.markdown(f"```\n{excerpt[:300]}\n```")

                if i < len(sources):
                    st.markdown("---")

    # --------------------------------------------------
    # Refusal / explanation display
    # --------------------------------------------------
    def _display_source_note(self, note: str):
        st.markdown("### 📚 Sources")
        st.info(note)
