#!/usr/bin/env python3
"""
Verification script để kiểm tra relationship patterns
"""

def show_entity_linking_analysis():
    """Phân tích cách entities được link"""
    
    print("🔍 ENTITY LINKING ANALYSIS")
    print("=" * 60)
    
    print("\n📋 Current Behavior:")
    print("-" * 30)
    print("1. Document A: '[CMP170] Đề cương HP...'")
    print("   ↓ HAS_ENTITY")
    print("   ├── Entity1 (__Entity__:Concept {id: 'programming'})")
    print("   ├── Entity2 (__Entity__:Topic {id: 'windows'})")
    print("   ├── Entity3 (__Entity__:Skill {id: 'coding'})")
    print("   └── ... TẤT CẢ entities khác")
    print()
    print("2. CurriculumLink: 'giáo_trình_CMP170_...'")
    print("   ↓ HAVE_TO (TẤT CẢ)")
    print("   ├── Entity1")
    print("   ├── Entity2") 
    print("   ├── Entity3")
    print("   └── ... TẤT CẢ entities từ Document A")

def show_verification_queries():
    """Show queries để verify behavior"""
    
    print("\n\n🔍 VERIFICATION QUERIES")
    print("=" * 60)
    
    queries = {
        "1. Xem entities trong một document cụ thể": """
// Ví dụ với document có filename chứa 'CMP170'
MATCH (d:Document)-[:HAS_ENTITY]->(e:__Entity__)
WHERE d.fileName CONTAINS '[CMP170]'
RETURN d.fileName, 
       labels(e) as entity_labels, 
       e.id as entity_id,
       count(*) as total_entities
""",
        
        "2. Xem CurriculumLink và các entities nó link đến": """
// Xem một CurriculumLink cụ thể
MATCH (a:CurriculumLink)-[:HAVE_TO]->(e:__Entity__)
WHERE a.name CONTAINS 'CMP170'
RETURN a.name,
       labels(e) as entity_labels,
       e.id as entity_id,
       count(*) as linked_entities
""",
        
        "3. Verify full chain từ Course đến Entities": """
// Full chain: Course → CurriculumLink → Entities
MATCH (c:Course)-[:POINT_TO]->(a:CurriculumLink)-[:HAVE_TO]->(e:__Entity__)
WHERE c.code = 'CMP170'
RETURN c.code, c.name,
       a.name as curriculum_link,
       labels(e) as entity_labels,
       count(e) as total_linked_entities
""",
        
        "4. So sánh entities trong Document vs CurriculumLink": """
// Kiểm tra xem CurriculumLink có link đến TẤT CẢ entities của document không
MATCH (d:Document)-[:HAS_ENTITY]->(e1:__Entity__)
WHERE d.fileName CONTAINS '[CMP170]'
WITH d, collect(e1) as doc_entities

MATCH (a:CurriculumLink)-[:HAVE_TO]->(e2:__Entity__)
WHERE a.name CONTAINS 'CMP170'
WITH d, doc_entities, a, collect(e2) as link_entities

RETURN d.fileName,
       a.name,
       size(doc_entities) as entities_in_document,
       size(link_entities) as entities_in_curriculum_link,
       size(doc_entities) = size(link_entities) as all_entities_linked
""",
        
        "5. Tìm entities chưa được link (nếu có)": """
// Entities trong document nhưng KHÔNG có trong CurriculumLink
MATCH (d:Document)-[:HAS_ENTITY]->(e:__Entity__)
WHERE d.fileName CONTAINS '[CMP170]'
  AND NOT EXISTS {
    MATCH (a:CurriculumLink)-[:HAVE_TO]->(e)
    WHERE a.name CONTAINS 'CMP170'
  }
RETURN d.fileName, 
       labels(e) as unlinked_entity_labels,
       e.id as unlinked_entity_id
"""
    }
    
    for title, query in queries.items():
        print(f"\n{title}:")
        print(query.strip())
        print("-" * 50)

def show_expected_results():
    """Show expected results"""
    
    print("\n\n📊 EXPECTED RESULTS")
    print("=" * 60)
    
    print("\n✅ Nếu code hoạt động đúng:")
    print("- Query 2 sẽ trả về TẤT CẢ entities từ document")
    print("- Query 4: entities_in_document = entities_in_curriculum_link")
    print("- Query 4: all_entities_linked = true")
    print("- Query 5: Không trả về kết quả (no unlinked entities)")
    
    print("\n❌ Nếu có vấn đề:")
    print("- Query 4: entities_in_document ≠ entities_in_curriculum_link")
    print("- Query 4: all_entities_linked = false")
    print("- Query 5: Có entities bị missing")

def main():
    """Main function"""
    show_entity_linking_analysis()
    show_verification_queries()
    show_expected_results()
    
    print("\n" + "=" * 60)
    print("🎯 ANSWER TO USER QUESTION:")
    print("=" * 60)
    print("✅ CÓ! CurriculumLink node sẽ có HAVE_TO relationship")
    print("   đến TẤT CẢ entities có label __Entity__ trong document đó.")
    print()
    print("📋 Workflow:")
    print("1. Document A có entities: E1, E2, E3, ...")
    print("2. Tất cả có label __Entity__ và relationship HAS_ENTITY từ Document")
    print("3. CurriculumLink sẽ tạo HAVE_TO đến TẤT CẢ: E1, E2, E3, ...")
    print("4. Không có filtering - lấy hết entities của document đó")

if __name__ == "__main__":
    main()
