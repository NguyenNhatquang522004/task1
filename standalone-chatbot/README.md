# Standalone Chatbot

A standalone chatbot application that clones the search functionality from the main LLM Graph Builder backend. This project provides an independent chatbot service with vector and graph search capabilities.

## Features

- **Multiple Chat Modes**: Vector search, graph queries, and hybrid approaches
- **Multi-LLM Support**: OpenAI, Google Gemini, Groq, Anthropic, and Ollama
- **Neo4j Integration**: Vector search and Cypher graph queries
- **Session Management**: Persistent chat history per session
- **FastAPI Backend**: RESTful API with automatic documentation
- **Document Filtering**: Optional document-specific searches

## Project Structure

```
standalone-chatbot/
├── main.py                    # FastAPI application entry point
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── models/
│   ├── __init__.py
│   ├── qa_models.py          # Request/response models
│   └── chat_models.py        # LLM integration models
├── services/
│   ├── __init__.py
│   ├── chat_service.py       # Main chat orchestration
│   ├── vector_service.py     # Vector search functionality
│   └── graph_service.py      # Graph query functionality
└── utils/
    ├── __init__.py
    ├── neo4j_utils.py        # Neo4j connection utilities
    └── embedding_utils.py    # Embedding model utilities
```

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd standalone-chatbot
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the project root:
   ```env
   # Neo4j Configuration
   NEO4J_URI=neo4j+s://your-database-uri
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your-password
   
   # LLM API Keys
   OPENAI_API_KEY=your-openai-key
   GOOGLE_API_KEY=your-google-key
   GROQ_API_KEY=your-groq-key
   ANTHROPIC_API_KEY=your-anthropic-key
   
   # Optional: Ollama configuration
   OLLAMA_BASE_URL=http://localhost:11434
   
   # Server Configuration
   HOST=0.0.0.0
   PORT=8001
   ```

## Usage

### Starting the Server

```bash
python main.py
```

The server will start at `http://localhost:8001` by default.

### API Documentation

- **Interactive docs**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### API Endpoints

#### Chat Endpoint
```http
POST /chat
Content-Type: application/json

{
    "question": "Your question here",
    "model": "gpt-4o-mini",
    "mode": "vector",
    "document_names": ["optional", "document", "filter"],
    "session_id": "optional-session-id"
}
```

#### Clear Chat History
```http
POST /clear_chat
Content-Type: application/json

{
    "session_id": "your-session-id"
}
```

#### Health Check
```http
GET /health
```

#### Available Models
```http
GET /models
```

## Chat Modes

- **vector**: Standard vector similarity search
- **vector_fulltext**: Vector search with full-text capabilities
- **parent_retriever**: Hierarchical document retrieval
- **hypothetical_questions**: Question-based document matching
- **summaries**: Summary-based document retrieval
- **graph**: Pure Cypher graph queries

## Configuration

The application uses several configuration files:

- `config.py`: Main configuration with Neo4j settings, LLM configurations, and chat templates
- `.env`: Environment variables for sensitive data
- `requirements.txt`: Python package dependencies

## Key Components

### Chat Service (`services/chat_service.py`)
- Main orchestration logic
- Session management
- Document formatting and context preparation

### Vector Service (`services/vector_service.py`)
- Neo4j vector index integration
- Multiple retrieval strategies
- Document similarity scoring

### Graph Service (`services/graph_service.py`)
- Cypher query generation and execution
- Graph-based question answering
- Entity and relationship queries

### Models (`models/`)
- Pydantic models for request/response validation
- LLM client management
- Type definitions

## Development

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Testing

```bash
pytest tests/
```

### Code Formatting

```bash
black .
flake8 .
```

## Dependencies

Key dependencies include:
- FastAPI for web framework
- LangChain for LLM orchestration
- Neo4j driver for database connectivity
- Sentence Transformers for embeddings
- Various LLM API clients

## Differences from Main Backend

This standalone version:
- Focuses solely on chat functionality
- Removes document upload and processing features
- Simplifies the API surface
- Maintains independence from the main application
- Uses port 8001 by default (vs 8000 for main backend)

## Troubleshooting

1. **Neo4j Connection Issues**: Verify database credentials and network connectivity
2. **LLM API Errors**: Check API keys and rate limits
3. **Import Errors**: Ensure all dependencies are installed with correct versions
4. **Memory Issues**: Monitor embedding model memory usage for large documents

## License

This project inherits the license from the main LLM Graph Builder project.
│   └── embedding_utils.py # Embedding model utilities
├── templates/            # Chat templates
├── requirements.txt
└── README.md
```

## Cách sử dụng
```bash
cd c:\edu\task1\llm-graph-builder\standalone-chatbot
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8001
```

## API Endpoints
- `POST /chat` - Main chat endpoint
- `POST /clear_chat` - Clear chat history
- `GET /health` - Health check
- `GET /models` - List available models
