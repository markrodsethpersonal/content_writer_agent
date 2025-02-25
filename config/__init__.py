import os
import yaml
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Config directory
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))

def load_config(filename: str) -> Any:
    """Load a configuration from a YAML file.
    
    Args:
        filename: The name of the YAML file to load
        
    Returns:
        config: The configuration data
    """
    try:
        # Make sure the filename has a .yaml extension
        if not filename.endswith(".yaml"):
            filename = f"{filename}.yaml"
        
        # Construct the full file path
        filepath = os.path.join(CONFIG_DIR, filename)
        
        # Check if the file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Config file not found: {filepath}")
        
        # Load the YAML file
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        return data
    except Exception as e:
        logger.error(f"Error loading config {filename}: {str(e)}")
        raise