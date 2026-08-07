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
          "message": "<clear and concise answer>"
        }

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