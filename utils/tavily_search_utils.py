from tavily import TavilyClient
import os

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_MAX_RESULTS = int(os.getenv("TAVILY_MAX_RESULTS", 1))  # Default to 1 if not set

# def search_tavily(query, max_results=TAVILY_MAX_RESULTS):
#     """
#     Search Tavily for a given query.
    
#     Args:
#         query (str): The search query.
    
#     Returns:
#         dict: The response from Tavily API.
#     """
#     if not TAVILY_API_KEY:
#         raise ValueError("Tavily API key not found")

#     # Initialize Tavily client
#     tavily_client = TavilyClient(TAVILY_API_KEY)
#     search_response = tavily_client.search(query, max_results=max_results)
#     return search_response

# web search using tavily api - basic or advanced search depth
def web_search(query, max_results=TAVILY_MAX_RESULTS, search_depth="advanced", time_range=None):  
  """
    Performs a web search using the Tavily API.

    This function initializes a Tavily client with an API key and performs a search
    query using their search engine. Tavily specializes in providing AI-optimized
    search results with high accuracy and relevance.

    Args:
        q (str): The search query string to be processed by Tavily's search engine.
        max_results (int): The maximum number of results to return.
        search_depth (str): The depth of the search. Can be "basic" or "advanced".
        "Advanced" search depth is more comprehensive but slower and more expensive.

        time_range (str): The time range of search results. Default is None. 
        Other options include: none, day, week, month, year

    Returns:
        dict: A dictionary containing the search results from Tavily. The results typically include:
            - title: The title of each search result
            - url: The URL of the webpage
            - content: A snippet or content preview
            - score: Relevance score of the result
            - published_date: When the content was published (if available)
  """
  query = query.strip('"')

  try:
      # Initialize the client
      client = TavilyClient()

      # Perform the search
      response = client.search(
          query=query,
          search_depth=search_depth,  
          max_results=max_results,
          time_range=time_range
      )
      return response
  except Exception as e:
      print(f"Search error: {e}")
      return None