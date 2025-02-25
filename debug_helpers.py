import logging
import json
import os
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("debug")

def log_state(state: Dict[str, Any], location: str):
    """Log the current state at a specific location in the code."""
    try:
        # Create a sanitized copy of the state for logging
        # This will handle non-serializable objects by converting them to strings
        serializable_state = {}
        for key, value in state.items():
            try:
                # Try to serialize the value to JSON to check if it's serializable
                json.dumps(value)
                serializable_state[key] = value
            except (TypeError, OverflowError):
                # If it's not serializable, convert to string
                serializable_state[key] = str(value)
        
        logger.debug(f"STATE AT {location}: {json.dumps(serializable_state, indent=2)}")
    except Exception as e:
        logger.error(f"Error logging state at {location}: {str(e)}")

def inspect_draft_update(old_draft, new_draft, location):
    """Compare old and new drafts to help debug changes."""
    try:
        # If drafts are identical, note that
        if old_draft == new_draft:
            logger.debug(f"DRAFT AT {location}: No changes detected")
            return
        
        # Log the length difference
        old_len = len(old_draft) if old_draft else 0
        new_len = len(new_draft) if new_draft else 0
        logger.debug(f"DRAFT AT {location}: Length changed from {old_len} to {new_len} characters")
        
        # If the draft is shorter than 1000 characters, log it entirely
        if new_len < 1000:
            logger.debug(f"DRAFT CONTENT AT {location}: {new_draft}")
        else:
            # Otherwise log the first and last 200 characters
            logger.debug(f"DRAFT BEGINNING AT {location}: {new_draft[:200]}...")
            logger.debug(f"DRAFT ENDING AT {location}: ...{new_draft[-200:]}")
    except Exception as e:
        logger.error(f"Error inspecting draft at {location}: {str(e)}")