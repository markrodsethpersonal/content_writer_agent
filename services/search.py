import logging
from typing import List, Dict, Any

from duckduckgo_search import DDGS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def search_internet(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search the internet for relevant information.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        
    Returns:
        results: A list of search results
    """
    try:
        logger.info(f"Searching internet for: {query}")
        
        # Initialize DuckDuckGo search
        ddgs = DDGS()
        
        # Perform the search
        raw_results = list(ddgs.text(query, max_results=max_results))
        
        # Format the results
        results = [
            {
                "title": result.get("title", ""),
                "body": result.get("body", ""),
                "url": result.get("href", ""),
                "source": "internet_search"
            }
            for result in raw_results
        ]
        
        logger.info(f"Found {len(results)} search results")
        
        return results
    except Exception as e:
        logger.error(f"Error in search_internet: {str(e)}")
        # Return an empty list if there's an error
        return []