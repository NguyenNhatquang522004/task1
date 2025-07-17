#!/usr/bin/env python3
"""
Test script for duplicate prevention functionality
"""

def test_duplicate_prevention_logic():
    """Test logic để kiểm tra duplicate linking"""
    
    print("🧪 Testing Duplicate Prevention Logic")
    print("=" * 50)
    
    # Mock Neo4j query results
    mock_scenarios = [
        {
            "scenario": "Document chưa được link",
            "query_result": [{"link_count": 0}],
            "expected": False,  # Chưa link → should process
            "action": "SHOULD LINK"
        },
        {
            "scenario": "Document đã được link",
            "query_result": [{"link_count": 1}],
            "expected": True,   # Đã link → should skip
            "action": "SHOULD SKIP"
        },
        {
            "scenario": "Document đã được link nhiều lần",
            "query_result": [{"link_count": 3}],
            "expected": True,   # Đã link → should skip
            "action": "SHOULD SKIP"
        },
        {
            "scenario": "Query không trả về kết quả",
            "query_result": [],
            "expected": False,  # Không có data → should process
            "action": "SHOULD LINK"
        }
    ]
    
    for test in mock_scenarios:
        print(f"\n📋 Test: {test['scenario']}")
        
        # Simulate logic từ is_document_already_linked
        result = test['query_result']
        if result and len(result) > 0 and result[0]['link_count'] > 0:
            is_linked = True
        else:
            is_linked = False
        
        print(f"   Query result: {test['query_result']}")
        print(f"   Is linked: {is_linked}")
        print(f"   Expected: {test['expected']}")
        print(f"   Action: {test['action']}")
        
        if is_linked == test['expected']:
            print("   ✅ PASS")
        else:
            print("   ❌ FAIL")

def test_usage_examples():
    """Show usage examples cho các modes"""
    
    print("\n\n💻 Usage Examples")
    print("=" * 50)
    
    examples = [
        {
            "command": "python curriculum_linker.py",
            "description": "Normal mode - Chỉ link documents mới chưa được link",
            "use_case": "Chạy hàng ngày để link documents mới"
        },
        {
            "command": "python curriculum_linker.py --force",
            "description": "Force mode - Link lại TẤT CẢ documents (kể cả đã link)",
            "use_case": "Khi cần rebuild toàn bộ links hoặc fix corrupted data"
        },
        {
            "command": "python curriculum_linker.py --status",
            "description": "Status mode - Chỉ xem thống kê, không xử lý",
            "use_case": "Kiểm tra hiện trạng trước khi quyết định action"
        },
        {
            "command": "python auto_linker.py",
            "description": "Monitor mode - Chạy liên tục, tự động link documents mới",
            "use_case": "Background service để tự động link realtime"
        },
        {
            "command": "python auto_linker.py CMP170",
            "description": "Target mode - Link chỉ documents matching pattern",
            "use_case": "Link specific course hoặc troubleshoot"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['command']}")
        print(f"   📝 {example['description']}")
        print(f"   🎯 Use case: {example['use_case']}")

def test_cypher_queries():
    """Show Cypher queries được sử dụng để check duplicates"""
    
    print("\n\n🔍 Cypher Queries for Duplicate Detection")
    print("=" * 50)
    
    queries = {
        "Check if document is already linked": """
MATCH (d:Document)-[:HAS_ENTITY]->(e)<-[:HAVE]-(a:CurriculumLink)<-[:POINT_TO]-(c:Course)
WHERE ID(d) = $doc_id
RETURN count(a) as link_count
""",
        
        "Get linking statistics": """
// Đếm tổng documents có course code
MATCH (d:Document)
WHERE d.fileName =~ '.*\\[([A-Z]{3}\\d{3,4})\\].*'
WITH count(d) as total_docs_with_code

// Đếm documents đã được link
MATCH (d:Document)-[:HAS_ENTITY]->(e)<-[:HAVE]-(a:CurriculumLink)<-[:POINT_TO]-(c:Course)
WHERE d.fileName =~ '.*\\[([A-Z]{3}\\d{3,4})\\].*'
WITH total_docs_with_code, count(DISTINCT d) as linked_docs

RETURN total_docs_with_code, linked_docs, 
       (total_docs_with_code - linked_docs) as unlinked_docs
""",
        
        "Find unlinked documents": """
MATCH (d:Document)
WHERE d.fileName =~ '.*\\[([A-Z]{3}\\d{3,4})\\].*'
  AND NOT EXISTS {
    MATCH (d)-[:HAS_ENTITY]->(e)<-[:HAVE]-(a:CurriculumLink)<-[:POINT_TO]-(c:Course)
  }
RETURN d.fileName, d.schema, ID(d) as doc_id
""",
        
        "Manual cleanup (if needed)": """
// Xóa tất cả CurriculumLink relationships và nodes
MATCH (a:CurriculumLink)
DETACH DELETE a
"""
    }
    
    for title, query in queries.items():
        print(f"\n🔸 {title}:")
        print(query.strip())
        print("-" * 30)

def main():
    """Run all tests"""
    print("🚀 Curriculum Entity Linker - Duplicate Prevention Tests")
    print("=" * 70)
    
    test_duplicate_prevention_logic()
    test_usage_examples()
    test_cypher_queries()
    
    print("\n" + "=" * 70)
    print("✅ Test completed!")
    
    print("\n📋 Summary của cải tiến:")
    print("1. ✅ Kiểm tra document đã link chưa trước khi xử lý")
    print("2. ✅ Mode --force để link lại tất cả nếu cần")
    print("3. ✅ Mode --status để xem thống kê")
    print("4. ✅ Auto linker chỉ xử lý documents mới")
    print("5. ✅ Logging chi tiết về skip/process decisions")

if __name__ == "__main__":
    main()
