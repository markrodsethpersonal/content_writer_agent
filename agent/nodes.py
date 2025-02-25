import logging
from typing import Dict, Any, List
from langgraph.types import interrupt

from .state import State, FeedbackType
from ..services.llm import get_completion
from ..services.search import search_internet
from ..services.vector_db import query_vector_db
from ..prompts import load_prompt

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def conduct_research(state: State) -> Dict[str, Any]:
    """Conduct research on the topic by searching the internet and vector DB."""
    try:
        topic = state["topic"]
        logger.info(f"Conducting research on topic: {topic}")
        
        # Search the internet
        search_results = search_internet(topic)
        
        # Query the vector DB
        vector_results = query_vector_db(topic)
        
        # Combine the results
        all_results = search_results + vector_results
        
        # Format the research into a single string
        research_prompt = load_prompt("research.yaml")
        combined_research = get_completion(
            research_prompt,
            {"results": all_results, "topic": topic}
        )
        
        logger.info("Research completed successfully")
        
        return {
            "research_results": search_results,
            "vector_db_results": vector_results,
            "combined_research": combined_research
        }
    except Exception as e:
        logger.error(f"Error in conduct_research: {str(e)}")
        return {"error": f"Research error: {str(e)}"}

def write_draft(state: State) -> Dict[str, Any]:
    """Write a draft based on the research and guidelines."""
    try:
        topic = state["topic"]
        research = state["combined_research"]
        
        logger.info(f"Writing draft for topic: {topic}")
        
        # Load the prompt template
        draft_prompt = load_prompt("draft.yaml")
        
        # Get the draft from the LLM
        draft = get_completion(
            draft_prompt,
            {
                "topic": topic,
                "research": research,
                "tone_of_voice": "config/tone_of_voice.yaml",
                "content_structure": "config/content_structure.yaml"
            }
        )
        
        logger.info("Draft written successfully")
        
        return {
            "draft": draft,
            "draft_version": 1,
            "feedback_type": FeedbackType.NONE  # Initialize with no feedback
        }
    except Exception as e:
        logger.error(f"Error in write_draft: {str(e)}")
        return {"error": f"Draft writing error: {str(e)}"}

def process_human_feedback(state: State) -> Dict[str, Any]:
    """Process human feedback using interrupt."""
    try:
        logger.info("Getting human feedback")
        
        # Use interrupt to get human feedback
        result = interrupt(
            {
                "task": "Review the draft and provide feedback for improvements",
                "draft": state["draft"],
                "topic": state["topic"],
                "version": state["draft_version"]
            }
        )
        
        logger.info("Received human feedback")
        
        # Check if the human provided feedback or wants to skip
        if not result or result.lower() in ["none", "skip", "no feedback"]:
            return {"feedback_type": FeedbackType.NONE}
        
        return {"human_feedback": result}
    except Exception as e:
        logger.error(f"Error in process_human_feedback: {str(e)}")
        return {"error": f"Human feedback error: {str(e)}"}

def generate_persona_feedback(state: State) -> Dict[str, Any]:
    """Generate feedback from different personas."""
    try:
        logger.info("Generating persona feedback")
        
        # Load the persona prompt template
        persona_prompt = load_prompt("persona.yaml")
        
        # Get the personas from config
        from ..config import load_config
        personas = load_config("personas.yaml")
        
        # Generate suggestions from each persona
        suggestions = []
        for persona in personas:
            suggestion = get_completion(
                persona_prompt,
                {
                    "draft": state["draft"],
                    "persona_name": persona["name"],
                    "persona_description": persona["description"],
                    "topic": state["topic"]
                }
            )
            
            suggestions.append({
                "persona": persona["name"],
                "suggestion": suggestion
            })
        
        # Use interrupt to let the user select which suggestions to incorporate
        result = interrupt(
            {
                "task": "Select which persona suggestions you would like to incorporate",
                "draft": state["draft"],
                "suggestions": suggestions,
                "version": state["draft_version"]
            }
        )
        
        logger.info(f"Received selected persona suggestions: {result}")
        
        # Check if any suggestions were selected
        if not result or not isinstance(result, list) or len(result) == 0:
            return {"feedback_type": FeedbackType.NONE}
        
        return {
            "persona_suggestions": suggestions,
            "selected_persona_suggestions": result
        }
    except Exception as e:
        logger.error(f"Error in generate_persona_feedback: {str(e)}")
        return {"error": f"Persona feedback error: {str(e)}"}

def update_draft(state: State, feedback_type: FeedbackType) -> Dict[str, Any]:
    """Update the draft based on feedback."""
    try:
        current_draft = state["draft"]
        topic = state["topic"]
        
        logger.info(f"Updating draft for topic: {topic} with {feedback_type} feedback")
        
        # Load the update prompt template
        update_prompt = load_prompt("update.yaml")
        
        feedback = ""
        if feedback_type == FeedbackType.HUMAN and "human_feedback" in state:
            feedback = state["human_feedback"]
        elif feedback_type == FeedbackType.PERSONA and "selected_persona_suggestions" in state:
            # Get the full suggestions for the selected personas
            selected_ids = state["selected_persona_suggestions"]
            all_suggestions = state["persona_suggestions"]
            
            selected_suggestions = [
                suggestion for suggestion in all_suggestions
                if suggestion["persona"] in selected_ids
            ]
            
            # Combine the selected suggestions
            feedback = "\n".join([
                f"Persona: {suggestion['persona']}\n{suggestion['suggestion']}"
                for suggestion in selected_suggestions
            ])
        
        # Get the updated draft from the LLM
        updated_draft = get_completion(
            update_prompt,
            {
                "topic": topic,
                "current_draft": current_draft,
                "feedback": feedback,
                "feedback_type": feedback_type,
                "tone_of_voice": "config/tone_of_voice.yaml",
                "content_structure": "config/content_structure.yaml"
            }
        )
        
        logger.info("Draft updated successfully")
        
        return {
            "draft": updated_draft,
            "draft_version": state.get("draft_version", 1) + 1,
            "feedback_type": FeedbackType.NONE  # Reset feedback type
        }
    except Exception as e:
        logger.error(f"Error in update_draft: {str(e)}")
        return {"error": f"Draft update error: {str(e)}"}

def finalize_draft(state: State) -> Dict[str, Any]:
    """Finalize the draft and save it."""
    try:
        final_draft = state["draft"]
        
        logger.info(f"Finalizing draft version {state['draft_version']}")
        
        # No need to do any processing, just mark it as the final version
        return {
            "final_article": final_draft
        }
    except Exception as e:
        logger.error(f"Error in finalize_draft: {str(e)}")
        return {"error": f"Draft finalization error: {str(e)}"}