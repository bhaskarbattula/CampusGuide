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
1. Synthesize information from ALL provided context chunks to create a complete answer
2. Combine related policy rules from different chunks into a coherent explanation
3. Present the answer in clear, student-friendly bullet points
4. Only refuse with "The requested information is not available in the provided documents." if NO chunks contain relevant policy information
5. For policy questions, summarize and organize the rules, restrictions, and procedures mentioned across the chunks
6. Cite the document name and page numbers for each piece of information

CONTEXT:
{context}

QUESTION: {query}

Provide a comprehensive answer based on all the context chunks above. Format your response as bullet points explaining the policy rules and procedures.

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
