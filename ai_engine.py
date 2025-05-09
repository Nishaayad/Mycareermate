# ai_engine.py

import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()  # Load Hugging Face API Key

hf_token = os.getenv("HUGGINGFACE_API_KEY")

# Connect to the Hugging Face Inference Client
client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.1",
    token=hf_token
)

def generate_response(prompt):
    try:
        response = client.text_generation(
            prompt,
            max_new_tokens=300,
            temperature=0.7
        )
        return response
    except Exception as e:
        print("❌ AI Error:", str(e))
        return "Error generating response. Please try again later."
