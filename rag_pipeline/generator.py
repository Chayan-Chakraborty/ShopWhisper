from openai import OpenAI
from config import OPENAI_API_KEY
import json

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_answer(context: str, query: str) -> str:
    prompt = f"""
You are a structured information extractor.

Given the context below and the question, extract the complete product information and return a JSON object.

Make sure to include all relevant fields for each product, such as:
- name, type, properties, wood_type, thickness, dimensions, color, price, brand, eco_friendly, fire_resistant, termite_resistant, recommended_for, rating, discount, stock.

Return only a valid JSON object inside a dictionary with the key "products", like this:

{{
  "products": [
    {{
      "name": "...",
      "type": "...",
      ...
    }},
    ...
  ]
}}

Use proper JSON formatting with double quotes and numeric values as numbers (no commas in numbers).

Context:
{context}

Question: {query}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    raw_text = response.choices[0].message.content.strip()

    try:
        # Parse and re-dump to enforce valid JSON formatting (double quotes, etc.)
        parsed = json.loads(raw_text)
        return json.dumps(parsed, indent=2)
    except json.JSONDecodeError:
        # If not parseable, return raw text for debugging
        return json.dumps({"error": "Could not parse JSON", "raw_response": raw_text}, indent=2)
