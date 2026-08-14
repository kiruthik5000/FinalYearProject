import json
import os
import logging
from typing import Any, Dict, List
from openai import OpenAI
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Generator:

    def __init__(self):
        load_dotenv()
        api_key = os.getenv("OR_API_KEY")
        if not api_key:
            logger.warning("OR_API_KEY environment variable is not set!")

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.prompt = """
        You are a RAG answer generation assistant.

        You will receive:
        1. A user query.
        2. A list of retrieved chunks.

        Rules:
        - Use ONLY the provided chunks.
        - Never use outside knowledge.
        - If none of the chunks answer the question, return:
        {
          "status": "failed",
          "message": "Cannot answer the question because the provided content is irrelevant."
        }
        - Otherwise choose the single most relevant chunk and return:
        {
          "status": "success",
          "file_name": "file name of the chunk_id chosen",
          "page_number": "page_number of the chunk_id chosen",
          "chunk_id": <number>,
          "message": "<answer, length and depth determined by the rules below>"
        }

        Answer depth rules for the "message" field:
        - Match the depth of the answer to the depth of the question and the amount of relevant content available in the chunk — do not default to a short answer when the chunk has more to offer.
        - If the query asks the model to "explain", "describe in detail", "elaborate", "walk through", or similar, or if the query is inherently conceptual (asking what something is, how it works, why it happens) — give a full, thorough answer. Use everything relevant in the chosen chunk. Do not compress it into 1-3 lines. Cover: what it is, how it works or why it matters, and any relevant detail, example, or nuance present in the chunk.
        - If the query asks for a specific fact, number, date, name, or a direct yes/no — a short, precise answer is correct. Do not pad these with unnecessary elaboration just to appear thorough.
        - If the query is ambiguous about depth, default to a moderately detailed answer (a short paragraph, not a one-liner) rather than the shortest possible answer.
        - Never omit relevant information from the chunk just to keep the message short. Brevity is not the goal — accuracy and completeness relative to the chunk content is the goal.
        - Do not repeat the question back or add filler like "Based on the provided content...". Go straight into the answer.

        Formatting rules for the "message" field:
        - Write the message as Markdown, but scale formatting to the content — don't over-format simple answers.
        - If the answer is a short fact or one-liner, write it as a plain sentence. No headers, no bullets, no bold.
        - If the answer is detailed and covers multiple points, steps, or aspects, break it into a short paragraph plus a bullet or numbered list where it improves readability.
        - If the answer involves code, commands, file paths, or config values, wrap them in backticks (inline `code`) or fenced code blocks with a language tag if it's a multi-line snippet.
        - Use **bold** only for a genuinely key term or number the user needs to notice — not decoratively.
        - Never use headers (##) inside the message field — it's a chat bubble, not a document.
        - The message must still be a single valid JSON string value — escape any newlines as \\n and quotes as \\" so the JSON stays valid.

        Return ONLY valid JSON.
        Do not wrap the JSON in markdown.
        """

    def refine_with_llm(self, query: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Refines search chunks into a direct concise answer using OpenRouter LLM.
        """
        try:
            response = self.client.chat.completions.create(
                model="meta-llama/llama-3.3-70b-instruct",
                temperature=0,
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": json.dumps({"query": query, "chunks": data})}
                ]
            )

            text = response.choices[0].message.content.strip()

            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()

            return json.loads(text)

        except json.JSONDecodeError as e:
            logger.error(f"Model returned non-JSON text: {text} | Error: {e}")
            return {
                "status": "failed",
                "message": "Model returned invalid JSON format."
            }

        except Exception as e:
            logger.error(f"LLM API Error during answer refinement: {e}", exc_info=True)
            return {
                "status": "failed",
                "message": str(e)
            }


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    gen = Generator()
    sample_data = [
        {"chunk_id": 1, "content": "AI is an emerging technology in the software industry."},
        {"chunk_id": 2, "content": "Lions live in prides across Africa."}
    ]
    print(gen.refine_with_llm("what is ai", sample_data))