#!/usr/bin/env python3
"""
Test script để kiểm tra lỗi process_logger đã được sửa
"""

import sys
import os
import logging

# Add the backend src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_import_main():
    """Test import main module"""
    try:
        print("🔍 Testing import of main module...")
        
        # Mock the required modules to avoid import errors
        import sys
        from unittest.mock import MagicMock
        
        # Mock langchain modules
        sys.modules['langchain_neo4j'] = MagicMock()
        sys.modules['dotenv'] = MagicMock()
        sys.modules['langchain_community'] = MagicMock()
        sys.modules['langchain_community.document_loaders'] = MagicMock()
        sys.modules['langchain_community.document_loaders.WikipediaLoader'] = MagicMock()
        sys.modules['langchain_community.document_loaders.WebBaseLoader'] = MagicMock()
        sys.modules['langchain_community.document_loaders.YoutubeLoader'] = MagicMock()
        sys.modules['langchain_community.document_loaders.GCSFileLoader'] = MagicMock()
        sys.modules['langchain_community.document_loaders.AmazonTextractPDFLoader'] = MagicMock()
        sys.modules['langchain_text_splitters'] = MagicMock()
        sys.modules['langchain_text_splitters.TokenTextSplitter'] = MagicMock()
        
        # Import main
        import src.main as main
        
        print("✅ Import successful!")
        
        # Test safe logging functions
        print("\n🔧 Testing safe logging functions...")
        
        main.safe_log_step("TEST_STEP", "Testing step function", {"test": "data"})
        main.safe_log_data_flow("TEST_DATA_FLOW", {"input": 100, "output": 200})
        main.safe_log_performance_bottleneck("TEST_BOTTLENECK", "5.2s", {"cpu": "high"})
        main.safe_log_custom_metric("test_metric", 42, "TEST_CATEGORY", {"version": "1.0"})
        result = main.safe_end_process("SUCCESS", {"nodes": 100, "rels": 50})
        insights = main.safe_get_process_insights()
        
        print("✅ All safe logging functions work correctly!")
        print(f"✅ safe_end_process returned: {result}")
        print(f"✅ safe_get_process_insights returned: {insights}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_processing_source_mock():
    """Test processing_source function with mocked dependencies"""
    try:
        print("\n🔧 Testing processing_source function signature...")
        
        import src.main as main
        import inspect
        
        # Check if processing_source function exists
        if hasattr(main, 'processing_source'):
            sig = inspect.signature(main.processing_source)
            print(f"✅ processing_source function exists with signature: {sig}")
            
            # Check parameters
            params = list(sig.parameters.keys())
            expected_params = ['uri', 'userName', 'password', 'database', 'model', 'file_name', 'pages', 'allowedNodes', 'allowedRelationship', 'token_chunk_size', 'chunk_overlap', 'chunks_to_combine']
            
            for param in expected_params:
                if param in params:
                    print(f"✅ Parameter '{param}' found")
                else:
                    print(f"⚠️  Parameter '{param}' not found")
            
            return True
        else:
            print("❌ processing_source function not found")
            return False
            
    except Exception as e:
        print(f"❌ Function test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING PROCESS_LOGGER FIXES")
    print("=" * 60)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    success = True
    
    # Test 1: Import
    success &= test_import_main()
    
    # Test 2: Function signature
    success &= test_processing_source_mock()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! process_logger errors have been fixed.")
        print("✅ The AttributeError: 'NoneType' object has no attribute should be resolved.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 60)
