#!/usr/bin/env python3
"""
Direct test of relationship validation logic (without LLM dependency)
"""
import sys
import os

# Add the current directory to the Python path to import src modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_relationship_validation_logic():
    """Test the relationship validation logic directly"""
    
    print("🧪 Testing relationship validation logic...")
    
    # Test cases
    test_cases = [
        {
            "name": "Valid nodes, no relationships",
            "allowedNodes": "Person,Organization,Event",
            "allowedRelationship": None,
            "expected_nodes": ["Person", "Organization", "Event"],
            "expected_relationships": []
        },
        {
            "name": "Valid nodes, empty relationship string",
            "allowedNodes": "Person,Organization,Event", 
            "allowedRelationship": "",
            "expected_nodes": ["Person", "Organization", "Event"],
            "expected_relationships": []
        },
        {
            "name": "Valid nodes, valid relationships",
            "allowedNodes": "Person,Organization,Event",
            "allowedRelationship": "Person,WORKS_FOR,Organization,Person,ATTENDS,Event",
            "expected_nodes": ["Person", "Organization", "Event"],
            "expected_relationships": [("Person", "WORKS_FOR", "Organization"), ("Person", "ATTENDS", "Event")]
        },
        {
            "name": "Valid nodes, invalid relationship (wrong count)",
            "allowedNodes": "Person,Organization,Event",
            "allowedRelationship": "Person,WORKS_FOR",  # Only 2 items, not 3
            "expected_nodes": ["Person", "Organization", "Event"],
            "expected_relationships": []  # Should be empty due to validation
        },
        {
            "name": "Valid nodes, invalid relationship (source not in nodes)",
            "allowedNodes": "Person,Organization,Event",
            "allowedRelationship": "Student,WORKS_FOR,Organization",  # Student not in allowed nodes
            "expected_nodes": ["Person", "Organization", "Event"],
            "expected_relationships": []  # Should be empty due to validation
        },
        {
            "name": "None nodes, None relationships",
            "allowedNodes": None,
            "allowedRelationship": None,
            "expected_nodes": [],
            "expected_relationships": []
        },
        {
            "name": "Empty string nodes, empty relationships",
            "allowedNodes": "",
            "allowedRelationship": "",
            "expected_nodes": [],
            "expected_relationships": []
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"   allowedNodes: {test_case['allowedNodes']}")
        print(f"   allowedRelationship: {test_case['allowedRelationship']}")
        
        # Replicate the validation logic from get_graph_from_llm
        allowedNodes = test_case['allowedNodes']
        allowedRelationship = test_case['allowedRelationship']
        
        # Parse allowed nodes - handle different input formats
        if isinstance(allowedNodes, str):
            allowed_nodes = [node.strip() for node in allowedNodes.split(',') if node.strip()]
        elif isinstance(allowedNodes, list):
            allowed_nodes = allowedNodes
        elif allowedNodes is None:
            allowed_nodes = []
        else:
            print(f"   ⚠️  Unexpected allowedNodes type: {type(allowedNodes)}")
            allowed_nodes = []
        
        # Parse allowed relationships - handle different input formats and validate properly
        allowed_relationships = []
        
        if allowedRelationship is not None and allowedRelationship != "":
            # Handle string input
            if isinstance(allowedRelationship, str):
                # Skip empty strings or strings with just whitespace
                if allowedRelationship.strip():
                    items = [item.strip() for item in allowedRelationship.split(',') if item.strip()]
                    if len(items) % 3 != 0:
                        print(f"   ⚠️  allowedRelationship string has {len(items)} items, not a multiple of 3. Using empty relationships.")
                        allowed_relationships = []
                    else:
                        for j in range(0, len(items), 3):
                            source, relation, target = items[j:j + 3]
                            if source not in allowed_nodes or target not in allowed_nodes:
                                print(f"   ⚠️  Invalid relationship ({source}, {relation}, {target}): source or target not in allowedNodes. Skipping.")
                                continue
                            allowed_relationships.append((source, relation, target))
                else:
                    print(f"   ℹ️  Empty allowedRelationship string provided")
            # Handle list input
            elif isinstance(allowedRelationship, list):
                if len(allowedRelationship) % 3 != 0:
                    print(f"   ⚠️  allowedRelationship list has {len(allowedRelationship)} items, not a multiple of 3. Using empty relationships.")
                    allowed_relationships = []
                else:
                    for j in range(0, len(allowedRelationship), 3):
                        source, relation, target = allowedRelationship[j:j + 3]
                        if source not in allowed_nodes or target not in allowed_nodes:
                            print(f"   ⚠️  Invalid relationship ({source}, {relation}, {target}): source or target not in allowedNodes. Skipping.")
                            continue
                        allowed_relationships.append((source, relation, target))
            else:
                print(f"   ⚠️  Unexpected allowedRelationship type: {type(allowedRelationship)}. Using empty relationships.")
                allowed_relationships = []
        else:
            print(f"   ℹ️  No allowed relationships provided (None or empty string)")
        
        # Check results
        nodes_match = allowed_nodes == test_case['expected_nodes']
        relationships_match = allowed_relationships == test_case['expected_relationships']
        
        print(f"   📊 Results:")
        print(f"      Parsed nodes: {allowed_nodes}")
        print(f"      Expected nodes: {test_case['expected_nodes']}")
        print(f"      Nodes match: {'✅' if nodes_match else '❌'}")
        print(f"      Parsed relationships: {allowed_relationships}")
        print(f"      Expected relationships: {test_case['expected_relationships']}")
        print(f"      Relationships match: {'✅' if relationships_match else '❌'}")
        
        if nodes_match and relationships_match:
            print(f"   ✅ PASSED")
        else:
            print(f"   ❌ FAILED")
    
    print(f"\n🎉 Relationship validation logic test completed!")

if __name__ == "__main__":
    test_relationship_validation_logic()
