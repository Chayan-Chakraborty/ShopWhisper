import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def generate_answer(context: str, query: str) -> str:
    prompt = f"Answer the question based on the context below:\n\n{context}\n\nQuestion: {query}\nAnswer:"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']
