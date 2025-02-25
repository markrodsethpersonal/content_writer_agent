import uuid
from typing import Dict, Any, Callable

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.constants import START, END

from .state import State, FeedbackType
from .nodes import (
    conduct_research,
    write_draft,
    process_human_feedback,
    generate_persona_feedback,
    update_draft,
    finalize_draft
)

def should_get_human_feedback(state: State) -> str:
    """Conditional router to determine if we need human feedback."""
    return "get_human_feedback" if state["feedback_type"] == FeedbackType.HUMAN else "router"

def should_get_persona_feedback(state: State) -> str:
    """Conditional router to determine if we need persona feedback."""
    return "get_persona_feedback" if state["feedback_type"] == FeedbackType.PERSONA else "router"

def should_continue_editing(state: State) -> str:
    """Conditional router to determine if we should continue editing or finalize the draft."""
    if state["feedback_type"] == FeedbackType.NONE:
        return "finalize_draft"
    
    # If we have human feedback, update the draft
    if state["feedback_type"] == FeedbackType.HUMAN and "human_feedback" in state:
        return "update_draft_human"
    
    # If we have persona feedback, update the draft
    if (state["feedback_type"] == FeedbackType.PERSONA and 
        "selected_persona_suggestions" in state and 
        state["selected_persona_suggestions"]):
        return "update_draft_persona"
    
    # Default back to the router (should only happen if feedback type is set but no actual feedback provided)
    return "router"

def create_agent(config: Dict[str, Any] = None) -> tuple:
    """Create the content writer agent workflow.
    
    Args:
        config: Configuration options for the agent
        
    Returns:
        graph: The compiled graph
        thread_id: A unique ID for this thread
    """
    # Generate a unique thread ID
    thread_id = str(uuid.uuid4())
    
    # Create memory checkpointer for interrupts
    checkpointer = MemorySaver()
    
    # Initialize the graph
    builder = StateGraph(State)
    
    # Add all the nodes
    builder.add_node("conduct_research", conduct_research)
    builder.add_node("write_draft", write_draft)
    builder.add_node("get_human_feedback", process_human_feedback)
    builder.add_node("get_persona_feedback", generate_persona_feedback)
    builder.add_node("update_draft_human", lambda state: update_draft(state, FeedbackType.HUMAN))
    builder.add_node("update_draft_persona", lambda state: update_draft(state, FeedbackType.PERSONA))
    builder.add_node("finalize_draft", finalize_draft)
    
    # Add the routing node
    builder.add_node("router", lambda state: state)
    
    # Create the workflow
    builder.add_edge(START, "conduct_research")
    builder.add_edge("conduct_research", "write_draft")
    builder.add_edge("write_draft", "router")
    
    # Routing logic
    builder.add_conditional_edges(
        "router",
        should_get_human_feedback,
        {
            "get_human_feedback": "get_human_feedback",
            "router": "router"
        }
    )
    
    builder.add_conditional_edges(
        "router",
        should_get_persona_feedback,
        {
            "get_persona_feedback": "get_persona_feedback", 
            "router": "router"
        }
    )
    
    builder.add_conditional_edges(
        "router",
        should_continue_editing,
        {
            "update_draft_human": "update_draft_human",
            "update_draft_persona": "update_draft_persona",
            "finalize_draft": "finalize_draft",
            "router": "router"  # Fallback case
        }
    )
    
    # Connect the update nodes back to the router
    builder.add_edge("update_draft_human", "router")
    builder.add_edge("update_draft_persona", "router")
    builder.add_edge("get_human_feedback", "router")
    builder.add_edge("get_persona_feedback", "router")
    
    # Connect finalize to END
    builder.add_edge("finalize_draft", END)
    
    # Compile the graph
    graph = builder.compile(checkpointer=checkpointer)
    
    return graph, thread_id

def get_thread_config(thread_id: str) -> Dict[str, Any]:
    """Get the thread configuration dictionary for the given thread ID."""
    return {"configurable": {"thread_id": thread_id}}