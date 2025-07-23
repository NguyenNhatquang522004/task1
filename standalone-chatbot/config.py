"""
Configuration for Standalone Chatbot
"""
import os
from typing import Dict, Any

# Neo4j Configuration
NEO4J_URI = "neo4j+s://013fb011.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "NH43Qy392yswBCfUFNrjYjIIvr4B_LcJB4eMRNzHrp4"
NEO4J_DATABASE = "neo4j"

# Chat Configuration
CHAT_MAX_TOKENS = 1000
CHAT_SEARCH_KWARG_SCORE_THRESHOLD = 0.5
CHAT_DOC_SPLIT_SIZE = 3000
CHAT_EMBEDDING_FILTER_SCORE_THRESHOLD = 0.10

# LLM Configuration
DEFAULT_MODEL = "gemini_2.0_flash"
AVAILABLE_MODELS = [
    "openai_gpt_3.5",
    "openai_gpt_4o",
    "openai_gpt_4o_mini",
    "gemini_1.5_pro",
    "gemini_1.5_flash", 
    "gemini_2.0_flash",
    "groq_llama3_70b",
    "anthropic_claude_3_5_sonnet",
    "ollama_llama3"
]

# Chat Modes
CHAT_VECTOR_MODE = "vector"
CHAT_GRAPH_MODE = "graph"
CHAT_ENTITY_VECTOR_MODE = "entity+vector"
CHAT_GLOBAL_VECTOR_FULLTEXT_MODE = "fulltext+vector"
CHAT_DEFAULT_MODE = CHAT_VECTOR_MODE

# Token limits per model
CHAT_TOKEN_CUT_OFF = {
    ('openai_gpt_3.5', 'gemini_1.0_pro', 'gemini_1.5_pro', 'gemini_1.5_flash', 'groq_llama3_70b', 'anthropic_claude_3_5_sonnet'): 4,
    ('openai_gpt_4o', 'openai_gpt_4o_mini', 'gemini_2.0_flash'): 28,
    ('ollama_llama3',): 2
}

# Chat mode configurations
CHAT_MODE_CONFIG_MAP: Dict[str, Dict[str, Any]] = {
    CHAT_VECTOR_MODE: {
        "index_name": "vector",
        "retrieval_query": """
WITH node AS chunk, score
MATCH (chunk)-[:PART_OF]->(d:Document)
WITH d, 
     collect(distinct {chunk: chunk, score: score}) AS chunks, 
     avg(score) AS avg_score

WITH d, avg_score, 
     [c IN chunks | c.chunk.text] AS texts, 
     [c IN chunks | {id: c.chunk.id, score: c.score}] AS chunkdetails

WITH d, avg_score, chunkdetails, 
     apoc.text.join(texts, "\\n----\\n") AS text

RETURN text, 
       avg_score AS score, 
       {source: COALESCE(CASE WHEN d.url CONTAINS "None" 
                             THEN d.fileName 
                             ELSE d.url 
                       END, 
                       d.fileName), 
        chunkdetails: chunkdetails} AS metadata
        """,
        "top_k": 5,
        "node_label": "Chunk",
        "embedding_node_property": "embedding",
        "text_node_properties": ["text"],
        "document_filter": True,
        "keyword_index": ""
    },
    CHAT_GRAPH_MODE: {
        # Graph mode doesn't use vector search
    },
    CHAT_ENTITY_VECTOR_MODE: {
        "index_name": "entity_vector",
        "retrieval_query": """
// Entity vector search query would go here
RETURN "Entity vector search not implemented" AS text
        """,
        "top_k": 5,
        "node_label": "Entity",
        "embedding_node_property": "embedding",
        "text_node_properties": ["description"],
        "document_filter": False,
        "keyword_index": ""
    }
}

# Chat Templates
CHAT_SYSTEM_TEMPLATE = """
You are an AI-powered question-answering agent. Your task is to provide accurate and comprehensive responses to user queries based on the given context, chat history, and available resources.

### Response Guidelines:
1. **Direct Answers**: Provide clear and thorough answers to the user's queries without headers unless requested. Avoid speculative responses.
2. **Utilize History and Context**: Leverage relevant information from previous interactions, the current user input, and the context provided below.
3. **No Greetings in Follow-ups**: Start with a greeting in initial interactions. Avoid greetings in subsequent responses unless there's a significant break or the chat restarts.
4. **Admit Unknowns**: Clearly state if an answer is unknown. Avoid making unsupported statements.
5. **Avoid Hallucination**: Only provide information based on the context provided. Do not invent information.
6. **Response Length**: Keep responses concise and relevant. Aim for clarity and completeness within 4-5 sentences unless more detail is requested.
7. **Tone and Style**: Maintain a professional and informative tone. Be friendly and approachable.
8. **Error Handling**: If a query is ambiguous or unclear, ask for clarification rather than providing a potentially incorrect answer.
9. **Fallback Options**: If the required information is not available in the provided context, provide a polite and helpful response.
10. **Context Availability**: If the context is empty, do not provide answers based solely on internal knowledge.

**IMPORTANT** : DO NOT ANSWER FROM YOUR KNOWLEDGE BASE USE THE BELOW CONTEXT

### Context:
<context>
{context}
</context>
"""

QUESTION_TRANSFORM_TEMPLATE = "Given the below conversation, generate a search query to look up in order to get information relevant to the conversation. Only respond with the query, nothing else."

# Embedding Model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8001
API_TITLE = "Standalone Chatbot API"
API_DESCRIPTION = "Standalone chatbot service with vector search and graph query capabilities"
API_VERSION = "1.0.0"
