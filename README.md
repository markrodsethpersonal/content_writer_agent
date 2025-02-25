# Content Writer Agent

A LangGraph-powered content writing assistant with Streamlit UI that incorporates both human feedback and AI persona review as part of the editing process.

## Features

- Web research integration
- Vector database for storing and retrieving relevant content
- OpenAI integration for draft generation and updates
- Human-in-the-loop feedback mechanism
- AI personas for specialized content feedback
- Markdown export of final articles

## Project Structure

```
content_writer_agent/
├── app.py                # Streamlit UI
├── agent/
│   ├── __init__.py
│   ├── graph.py          # LangGraph implementation
│   ├── nodes.py          # Node implementations
│   ├── state.py          # State definition
│   └── utils.py          # Utility functions
├── config/
│   ├── __init__.py
│   ├── content_structure.yaml  # Content structure guide
│   ├── personas.yaml           # Personas configuration
│   └── tone_of_voice.yaml      # Tone of voice guide
├── prompts/
│   ├── __init__.py
│   ├── research.yaml     # Research prompt template
│   ├── draft.yaml        # Draft writing prompt template
│   ├── human_review.yaml # Human review prompt template
│   ├── persona.yaml      # Persona review prompt template
│   └── update.yaml       # Update draft prompt template
├── services/
│   ├── __init__.py
│   ├── llm.py            # OpenAI integration
│   ├── search.py         # Internet search integration
│   └── vector_db.py      # ChromaDB integration
```

## Installation

1. Clone the repository
2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Set up your environment variables (create a `.env` file):

```
OPENAI_API_KEY=your_openai_api_key
```

## Usage

1. Start the Streamlit app:

```bash
streamlit run app.py
```

2. Enter a topic in the UI to start the content creation process
3. Review the draft and provide feedback
4. Utilize AI personas for specialized feedback
5. Save the final article as Markdown

## Workflow

1. **Research**: The agent searches the web and local vector database for relevant information
2. **Draft Writing**: Using the research, the agent generates an initial draft
3. **Human Review**: You can provide feedback on the draft
4. **Persona Review**: AI personas offer specialized suggestions from different perspectives
5. **Draft Updates**: The agent revises the draft based on feedback
6. **Finalization**: The completed article is saved in Markdown format

## Personas

The system includes several pre-configured personas:

- SEO Specialist
- Industry Expert
- Target Reader
- Content Editor
- Conversion Specialist

Each persona provides specialized feedback based on their area of expertise.

## Customization

- Edit `config/tone_of_voice.yaml` to modify the writing style
- Edit `config/content_structure.yaml` to change the article structure
- Add or modify personas in `config/personas.yaml`
- Customize prompt templates in the `prompts/` directory

## Dependencies

- langraph
- streamlit
- openai
- chromadb
- duckduckgo-search
- pyyaml
- python-dotenv

## License

MIT