import os
import yaml
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Prompt templates directory
PROMPTS_DIR = os.path.dirname(os.path.abspath(__file__))

def load_prompt(filename: str) -> str:
    """Load a prompt template from a YAML file.
    
    Args:
        filename: The name of the YAML file to load
        
    Returns:
        prompt: The prompt template
    """
    try:
        # Make sure the filename has a .yaml extension
        if not filename.endswith(".yaml"):
            filename = f"{filename}.yaml"
        
        # Construct the full file path
        filepath = os.path.join(PROMPTS_DIR, filename)
        
        # Check if the file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Prompt file not found: {filepath}")
        
        # Load the YAML file
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        # Extract the prompt template
        if "prompt" not in data:
            raise ValueError(f"No 'prompt' key found in {filename}")
        
        prompt = data["prompt"]
        
        return prompt
    except Exception as e:
        logger.error(f"Error loading prompt {filename}: {str(e)}")
        raise