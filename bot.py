import os
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA

load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")

chat_model = ChatNVIDIA(
    model="mistralai/mistral-7b-instruct-v0.3",  # Make sure the model name is correct
    api_key=api_key
)

def carrermate_aibot(query):
    prompt = f"Answer the following user query clearly and concisely:\n{query}"
    try:
        response = chat_model.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error: {str(e)}"
