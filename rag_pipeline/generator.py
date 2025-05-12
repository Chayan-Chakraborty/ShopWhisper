from openai import OpenAI
from config import OPENAI_API_KEY
import json

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_answer(context: str, query: str) -> dict:
    prompt = f"""
You are a structured information extractor.

Given the context below and the question, extract the complete product information and return a JSON object.

Make sure to include all relevant fields for each product, such as:
- name, type, properties, wood_type, thickness, dimensions, color, price, brand, eco_friendly, fire_resistant, termite_resistant, recommended_for, rating, discount, stock.

Respond only in a valid JSON object with proper formatting (use numbers for price, rating, and stock).

Context:
{context}

Question: {query}
Return only a valid JSON object.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Try to parse the response into JSON (optional)
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return {"error": "Could not parse JSON", "raw_response": response.choices[0].message.content}
