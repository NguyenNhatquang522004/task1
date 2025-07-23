#!/usr/bin/env python3
"""
Test script để kiểm tra lỗi safe_log_data_flow đã được sửa
"""

import sys
import os
import logging

# Add the backend src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_safe_log_data_flow():
    """Test safe_log_data_flow function with different parameters"""
    try:
        print("🔍 Testing safe_log_data_flow function...")
        
        # Mock the required modules to avoid import errors
        import sys
        from unittest.mock import MagicMock
        
        # Mock langchain modules
        sys.modules['langchain_neo4j'] = MagicMock()
        sys.modules['dotenv'] = MagicMock()
        sys.modules['langchain_community'] = MagicMock()
        sys.modules['langchain_community.document_loaders'] = MagicMock()
        
        # Import main and test safe_log_data_flow
        import src.main as main
        
        print("✅ Import successful!")
        
        # Test with 2 parameters (old way)
        print("\n🧪 Test 1: safe_log_data_flow with 2 parameters")
        main.safe_log_data_flow("TEST_STEP", {"input": "data"})
        print("✅ Test 1 passed!")
        
        # Test with 4 parameters (new way - as used in processing_source)
        print("\n🧪 Test 2: safe_log_data_flow with 4 parameters")
        main.safe_log_data_flow(
            "CHUNKING_COMPLETE",
            {
                'input_pages': 5,
                'token_chunk_size': 1024,
                'chunk_overlap': 100
            },
            {
                'total_chunks': 10,
                'chunk_list_length': 10,
                'first_chunk_sample': 'sample'
            },
            2.5  # duration
        )
        print("✅ Test 2 passed!")
        
        # Test with 5 parameters (full signature)
        print("\n🧪 Test 3: safe_log_data_flow with 5 parameters")
        main.safe_log_data_flow(
            "ENTITY_EXTRACTION_COMPLETE",
            {
                'input_chunks': 10,
                'model': 'test_model',
                'chunks_to_combine': 6
            },
            {
                'graph_documents': 5,
                'entities_extracted': 100,
                'relationships_extracted': 50
            },
            15.2,  # duration
            {
                'extraction_quality': 'high',
                'avg_entities_per_chunk': 10,
                'avg_relationships_per_chunk': 5
            }
        )
        print("✅ Test 3 passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING SAFE_LOG_DATA_FLOW FIXES")
    print("=" * 60)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    success = test_safe_log_data_flow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! safe_log_data_flow error has been fixed.")
        print("✅ The TypeError: safe_log_data_flow() takes 2 positional arguments but 4 were given should be resolved.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 60)
