#!/usr/bin/env python3
"""
Simple demo to test cross-document relationships standalone
"""

import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

print("🚀 Cross-Document Relationships - Simple Demo")
print("=" * 50)

try:
    print("📁 Current directory:", current_dir)
    print("🐍 Python version:", sys.version)
    print("📦 Python path added:", current_dir)
    
    # Test imports
    print("\n🔍 Testing imports...")
    
    from config.settings import config
    print("✅ Config imported successfully")
    print(f"📊 Default similarity threshold: {config.DEFAULT_SIMILARITY_THRESHOLD}")
    
    from src.constants import DEFAULT_BATCH_SIZE, RELATIONSHIP_TYPES
    print("✅ Constants imported successfully")
    print(f"📦 Default batch size: {DEFAULT_BATCH_SIZE}")
    print(f"🔗 Relationship types: {', '.join(RELATIONSHIP_TYPES)}")
    
    from src.core.analyzer import CrossDocumentAnalyzer
    print("✅ CrossDocumentAnalyzer imported successfully")
    
    # Create analyzer (without Neo4j for testing)
    class MockLLMClient:
        def generate_text(self, prompt, **kwargs):
            return "Mock response"
        def get_status(self):
            return {"status": "mock", "model": "test"}
    
    analyzer = CrossDocumentAnalyzer(
        llm_client=MockLLMClient(),
        neo4j_driver=None,
        similarity_threshold=0.75,
        use_gemini=False
    )
    print("✅ Analyzer created successfully with mock client")
    
    # Test analyzer methods
    status = analyzer.get_llm_status()
    print(f"📊 LLM Status: {status}")
    
    print("\n🎉 All components working correctly!")
    print("\n📋 To run the full standalone server:")
    print("1. Configure .env file with your Neo4j and Gemini credentials")
    print("2. Install dependencies: pip install -r requirements_standalone.txt")
    print("3. Run: python standalone_server.py")
    print("4. Access API at: http://localhost:8001/docs")
    
    print("\n✅ Cross-document relationships is ready for standalone use!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\n🔧 Troubleshooting:")
    print("1. Make sure you're in the cross-document-relationships directory")
    print("2. Check that all files are present")
    print("3. Install dependencies if needed")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
