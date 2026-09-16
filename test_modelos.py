import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

print("Tus modelos disponibles para generar texto son:")
for model in client.models.list():
    # Filtramos solo los modelos que soportan generación de contenido
    if 'generateContent' in model.supported_actions:
        print(f"- {model.name}")