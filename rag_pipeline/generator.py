from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_answer(context: str, query: str) -> dict:
    prompt = f"""
You are a structured information extractor.

Given the context below and the question, extract only the required information and return a JSON object.

Respond in strict JSON format with keys and values based on the query.

Context:
{context}

Question: {query}
Return only a JSON object.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Try to parse the response into JSON (optional)
    import json
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return {"error": "Could not parse JSON", "raw_response": response.choices[0].message.content}
