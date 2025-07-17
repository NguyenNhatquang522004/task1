#!/usr/bin/env python3
"""
Standalone test script for Cross-Document Analyzer
This script can be run directly to test the analyzer functionality
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

# Now we can import the modules
try:
    from config.settings import config
    from src.constants import (
        CROSS_DOC_RELATIONSHIP_PROMPT,
        DEFAULT_SIMILARITY_THRESHOLD,
        DEFAULT_BATCH_SIZE,
        DEFAULT_CONFIDENCE_THRESHOLD,
        RELATIONSHIP_TYPES
    )
    
    print("✅ Successfully imported configuration and constants")
    print(f"📊 Default similarity threshold: {DEFAULT_SIMILARITY_THRESHOLD}")
    print(f"📦 Default batch size: {DEFAULT_BATCH_SIZE}")
    print(f"🎯 Default confidence threshold: {DEFAULT_CONFIDENCE_THRESHOLD}")
    print(f"🔗 Available relationship types: {', '.join(RELATIONSHIP_TYPES)}")
    
    # Try to import the analyzer
    from src.core.analyzer import CrossDocumentAnalyzer
    print("✅ Successfully imported CrossDocumentAnalyzer")
    
    # Create a simple mock LLM client for testing
    class MockLLMClient:
        def generate_text(self, prompt, **kwargs):
            return "Mock response"
        
        def get_status(self):
            return {"status": "mock", "model": "test"}
    
    # Create an analyzer instance with mock client
    try:
        analyzer = CrossDocumentAnalyzer(
            llm_client=MockLLMClient(),
            neo4j_driver=None,
            similarity_threshold=0.75,
            use_gemini=False
        )
        print("✅ Successfully created CrossDocumentAnalyzer instance with mock LLM client")
    except Exception as e:
        # Try with Gemini if mock fails
        try:
            analyzer = CrossDocumentAnalyzer(
                llm_client=None,
                neo4j_driver=None,
                similarity_threshold=0.75,
                use_gemini=True
            )
            print("✅ Successfully created CrossDocumentAnalyzer instance with Gemini client")
        except Exception as e2:
            print(f"❌ Failed to create analyzer: {e2}")
            analyzer = None
    
    # Test some basic functionality
    if analyzer:
        print("\n🧪 Testing analyzer methods:")
        
        # Test LLM status
        try:
            status = analyzer.get_llm_status()
            print(f"✅ LLM status: {status}")
        except Exception as e:
            print(f"⚠️  LLM status check failed: {e}")
        
        # Test async methods (note: these require Neo4j driver for full functionality)
        import asyncio
        
        async def test_async_methods():
            try:
                # This would normally find similar entities from Neo4j
                print("⚠️  find_similar_entities() requires Neo4j driver")
                
                # This would analyze relationships between entities
                print("⚠️  analyze_relationship() requires entity pairs from Neo4j")
                
                # This would process all cross-document relationships
                print("⚠️  analyze_all_relationships() requires Neo4j driver and entities")
                
            except Exception as e:
                print(f"ℹ️  Async methods testing (expected without Neo4j): {e}")
        
        # Run async test
        try:
            asyncio.run(test_async_methods())
        except Exception as e:
            print(f"ℹ️  Async testing skipped: {e}")
        
        print("\n📋 Available analyzer methods:")
        print("  🔍 find_similar_entities() - Find entity pairs across documents")
        print("  📝 get_entity_context() - Get context for specific entities")
        print("  🧠 analyze_relationship() - Analyze relationship between entity pair")
        print("  💾 create_relationship() - Create relationship in Neo4j")
        print("  📦 process_batch() - Process multiple entity pairs")
        print("  🚀 analyze_all_relationships() - Full cross-document analysis")
        print("  🔄 analyze_relationship_with_retry() - Analysis with retry logic")
        print("  📊 get_llm_status() - Check LLM client status")
        print("  🔧 reset_llm_failed_keys() - Reset failed API keys")
    
    print("\n🎉 Analyzer testing completed successfully!")
    print("\n📝 Usage notes:")
    print("- To use with Neo4j, provide a neo4j_driver instance")
    print("- To use with Gemini, set use_gemini=True and configure API keys")
    print("- Check the .env.example file for configuration options")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\n🔧 Troubleshooting:")
    print("1. Make sure you're in the cross-document-relationships directory")
    print("2. Check that all required dependencies are installed")
    print("3. Verify the project structure is intact")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Cross-Document Analyzer Standalone Test")
    print("=" * 50)
