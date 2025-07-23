"""
Folder Node Creator
Tạo các folder nodes với label = folder_name
"""
import logging
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

class FolderNodeCreator:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        self.logger = logging.getLogger(__name__)
    
    def close(self):
        """Đóng kết nối database"""
        self.driver.close()
    
    def create_folder_node(self, folder_name):
        """Tạo một folder node với label = folder_name"""
        # Escape special characters in folder name for Cypher
        safe_label = folder_name.replace(' ', '_').replace('-', '_')
        
        query = f"""
        MERGE (f:`{folder_name}` {{name: $folder_name}})
        SET f.course_code = '',
            f.created_at = datetime(),
            f.created_by = 'folder-course-linker'
        RETURN f.name AS name, head(labels(f)) AS label
        """
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query, folder_name=folder_name)
            record = result.single()
            if record:
                self.logger.info(f"✅ Created folder node: {record['name']} with label {record['label']}")
                return True
            return False
    
    def create_all_folder_nodes(self, folder_names):
        """Tạo tất cả folder nodes từ danh sách folder_names"""
        created_count = 0
        failed_count = 0
        
        for folder_name in folder_names:
            try:
                if self.create_folder_node(folder_name):
                    created_count += 1
                else:
                    failed_count += 1
                    self.logger.warning(f"❌ Failed to create folder node: {folder_name}")
            except Exception as e:
                failed_count += 1
                self.logger.error(f"❌ Error creating folder node {folder_name}: {e}")
        
        self.logger.info(f"📊 Folder node creation summary: {created_count} created, {failed_count} failed")
        return created_count, failed_count
    
    def get_folder_names_from_documents(self):
        """Lấy danh sách folder_name từ Document nodes"""
        query = """
        MATCH (d:Document)
        WHERE d.folder_name IS NOT NULL AND trim(d.folder_name) <> ''
        RETURN DISTINCT trim(d.folder_name) AS folder_name
        ORDER BY folder_name
        """
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query)
            return [record['folder_name'] for record in result]
    
    def check_existing_folder_nodes(self):
        """Kiểm tra folder nodes đã tồn tại"""
        query = """
        MATCH (f)
        WHERE f.created_by = 'folder-course-linker'
        RETURN f.name AS name, head(labels(f)) AS label
        ORDER BY f.name
        """
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query)
            return [{'name': record['name'], 'label': record['label']} for record in result]
    
    def delete_all_folder_nodes(self):
        """Xóa tất cả folder nodes đã tạo bởi tool này"""
        query = """
        MATCH (f)
        WHERE f.created_by = 'folder-course-linker'
        DELETE f
        RETURN count(f) AS deleted_count
        """
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query)
            deleted_count = result.single()['deleted_count']
            self.logger.info(f"🗑️ Deleted {deleted_count} folder nodes")
            return deleted_count
    
    def run_creation_process(self):
        """Chạy toàn bộ quá trình tạo folder nodes"""
        print("🚀 Starting folder node creation process...")
        
        # 1. Lấy folder names từ documents
        folder_names = self.get_folder_names_from_documents()
        print(f"📁 Found {len(folder_names)} unique folder names: {folder_names}")
        
        # 2. Kiểm tra nodes đã tồn tại
        existing_nodes = self.check_existing_folder_nodes()
        if existing_nodes:
            print(f"⚠️ Found {len(existing_nodes)} existing folder nodes")
            for node in existing_nodes:
                print(f"   - {node['label']}: {node['name']}")
            
            response = input("Do you want to delete existing nodes and recreate? (y/N): ")
            if response.lower() == 'y':
                self.delete_all_folder_nodes()
        
        # 3. Tạo folder nodes
        if folder_names:
            created_count, failed_count = self.create_all_folder_nodes(folder_names)
            print(f"✅ Creation completed: {created_count} created, {failed_count} failed")
        else:
            print("❌ No folder names found in documents")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    creator = FolderNodeCreator()
    try:
        creator.run_creation_process()
    finally:
        creator.close()
