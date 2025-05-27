import os
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA

load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")

chat_model = ChatNVIDIA(
    model="mistralai/mistral-7b-instruct-v0.3", 
    api_key=api_key
)

def carrermate_aibot(query):
    prompt = f"""
You are an AI career guide. Based on the user's query below, give a short and helpful career suggestion with 2–3 job roles and 2 skills to focus on:

User query: {query}
"""

    try:
        response = chat_model.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error: {str(e)}"
