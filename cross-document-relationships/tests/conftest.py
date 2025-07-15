"""
Test configuration and fixtures for cross-document analysis tests
"""

import pytest
from unittest.mock import Mock, MagicMock
import asyncio

@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing"""
    client = Mock()
    client.generate_response = AsyncMock()
    return client

@pytest.fixture  
def mock_neo4j_driver():
    """Mock Neo4j driver for testing"""
    driver = Mock()
    session = Mock()
    driver.session.return_value.__enter__.return_value = session
    driver.session.return_value.__exit__.return_value = None
    return driver

@pytest.fixture
def sample_entity_pair():
    """Sample entity pair for testing"""
    return {
        "entity1_id": "entity_1",
        "entity1_name": "Machine Learning",
        "entity2_id": "entity_2",
        "entity2_name": "Deep Learning",
        "document1": "intro_to_ml.pdf",
        "document2": "advanced_dl.pdf",
        "similarity": 0.85
    }

@pytest.fixture
def sample_llm_response():
    """Sample LLM response for testing"""
    return """{
        "relationship_type": "PREREQUISITE",
        "confidence": 0.9,
        "explanation": "Machine Learning is a prerequisite for Deep Learning",
        "direction": "entity1_to_entity2"
    }"""

@pytest.fixture
def sample_analysis_result():
    """Sample analysis result for testing"""
    return {
        "entity1_id": "entity_1",
        "entity2_id": "entity_2",
        "entity1_name": "Machine Learning", 
        "entity2_name": "Deep Learning",
        "document1": "intro_to_ml.pdf",
        "document2": "advanced_dl.pdf",
        "similarity_score": 0.85,
        "relationship_type": "PREREQUISITE",
        "confidence": 0.9,
        "explanation": "Machine Learning is a prerequisite for Deep Learning",
        "direction": "entity1_to_entity2"
    }

class AsyncMock(MagicMock):
    """Async mock for testing async functions"""
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)

# Test data
TEST_ENTITY_PAIRS = [
    {
        "entity1_id": "e1", "entity1_name": "Python", 
        "entity2_id": "e2", "entity2_name": "Programming Language",
        "document1": "python_guide.pdf", "document2": "lang_overview.pdf",
        "similarity": 0.92
    },
    {
        "entity1_id": "e3", "entity1_name": "Neural Networks",
        "entity2_id": "e4", "entity2_name": "Artificial Neural Networks", 
        "document1": "nn_basics.pdf", "document2": "ai_concepts.pdf",
        "similarity": 0.88
    }
]

TEST_LLM_RESPONSES = {
    "PREREQUISITE": """{
        "relationship_type": "PREREQUISITE",
        "confidence": 0.85,
        "explanation": "Entity1 is foundational knowledge for Entity2",
        "direction": "entity1_to_entity2"
    }""",
    "EQUIVALENT": """{
        "relationship_type": "EQUIVALENT", 
        "confidence": 0.95,
        "explanation": "Both entities refer to the same concept",
        "direction": "bidirectional"
    }""",
    "RELATED": """{
        "relationship_type": "RELATED",
        "confidence": 0.75,
        "explanation": "Entities are conceptually related",
        "direction": "bidirectional"
    }""",
    "UNRELATED": """{
        "relationship_type": "UNRELATED",
        "confidence": 0.9,
        "explanation": "No meaningful relationship exists",
        "direction": "none"
    }"""
}
