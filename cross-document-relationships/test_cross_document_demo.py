#!/usr/bin/env python3
"""
Cross-Document Relationships Test Demo
=====================================

Script để test standalone server hoàn chỉnh với focus vào cross-document relationship assignment.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

async def test_cross_document_server():
    """Test comprehensive cross-document relationship functionality"""
    print("🧪 Testing Cross-Document Relationships Server")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. Health check
        print("\n1️⃣ Testing health check...")
        try:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    health = await response.json()
                    print(f"✅ Health: {health['status']}")
                    print(f"   Components: {health['components']}")
                else:
                    print(f"❌ Health check failed: {response.status}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        # 2. System status
        print("\n2️⃣ Testing system status...")
        try:
            async with session.get(f"{BASE_URL}/status") as response:
                if response.status == 200:
                    status_data = await response.json()
                    print("✅ System status retrieved")
                    if "data" in status_data:
                        data = status_data["data"]
                        print(f"   Neo4j nodes: {data.get('neo4j_status', {}).get('node_count', 'N/A')}")
                        print(f"   Neo4j relationships: {data.get('neo4j_status', {}).get('relationship_count', 'N/A')}")
                        print(f"   Similarity threshold: {data.get('similarity_threshold', 'N/A')}")
                else:
                    print(f"❌ Status check failed: {response.status}")
        except Exception as e:
            print(f"❌ Status check error: {e}")
        
        # 3. Get cross-document statistics
        print("\n3️⃣ Testing cross-document statistics...")
        try:
            async with session.get(f"{BASE_URL}/cross-document-stats") as response:
                if response.status == 200:
                    stats_data = await response.json()
                    print("✅ Cross-document statistics retrieved")
                    if "data" in stats_data:
                        stats = stats_data["data"]
                        print(f"   Cross-document relationships: {stats.get('cross_document_relationships', 0)}")
                        print(f"   Documents with connections: {stats.get('documents_with_cross_connections', 0)}")
                        print(f"   Relationship types: {len(stats.get('relationship_types', {}))}")
                else:
                    print(f"❌ Statistics failed: {response.status}")
        except Exception as e:
            print(f"❌ Statistics error: {e}")
        
        # 4. Get potential entity pairs
        print("\n4️⃣ Testing entity pairs discovery...")
        try:
            params = {
                "limit": 50,
                "similarity_threshold": 0.75
            }
            async with session.get(f"{BASE_URL}/entity-pairs", params=params) as response:
                if response.status == 200:
                    pairs_data = await response.json()
                    print("✅ Entity pairs retrieved")
                    if "data" in pairs_data:
                        data = pairs_data["data"]
                        print(f"   Found pairs: {data.get('total_found', 0)}")
                        print(f"   Similarity threshold: {data.get('similarity_threshold', 'N/A')}")
                        
                        # Show some examples
                        pairs = data.get('entity_pairs', [])
                        if pairs:
                            print("   Sample pairs:")
                            for i, pair in enumerate(pairs[:3]):
                                print(f"     {i+1}. {pair.get('entity1', 'N/A')} <-> {pair.get('entity2', 'N/A')} (similarity: {pair.get('similarity', 'N/A'):.3f})")
                else:
                    print(f"❌ Entity pairs failed: {response.status}")
        except Exception as e:
            print(f"❌ Entity pairs error: {e}")
        
        # 5. Test relationship assignment (chỉ nếu có entity pairs)
        print("\n5️⃣ Testing cross-document relationship assignment...")
        try:
            # Chạy với parameters nhỏ để test
            form_data = {
                "max_pairs": 10,
                "batch_size": 5,
                "similarity_threshold": 0.75,
                "confidence_threshold": 0.6
            }
            
            async with session.post(f"{BASE_URL}/analyze", data=form_data) as response:
                if response.status == 200:
                    result_data = await response.json()
                    print("✅ Cross-document analysis completed")
                    if "data" in result_data:
                        data = result_data["data"]
                        results = data.get("assignment_results", {})
                        print(f"   Created relationships: {results.get('created_relationships', 0)}")
                        print(f"   Processed pairs: {results.get('processed_pairs', 0)}")
                        print(f"   Success rate: {results.get('success_rate', 0):.1%}")
                else:
                    error_text = await response.text()
                    print(f"❌ Analysis failed: {response.status}")
                    print(f"   Error: {error_text[:200]}...")
        except Exception as e:
            print(f"❌ Analysis error: {e}")
        
        # 6. Final statistics after assignment
        print("\n6️⃣ Testing final statistics...")
        try:
            async with session.get(f"{BASE_URL}/cross-document-stats") as response:
                if response.status == 200:
                    stats_data = await response.json()
                    print("✅ Final statistics retrieved")
                    if "data" in stats_data:
                        stats = stats_data["data"]
                        print(f"   Total cross-document relationships: {stats.get('cross_document_relationships', 0)}")
                        print(f"   Top relationship types:")
                        rel_types = stats.get('relationship_types', {})
                        for rel_type, count in list(rel_types.items())[:5]:
                            print(f"     - {rel_type}: {count}")
                else:
                    print(f"❌ Final statistics failed: {response.status}")
        except Exception as e:
            print(f"❌ Final statistics error: {e}")

    print("\n" + "=" * 60)
    print("🎯 Cross-Document Relationships Test Complete!")
    print("\nKey Features Tested:")
    print("✅ Standalone server functionality")
    print("✅ Neo4j integration")
    print("✅ Cross-document entity pair discovery")
    print("✅ LLM-based relationship analysis")
    print("✅ Relationship assignment to graph")
    print("✅ Statistics and monitoring")
    print("\n💡 Server tách biệt hoàn toàn với backend, tập trung vào cross-document relationships!")

if __name__ == "__main__":
    print(f"🚀 Starting Cross-Document Relationships Test at {datetime.now()}")
    print("🔗 Testing server at: http://localhost:8001")
    print("📋 Make sure server is running: python standalone_server.py")
    print()
    
    asyncio.run(test_cross_document_server())
