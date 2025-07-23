"""
Test script để kiểm tra logic schema validation mới
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.main import get_schema_info_from_folder_name, load_additional_instructions

def test_schema_detection():
    """Test logic auto-detect schema từ folder_name"""
    
    test_cases = [
        {
            'folder_name': 'Đề cương HP Lập Trình Windows',
            'expected_schema': 'decuong'
        },
        {
            'folder_name': 'Giáo trình chính thức Java',
            'expected_schema': 'giaotrinh'
        },
        {
            'folder_name': 'Ebook Programming', 
            'expected_schema': 'ebook'
        },
        {
            'folder_name': 'Random folder',
            'expected_schema': 'default'
        }
    ]
    
    print("🧪 Testing schema detection logic:")
    for case in test_cases:
        result = get_schema_info_from_folder_name(case['folder_name'])
        print(f"  📁 Folder: '{case['folder_name']}'")
        print(f"     ✅ Expected: {case['expected_schema']}")
        print(f"     📊 Got: {result['schema']}")
        print(f"     🔗 Triplet: {result['triplet']}")
        if result.get('additional_instructions_file'):
            print(f"     📝 Instructions file: {result['additional_instructions_file']}")
        print()

def test_document_schema_logic():
    """Simulate logic kiểm tra schema từ document"""
    
    print("🔍 Testing document schema checking logic:")
    
    # Simulate existing document có schema properties
    existing_document = {
        'schema': 'decuong',
        'triplet': 'decuong',
        'additional_instructions': 'Instructions for decuong schema...'
    }
    
    # Interface input
    interface_schema = 'giaotrinh'  
    interface_additional_instructions = 'Interface instructions...'
    
    # Logic kiểm tra (giống như trong main.py)
    effective_schema = interface_schema
    effective_triplet = None
    effective_additional_instructions = interface_additional_instructions
    
    if existing_document:
        existing_schema = existing_document.get('schema')
        existing_triplet = existing_document.get('triplet')
        existing_additional_instructions = existing_document.get('additional_instructions')
        
        if existing_schema and str(existing_schema).strip() and str(existing_schema).lower() != 'none':
            effective_schema = existing_schema
            print(f"✅ Using existing schema from document: {effective_schema}")
            
            if existing_triplet and str(existing_triplet).strip() and str(existing_triplet).lower() != 'none':
                effective_triplet = existing_triplet
                print(f"✅ Using existing triplet from document: {effective_triplet}")
            
            if existing_additional_instructions and str(existing_additional_instructions).strip():
                effective_additional_instructions = existing_additional_instructions
                print(f"✅ Using existing additional_instructions from document (length: {len(effective_additional_instructions)} chars)")
        else:
            print(f"⚠️ No valid schema found in document, using schema from interface: {effective_schema}")
    else:
        print(f"⚠️ Document does not exist yet, using schema from interface: {effective_schema}")
    
    print(f"\n🎯 Final effective values:")
    print(f"  - Schema: {effective_schema}")
    print(f"  - Triplet: {effective_triplet}")
    print(f"  - Additional instructions: {len(effective_additional_instructions or '')} chars")

if __name__ == "__main__":
    test_schema_detection()
    print("=" * 50)
    test_document_schema_logic()
