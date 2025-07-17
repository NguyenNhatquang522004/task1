#!/usr/bin/env python3
"""
Practical example of running cross-document-relationships
"""

import sys
import os

# Add cross-document-relationships to Python path
current_dir = os.getcwd()
cross_doc_path = os.path.join(current_dir, "cross-document-relationships")
sys.path.insert(0, cross_doc_path)

print("🚀 Running Cross-Document Relationships")
print("=" * 40)

try:
    # Now import should work
    from integration import CrossDocumentIntegration
    from src.core.analyzer import CrossDocumentAnalyzer
    from config.settings import config
    
    print("✅ All imports successful!")
    print(f"📊 Default similarity threshold: {config.DEFAULT_SIMILARITY_THRESHOLD}")
    print(f"📦 Default batch size: {config.DEFAULT_BATCH_SIZE}")
    
    # Create integration
    integration = CrossDocumentIntegration()
    print("✅ CrossDocumentIntegration created")
    
    print("\n🎯 To run with real data:")
    print("1. Make sure Neo4j is running with your knowledge graph")
    print("2. Configure .env file with Gemini API keys")
    print("3. Run your main backend server")
    print("4. Use the API endpoints or Python integration")
    
    print("\n📍 API Endpoints (when integrated):")
    print("POST /api/cross-document/analyze - Start analysis")
    print("GET  /api/cross-document/similar-entities - Get entity pairs")  
    print("GET  /api/cross-document/status - Check status")
    
    print("\n✅ Cross-document module is ready to use!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
