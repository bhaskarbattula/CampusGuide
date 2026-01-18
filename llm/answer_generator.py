from typing import List, Dict, Any, Optional
from openai import OpenAI
from config.config import Config
from llm.prompt_templates import PromptTemplates


class AnswerGenerator:
    def __init__(self):
        self.config = Config()
        self.client = OpenAI(
            api_key=self.config.API_KEY, base_url=self.config.API_BASE_URL
        )
        self.prompt_templates = PromptTemplates()

    def generate_answer(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Generate an answer using retrieved context.

        Args:
            query: User query
            chunks: Retrieved document chunks

        Returns:
            Generated answer
        """
        if not chunks:
            return (
                "The requested information is not available in the provided documents."
            )

        # Validate chunks contain valid text content
        valid_chunks = []
        for chunk in chunks:
            text = chunk.get("text", "")
            if text and isinstance(text, str):
                text = text.strip()
                if len(text) > 10:  # Relaxed validation for policy content
                    valid_chunks.append(chunk)

        if not valid_chunks:
            return (
                "The requested information is not available in the provided documents."
            )

        chunks = valid_chunks  # Use only valid chunks

        prompt = self.prompt_templates.get_answer_generation_prompt(query, chunks)

        try:
            response = self.client.chat.completions.create(
                model=self.config.LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based only on provided context.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self.config.LLM_TEMPERATURE,
                max_tokens=1000,
            )

            if response.choices and len(response.choices) > 0:
                raw_answer = response.choices[0].message.content
                if raw_answer:
                    answer = raw_answer.strip()
                else:
                    answer = "The requested information is not available in the provided documents."
            else:
                answer = "API returned no choices in response."

            # Post-process answer to ensure it follows rules
            answer = self._post_process_answer(answer)

            return answer

        except Exception as e:
            print(
                f"DEBUG: API call failed with exception: {type(e).__name__}: {str(e)}"
            )
            return (
                "The requested information is not available in the provided documents."
            )

    def validate_grounding(self, answer: str, chunks: List[Dict[str, Any]]) -> bool:
        """
        Validate if the answer is properly grounded in the context.

        Args:
            answer: Generated answer
            chunks: Retrieved document chunks

        Returns:
            True if answer is grounded, False otherwise
        """
        if not chunks or (
            answer
            and answer.strip()
            == "The requested information is not available in the provided documents."
        ):
            return True  # Refusal is always valid

        prompt = self.prompt_templates.get_grounding_validation_prompt(answer, chunks)

        try:
            response = self.client.chat.completions.create(
                model=self.config.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,  # Deterministic validation
                max_tokens=200,
            )

            validation_result = response.choices[0].message.content.strip().upper()

            return "VALID" in validation_result

        except Exception as e:
            error_msg = str(e)
            if "API key" in error_msg.lower():
                return "❌ API Key Error: Please check your xAI API key in the .env file. Get a key from https://console.x.ai"
            else:
                print(f"API call failed: {error_msg}")
                return "The requested information is not available in the provided documents."

        # Ensure answer doesn't contradict grounding rules
        forbidden_phrases = [
            "I believe",
            "I think",
            "probably",
            "likely",
            "typically",
            "usually",
            "in my experience",
            "as far as I know",
        ]

        answer_lower = answer.lower()
        for phrase in forbidden_phrases:
            if phrase in answer_lower:
                return "The requested information is not available in the provided documents."

        return answer.strip()

    def _is_valid_chunk_text(self, text: str) -> bool:
        """
        Validate that chunk text contains meaningful policy content.

        Args:
            text: Text to validate

        Returns:
            True if text contains valid policy information
        """
        if not text or len(text) < 10:
            return False

        text_lower = text.lower()

        # Check for error messages or invalid content
        invalid_patterns = [
            "cannot read",
            "model does not support",
            "this model does not support image input",
            "error",
            "failed",
            "screenshot",
            "image file",
        ]

        for pattern in invalid_patterns:
            if pattern in text_lower:
                return False

        # For policy documents, be more lenient with special characters
        # Allow policy-specific characters like %, $, etc.
        special_chars = sum(
            1
            for char in text
            if not char.isalnum() and not char.isspace() and char not in ".,!?-()$%/&"
        )
        if special_chars > len(text) * 0.6:  # Allow more special chars for policy text
            return False

        # Must contain some policy-relevant keywords
        policy_keywords = [
            "student",
            "offer",
            "placement",
            "policy",
            "company",
            "recruitment",
            "eligible",
            "allowed",
            "must",
            "shall",
        ]
        has_policy_content = any(keyword in text_lower for keyword in policy_keywords)

        return has_policy_content
