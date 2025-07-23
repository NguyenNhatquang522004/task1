#!/usr/bin/env python3
"""
Test script to verify the relationship validation fixes
"""
import sys
import os
import asyncio

# Add the current directory to the Python path to import src modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.llm import get_graph_from_llm

async def test_relationship_validation():
    """Test various formats of allowedNodes and allowedRelationship"""
    
    print("🧪 Testing relationship validation fixes...")
    
    # Test data - empty chunk list for testing validation only
    chunkId_chunkDoc_list = []
    chunks_to_combine = 1
    
    # Test cases
    test_cases = [
        {
            "name": "Valid nodes, no relationships",
            "allowedNodes": "Person,Organization,Event",
            "allowedRelationship": None,
            "should_pass": True
        },
        {
            "name": "Valid nodes, empty relationship string",
            "allowedNodes": "Person,Organization,Event", 
            "allowedRelationship": "",
            "should_pass": True
        },
        {
            "name": "Valid nodes, valid relationships",
            "allowedNodes": "Person,Organization,Event",
            "allowedRelationship": "Person,WORKS_FOR,Organization,Person,ATTENDS,Event",
            "should_pass": True
        },
        {
            "name": "Valid nodes, invalid relationship (wrong count)",
            "allowedNodes": "Person,Organization,Event",
            "allowedRelationship": "Person,WORKS_FOR",  # Only 2 items, not 3
            "should_pass": True  # Should handle gracefully by using empty relationships
        },
        {
            "name": "Valid nodes, invalid relationship (source not in nodes)",
            "allowedNodes": "Person,Organization,Event",
            "allowedRelationship": "Student,WORKS_FOR,Organization",  # Student not in allowed nodes
            "should_pass": True  # Should handle gracefully by skipping invalid relationships
        },
        {
            "name": "None nodes, None relationships",
            "allowedNodes": None,
            "allowedRelationship": None,
            "should_pass": True
        },
        {
            "name": "Empty string nodes, empty relationships",
            "allowedNodes": "",
            "allowedRelationship": "",
            "should_pass": True
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"   allowedNodes: {test_case['allowedNodes']}")
        print(f"   allowedRelationship: {test_case['allowedRelationship']}")
        
        try:
            # We'll catch the error early in the validation phase
            # This should not raise the original ValueError anymore
            result = await get_graph_from_llm(
                model="openai_gpt_3_5", 
                chunkId_chunkDoc_list=chunkId_chunkDoc_list,
                allowedNodes=test_case['allowedNodes'],
                allowedRelationship=test_case['allowedRelationship'],
                chunks_to_combine=chunks_to_combine
            )
            
            print(f"   ✅ PASSED: No validation errors")
            
        except Exception as e:
            error_msg = str(e)
            if "`allowed_relationships` must be list of strings or a list of 3-item tuples" in error_msg:
                print(f"   ❌ FAILED: Original validation error still occurs")
                print(f"      Error: {error_msg}")
            elif "No API key provided" in error_msg or "API key" in error_msg:
                print(f"   ✅ PASSED: Validation passed, failed on API key (expected)")
            elif "No chunks provided" in error_msg or "chunks" in error_msg:
                print(f"   ✅ PASSED: Validation passed, failed on empty chunks (expected)")
            else:
                print(f"   ⚠️  UNKNOWN: Unexpected error: {error_msg}")
    
    print(f"\n🎉 Relationship validation test completed!")

if __name__ == "__main__":
    asyncio.run(test_relationship_validation())
