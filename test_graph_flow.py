#!/usr/bin/env python
"""
Test script to debug the graph flow issue.
"""

import logging
import json
from agent.graph import create_agent, get_thread_config
from agent.state import FeedbackType
from debug_helpers import log_state

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("graph_flow_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_finalize_flow():
    """Test the flow that leads to finalization."""
    # Create the agent
    graph, thread_id = create_agent()
    logger.info(f"Created agent with thread ID: {thread_id}")
    
    # Get thread config
    config = get_thread_config(thread_id)
    
    # Create a minimal state that would lead to finalization
    # This mimics a state where we've already done research and have a draft
    state = {
        "topic": "test topic",
        "draft": "This is a test draft article.",
        "draft_version": 1,
        "feedback_type": FeedbackType.NONE,
        # Include any other required fields
    }
    
    logger.info("Starting graph execution with test state")
    log_state(state, "INITIAL TEST STATE")
    
    # Run the graph
    try:
        # Use stream to see each step
        for i, chunk in enumerate(graph.stream(state, config=config)):
            logger.info(f"Step {i}: Received chunk")
            log_state(chunk, f"CHUNK {i}")
            
            # Check for final_article
            if "final_article" in chunk:
                logger.info(f"Final article found in chunk {i}")
                break
    except Exception as e:
        logger.error(f"Error executing graph: {str(e)}", exc_info=True)

if __name__ == "__main__":
    test_finalize_flow()