from typing import TypedDict, List, Dict, Optional, Any, Union
from enum import Enum

class FeedbackType(str, Enum):
    HUMAN = "human"
    PERSONA = "persona"
    NONE = "none"

class State(TypedDict, total=False):
    """State for the content writer agent workflow."""
    # Input
    topic: str
    
    # Research
    research_results: List[Dict[str, Any]]
    vector_db_results: List[Dict[str, Any]]
    combined_research: str
    
    # Draft
    draft: str
    draft_version: int
    
    # Human feedback
    human_feedback: Optional[str]
    
    # Persona feedback
    persona_suggestions: List[Dict[str, str]]
    selected_persona_suggestions: List[str]
    
    # Workflow control
    feedback_type: FeedbackType
    
    # Final output
    final_article: Optional[str]
    
    # Error handling
    error: Optional[str]