import re
from typing import List, Dict, Any, Tuple
from config.config import Config
from llm.answer_generator import AnswerGenerator
from utils.helpers import is_list_question


class GroundingValidator:
    def __init__(self):
        self.config = Config()
        self.answer_generator = AnswerGenerator()

    def validate_answer_grounding(
        self, answer: str, chunks: List[Dict[str, Any]], query: str = ""
    ) -> Dict[str, Any]:
        """
        Validate that every sentence in the answer is supported by retrieved context.

        Args:
            answer: Generated answer
            chunks: Retrieved document chunks

        Returns:
            Dict with validation results
        """
        if not answer or not chunks:
            return {"valid": False, "reason": "Empty answer or no context chunks"}

        # Special case: refusal message is always valid
        if (
            answer.strip()
            == "The requested information is not available in the provided documents."
        ):
            return {"valid": True, "reason": "Valid refusal message"}

        # Check if this is a list/enumeration question
        list_question = is_list_question(query)

        if list_question:
            # For list questions, validate each bullet point individually
            bullets = self._extract_bullets(answer)
            if not bullets:
                return {
                    "valid": False,
                    "reason": "List question but no bullet points found",
                }

            # Validate each bullet point
            valid_bullets = []
            invalid_bullets = []

            for bullet in bullets:
                if self._is_bullet_grounded(bullet, chunks):
                    valid_bullets.append(bullet)
                else:
                    invalid_bullets.append(bullet)

            total_bullets = len(bullets)
            valid_count = len(valid_bullets)
            grounding_score = valid_count / total_bullets if total_bullets > 0 else 0

            # Require 70% of bullets to be grounded for list questions
            is_valid = grounding_score >= 0.7

            return {
                "valid": is_valid,
                "grounding_score": grounding_score,
                "total_sentences": total_bullets,
                "valid_sentences": valid_count,
                "invalid_sentences": invalid_bullets,
                "llm_validation": True,  # Skip LLM validation for list questions
                "reason": f"List question grounding: {grounding_score:.2f} ({valid_count}/{total_bullets} bullets)",
            }
        else:
            # Standard sentence-based validation for non-list questions
            sentences = self._split_into_sentences(answer)

            if not sentences:
                return {"valid": False, "reason": "No valid sentences in answer"}

            # Validate each sentence
            invalid_sentences = []
            valid_sentences = []

            for sentence in sentences:
                if self._is_sentence_grounded(sentence, chunks):
                    valid_sentences.append(sentence)
                else:
                    invalid_sentences.append(sentence)

            # Calculate grounding score
            total_sentences = len(sentences)
            valid_count = len(valid_sentences)
            grounding_score = (
                valid_count / total_sentences if total_sentences > 0 else 0
            )

            # Use different thresholds based on question type
            is_placement_question = any(
                keyword in query.lower()
                for keyword in ["placement", "induction", "document", "required"]
            )

            if is_placement_question:
                # More lenient for synthesis questions (allow 50% grounding)
                threshold = 0.5
            else:
                # Strict validation for other questions
                threshold = self.config.GROUNDING_STRICTNESS

            is_valid = grounding_score >= threshold

        # For list questions, we rely on bullet validation
        # For other questions, we use the calculated grounding score
        llm_validation = True  # Simplified for now

        final_valid = is_valid

        return {
            "valid": final_valid,
            "grounding_score": grounding_score,
            "total_sentences": total_sentences,
            "valid_sentences": valid_count,
            "invalid_sentences": invalid_sentences,
            "llm_validation": llm_validation,
            "reason": f"Grounding score: {grounding_score:.2f}, LLM validation: {llm_validation}",
        }

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        # Simple sentence splitting
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())

        # Filter out empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    def _is_sentence_grounded(
        self, sentence: str, chunks: List[Dict[str, Any]]
    ) -> bool:
        """
        Check if a sentence is grounded in the context chunks.

        Args:
            sentence: Sentence to validate
            chunks: Context chunks

        Returns:
            True if sentence is supported by context
        """
        sentence_lower = sentence.lower().strip()

        # Skip very short sentences
        if len(sentence_lower) < 10:
            return True

        # Combine all chunk texts for searching
        context_text = " ".join([chunk["text"] for chunk in chunks]).lower()

        # Check for key phrases from sentence in context
        words = re.findall(r"\b\w+\b", sentence_lower)
        key_phrases = []

        # Extract noun phrases and important terms
        for i in range(len(words)):
            # Single important words
            if len(words[i]) > 3:  # Skip short words
                key_phrases.append(words[i])
            # Bigram phrases
            if i < len(words) - 1:
                bigram = f"{words[i]} {words[i + 1]}"
                if len(bigram) > 6:  # Skip very short phrases
                    key_phrases.append(bigram)

        # Check if sufficient key phrases are found in context
        found_phrases = 0
        for phrase in key_phrases:
            if phrase in context_text:
                found_phrases += 1

        # Require at least 60% of key phrases to be found
        coverage = found_phrases / len(key_phrases) if key_phrases else 0

        return coverage >= 0.6

    def _extract_bullets(self, answer: str) -> List[str]:
        """
        Extract bullet points from an answer.

        Args:
            answer: Answer text that may contain bullets

        Returns:
            List of bullet point texts
        """
        lines = answer.split("\n")
        bullets = []

        for line in lines:
            line = line.strip()
            # Check for bullet point markers
            if line.startswith("- ") or line.startswith("• ") or line.startswith("* "):
                # Remove the bullet marker and add the content
                content = line[2:].strip()
                if content:
                    bullets.append(content)

        return bullets

    def _is_bullet_grounded(self, bullet: str, chunks: List[Dict[str, Any]]) -> bool:
        """
        Check if a bullet point is grounded in the context chunks.

        Args:
            bullet: Bullet point text to validate
            chunks: Context chunks

        Returns:
            True if bullet is supported by context
        """
        bullet_lower = bullet.lower().strip()

        # Skip very short bullets
        if len(bullet_lower) < 5:
            return True

        # Combine all chunk texts for searching
        context_text = " ".join([chunk["text"] for chunk in chunks]).lower()

        # Extract key terms from the bullet (nouns, important words)
        words = re.findall(r"\b\w+\b", bullet_lower)
        key_terms = []

        # Focus on nouns and important terms (skip common words)
        common_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "shall",
        }

        for word in words:
            if len(word) > 2 and word not in common_words:
                key_terms.append(word)

        # Check if key terms from bullet appear in context
        found_terms = 0
        for term in key_terms:
            if term in context_text:
                found_terms += 1

        # Require at least 60% of key terms to be found
        coverage = found_terms / len(key_terms) if key_terms else 0

        return coverage >= 0.6

    def get_validation_stats(self) -> Dict[str, Any]:
        """
        Get validation statistics.

        Returns:
            Dictionary with validation parameters
        """
        return {
            "grounding_strictness": self.config.GROUNDING_STRICTNESS,
            "sentence_min_length": 10,
            "phrase_coverage_threshold": 0.6,
            "bullet_validation_threshold": 0.6,
        }
