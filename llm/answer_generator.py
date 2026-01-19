from typing import List, Dict, Any
import os
from groq import Groq
from config.config import Config
from llm.prompt_templates import PromptTemplates
import logging

logger = logging.getLogger(__name__)


REFUSAL_TEXT = "The requested information is not available in the provided documents."


class AnswerGenerator:
    def __init__(self):
        self.config = Config()
        self.client = Groq(api_key=self.config.API_KEY)
        self.prompt_templates = PromptTemplates()

    def generate_answer(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        if not chunks:
            return REFUSAL_TEXT

        # Prepare grounded prompt
        prompt = self.prompt_templates.get_answer_generation_prompt(query, chunks)

        try:
            response = self.client.chat.completions.create(
                model=self.config.LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an academic policy assistant. "
                            "Answer ONLY using the provided context. "
                            "If the context does not explicitly contain the answer, "
                            "say the information is not available."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self.config.LLM_TEMPERATURE,
                max_tokens=700,
            )

            answer = response.choices[0].message.content.strip()

            return self._post_process_answer(answer)

        except Exception as e:
            print(f"Groq API error: {e}")
            return REFUSAL_TEXT

    def _post_process_answer(self, answer: str) -> str:
        if not answer:
            return REFUSAL_TEXT

        forbidden = [
            "i think",
            "probably",
            "usually",
            "generally",
            "in my opinion",
        ]

        lower = answer.lower()
        if any(word in lower for word in forbidden):
            return REFUSAL_TEXT

        return answer.strip()
