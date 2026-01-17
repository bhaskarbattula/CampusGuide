from typing import List, Dict, Any


class PromptTemplates:
    @staticmethod
    def get_answer_generation_prompt(query: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Generate the prompt for answer generation using retrieved context.

        Args:
            query: User query
            chunks: Retrieved document chunks

        Returns:
            Formatted prompt string
        """
        # Build context from chunks
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get("metadata", {})
            pages = chunk.get("pages", [])
            filename = metadata.get("filename", "Unknown document")

            context_part = f"[Document {i}: {filename}"
            if pages:
                context_part += f", Pages: {', '.join(map(str, pages))}"
            context_part += f"]\n{chunk['text']}\n"

            context_parts.append(context_part)

        context = "\n".join(context_parts)

        prompt = f"""You are CampusGuide, an AI assistant for ICFAI University students, faculty, and staff.

Your task is to answer questions using ONLY the provided document context. You must NEVER use external knowledge, assumptions, or information not present in the given documents.

INSTRUCTIONS:
1. Answer questions strictly based on the provided context
2. If the context does not contain sufficient information to answer the question, respond with exactly: "The requested information is not available in the provided documents."
3. Cite specific documents and page numbers for every piece of information
4. Do not make assumptions or inferences beyond what's explicitly stated
5. Be concise but complete in your answers
6. If asked about topics not covered in the documents, refuse to answer

CONTEXT:
{context}

QUESTION: {query}

ANSWER:"""

        return prompt

    @staticmethod
    def get_grounding_validation_prompt(
        answer: str, chunks: List[Dict[str, Any]]
    ) -> str:
        """
        Generate prompt for validating if answer is grounded in context.

        Args:
            answer: Generated answer
            chunks: Retrieved document chunks

        Returns:
            Validation prompt
        """
        context = "\n".join([chunk["text"] for chunk in chunks])

        prompt = f"""Validate if the following ANSWER is fully grounded in the provided CONTEXT.

CONTEXT:
{context}

ANSWER:
{answer}

VALIDATION RULES:
- Every factual statement in the answer must be directly supported by the context
- No assumptions or external knowledge allowed
- Check for hallucinations or unsupported claims

Respond with only "VALID" if the answer is fully grounded, or "INVALID" with specific reasons if not."""

        return prompt
