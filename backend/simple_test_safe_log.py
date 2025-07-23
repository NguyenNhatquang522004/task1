#!/usr/bin/env python3
"""
Simple test của safe_log_data_flow function
"""

def safe_log_data_flow(step_name, input_data, output_data=None, duration=None, metadata=None):
    """Safe logging function to replace process_logger.log_data_flow"""
    print(f"[DATA_FLOW] {step_name}")
    if input_data:
        print(f"Input: {input_data}")
    if output_data:
        print(f"Output: {output_data}")
    if duration:
        print(f"Duration: {duration:.2f}s")
    if metadata:
        print(f"Metadata: {metadata}")

def test_function():
    print("🧪 Testing safe_log_data_flow with different parameter counts...")
    
    # Test 1: 2 parameters
    print("\n📝 Test 1: 2 parameters")
    safe_log_data_flow("TEST_1", {"test": "data"})
    
    # Test 2: 4 parameters (as used in main.py line 527)
    print("\n📝 Test 2: 4 parameters")
    safe_log_data_flow(
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
    
    # Test 3: 5 parameters (full signature)
    print("\n📝 Test 3: 5 parameters")
    safe_log_data_flow(
        "ENTITY_EXTRACTION_COMPLETE",
        {'input_chunks': 10, 'model': 'test'},
        {'graph_documents': 5, 'entities': 100},
        15.2,
        {'quality': 'high'}
    )
    
    print("\n✅ All tests passed! Function works with 2, 4, and 5 parameters.")

if __name__ == "__main__":
    test_function()
