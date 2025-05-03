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
def get_llm(use_openai: bool = None, model_name: str = None, base_url: str = None):
    """
    Get an LLM instance based on specified parameters.
    
    Args:
        use_openai (bool, optional): Whether to use OpenAI. If None, uses Config.USE_OPENAI
        model_name (str, optional): 
            - For OpenAI: model name (e.g., "gpt-4", "gpt-3.5-turbo")
            - For Ollama: model name (e.g., "llama2", "mistral", "phi")
        base_url (str, optional): Base URL for Ollama. If None, uses Config.OLLAMA_URL
    
    Returns:
        LLM instance (ChatOpenAI or OllamaLLM)
    """
    # Use provided parameters or fall back to config values
    use_openai = use_openai if use_openai is not None else Config.USE_OPENAI
    base_url = base_url or Config.OLLAMA_URL
    
    if use_openai:  # Use OpenAI
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found")
        # Use provided model name or default to gpt-4
        model = model_name or "gpt-4"
        return ChatOpenAI(api_key=Config.OPENAI_API_KEY, model=model)
    else:  # Use Ollama
        # Use provided model name or fall back to config
        model = model_name or Config.OLLAMA_MODEL
        return OllamaLLM(model=model, base_url=base_url)

def summarize(prompt, text):
    
    if prompt is None:
        prompt = f"""
        Summarize the following text:
        """

    if Config.USE_OPENAI:
        llm = get_llm()
        response = llm.invoke(prompt + "\n" + text)
        response = response.content
    else:
        llm = get_llm()     
        response = llm.invoke(prompt + "\n" + text)

    return response  


def summarize_text_partnership(text, partner1, partner2):
    prompt = f"""
    Summarize the following AI partnership announcement in one sentence:
    {partner1} and {partner2}
    {text}
    """

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