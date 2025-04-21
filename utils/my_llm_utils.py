import os
from dotenv import load_dotenv

from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI

from urllib.parse import urlparse

# Load environment variables
load_dotenv()

# Configuration - application settings
class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    USE_OPENAI = os.getenv("USE_OPENAI", "true").lower() == "true" # default to True
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3") # default model
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434") # default URL
    MAX_RETRIES = 3 # default retries
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Initialize LLMs
def get_llm():
    if Config.USE_OPENAI:  # Use OpenAI
        if not Config.OPENAI_API_KEY: # Check if API key is set
            raise ValueError("OpenAI API key not found") 
        return ChatOpenAI(api_key=Config.OPENAI_API_KEY, model="gpt-4o") # default to gpt-4o
    else: # Use Ollama
        return OllamaLLM(model=Config.OLLAMA_MODEL, base_url=Config.OLLAMA_URL) 
    

def summarize_text(text):
    prompt = "Summarize the following AI partnership announcement in one sentence:"

    if Config.USE_OPENAI:
        llm = get_llm()
        response = llm.invoke(prompt + "\n" + text)
        response = response.content
    else:
        llm = get_llm()     
        response = llm.invoke(prompt + "\n" + text)

    return response

# Validate Link (basic check)
def validate_link(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False