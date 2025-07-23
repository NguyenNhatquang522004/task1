"""
Data Analyzer for Document-Folder Linker
Analyzes current state of documents and folder nodes
"""

import logging
from typing import Dict, List, Tuple, Any
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

class DataAnalyzer:
    def __init__(self):
        """Initialize DataAnalyzer with Neo4j connection"""
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        self.logger = logging.getLogger(__name__)
        
    def close(self):
        """Close database connection"""
        if hasattr(self, 'driver'):
            self.driver.close()
            
    def analyze_documents(self) -> Dict[str, Any]:
        """Analyze document nodes with folder_name and course_code"""
        with self.driver.session() as session:
            # Count documents with required properties
            query_with_props = """
            MATCH (d:Document) 
            WHERE d.folder_name IS NOT NULL AND d.course_code IS NOT NULL
            RETURN count(d) as count_with_props
            """
            
            query_without_props = """
            MATCH (d:Document) 
            WHERE d.folder_name IS NULL OR d.course_code IS NULL
            RETURN count(d) as count_without_props
            """
            
            query_total = """
            MATCH (d:Document) 
            RETURN count(d) as total_count
            """
            
            query_sample = """
            MATCH (d:Document) 
            WHERE d.folder_name IS NOT NULL AND d.course_code IS NOT NULL
            RETURN d.folder_name, d.course_code, d.fileName
            LIMIT 10
            """
            
            query_unique_combinations = """
            MATCH (d:Document) 
            WHERE d.folder_name IS NOT NULL AND d.course_code IS NOT NULL
            RETURN DISTINCT d.folder_name as folder_name, d.course_code as course_code
            ORDER BY d.course_code, d.folder_name
            """
            
            with_props = session.run(query_with_props).single()['count_with_props']
            without_props = session.run(query_without_props).single()['count_without_props']
            total = session.run(query_total).single()['total_count']
            
            sample_records = session.run(query_sample).data()
            unique_combinations = session.run(query_unique_combinations).data()
            
            return {
                'total_documents': total,
                'documents_with_properties': with_props,
                'documents_without_properties': without_props,
                'sample_documents': sample_records,
                'unique_combinations': unique_combinations,
                'unique_combinations_count': len(unique_combinations)
            }
    
    def analyze_folder_nodes(self) -> Dict[str, Any]:
        """Analyze folder nodes with name and course_code"""
        with self.driver.session() as session:
            # Get folder nodes with required properties
            query_folder_stats = """
            MATCH (f)
            WHERE size(labels(f)) = 1 
                AND f.name IS NOT NULL 
                AND f.course_code IS NOT NULL
                AND NOT f:Document AND NOT f:Course
            WITH labels(f)[0] as folder_type, f.name as name, f.course_code as course_code
            RETURN folder_type, name, course_code, count(*) as node_count
            ORDER BY course_code, folder_type
            """
            
            query_total_folders = """
            MATCH (f)
            WHERE size(labels(f)) = 1 
                AND f.name IS NOT NULL 
                AND f.course_code IS NOT NULL
                AND NOT f:Document AND NOT f:Course
            RETURN count(f) as total_folder_count
            """
            
            query_unique_folder_combinations = """
            MATCH (f)
            WHERE size(labels(f)) = 1 
                AND f.name IS NOT NULL 
                AND f.course_code IS NOT NULL
                AND NOT f:Document AND NOT f:Course
            RETURN DISTINCT f.name as name, f.course_code as course_code
            ORDER BY f.course_code, f.name
            """
            
            folder_stats = session.run(query_folder_stats).data()
            total_folders = session.run(query_total_folders).single()['total_folder_count']
            unique_folder_combinations = session.run(query_unique_folder_combinations).data()
            
            return {
                'total_folder_nodes': total_folders,
                'folder_statistics': folder_stats,
                'unique_folder_combinations': unique_folder_combinations,
                'unique_folder_combinations_count': len(unique_folder_combinations)
            }
    
    def analyze_existing_relationships(self) -> Dict[str, Any]:
        """Analyze existing HAVE relationships"""
        with self.driver.session() as session:
            query_have_relationships = """
            MATCH (f)-[:HAVE]->(e)
            WHERE size(labels(f)) = 1 
                AND f.name IS NOT NULL 
                AND f.course_code IS NOT NULL
                AND NOT f:Document AND NOT f:Course
            RETURN count(*) as have_relationships_count
            """
            
            query_sample_relationships = """
            MATCH (f)-[:HAVE]->(e)
            WHERE size(labels(f)) = 1 
                AND f.name IS NOT NULL 
                AND f.course_code IS NOT NULL
                AND NOT f:Document AND NOT f:Course
            RETURN f.name as folder_name, f.course_code as folder_course_code, 
                   labels(e) as entity_labels, e.id as entity_id
            LIMIT 10
            """
            
            have_count = session.run(query_have_relationships).single()['have_relationships_count']
            sample_relationships = session.run(query_sample_relationships).data()
            
            return {
                'existing_have_relationships': have_count,
                'sample_relationships': sample_relationships
            }
    
    def find_matching_pairs(self) -> List[Dict[str, Any]]:
        """Find matching pairs between folder nodes and documents"""
        with self.driver.session() as session:
            query_matches = """
            MATCH (d:Document), (f)
            WHERE d.folder_name IS NOT NULL 
                AND d.course_code IS NOT NULL
                AND size(labels(f)) = 1 
                AND f.name IS NOT NULL 
                AND f.course_code IS NOT NULL
                AND NOT f:Document AND NOT f:Course
                AND f.name = d.folder_name
                AND f.course_code = d.course_code
            RETURN f.name as folder_name, 
                   f.course_code as course_code,
                   labels(f)[0] as folder_label,
                   d.fileName as document_name,
                   count(*) as document_count
            ORDER BY f.course_code, f.name
            """
            
            matches = session.run(query_matches).data()
            return matches
    
    def generate_analysis_report(self) -> str:
        """Generate comprehensive analysis report"""
        doc_analysis = self.analyze_documents()
        folder_analysis = self.analyze_folder_nodes()
        relationship_analysis = self.analyze_existing_relationships()
        matching_pairs = self.find_matching_pairs()
        
        report = []
        report.append("=" * 60)
        report.append("📊 DOCUMENT-FOLDER LINKER - ANALYSIS REPORT")
        report.append("=" * 60)
        
        # Document Analysis
        report.append("\n🗂️ DOCUMENT ANALYSIS:")
        report.append(f"   - Total documents: {doc_analysis['total_documents']}")
        report.append(f"   - Documents with folder_name & course_code: {doc_analysis['documents_with_properties']}")
        report.append(f"   - Documents missing properties: {doc_analysis['documents_without_properties']}")
        report.append(f"   - Unique (folder_name, course_code) combinations: {doc_analysis['unique_combinations_count']}")
        
        if doc_analysis['sample_documents']:
            report.append("\n📄 Sample documents:")
            for i, doc in enumerate(doc_analysis['sample_documents'][:5], 1):
                filename = doc.get('fileName') or doc.get('d.fileName', 'Unknown')
                folder_name = doc.get('folder_name') or doc.get('d.folder_name', 'Unknown')  
                course_code = doc.get('course_code') or doc.get('d.course_code', 'Unknown')
                report.append(f"   {i}. {filename} (folder: {folder_name}, course: {course_code})")
        
        # Folder Analysis
        report.append(f"\n📁 FOLDER NODE ANALYSIS:")
        report.append(f"   - Total folder nodes: {folder_analysis['total_folder_nodes']}")
        report.append(f"   - Unique (name, course_code) combinations: {folder_analysis['unique_folder_combinations_count']}")
        
        if folder_analysis['folder_statistics']:
            report.append("\n📂 Folder node distribution:")
            for stat in folder_analysis['folder_statistics'][:10]:
                report.append(f"   - {stat['folder_type']}: {stat['name']} (course: {stat['course_code']}) - {stat['node_count']} nodes")
        
        # Relationship Analysis
        report.append(f"\n🔗 RELATIONSHIP ANALYSIS:")
        report.append(f"   - Existing HAVE relationships: {relationship_analysis['existing_have_relationships']}")
        
        if relationship_analysis['sample_relationships']:
            report.append("\n🔗 Sample existing relationships:")
            for i, rel in enumerate(relationship_analysis['sample_relationships'][:5], 1):
                report.append(f"   {i}. {rel['folder_name']} ({rel['folder_course_code']}) -[:HAVE]-> {rel['entity_labels']} ({rel['entity_id']})")
        
        # Matching Analysis
        report.append(f"\n🎯 MATCHING ANALYSIS:")
        report.append(f"   - Potential matches found: {len(matching_pairs)}")
        
        if matching_pairs:
            report.append("\n🎯 Matching pairs (folder ↔ documents):")
            for i, match in enumerate(matching_pairs[:10], 1):
                report.append(f"   {i}. {match['folder_label']}:{match['folder_name']} ({match['course_code']}) ↔ {match['document_count']} documents")
        
        # Summary
        report.append(f"\n💭 SUMMARY:")
        report.append(f"   - Documents ready for linking: {doc_analysis['documents_with_properties']}")
        report.append(f"   - Folder nodes ready for linking: {folder_analysis['total_folder_nodes']}")
        report.append(f"   - Potential relationships to create: {sum(match['document_count'] for match in matching_pairs)}")
        report.append(f"   - Status: {'✅ READY' if matching_pairs else '⚠️ NO MATCHES'}")
        
        return "\n".join(report)
