from typing import List, Dict, Any, Optional
from openai import OpenAI
from config.config import Config
from llm.prompt_templates import PromptTemplates


class AnswerGenerator:
    def __init__(self):
        self.config = Config()
        self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)
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

            answer = response.choices[0].message.content.strip()

            # Post-process answer to ensure it follows rules
            answer = self._post_process_answer(answer)

            return answer

        except Exception as e:
            return f"Error generating answer: {str(e)}"

    def validate_grounding(self, answer: str, chunks: List[Dict[str, Any]]) -> bool:
        """
        Validate if the answer is properly grounded in the context.

        Args:
            answer: Generated answer
            chunks: Retrieved document chunks

        Returns:
            True if answer is grounded, False otherwise
        """
        if (
            not chunks
            or answer
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
            print(f"Grounding validation failed: {str(e)}")
            return False

    def _post_process_answer(self, answer: str) -> str:
        """
        Post-process the generated answer to ensure compliance.

        Args:
            answer: Raw generated answer

        Returns:
            Processed answer
        """
        # Remove any attempts to use external knowledge
        if "based on my knowledge" in answer.lower() or "generally" in answer.lower():
            return (
                "The requested information is not available in the provided documents."
            )

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
