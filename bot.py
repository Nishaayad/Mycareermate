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
    prompt =   prompt = f"""
You are a friendly and helpful AI career mentor. Based on the user's question below, give a simple and clear answer in a human tone.

1. Start with a warm sentence that makes the user feel supported.
2. Suggest 2–3 career paths that match their interest.
3. Mention 2 easy-to-start skills or tools to focus on.
4. Keep the language short, positive, and beginner-friendly.

User: {query}
"""

    try:
        response = chat_model.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error: {str(e)}"
