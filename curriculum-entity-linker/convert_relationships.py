#!/usr/bin/env python3
"""
Convert HAVE_TO relationships to HAVE
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

def convert_relationships():
    # Database connection
    uri = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "12345678")
    
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    try:
        with driver.session() as session:
            print("🔄 CONVERTING RELATIONSHIPS: HAVE_TO → HAVE")
            print("="*50)
            
            # 1. Check current state
            result = session.run("MATCH ()-[r:HAVE_TO]->() RETURN count(r) as count")
            have_to_count = result.single()["count"]
            
            result = session.run("MATCH ()-[r:HAVE]->() RETURN count(r) as count")
            have_count = result.single()["count"]
            
            print(f"Current HAVE_TO relationships: {have_to_count}")
            print(f"Current HAVE relationships: {have_count}")
            
            if have_to_count == 0:
                print("✅ No HAVE_TO relationships found - conversion not needed")
                return
            
            # 2. Convert relationships
            print(f"\n🔄 Converting {have_to_count} HAVE_TO relationships...")
            
            # Get all HAVE_TO relationships
            result = session.run("""
                MATCH (a)-[r:HAVE_TO]->(b)
                RETURN ID(a) as from_id, ID(b) as to_id
            """)
            relationships = list(result)
            
            converted_count = 0
            for rel in relationships:
                from_id = rel["from_id"]
                to_id = rel["to_id"]
                
                # Create HAVE relationship
                session.run("""
                    MATCH (a), (b)
                    WHERE ID(a) = $from_id AND ID(b) = $to_id
                    MERGE (a)-[:HAVE]->(b)
                """, from_id=from_id, to_id=to_id)
                
                converted_count += 1
                if converted_count % 100 == 0:
                    print(f"   Converted {converted_count}/{len(relationships)}...")
            
            # 3. Delete old HAVE_TO relationships
            print("🗑️  Deleting old HAVE_TO relationships...")
            result = session.run("MATCH ()-[r:HAVE_TO]->() DELETE r RETURN count(*) as deleted")
            deleted_count = result.single()["deleted"]
            
            # 4. Verify final state
            result = session.run("MATCH ()-[r:HAVE]->() RETURN count(r) as count")
            final_have_count = result.single()["count"]
            
            result = session.run("MATCH ()-[r:HAVE_TO]->() RETURN count(r) as count")
            remaining_have_to = result.single()["count"]
            
            print("\n📊 CONVERSION RESULTS:")
            print(f"✅ Converted relationships: {converted_count}")
            print(f"✅ Deleted old relationships: {deleted_count}")
            print(f"📈 Final HAVE relationships: {final_have_count}")
            print(f"📉 Remaining HAVE_TO relationships: {remaining_have_to}")
            
            if remaining_have_to == 0:
                print("\n🎉 SUCCESS: All HAVE_TO relationships converted to HAVE!")
            else:
                print("\n⚠️  Warning: Some HAVE_TO relationships still remain")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    convert_relationships()
