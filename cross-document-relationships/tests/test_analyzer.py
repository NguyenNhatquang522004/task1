"""
Tests for cross-document analyzer core functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import json

# Import the module under test
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.core.analyzer import CrossDocumentAnalyzer
from src.constants import RELATIONSHIP_TYPES

class TestCrossDocumentAnalyzer:
    """Test cases for CrossDocumentAnalyzer"""
    
    @pytest.fixture
    def analyzer(self, mock_llm_client, mock_neo4j_driver):
        """Create analyzer instance for testing"""
        return CrossDocumentAnalyzer(
            llm_client=mock_llm_client,
            neo4j_driver=mock_neo4j_driver,
            similarity_threshold=0.75
        )
    
    @pytest.mark.asyncio
    async def test_find_similar_entities_success(self, analyzer, mock_neo4j_driver):
        """Test successful entity pair finding"""
        # Setup mock data
        mock_records = [
            {
                "entity1_id": "e1", "entity1_name": "Python",
                "entity2_id": "e2", "entity2_name": "Programming", 
                "document1": "doc1.pdf", "document2": "doc2.pdf",
                "similarity": 0.85
            }
        ]
        
        mock_session = Mock()
        mock_result = Mock()
        mock_result.__iter__ = Mock(return_value=iter(mock_records))
        mock_session.run.return_value = mock_result
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session
        
        # Test
        result = await analyzer.find_similar_entities(limit=10)
        
        # Assertions
        assert len(result) == 1
        assert result[0]["entity1_name"] == "Python"
        assert result[0]["similarity"] == 0.85
        mock_session.run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_entity_context_success(self, analyzer, mock_neo4j_driver):
        """Test successful entity context retrieval"""
        # Setup mock data
        mock_record = {
            "description": "A programming language",
            "chunk_texts": ["Python is a high-level language", "Used for web development"]
        }
        
        mock_session = Mock()
        mock_result = Mock()
        mock_result.single.return_value = mock_record
        mock_session.run.return_value = mock_result
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session
        
        # Test
        context = await analyzer.get_entity_context("entity_123")
        
        # Assertions
        assert context is not None
        assert "programming language" in context
        assert "Python is a high-level language" in context
    
    @pytest.mark.asyncio
    async def test_get_entity_context_not_found(self, analyzer, mock_neo4j_driver):
        """Test entity context when entity not found"""
        mock_session = Mock()
        mock_result = Mock()
        mock_result.single.return_value = None
        mock_session.run.return_value = mock_result
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session
        
        # Test
        context = await analyzer.get_entity_context("nonexistent")
        
        # Assertions
        assert context is None
    
    @pytest.mark.asyncio
    async def test_analyze_relationship_success(self, analyzer, mock_llm_client, sample_entity_pair, sample_llm_response):
        """Test successful relationship analysis"""
        # Setup mocks
        mock_llm_client.generate_response.return_value = sample_llm_response
        
        # Mock get_entity_context
        with patch.object(analyzer, 'get_entity_context') as mock_get_context:
            mock_get_context.side_effect = [
                "Description: Machine Learning concepts",
                "Description: Deep Learning techniques"
            ]
            
            # Test
            result = await analyzer.analyze_relationship(sample_entity_pair)
            
            # Assertions
            assert result is not None
            assert result["relationship_type"] == "PREREQUISITE"
            assert result["confidence"] == 0.9
            assert result["entity1_name"] == "Machine Learning"
            mock_llm_client.generate_response.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_relationship_missing_context(self, analyzer, sample_entity_pair):
        """Test relationship analysis with missing entity context"""
        # Mock get_entity_context to return None
        with patch.object(analyzer, 'get_entity_context') as mock_get_context:
            mock_get_context.side_effect = [None, "Some context"]
            
            # Test
            result = await analyzer.analyze_relationship(sample_entity_pair)
            
            # Assertions
            assert result is None
    
    @pytest.mark.asyncio
    async def test_analyze_relationship_invalid_llm_response(self, analyzer, mock_llm_client, sample_entity_pair):
        """Test relationship analysis with invalid LLM response"""
        # Setup invalid JSON response
        mock_llm_client.generate_response.return_value = "Invalid JSON response"
        
        with patch.object(analyzer, 'get_entity_context') as mock_get_context:
            mock_get_context.side_effect = ["Context 1", "Context 2"]
            
            # Test
            result = await analyzer.analyze_relationship(sample_entity_pair)
            
            # Assertions
            assert result is None
    
    @pytest.mark.asyncio
    async def test_create_relationship_success(self, analyzer, mock_neo4j_driver, sample_analysis_result):
        """Test successful relationship creation"""
        # Setup mock
        mock_session = Mock()
        mock_result = Mock()
        mock_result.single.return_value = {"relationship": "created"}
        mock_session.run.return_value = mock_result
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session
        
        # Test
        success = await analyzer.create_relationship(sample_analysis_result)
        
        # Assertions
        assert success is True
        mock_session.run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_relationship_failure(self, analyzer, mock_neo4j_driver, sample_analysis_result):
        """Test relationship creation failure"""
        # Setup mock to return None
        mock_session = Mock()
        mock_result = Mock()
        mock_result.single.return_value = None
        mock_session.run.return_value = mock_result
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session
        
        # Test
        success = await analyzer.create_relationship(sample_analysis_result)
        
        # Assertions
        assert success is False
    
    @pytest.mark.asyncio
    async def test_process_batch_success(self, analyzer):
        """Test successful batch processing"""
        entity_pairs = [
            {"entity1_id": "e1", "entity1_name": "Test1", "entity2_id": "e2", "entity2_name": "Test2", 
             "document1": "doc1.pdf", "document2": "doc2.pdf", "similarity": 0.8}
        ]
        
        mock_analysis = {
            "relationship_type": "RELATED", "confidence": 0.8, "explanation": "Test relationship",
            "entity1_id": "e1", "entity2_id": "e2", "entity1_name": "Test1", "entity2_name": "Test2"
        }
        
        with patch.object(analyzer, 'analyze_relationship') as mock_analyze, \
             patch.object(analyzer, 'create_relationship') as mock_create:
            
            mock_analyze.return_value = mock_analysis
            mock_create.return_value = True
            
            # Test
            stats = await analyzer.process_batch(entity_pairs, confidence_threshold=0.7)
            
            # Assertions
            assert stats["total_pairs"] == 1
            assert stats["analyzed"] == 1
            assert stats["created"] == 1
            assert stats["failed"] == 0
    
    @pytest.mark.asyncio
    async def test_process_batch_low_confidence(self, analyzer):
        """Test batch processing with low confidence results"""
        entity_pairs = [
            {"entity1_id": "e1", "entity1_name": "Test1", "entity2_id": "e2", "entity2_name": "Test2",
             "document1": "doc1.pdf", "document2": "doc2.pdf", "similarity": 0.8}
        ]
        
        mock_analysis = {
            "relationship_type": "RELATED", "confidence": 0.5, "explanation": "Low confidence",
            "entity1_id": "e1", "entity2_id": "e2"
        }
        
        with patch.object(analyzer, 'analyze_relationship') as mock_analyze:
            mock_analyze.return_value = mock_analysis
            
            # Test with higher confidence threshold
            stats = await analyzer.process_batch(entity_pairs, confidence_threshold=0.7)
            
            # Assertions
            assert stats["analyzed"] == 1
            assert stats["skipped_low_confidence"] == 1
            assert stats["created"] == 0

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__])
