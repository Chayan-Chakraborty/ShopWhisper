from openai import OpenAI
from config import OPENAI_API_KEY
import os

# Print debug information
print("Environment variables:")
print(f"OPENAI_API_KEY in env: {os.getenv('OPENAI_API_KEY')[:10] if os.getenv('OPENAI_API_KEY') else 'Not set'}")
print(f"OPENAI_API_KEY from config: {OPENAI_API_KEY[:10]}")

# Create a global OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY) 