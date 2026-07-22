import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("Listing models that support embedContent:")
for model in client.models.list():
    if "embedContent" in model.supported_generation_methods:
        print(model.name)
