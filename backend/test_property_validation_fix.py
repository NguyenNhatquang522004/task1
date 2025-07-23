"""
Test property validation fixes for Neo4j large property values
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.property_validator import validate_graph_documents_list, truncate_property_value
from src.neo4j_config import get_property_max_length
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_property_truncation():
    """Test basic property truncation"""
    print("Testing property truncation...")
    
    # Test normal property
    large_text = "A" * 15000  # 15KB text
    truncated = truncate_property_value(large_text, property_name="description")
    print(f"Original length: {len(large_text)}")
    print(f"Truncated length: {len(truncated)}")
    print(f"Max allowed for 'description': {get_property_max_length('description')}")
    
    # Test ID property
    large_id = "ID_" + "X" * 1000
    truncated_id = truncate_property_value(large_id, property_name="id")
    print(f"Large ID truncated from {len(large_id)} to {len(truncated_id)}")
    
    # Test aggressive truncation
    aggressive_truncated = truncate_property_value(large_text, property_name="description", aggressive=True)
    print(f"Aggressive truncation: {len(aggressive_truncated)}")
    
    # Test emergency truncation
    emergency_truncated = truncate_property_value(large_text, property_name="description", emergency=True)
    print(f"Emergency truncation: {len(emergency_truncated)}")

def test_mock_graph_document():
    """Test with mock graph document structure"""
    print("\nTesting mock graph document...")
    
    class MockNode:
        def __init__(self):
            self.id = "VERY_LONG_ID_" + "X" * 1000
            self.properties = {
                "description": "A" * 15000,  # Very large description
                "content": "B" * 12000,     # Large content
                "name": "Test Entity",
                "id": "entity_" + "C" * 800  # Large ID
            }
    
    class MockRelationship:
        def __init__(self):
            self.properties = {
                "description": "D" * 8000,
                "weight": 0.5,
                "type": "RELATES_TO"
            }
    
    class MockGraphDocument:
        def __init__(self):
            self.nodes = [MockNode()]
            self.relationships = [MockRelationship()]
    
    # Test normal validation
    docs = [MockGraphDocument()]
    cleaned_docs = validate_graph_documents_list(docs)
    
    print(f"Original node description length: {len(docs[0].nodes[0].properties['description'])}")
    print(f"Cleaned node description length: {len(cleaned_docs[0].nodes[0].properties['description'])}")
    
    print(f"Original node ID length: {len(docs[0].nodes[0].id)}")
    print(f"Cleaned node ID length: {len(cleaned_docs[0].nodes[0].id)}")
    
    # Test aggressive validation
    docs_aggressive = [MockGraphDocument()]
    cleaned_aggressive = validate_graph_documents_list(docs_aggressive, aggressive=True)
    print(f"Aggressive cleaned description length: {len(cleaned_aggressive[0].nodes[0].properties['description'])}")
    
    # Test emergency validation
    docs_emergency = [MockGraphDocument()]
    cleaned_emergency = validate_graph_documents_list(docs_emergency, emergency=True)
    print(f"Emergency cleaned description length: {len(cleaned_emergency[0].nodes[0].properties['description'])}")

def simulate_neo4j_error_scenario():
    """Simulate the exact error scenario"""
    print("\nSimulating Neo4j property size error scenario...")
    
    # Create a property value similar to the one that caused the error (13494 bytes)
    problematic_property = "Entity description: " + "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 250
    print(f"Problematic property size: {len(problematic_property)} bytes")
    
    # Test all truncation levels
    normal_truncated = truncate_property_value(problematic_property, property_name="description")
    print(f"Normal truncation: {len(normal_truncated)} bytes")
    
    aggressive_truncated = truncate_property_value(problematic_property, property_name="description", aggressive=True)
    print(f"Aggressive truncation: {len(aggressive_truncated)} bytes")
    
    emergency_truncated = truncate_property_value(problematic_property, property_name="description", emergency=True)
    print(f"Emergency truncation: {len(emergency_truncated)} bytes")
    
    # All of these should be well under Neo4j limits
    print(f"All truncated values are under 8000 bytes: {all(len(t) < 8000 for t in [normal_truncated, aggressive_truncated, emergency_truncated])}")

if __name__ == "__main__":
    print("=== Property Validation Fix Tests ===")
    test_property_truncation()
    test_mock_graph_document()
    simulate_neo4j_error_scenario()
    print("\n=== Tests Completed ===")
    print("The property validation fixes should now prevent 'Property value is too large to index' errors.")
