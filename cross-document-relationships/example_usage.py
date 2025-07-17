#!/usr/bin/env python3
"""
Example usage of Cross-Document Analyzer in LLM Graph Builder context
This script demonstrates how to properly integrate and use the analyzer
"""

import sys
import os
import asyncio

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

def main():
    print("🚀 Cross-Document Analyzer Usage Example")
    print("=" * 50)
    
    try:
        # Import the integration module (recommended approach)
        from integration import CrossDocumentIntegration
        
        print("✅ Successfully imported CrossDocumentIntegration")
        
        # Create integration instance
        integration = CrossDocumentIntegration()
        print("✅ Created CrossDocumentIntegration instance")
        
        print("\n📖 How to use in your LLM Graph Builder application:")
        print("""
1. In your main application (e.g., backend/score.py):

   from cross_document_relationships.integration import setup_cross_document_analysis
   
   # Setup with your existing Neo4j driver and LLM client
   setup_cross_document_analysis(
       app=your_fastapi_app,
       llm_client=your_llm_client,  # Optional if using Gemini
       neo4j_driver=your_neo4j_driver
   )

2. The analyzer will be available at these endpoints:
   
   POST /api/cross-document/analyze - Run full analysis
   GET  /api/cross-document/similar-entities - Find similar entities
   GET  /api/cross-document/status - Check system status

3. Direct usage in Python code:

   from cross_document_relationships import CrossDocumentAnalyzer
   
   analyzer = CrossDocumentAnalyzer(
       llm_client=your_llm_client,    # Or None for Gemini
       neo4j_driver=your_neo4j_driver,
       use_gemini=True                # Use Gemini 2.0 Flash
   )
   
   # Run analysis
   results = await analyzer.analyze_all_relationships(
       max_pairs=1000,
       batch_size=50
   )

4. Configuration via environment variables (.env file):
   
   GEMINI_API_KEYS=key1,key2,key3
   CROSS_DOC_SIMILARITY_THRESHOLD=0.75
   CROSS_DOC_CONFIDENCE_THRESHOLD=0.6
   CROSS_DOC_BATCH_SIZE=50
   CROSS_DOC_MAX_PAIRS=1000
        """)
        
        print("\n🔧 Prerequisites:")
        print("- Neo4j database with document entities")
        print("- Gemini API keys (or other LLM client)")
        print("- Vector embeddings for entities (for similarity)")
        print("- Proper .env configuration")
        
        print("\n📊 Expected workflow:")
        print("1. Documents are processed and entities extracted")
        print("2. Vector embeddings are created for entities")
        print("3. Cross-document analyzer finds similar entity pairs")
        print("4. LLM analyzes relationships between entity pairs")
        print("5. Valid relationships are stored in Neo4j")
        print("6. Results can be queried via API or Cypher")
        
        print("\n⚠️  Note: This example runs without Neo4j/LLM for demonstration")
        print("   For full functionality, integrate with your main application")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the cross-document-relationships directory")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
