import os

def create_directory(directory):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def create_file(filepath, content=""):
    """Create empty file."""
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Created file: {filepath}")

def setup_project():
    """Setup the content writer agent project structure."""
    # Project root directory
    root_dir = "content_writer_agent"
    create_directory(root_dir)
    
    # Create subdirectories
    directories = [
        "agent",
        "config",
        "prompts",
        "services",
    ]
    
    for directory in directories:
        create_directory(os.path.join(root_dir, directory))
    
    # Create files
    files = [
        # Root files
        "requirements.txt",
        "README.md",
        "app.py",
        
        # Agent files
        "agent/__init__.py",
        "agent/graph.py",
        "agent/nodes.py",
        "agent/state.py",
        "agent/utils.py",
        
        # Config files
        "config/__init__.py",
        "config/content_structure.yaml",
        "config/personas.yaml",
        "config/tone_of_voice.yaml",
        
        # Prompts files
        "prompts/__init__.py",
        "prompts/research.yaml",
        "prompts/draft.yaml",
        "prompts/human_review.yaml",
        "prompts/persona.yaml",
        "prompts/update.yaml",
        
        # Services files
        "services/__init__.py",
        "services/llm.py",
        "services/search.py",
        "services/vector_db.py",
    ]
    
    for file in files:
        create_file(os.path.join(root_dir, file))

if __name__ == "__main__":
    setup_project()
    print("Project structure created successfully!")