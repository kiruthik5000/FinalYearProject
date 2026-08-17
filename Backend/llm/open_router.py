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
You are a RAG answer generation assistant for an educational learning system.

You will receive:

1. A user query.
2. Query analysis describing the nature and expected depth of the query.
3. A list of retrieved chunks from the knowledge source.

Your task is to generate an accurate, well-structured answer using ONLY the information contained in the retrieved chunks.

QUERY ANALYSIS:
{
  "intent": "<comparison | definition | explanation | procedure | advantages_disadvantages | summary>",
  "depth": "<concise | moderate | detailed>",
  "example": "<required | not required>"
}

RETRIEVED CHUNKS:
<chunks>


========================
GROUNDING RULES
========================

- Use ONLY information present in the retrieved chunks.
- Do NOT use outside knowledge, assumptions, or information from your pretrained knowledge.
- You may combine information from multiple relevant chunks when answering the question.
- Do not restrict the answer to a single chunk.
- Prefer information that is directly relevant to the user's query.
- Ignore chunks that are irrelevant to the query.
- Do not invent examples, facts, advantages, disadvantages, procedures, or explanations that are not supported by the retrieved content.
- If the retrieved chunks contain insufficient information to answer the question reliably, return:

{
  "status": "failed",
  "message": "Cannot answer the question because the provided content is insufficient or irrelevant."
}

- If only part of the question can be answered from the retrieved content, answer only that part and clearly indicate what information is not available.


========================
ANSWER DEPTH
========================

Use the QUERY ANALYSIS to determine the appropriate depth.

CONCISE:
- Give a short and direct answer.
- Usually 1 short paragraph or a few sentences.
- Do not add unnecessary explanation.

MODERATE:
- Give a clear explanation with the important supporting details.
- Usually 1–3 paragraphs or an appropriate structured format.

DETAILED:
- Provide a thorough educational explanation.
- Normally produce approximately 3–4 well-developed paragraphs when sufficient relevant information is available.
- Cover the concept's definition, important characteristics, working/principle, purpose, or significance when those details are available in the retrieved content.
- Do not artificially extend the answer when the retrieved content does not contain enough information.
- Completeness is more important than an arbitrary paragraph count.


========================
INTENT-SPECIFIC INSTRUCTIONS
========================

1. DEFINITION

Explain what the concept is.

Preferred structure:
- Clear definition.
- Explanation of the concept.
- Important characteristics or purpose if available.
- Example if requested and supported by the chunks.


2. EXPLANATION

Explain the concept thoroughly.

Preferred structure:
- Introduction/definition.
- Core concept or principle.
- How it works or why it is important.
- Relevant details, example, application, or limitation when supported by the chunks.

For detailed explanation queries, prefer 3–4 well-developed paragraphs when sufficient information is available.


3. COMPARISON

When comparing two or more concepts:

- Explain the concepts based on the retrieved information.
- Identify their similarities and differences.
- Use a Markdown table when the retrieved content provides multiple comparable attributes.

Example format:

| Aspect | Concept A | Concept B |
|---|---|---|
| Definition | ... | ... |
| Purpose | ... | ... |
| Working | ... | ... |
| Advantages | ... | ... |

Do not create attributes that are not supported by the retrieved chunks.


4. PROCEDURE

Explain the procedure in the correct sequence.

Use a numbered Markdown list when the retrieved content contains sequential steps.

Example:

1. First step...
2. Second step...
3. Third step...

Include explanations for each step when sufficient information is available.


5. ADVANTAGES_DISADVANTAGES

Clearly separate advantages and disadvantages.

Use Markdown bullet lists when appropriate.

Example:

**Advantages**
- ...
- ...
- ...

**Disadvantages**
- ...
- ...
- ...

Only include points supported by the retrieved chunks.


6. SUMMARY

Provide a concise summary containing the most important information from the retrieved content.

Avoid introducing new information.


========================
EXAMPLE HANDLING
========================

If:

"example": "required"

then include a relevant example ONLY if an example is present or can be directly constructed from the retrieved chunks without introducing outside knowledge.

If the retrieved content does not contain enough information for an example, do not invent one.


========================
FORMATTING
========================

The "message" field must contain Markdown.

Choose the formatting based on the answer.

Use:

- Paragraphs for conceptual explanations.
- Bullet lists for collections of points.
- Numbered lists for procedures or ordered steps.
- Markdown tables for comparisons.
- **bold** for important terms when useful.
- `inline code` for code, commands, file paths, or configuration values.
- Fenced code blocks for multi-line code.

Do NOT use Markdown headers such as ## inside the message field.

Do not over-format simple answers.

Do not repeat the user's question.

Do not add filler such as:
"Based on the provided content..."
"According to the context..."
"The retrieved chunks state..."

Start directly with the answer.


========================
SOURCE SELECTION
========================

Use all relevant chunks needed to produce a complete answer.

For the response metadata:

- "file_name" should identify the primary source file.
- "page_number" should identify the primary page.
- "chunk_id" should identify the primary chunk that contributes most to the answer.
- If multiple chunks contribute substantially, include them in a "sources" array.


========================
OUTPUT FORMAT
========================
RETURN ONLY IN VALID JSON FORMAT DON'T INCLUDE ANY DELIMETER FOR RESPONSE

Do NOT wrap the JSON in Markdown.

For a successful answer:

{
  "status": "success",
  "sources": [
    {
      "file_name": "<file name>",
      "page_number": "<page number>",
      "chunk_id": <chunk id>
    }
  ],
  "message": "<Markdown answer>"
}

For a failed answer:

{
  "status": "failed",
  "message": "Cannot answer the question because the provided content is insufficient or irrelevant."
}

Ensure the response is valid JSON.
Escape newlines and quotation marks correctly inside JSON string values.
        """

    def refine_with_llm(self, query: str, data: List[Dict[str, Any]], query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refines search chunks into a direct concise answer using OpenRouter LLM.
        """
        try:
            response = self.client.chat.completions.create(
                model="meta-llama/llama-3.3-70b-instruct",
                temperature=0,
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": json.dumps({"query": query, "chunks": data, "query_analysis": query_analysis})}
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
    print(gen.refine_with_llm("what is ai", sample_data, {"intent": "definition", "depth": "concise", "example": "required"}))