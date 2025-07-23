"""
Configuration for Folder Course Linker
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Neo4j Configuration
NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')
NEO4J_DATABASE = os.getenv('NEO4J_DATABASE', 'neo4j')

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Project Configuration
PROJECT_NAME = 'Folder Course Linker'
VERSION = '1.0.0'

# Relationship Configuration
COURSE_TO_FOLDER_RELATIONSHIP = 'POINT_TO'

# Folder name mappings (if needed)
FOLDER_NAME_MAPPINGS = {
    'đề cương': 'de_cuong',
    'giáo trình': 'giao_trinh', 
    'tham khảo': 'tham_khao'
}
