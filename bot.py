import os
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA

# Load environment variables
load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")

# Initialize the NVIDIA chat model
chat_model = ChatNVIDIA(
    model="mistralai/mistral-7b-instruct-v0.3",  # Make sure the model name is correct
    api_key=api_key
)

# Define the chatbot response function
def carrermate_aibot(query):
    prompt = f"Answer the following user query clearly and concisely:\n{query}"
    try:
        response = chat_model.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error: {str(e)}"
