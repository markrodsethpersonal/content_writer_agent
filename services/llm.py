import os
import logging
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Default model to use
DEFAULT_MODEL = "gpt-4o"

def get_completion(
    prompt_template: str,
    variables: Dict[str, Any],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4000
) -> str:
    """Get a completion from OpenAI.
    
    Args:
        prompt_template: The prompt template to use
        variables: The variables to substitute into the prompt template
        model: The model to use (defaults to DEFAULT_MODEL)
        temperature: The temperature to use
        max_tokens: The maximum number of tokens to generate
        
    Returns:
        completion: The generated completion
    """
    try:
        # Format the prompt with the provided variables
        prompt = prompt_template.format(**variables)
        
        # Log the formatted prompt for debugging (in a production system, you might want to sanitize this)
        logger.debug(f"Formatted prompt: {prompt}")
        
        # Call the OpenAI API
        response = client.chat.completions.create(
            model=model or DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Extract and return the completion
        completion = response.choices[0].message.content
        
        return completion
    except Exception as e:
        logger.error(f"Error in get_completion: {str(e)}")
        raise