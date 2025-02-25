import os
import streamlit as st
import time
import logging
from typing import Dict, Any, List, Optional
import json

from agent.graph import create_agent, get_thread_config
from agent.state import FeedbackType
from agent.utils import save_markdown

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(
    page_title="Content Writer Agent",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = False
    st.session_state.topic = ""
    st.session_state.graph = None
    st.session_state.thread_id = None
    st.session_state.current_step = "start"
    st.session_state.draft = ""
    st.session_state.draft_version = 0
    st.session_state.research = ""
    st.session_state.messages = []
    st.session_state.saved_path = None

def initialize_agent():
    """Initialize the agent graph and thread ID."""
    if not st.session_state.initialized:
        with st.spinner("Initializing content writer agent..."):
            try:
                graph, thread_id = create_agent()
                st.session_state.graph = graph
                st.session_state.thread_id = thread_id
                st.session_state.initialized = True
                logger.info(f"Agent initialized with thread ID: {thread_id}")
            except Exception as e:
                st.error(f"Error initializing agent: {str(e)}")
                logger.error(f"Error initializing agent: {str(e)}")

def reset_agent():
    """Reset the agent state."""
    st.session_state.initialized = False
    st.session_state.topic = ""
    st.session_state.graph = None
    st.session_state.thread_id = None
    st.session_state.current_step = "start"
    st.session_state.draft = ""
    st.session_state.draft_version = 0
    st.session_state.research = ""
    st.session_state.messages = []
    st.session_state.saved_path = None
    
    # Reinitialize the agent
    initialize_agent()

def run_agent_step(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run a step in the agent workflow.
    
    Args:
        input_data: The input data for the step
        
    Returns:
        output: The output from the step
    """
    try:
        # Get the thread config
        thread_config = get_thread_config(st.session_state.thread_id)
        
        # Process the step
        with st.spinner("Processing..."):
            result = st.session_state.graph.invoke(input_data, config=thread_config)
        
        return result
    except Exception as e:
        st.error(f"Error running agent step: {str(e)}")
        logger.error(f"Error running agent step: {str(e)}")
        return {"error": str(e)}

def handle_interrupt(chunk, wait_time: int = 1):
    """Handle an interrupt from the graph.
    
    Args:
        chunk: The chunk containing the interrupt
        wait_time: Time to wait for a better UX, in seconds
        
    Returns:
        result: The result to resume with
    """
    # Extract the interrupt data
    interrupt_data = chunk.get("__interrupt__", {})
    
    # Add to messages
    st.session_state.messages.append({
        "role": "agent",
        "content": interrupt_data,
        "timestamp": time.time()
    })
    
    # Display the messages
    display_messages()
    
    # Handle different types of interrupts
    if "task" in interrupt_data and "draft" in interrupt_data:
        # This is a review task
        task = interrupt_data["task"]
        draft = interrupt_data["draft"]
        
        # Update the draft in session state
        st.session_state.draft = draft
        
        # Wait a moment for better UX
        time.sleep(wait_time)
        
        if "suggestions" in interrupt_data:
            # This is a persona feedback task
            suggestions = interrupt_data["suggestions"]
            return handle_persona_feedback(suggestions)
        else:
            # This is a human feedback task
            return handle_human_feedback()
    
    # Default: return None to continue
    return None

def handle_human_feedback() -> str:
    """Handle human feedback interrupt.
    
    Returns:
        feedback: The human feedback
    """
    st.markdown("### Provide Feedback")
    st.markdown("Please review the draft and provide your feedback for improvements:")
    
    # Show the current draft
    with st.expander("Current Draft", expanded=True):
        st.markdown(st.session_state.draft)
    
    # Get feedback
    feedback = st.text_area("Your Feedback", height=200, key="human_feedback_input")
    
    # Buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Submit Feedback"):
            # Add to messages
            st.session_state.messages.append({
                "role": "user",
                "content": feedback,
                "timestamp": time.time()
            })
            return feedback
    
    with col2:
        if st.button("Skip Feedback"):
            # Add to messages
            st.session_state.messages.append({
                "role": "user",
                "content": "No feedback provided",
                "timestamp": time.time()
            })
            return "none"
    
    # If no button clicked, just return None to continue waiting
    st.stop()

def handle_persona_feedback(suggestions: List[Dict[str, str]]) -> List[str]:
    """Handle persona feedback interrupt.
    
    Args:
        suggestions: The persona suggestions
        
    Returns:
        selected: List of selected persona names
    """
    st.markdown("### Persona Feedback")
    st.markdown("The following personas have reviewed your article. Please select which suggestions you'd like to incorporate:")
    
    # Show the current draft
    with st.expander("Current Draft", expanded=True):
        st.markdown(st.session_state.draft)
    
    # Display each persona's suggestions
    selected_personas = []
    
    for suggestion in suggestions:
        persona = suggestion["persona"]
        suggestion_text = suggestion["suggestion"]
        
        with st.expander(f"Feedback from: {persona}", expanded=True):
            st.markdown(suggestion_text)
            
            if st.checkbox(f"Include suggestions from {persona}", key=f"persona_{persona}"):
                selected_personas.append(persona)
    
    # Buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Apply Selected Suggestions"):
            # Add to messages
            st.session_state.messages.append({
                "role": "user",
                "content": f"Selected persona suggestions: {', '.join(selected_personas)}",
                "timestamp": time.time()
            })
            return selected_personas
    
    with col2:
        if st.button("Skip Persona Feedback"):
            # Add to messages
            st.session_state.messages.append({
                "role": "user",
                "content": "No persona suggestions selected",
                "timestamp": time.time()
            })
            return []
    
    # If no button clicked, just return None to continue waiting
    st.stop()

def display_messages():
    """Display the conversation messages."""
    # Only show if we have messages
    if not st.session_state.messages:
        return
    
    # Container for messages
    with st.container():
        st.markdown("### Agent Activity")
        
        for msg in st.session_state.messages:
            role = msg["role"]
            content = msg["content"]
            
            # Format based on role
            if role == "agent":
                # Agent messages may be more complex
                if isinstance(content, dict):
                    # This is an interrupt with structured data
                    if "task" in content:
                        st.info(f"**Agent:** {content['task']}")
                else:
                    # Regular message
                    st.info(f"**Agent:** {content}")
            else:
                # User messages
                st.success(f"**You:** {content}")

def start_page():
    """Display the start page to get the topic."""
    st.title("Content Writer Agent")
    st.markdown("This agent helps you write content with AI and human collaboration.")
    
    # Get the topic
    topic = st.text_input("What topic would you like to write about?", key="topic_input")
    
    if st.button("Start Writing"):
        if topic:
            st.session_state.topic = topic
            st.session_state.current_step = "writing"
            st.session_state.messages.append({
                "role": "user",
                "content": f"Topic: {topic}",
                "timestamp": time.time()
            })
            st.rerun()
        else:
            st.warning("Please enter a topic first.")

def writing_process():
    """Handle the main writing process."""
    st.title(f"Writing Article: {st.session_state.topic}")
    
    # Initialize the process
    if not st.session_state.get("writing_started", False):
        # Start the process with the topic
        input_data = {"topic": st.session_state.topic}
        
        # Run the process
        try:
            for chunk in st.session_state.graph.stream(input_data, config=get_thread_config(st.session_state.thread_id)):
                # Check for interrupts
                if "__interrupt__" in chunk:
                    # Handle the interrupt
                    result = handle_interrupt(chunk)
                    
                    if result is not None:
                        # Resume the process with the result
                        from langgraph.types import Command
                        st.session_state.graph.invoke(Command(resume=result), config=get_thread_config(st.session_state.thread_id))
                
                # Check for final state
                if "final_article" in chunk:
                    st.session_state.final_article = chunk["final_article"]
                    st.session_state.current_step = "completed"
                    st.rerun()
                
                # Update the draft if available
                if "draft" in chunk:
                    st.session_state.draft = chunk["draft"]
                    if "draft_version" in chunk:
                        st.session_state.draft_version = chunk["draft_version"]
                
                # Update research if available
                if "combined_research" in chunk:
                    st.session_state.research = chunk["combined_research"]
                
                # Show progress
                if not st.session_state.get("progress_placeholder"):
                    st.session_state.progress_placeholder = st.empty()
                    
                st.session_state.progress_placeholder.info("Processing...")
            
            # Mark as started
            st.session_state.writing_started = True
            
        except Exception as e:
            st.error(f"Error in writing process: {str(e)}")
            logger.error(f"Error in writing process: {str(e)}")
    
    # Display the current state
    if st.session_state.current_step == "writing":
        # Show the current draft
        if st.session_state.draft:
            st.markdown("### Current Draft")
            st.markdown(st.session_state.draft)
        
        # Show options for next steps
        st.markdown("### What would you like to do next?")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Add Human Feedback"):
                run_agent_step({"feedback_type": FeedbackType.HUMAN})
                st.rerun()
        
        with col2:
            if st.button("Get Persona Feedback"):
                run_agent_step({"feedback_type": FeedbackType.PERSONA})
                st.rerun()
        
        with col3:
            if st.button("Finalize Draft"):
                run_agent_step({"feedback_type": FeedbackType.NONE})
                st.rerun()
        
        # Display the messages
        display_messages()
        
        # Show research in sidebar
        if st.session_state.research:
            with st.sidebar:
                st.markdown("### Research Summary")
                st.markdown(st.session_state.research)

def completed_page():
    """Display the completed article."""
    st.title("Article Completed! 🎉")
    
    # Display the final article
    st.markdown("### Final Article")
    st.markdown(st.session_state.final_article)
    
    # Save the article
    if st.button("Save Article as Markdown") and not st.session_state.saved_path:
        try:
            filepath = save_markdown(
                st.session_state.final_article,
                st.session_state.topic,
                st.session_state.draft_version
            )
            st.session_state.saved_path = filepath
            st.success(f"Article saved to: {filepath}")
        except Exception as e:
            st.error(f"Error saving article: {str(e)}")
    
    # Option to start over
    if st.button("Start a New Article"):
        reset_agent()
        st.rerun()

def main():
    """Main application."""
    # Make sure agent is initialized
    initialize_agent()
    
    # Handle different steps
    if st.session_state.current_step == "start":
        start_page()
    elif st.session_state.current_step == "writing":
        writing_process()
    elif st.session_state.current_step == "completed":
        completed_page()
    else:
        st.error("Unknown step")
        if st.button("Reset"):
            reset_agent()
            st.rerun()

if __name__ == "__main__":
    main()