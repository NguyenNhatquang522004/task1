#!/usr/bin/env python3
"""
Integration Demo for Cross-Document Relationships
This script shows how to integrate with the main LLM Graph Builder project
"""

import sys
import os

def main():
    print("🔗 Cross-Document Relationships Integration Demo")
    print("=" * 50)
    
    # Check if we're in the right directory
    current_dir = os.getcwd()
    print(f"📍 Current directory: {current_dir}")
    
    if "llm-graph-builder" not in current_dir:
        print("⚠️  Please run this from the main llm-graph-builder directory")
        print("   cd C:\\edu\\task1\\llm-graph-builder")
        return
    
    # Check if cross-document-relationships exists
    cross_doc_path = os.path.join(current_dir, "cross-document-relationships")
    if not os.path.exists(cross_doc_path):
        print("❌ cross-document-relationships directory not found")
        return
    
    print("✅ Found cross-document-relationships directory")
    
    # Test import
    try:
        from cross_document_relationships.integration import CrossDocumentIntegration
        print("✅ Successfully imported CrossDocumentIntegration")
        
        # Create integration
        integration = CrossDocumentIntegration()
        print("✅ Created integration instance")
        
        # Show how to integrate with FastAPI
        print("\n📖 Integration Example:")
        print("""
# In your backend/score.py file, add this:

from cross_document_relationships.integration import setup_cross_document_analysis

# After creating your FastAPI app and Neo4j driver:
app = FastAPI()
neo4j_driver = your_neo4j_driver

# Add cross-document functionality
setup_cross_document_analysis(
    app=app,
    neo4j_driver=neo4j_driver,
    llm_client=None,  # Will use Gemini if None
    use_gemini=True
)

# Your app now has these new endpoints:
# POST /api/cross-document/analyze
# GET  /api/cross-document/similar-entities  
# GET  /api/cross-document/status
        """)
        
        # Show configuration
        print("\n⚙️  Configuration:")
        print("1. Copy .env.example to .env in cross-document-relationships/")
        print("2. Add your Gemini API keys:")
        print("   GEMINI_API_KEYS=key1,key2,key3")
        print("3. Adjust thresholds as needed:")
        print("   CROSS_DOC_SIMILARITY_THRESHOLD=0.75")
        print("   CROSS_DOC_CONFIDENCE_THRESHOLD=0.6")
        
        # Show testing
        print("\n🧪 Testing:")
        print("1. Start your main backend server")
        print("2. Test the cross-document endpoints:")
        print("   curl -X GET http://localhost:8000/api/cross-document/status")
        print("   curl -X POST http://localhost:8000/api/cross-document/analyze")
        
        print("\n✅ Integration ready! Check the endpoints when your server is running.")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("Make sure cross-document-relationships is properly set up")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
