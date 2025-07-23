"""
Data Analyzer for Folder Course Linker
Phân tích dữ liệu hiện tại trong Neo4j database
"""
import logging
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

class DataAnalyzer:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI, 
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        self.logger = logging.getLogger(__name__)
    
    def close(self):
        """Đóng kết nối database"""
        self.driver.close()
    
    def get_course_framework_count(self):
        """Đếm số Course khung sườn (chỉ có 1 label là Course)"""
        query = """
        MATCH (c:Course)
        WHERE size(labels(c)) = 1
        RETURN count(c) AS course_count
        """
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query)
            return result.single()['course_count']
    
    def get_course_framework_list(self, limit=20):
        """Lấy danh sách Course khung sườn"""
        query = """
        MATCH (c:Course)
        WHERE size(labels(c)) = 1
        RETURN c.code AS code, c.name AS name
        ORDER BY c.code
        LIMIT $limit
        """
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query, limit=limit)
            return [{'code': record['code'], 'name': record['name']} 
                   for record in result]
    
    def get_folder_names_from_documents(self):
        """Lấy tất cả folder_name unique từ Document nodes"""
        query = """
        MATCH (d:Document)
        WHERE d.folder_name IS NOT NULL AND trim(d.folder_name) <> ''
        RETURN DISTINCT trim(d.folder_name) AS folder_name
        ORDER BY folder_name
        """
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query)
            return [record['folder_name'] for record in result]
    
    def get_document_statistics(self):
        """Thống kê Document nodes"""
        query = """
        MATCH (d:Document)
        WITH d,
             CASE 
                WHEN d.folder_name IS NOT NULL AND trim(d.folder_name) <> '' 
                THEN 'has_folder_name'
                ELSE 'no_folder_name'
             END AS folder_status
        RETURN folder_status, count(d) AS count
        """
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query)
            return {record['folder_status']: record['count'] for record in result}
    
    def check_existing_folder_nodes(self):
        """Kiểm tra các folder nodes đã tồn tại"""
        query = """
        MATCH (f)
        WHERE f.created_by = 'folder-course-linker'
        RETURN head(labels(f)) AS label, f.name AS name, f.course_code AS course_code
        ORDER BY f.name
        """
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query)
            return [{'label': record['label'], 'name': record['name'], 
                    'course_code': record['course_code']} for record in result]
    
    def check_existing_relationships(self):
        """Kiểm tra relationships POINT_TO đã tồn tại"""
        query = """
        MATCH (c:Course)-[r:POINT_TO]->(f)
        WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
        RETURN count(r) AS relationship_count,
               count(DISTINCT c) AS course_count,
               count(DISTINCT f) AS folder_count
        """
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query)
            record = result.single()
            return {
                'relationship_count': record['relationship_count'],
                'course_count': record['course_count'], 
                'folder_count': record['folder_count']
            }
    
    def print_analysis_report(self):
        """In báo cáo phân tích đầy đủ"""
        print("=" * 60)
        print("📊 FOLDER COURSE LINKER - DATA ANALYSIS REPORT")
        print("=" * 60)
        
        # Course framework statistics
        course_count = self.get_course_framework_count()
        print(f"\n🎯 COURSE KHUNG SƯỜN: {course_count} courses")
        
        courses = self.get_course_framework_list(10)
        print("\n📋 Sample courses:")
        for course in courses[:5]:
            print(f"   - {course['code']}: {course['name']}")
        if len(courses) > 5:
            print(f"   ... và {len(courses)-5} courses khác")
        
        # Document statistics
        doc_stats = self.get_document_statistics()
        print(f"\n📄 DOCUMENT STATISTICS:")
        print(f"   - Documents có folder_name: {doc_stats.get('has_folder_name', 0)}")
        print(f"   - Documents không có folder_name: {doc_stats.get('no_folder_name', 0)}")
        
        # Folder names
        folder_names = self.get_folder_names_from_documents()
        print(f"\n📁 FOLDER NAMES ({len(folder_names)} unique):")
        for folder_name in folder_names:
            print(f"   - '{folder_name}'")
        
        # Existing folder nodes
        existing_nodes = self.check_existing_folder_nodes()
        print(f"\n🔗 EXISTING FOLDER NODES: {len(existing_nodes)}")
        for node in existing_nodes:
            print(f"   - {node['label']}: {node['name']} (course_code: {node['course_code']})")
        
        # Existing relationships
        rel_stats = self.check_existing_relationships()
        print(f"\n🔗 EXISTING RELATIONSHIPS:")
        print(f"   - Total POINT_TO relationships: {rel_stats['relationship_count']}")
        print(f"   - Courses involved: {rel_stats['course_count']}")
        print(f"   - Folder nodes involved: {rel_stats['folder_count']}")
        
        expected_relationships = course_count * len(folder_names)
        print(f"\n💭 EXPECTED vs ACTUAL:")
        print(f"   - Expected relationships: {expected_relationships}")
        print(f"   - Actual relationships: {rel_stats['relationship_count']}")
        print(f"   - Status: {'✅ Complete' if rel_stats['relationship_count'] == expected_relationships else '❌ Incomplete'}")
        
        print("=" * 60)

if __name__ == "__main__":
    analyzer = DataAnalyzer()
    try:
        analyzer.print_analysis_report()
    finally:
        analyzer.close()
