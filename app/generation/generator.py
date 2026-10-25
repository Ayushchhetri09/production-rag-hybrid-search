import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


class RAGGenerator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set in the .env file."
            )

        self.client = genai.Client(api_key=api_key)

        self.model = "gemini-3.6-flash"

    def generate(self, query: str, results: list[dict]) -> str:

        # Build context from retrieved documents
        context_parts = []

        for i, result in enumerate(results, start=1):
            chunk = result["chunk"]

            context_parts.append(
                f"""
SOURCE {i}
Document: {chunk['source']}
Page: {chunk['page']}

{chunk['text']}
"""
            )

        context = "\n".join(context_parts)

        # Prompt for Gemini
        prompt = f"""
You are a helpful question-answering assistant.

Answer the user's question using ONLY the provided context.

If the answer cannot be determined from the context,
say that the information is not available in the provided
documents.

Do not invent facts.

Cite the relevant source page in your answer.

USER QUESTION:
{query}

CONTEXT:
{context}

ANSWER:
"""

        # Generate answer
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                ),
            )

            return response.text

        # Handle Gemini quota/rate-limit errors
        except Exception as e:
            error_text = str(e)

            if (
                "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
            ):
                raise RuntimeError(
                    "Gemini API quota has been reached. "
                    "Please wait for the quota to reset "
                    "or check your Gemini API plan."
                ) from e

            # Handle temporary Gemini server problems
            if (
                "503" in error_text
                or "UNAVAILABLE" in error_text
            ):
                raise RuntimeError(
                    "Gemini is temporarily unavailable. "
                    "Please try again in a moment."
                ) from e

            # Pass other unexpected errors upward
            raise