import os
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def save_markdown(content: str, topic: str, version: Optional[int] = None) -> str:
    """Save content as a markdown file.
    
    Args:
        content: The content to save
        topic: The topic of the content (used for filename)
        version: Optional version number to include in the filename
        
    Returns:
        filepath: The path where the file was saved
    """
    try:
        # Create a directory for saved content if it doesn't exist
        os.makedirs("saved_articles", exist_ok=True)
        
        # Create a safe filename from the topic
        safe_topic = "".join(c if c.isalnum() else "_" for c in topic)
        
        # Add version if provided
        version_str = f"_v{version}" if version is not None else ""
        
        # Create the filepath
        filepath = f"saved_articles/{safe_topic}{version_str}.md"
        
        # Save the content
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"Saved content to {filepath}")
        
        return filepath
    except Exception as e:
        logger.error(f"Error saving markdown: {str(e)}")
        return f"Error saving file: {str(e)}"

def format_error(error: str) -> Dict[str, Any]:
    """Format an error message for the UI.
    
    Args:
        error: The error message
        
    Returns:
        error_dict: A dictionary with the formatted error
    """
    return {
        "error": True,
        "message": error
    }