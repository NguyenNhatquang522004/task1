#!/usr/bin/env python3
"""
How to Run Cross-Document Relationships Project
This script demonstrates all the different ways to run and use the project
"""

import sys
import os
import asyncio

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

def show_project_structure():
    """Show the project structure"""
    print("📁 Project Structure:")
    print("""
cross-document-relationships/
├── 📄 .env.example              # Environment configuration template
├── 📄 requirements.txt          # Python dependencies
├── 📄 README.md                 # Project documentation
├── 📄 integration.py            # Main integration module
├── 📁 config/
│   └── 📄 settings.py           # Configuration settings
├── 📁 src/
│   ├── 📄 constants.py          # Project constants
│   ├── 📁 core/
│   │   └── 📄 analyzer.py       # Main analyzer class
│   ├── 📁 utils/
│   │   ├── 📄 helpers.py        # Helper functions
│   │   └── 📄 gemini_client.py  # Gemini LLM client
│   └── 📁 api/
│       └── 📄 routes.py         # FastAPI routes
├── 📁 tests/
│   └── 📄 test_analyzer.py      # Unit tests
└── 📄 example_usage.py          # This file
    """)

def show_setup_steps():
    """Show setup steps"""
    print("🔧 Setup Steps:")
    print("""
1. Create .env file from template:
   cp .env.example .env

2. Edit .env file with your configuration:
   - Add your Gemini API keys
   - Configure thresholds and batch sizes
   - Set logging preferences

3. Install dependencies:
   pip install -r requirements.txt

4. Make sure Neo4j is running with your knowledge graph

5. Ensure your main LLM Graph Builder is set up and running
    """)

def show_running_methods():
    """Show different ways to run the project"""
    print("🚀 How to Run:")
    print("""
METHOD 1: Standalone Testing (Current Directory)
================================================
cd cross-document-relationships
python test_analyzer_standalone.py    # Test functionality
python example_usage.py               # Show usage examples

METHOD 2: Integration with Main Project
=======================================
# In your main backend/score.py or main application:

from cross_document_relationships.integration import setup_cross_document_analysis

# Add to your FastAPI app
setup_cross_document_analysis(
    app=app,                           # Your FastAPI app
    llm_client=llm_client,            # Optional if using Gemini
    neo4j_driver=neo4j_driver         # Your Neo4j driver
)

METHOD 3: Direct API Usage
==========================
# Start your main application with cross-document integration
# Then call the endpoints:

POST http://localhost:8000/api/cross-document/analyze
GET  http://localhost:8000/api/cross-document/similar-entities
GET  http://localhost:8000/api/cross-document/status

METHOD 4: Python Script Usage
==============================
# Create a script in your main project:

import asyncio
from cross_document_relationships import CrossDocumentAnalyzer

async def main():
    analyzer = CrossDocumentAnalyzer(
        neo4j_driver=your_driver,
        use_gemini=True
    )
    
    results = await analyzer.analyze_all_relationships(
        max_pairs=1000,
        batch_size=50
    )
    
    print(f"Created {results['created']} relationships")

asyncio.run(main())

METHOD 5: Module Import in Main Project
=======================================
# From your main project directory:
python -c "
from cross_document_relationships.integration import CrossDocumentIntegration
integration = CrossDocumentIntegration()
print('Cross-document module ready!')
"
    """)

def show_api_examples():
    """Show API usage examples"""
    print("🌐 API Usage Examples:")
    print("""
# Start full cross-document analysis
curl -X POST http://localhost:8000/api/cross-document/analyze \\
     -H "Content-Type: application/json" \\
     -d '{
       "max_pairs": 500,
       "batch_size": 25,
       "similarity_threshold": 0.8
     }'

# Get similar entities
curl -X GET http://localhost:8000/api/cross-document/similar-entities?limit=100

# Check system status
curl -X GET http://localhost:8000/api/cross-document/status

# Response example:
{
  "status": "success",
  "processed_pairs": 245,
  "created_relationships": 23,
  "processing_time": "45.2s",
  "llm_status": "active",
  "neo4j_status": "connected"
}
    """)

def show_troubleshooting():
    """Show troubleshooting tips"""
    print("🔍 Troubleshooting:")
    print("""
Common Issues and Solutions:

1. ImportError: No module named 'cross_document_relationships'
   Solution: Make sure you're running from the main project directory
   cd /path/to/llm-graph-builder
   python -c "from cross_document_relationships import ..."

2. ImportError: attempted relative import with no known parent package
   Solution: Don't run src/core/analyzer.py directly
   Use the integration module or run as a package

3. Neo4j connection errors
   Solution: Check your Neo4j connection in main project
   Make sure the database contains entities with embeddings

4. Gemini API errors
   Solution: Check your .env file has valid GEMINI_API_KEYS
   Test with: python -c "import google.generativeai as genai"

5. No similar entities found
   Solution: Ensure your entities have vector embeddings
   Check similarity threshold (try lowering to 0.5)

6. LLM timeout errors
   Solution: Reduce batch size, increase retry settings
   Check CROSS_DOC_BATCH_SIZE and CROSS_DOC_MAX_RETRIES
    """)

def main():
    print("🎯 Cross-Document Relationships - Complete Running Guide")
    print("=" * 60)
    
    show_project_structure()
    print()
    
    show_setup_steps()
    print()
    
    show_running_methods()
    print()
    
    show_api_examples()
    print()
    
    show_troubleshooting()
    print()
    
    print("📝 Quick Start Commands:")
    print("=" * 30)
    print("# From main project directory:")
    print("cd C:\\edu\\task1\\llm-graph-builder")
    print("python -m cross_document_relationships.integration")
    print()
    print("# From cross-document directory:")
    print("cd C:\\edu\\task1\\llm-graph-builder\\cross-document-relationships")
    print("python test_analyzer_standalone.py")
    print()
    print("# Integration test:")
    print("cd C:\\edu\\task1\\llm-graph-builder")
    print("python -c \"from cross_document_relationships.integration import CrossDocumentIntegration; print('✅ Integration ready!')\"")

if __name__ == "__main__":
    main()
