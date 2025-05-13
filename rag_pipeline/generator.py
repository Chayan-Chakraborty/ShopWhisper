from openai import OpenAI
from config import OPENAI_API_KEY
import json
from pydantic import BaseModel
from typing import List, Optional

client = OpenAI(api_key=OPENAI_API_KEY)

class Product(BaseModel):
    ID: str
    name: str
    type: str
    properties: List[str]
    wood_type: str
    thickness: str
    dimensions: str
    color: str
    price: float
    brand: str
    eco_friendly: bool
    fire_resistant: bool
    termite_resistant: bool
    recommended_for: List[str]
    rating: Optional[float]
    discount: Optional[str]
    stock: bool
    isSponsored: bool

def generate_answer(context: str, query: str) -> str:
    prompt = f"""
You are a structured information extractor.

Maintain consistent data types for each field.

Given the context below and the question, extract the complete product information and return a JSON object.

Ensure the following data types for each product field:
- "ID": string
- "name": string
- "type": string
- "properties": array of strings
- "wood_type": string
- "thickness": string
- "dimensions": string
- "color": string
- "price": number
- "brand": string
- "eco_friendly": boolean
- "fire_resistant": boolean
- "termite_resistant": boolean
- "recommended_for": array of strings
- "rating": number or null
- "discount": string or null (percent with % symbol)
- "stock": boolean (true if stock > 0, false if 0)
- "isSponsored": boolean

Return only a valid JSON object like this:

{{
  "products": [
    {{
      "ID": "1",
      "name": "BWP Marine Plywood 18mm",
      "type": "Plywood",
      "properties": ["Waterproof", "Termite-Proof"],
      "wood_type": "Hardwood",
      "thickness": 18,
      "dimensions": "8x4 ft",
      "color": "Brown",
      "price": 1650,
      "brand": "GreenPly",
      "eco_friendly": false,
      "fire_resistant": false,
      "termite_resistant": true,
      "recommended_for": ["Bathrooms", "Boats"],
      "rating": 4.7,
      "discount": "5%",
      "stock": true,
      "isSponsored": true
    }}
  ]
}}

Use valid JSON with double quotes and no trailing commas.

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
        parsed = json.loads(raw_text)
        return json.dumps(parsed, indent=2)
    except json.JSONDecodeError:
        return json.dumps({"error": "Could not parse JSON", "raw_response": raw_text}, indent=2)
