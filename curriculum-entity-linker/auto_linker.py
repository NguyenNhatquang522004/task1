#!/usr/bin/env python3
"""
Auto Linker - Automatically link new documents when they are processed
"""

import time
import logging
from curriculum_linker import CurriculumEntityLinker
import os
from dotenv import load_dotenv

load_dotenv()

def monitor_and_link():
    """Monitor for new documents and automatically link them"""
    
    # Neo4j connection
    uri = os.getenv('NEO4J_URI', 'neo4j+s://013fb011.databases.neo4j.io')
    username = os.getenv('NEO4J_USERNAME', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', 'NH43Qy392yswBCfUFNrjYjIIvr4B_LcJB4eMRNzHrp')
    database = os.getenv('NEO4J_DATABASE', 'neo4j')
    
    linker = CurriculumEntityLinker(uri, username, password, database)
    
    # Keep track of processed documents
    processed_docs = set()
    
    try:
        while True:
            print("🔍 Checking for new documents...")
            
            # Get all documents with course codes (only unlinked ones)
            current_docs = linker.get_unlinked_documents()
            
            # Find new documents
            new_docs = []
            for doc in current_docs:
                doc_id = doc['doc_id']
                if doc_id not in processed_docs:
                    new_docs.append(doc)
                    processed_docs.add(doc_id)
            
            if new_docs:
                print(f"📋 Found {len(new_docs)} new documents to link")
                
                for doc in new_docs:
                    course_code = doc['course_code']
                    filename = doc['filename']
                    schema = doc['schema']
                    doc_id = doc['doc_id']
                    
                    print(f"🔗 Linking: {course_code} - {filename}")
                    
                    # Find course framework
                    course_framework = linker.find_course_framework(course_code)
                    
                    if course_framework:
                        # Create intermediate node and links
                        intermediate_node_id = linker.create_intermediate_node(schema, filename)
                        if intermediate_node_id:
                            linker.create_point_to_relationship(course_framework['course_id'], intermediate_node_id)
                            linker.create_have_to_relationships(intermediate_node_id, doc_id)
                            print(f"✅ Successfully linked: {course_code}")
                        else:
                            print(f"❌ Failed to create intermediate node for: {course_code}")
                    else:
                        print(f"⚠️  No course framework found for: {course_code}")
            else:
                print("📝 No new documents found")
            
            # Wait before next check
            print("⏰ Waiting 30 seconds before next check...")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Error in monitoring: {e}")
    finally:
        linker.close()

def link_single_document(filename_pattern: str):
    """Link a specific document by filename pattern"""
    
    uri = os.getenv('NEO4J_URI', 'neo4j://localhost:7687')
    username = os.getenv('NEO4J_USERNAME', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', 'password')
    database = os.getenv('NEO4J_DATABASE', 'neo4j')
    
    linker = CurriculumEntityLinker(uri, username, password, database)
    
    try:
        # Find documents matching pattern (only unlinked ones)
        documents = linker.get_unlinked_documents()
        matching_docs = [doc for doc in documents if filename_pattern.lower() in doc['filename'].lower()]
        
        if not matching_docs:
            print(f"❌ No documents found matching: {filename_pattern}")
            return
        
        print(f"📋 Found {len(matching_docs)} matching documents:")
        
        for i, doc in enumerate(matching_docs, 1):
            print(f"{i}. {doc['course_code']} - {doc['filename']}")
        
        # Process each matching document
        for doc in matching_docs:
            course_code = doc['course_code']
            filename = doc['filename']
            schema = doc['schema']
            doc_id = doc['doc_id']
            
            print(f"\n🔗 Processing: {course_code} - {filename}")
            
            # Find course framework
            course_framework = linker.find_course_framework(course_code)
            
            if course_framework:
                # Create intermediate node and links
                intermediate_node_id = linker.create_intermediate_node(schema, filename)
                if intermediate_node_id:
                    linker.create_point_to_relationship(course_framework['course_id'], intermediate_node_id)
                    linker.create_have_to_relationships(intermediate_node_id, doc_id)
                    print(f"✅ Successfully linked: {course_code}")
                else:
                    print(f"❌ Failed to create intermediate node for: {course_code}")
            else:
                print(f"⚠️  No course framework found for: {course_code}")
                
    except Exception as e:
        print(f"❌ Error linking document: {e}")
    finally:
        linker.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Link specific document
        pattern = sys.argv[1]
        print(f"🎯 Linking documents matching: {pattern}")
        link_single_document(pattern)
    else:
        # Start monitoring mode
        print("🚀 Starting auto-linking monitor...")
        print("Press Ctrl+C to stop")
        monitor_and_link()
