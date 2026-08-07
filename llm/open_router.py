import json
import os
from typing import Any, Dict
from openai import OpenAI
from dotenv import load_dotenv

class Generator:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OR_API_KEY")
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
          "chunk_id": <number>,
          "message": "<clear and concise answer>"
        }

        Return ONLY valid JSON.
        Do not wrap the JSON in markdown.
        """

    def refine_with_llm(self, query, data):

        try:

            response = self.client.chat.completions.create(
                model="meta-llama/llama-3.3-70b-instruct",
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": self.prompt
                    },
                    {
                        "role": "user",
                        "content": json.dumps({
                            "query": query,
                            "chunks": data
                        })
                    }
                ]
            )

            text = response.choices[0].message.content.strip()

            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()

            return json.loads(text)

        except json.JSONDecodeError:
            return {
                "status": "failed",
                "message": "Model returned invalid JSON."
            }

        except Exception as e:
            return {
                "status": "failed",
                "message": str(e)
            }

if __name__ == '__main__':
    gen = Generator()
    data = [
        {"chunk_id": 1, "content": "AI is one of the emerging technolog in the software industry and it impacts in the feilds like IT, robotics, Medical"},
        {"chunk_id": 2, "content": "Lion is also known as the king of jungle, Lion is mostly living in the south africa due to its hot weather it suffers a lot"}
    ]
    print(gen.refine_with_llm("what is ai", data))
    print(gen.refine_with_llm("explain lion", data))