import openai

openai.api_key = "your_openai_api_key"

def get_embedding(text: str, model="text-embedding-3-small"):
    response = openai.embeddings.create(input=[text], model=model)
    return response.data[0].embedding
