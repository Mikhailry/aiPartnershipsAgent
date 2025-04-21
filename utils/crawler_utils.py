import asyncio
import nest_asyncio
nest_asyncio.apply()
from crawl4ai import AsyncWebCrawler, CacheMode, BrowserConfig, CrawlerRunConfig

# async def simple_crawl():
#     # Create browser config specifying Firefox
#     browser_config = BrowserConfig(browser_type="firefox")
    
#     # Create crawler run config with cache bypassed
#     crawler_run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
    
#     # Initialize the crawler with Firefox browser config
#     async with AsyncWebCrawler() as crawler:
#         # Override the browser config when running
#         result = await crawler.arun(
#             url="https://www.crn.com/news/ai/2024/accenture-to-train-30-000-staff-on-nvidia-ai-tech-in-blockbuster-deal",
#             config=crawler_run_config,
#             browser_config=browser_config
#         )
#         print(result.markdown.raw_markdown[:500].replace("\n", " -- ")) # Print the first 500 characters

# asyncio.run(simple_crawl())

#------------------------------------------------------------

async def crawlWeb(url):
    """
    Crawl a webpage and return its text content.
    
    Args:
        url (str): The URL to crawl
    
    Returns:
        str: The raw markdown content of the crawled webpage
    """
    # Create browser config specifying Firefox
    browser_config = BrowserConfig(browser_type="firefox")
    
    # Create crawler run config with cache bypassed
    crawler_run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
    
    # Initialize the crawler with Firefox browser config
    async with AsyncWebCrawler() as crawler:
        # Override the browser config when running
        result = await crawler.arun(
            url=url,
            config=crawler_run_config,
            browser_config=browser_config
        )
    
    # Return the raw markdown content
    return result.markdown.raw_markdown

# Helper function to run the async crawl function synchronously
def crawl_url(url):
    """
    Synchronous wrapper for crawlWeb function.
    
    Args:
        url (str): The URL to crawl
    
    Returns:
        str: The raw markdown content of the crawled webpage
    """
    return asyncio.run(crawlWeb(url))