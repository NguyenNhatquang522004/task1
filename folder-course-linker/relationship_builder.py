"""
Relationship Builder
Tạo relationships POINT_TO từ Course khung sườn đến folder nodes
"""
import logging
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE, COURSE_TO_FOLDER_RELATIONSHIP

class RelationshipBuilder:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        self.logger = logging.getLogger(__name__)
    
    def close(self):
        """Đóng kết nối database"""
        self.driver.close()
    
    def create_course_to_folder_relationships(self):
        """Tạo relationships từ mỗi Course khung sườn đến các folder nodes riêng của nó"""
        # Bước 1: Lấy danh sách courses và folder names
        courses_query = """
        MATCH (c:Course)
        WHERE size(labels(c)) = 1
        RETURN c.code AS code
        ORDER BY c.code
        """
        
        folder_names_query = """
        MATCH (d:Document)
        WHERE d.folder_name IS NOT NULL AND trim(d.folder_name) <> ''
        RETURN DISTINCT trim(d.folder_name) AS folder_name
        ORDER BY folder_name
        """
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Lấy courses
            courses_result = session.run(courses_query)
            courses = [record['code'] for record in courses_result]
            
            # Lấy folder names
            folder_names_result = session.run(folder_names_query)
            folder_names = [record['folder_name'] for record in folder_names_result]
            
            self.logger.info(f"Found {len(courses)} courses and {len(folder_names)} folder types")
            
            # Bước 2: Tạo folder nodes cho mỗi course
            total_created = 0
            for course_code in courses:
                for folder_name in folder_names:
                    # Tạo node với label = folder_name
                    create_node_query = f"""
                    MERGE (f:`{folder_name}` {{name: $folder_name, course_code: $course_code}})
                    SET f.created_at = datetime(),
                        f.created_by = 'folder-course-linker'
                    RETURN f
                    """
                    
                    # Tạo relationship
                    create_rel_query = f"""
                    MATCH (c:Course {{code: $course_code}})
                    WHERE size(labels(c)) = 1
                    MATCH (f:`{folder_name}` {{name: $folder_name, course_code: $course_code}})
                    MERGE (c)-[:{COURSE_TO_FOLDER_RELATIONSHIP}]->(f)
                    RETURN count(*) AS created
                    """
                    
                    try:
                        # Tạo node
                        session.run(create_node_query, folder_name=folder_name, course_code=course_code)
                        # Tạo relationship
                        rel_result = session.run(create_rel_query, course_code=course_code, folder_name=folder_name)
                        total_created += rel_result.single()['created']
                        
                    except Exception as e:
                        self.logger.error(f"Error creating node/relationship for {course_code} -> {folder_name}: {e}")
            
            total_folder_nodes = len(courses) * len(folder_names)
            
            self.logger.info(f"✅ Created relationships: {len(courses)} courses × {len(folder_names)} folder types = {total_folder_nodes} folder nodes with {total_created} relationships")
            return len(courses), total_folder_nodes, total_created
    
    def get_relationship_statistics(self):
        """Lấy thống kê relationships hiện tại"""
        query = f"""
        MATCH (c:Course)-[r:{COURSE_TO_FOLDER_RELATIONSHIP}]->(f)
        WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
        RETURN count(r) AS total_relationships,
               count(DISTINCT c) AS course_count,
               count(DISTINCT f) AS folder_count
        """
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query)
            record = result.single()
            return {
                'total_relationships': record['total_relationships'],
                'course_count': record['course_count'],
                'folder_count': record['folder_count']
            }
    
    def get_relationship_details(self, limit=50):
        """Lấy chi tiết relationships"""
        query = f"""
        MATCH (c:Course)-[r:{COURSE_TO_FOLDER_RELATIONSHIP}]->(f)
        WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
        RETURN c.code AS course_code,
               c.name AS course_name,
               f.name AS folder_name,
               head(labels(f)) AS folder_label,
               type(r) AS relationship_type
        ORDER BY c.code, f.name
        LIMIT $limit
        """
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query, limit=limit)
            return [{
                'course_code': record['course_code'],
                'course_name': record['course_name'],
                'folder_name': record['folder_name'],
                'folder_label': record['folder_label'],
                'relationship_type': record['relationship_type']
            } for record in result]
    
    def delete_all_relationships(self):
        """Xóa tất cả relationships POINT_TO"""
        query = f"""
        MATCH (c:Course)-[r:{COURSE_TO_FOLDER_RELATIONSHIP}]->(f)
        WHERE size(labels(c)) = 1 AND f.created_by = 'folder-course-linker'
        DELETE r
        RETURN count(r) AS deleted_count
        """
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query)
            deleted_count = result.single()['deleted_count']
            self.logger.info(f"🗑️ Deleted {deleted_count} relationships")
            return deleted_count
    
    def validate_relationships(self):
        """Kiểm tra tính đúng đắn của relationships"""
        # Lấy số lượng course khung sườn
        course_query = "MATCH (c:Course) WHERE size(labels(c)) = 1 RETURN count(c) AS count"
        
        # Lấy số folder_name unique từ documents
        folder_types_query = """
        MATCH (d:Document)
        WHERE d.folder_name IS NOT NULL AND trim(d.folder_name) <> ''
        RETURN count(DISTINCT trim(d.folder_name)) AS count
        """
        
        # Lấy số folder nodes thực tế
        folder_nodes_query = "MATCH (f) WHERE f.created_by = 'folder-course-linker' RETURN count(f) AS count"
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            course_count = session.run(course_query).single()['count']
            folder_types_count = session.run(folder_types_query).single()['count']
            folder_nodes_count = session.run(folder_nodes_query).single()['count']
            
            # Tính toán expected
            expected_folder_nodes = course_count * folder_types_count
            expected_relationships = course_count * folder_types_count
            
            # Lấy số relationships thực tế
            stats = self.get_relationship_statistics()
            actual_relationships = stats['total_relationships']
            
            return {
                'course_count': course_count,
                'folder_types_count': folder_types_count,
                'expected_folder_nodes': expected_folder_nodes,
                'actual_folder_nodes': folder_nodes_count,
                'expected_relationships': expected_relationships,
                'actual_relationships': actual_relationships,
                'folder_nodes_valid': folder_nodes_count == expected_folder_nodes,
                'relationships_valid': actual_relationships == expected_relationships,
                'is_valid': (folder_nodes_count == expected_folder_nodes and 
                           actual_relationships == expected_relationships)
            }
    
    def run_relationship_building(self):
        """Chạy toàn bộ quá trình tạo relationships"""
        print("🔗 Starting relationship building process...")
        
        # 1. Kiểm tra relationships hiện tại
        stats = self.get_relationship_statistics()
        if stats['total_relationships'] > 0:
            print(f"⚠️ Found {stats['total_relationships']} existing relationships")
            response = input("Do you want to delete existing relationships and recreate? (y/N): ")
            if response.lower() == 'y':
                self.delete_all_relationships()
        
        # 2. Tạo relationships
        course_count, folder_count, relationship_count = self.create_course_to_folder_relationships()
        
        # 3. Validate
        validation = self.validate_relationships()
        print(f"\n📊 Relationship Building Results:")
        print(f"   - Courses: {validation['course_count']}")
        print(f"   - Folders: {validation['folder_count']}")
        print(f"   - Expected relationships: {validation['expected_relationships']}")
        print(f"   - Actual relationships: {validation['actual_relationships']}")
        print(f"   - Status: {'✅ Valid' if validation['is_valid'] else '❌ Invalid'}")
        
        # 4. Show sample relationships
        print(f"\n🔗 Sample relationships:")
        details = self.get_relationship_details(10)
        for detail in details[:5]:
            print(f"   - {detail['course_code']} → {detail['folder_name']}")
        if len(details) > 5:
            print(f"   ... and {len(details)-5} more")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    builder = RelationshipBuilder()
    try:
        builder.run_relationship_building()
    finally:
        builder.close()
