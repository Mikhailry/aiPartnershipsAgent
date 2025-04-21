from tavily import TavilyClient
import os

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_MAX_RESULTS = int(os.getenv("TAVILY_MAX_RESULTS", 1))  # Default to 1 if not set

def search_tavily(query, max_results=TAVILY_MAX_RESULTS):
    """
    Search Tavily for a given query.
    
    Args:
        query (str): The search query.
    
    Returns:
        dict: The response from Tavily API.
    """
    if not TAVILY_API_KEY:
        raise ValueError("Tavily API key not found")

    # Initialize Tavily client
    tavily_client = TavilyClient(TAVILY_API_KEY)
    search_response = tavily_client.search(query, max_results=max_results)
    return search_response
