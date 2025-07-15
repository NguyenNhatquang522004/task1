"""
Cross-Document Entity Relationships Module for LLM Graph Builder

This module provides functionality to analyze and create relationships between entities
from different documents using vector similarity and LLM-based semantic analysis.

Main components:
- CrossDocumentAnalyzer: Core analysis logic
- FastAPI routes: REST API endpoints  
- Integration utilities: Setup and dependency injection
- Configuration: Environment-based settings

Usage:
    from cross_document_relationships.integration import setup_cross_document_analysis
    
    # In your FastAPI app
    setup_cross_document_analysis(app, llm_client, neo4j_driver)
"""

from .src.core.analyzer import CrossDocumentAnalyzer
from .src.constants import RELATIONSHIP_TYPES, DEFAULT_SIMILARITY_THRESHOLD
from .config.settings import config
from .integration import setup_cross_document_analysis, get_cross_document_analyzer

__version__ = "1.0.0"
__author__ = "LLM Graph Builder Team"

__all__ = [
    "CrossDocumentAnalyzer",
    "RELATIONSHIP_TYPES", 
    "DEFAULT_SIMILARITY_THRESHOLD",
    "config",
    "setup_cross_document_analysis",
    "get_cross_document_analyzer"
]
