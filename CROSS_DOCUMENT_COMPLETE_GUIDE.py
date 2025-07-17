#!/usr/bin/env python3
"""
Complete Guide: How to Run Cross-Document Relationships Project
"""

def print_section(title, content):
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(content)

def main():
    print("🎯 CROSS-DOCUMENT RELATIONSHIPS - COMPLETE RUNNING GUIDE")
    
    print_section("1. PROJECT LOCATION", """
The cross-document-relationships project is located at:
📁 C:\\edu\\task1\\llm-graph-builder\\cross-document-relationships\\

Main files:
- src/core/analyzer.py        (The analyzer you were looking for)
- integration.py              (Main integration module)
- config/settings.py          (Configuration)
- .env.example               (Environment template)
""")

    print_section("2. RUNNING METHODS", """
🚀 METHOD 1: Standalone Testing
------------------------------
cd C:\\edu\\task1\\llm-graph-builder\\cross-document-relationships
python test_analyzer_standalone.py

🚀 METHOD 2: Integration with Main Backend
------------------------------------------
Add to backend/score.py:

# Add import at top
import sys
sys.path.append('../cross-document-relationships')

from integration import CrossDocumentIntegration

# In your app setup section
integration = CrossDocumentIntegration()
integration.initialize(
    neo4j_driver=neo4j_driver,
    use_gemini=True
)

🚀 METHOD 3: Direct Module Usage
-------------------------------
cd C:\\edu\\task1\\llm-graph-builder
python -c "
import sys
sys.path.append('./cross-document-relationships')
from integration import CrossDocumentIntegration
print('✅ Cross-document module ready!')
"

🚀 METHOD 4: API Endpoints (after integration)
---------------------------------------------
POST /api/cross-document/analyze
GET  /api/cross-document/similar-entities
GET  /api/cross-document/status
""")

    print_section("3. CONFIGURATION STEPS", """
1️⃣ Create .env file:
cd cross-document-relationships
copy .env.example .env

2️⃣ Edit .env with your settings:
GEMINI_API_KEYS=your_key_1,your_key_2,your_key_3
CROSS_DOC_SIMILARITY_THRESHOLD=0.75
CROSS_DOC_CONFIDENCE_THRESHOLD=0.6
CROSS_DOC_BATCH_SIZE=50

3️⃣ Install dependencies:
pip install -r cross-document-relationships/requirements.txt

4️⃣ Ensure Neo4j is running with your knowledge graph
""")

    print_section("4. CURRENT WORKING EXAMPLES", """
✅ These scripts work RIGHT NOW:

1. Testing functionality:
   cd C:\\edu\\task1\\llm-graph-builder\\cross-document-relationships
   python test_analyzer_standalone.py

2. Show usage examples:
   cd C:\\edu\\task1\\llm-graph-builder\\cross-document-relationships  
   python HOW_TO_RUN.py

3. API integration ready (needs Neo4j + Gemini keys):
   The integration.py module is ready to use
""")

    print_section("5. PRODUCTION INTEGRATION EXAMPLE", """
# In your backend/score.py, add this section:

# === CROSS-DOCUMENT RELATIONSHIPS INTEGRATION ===
import sys
import os
cross_doc_path = os.path.join(os.path.dirname(__file__), '..', 'cross-document-relationships')
sys.path.insert(0, cross_doc_path)

try:
    from integration import setup_cross_document_analysis
    
    # Add after your app and neo4j_driver are created
    setup_cross_document_analysis(
        app=app,
        neo4j_driver=neo4j_driver,
        use_gemini=True
    )
    logger.info("✅ Cross-document analysis enabled")
except Exception as e:
    logger.warning(f"Cross-document analysis not available: {e}")

# === END CROSS-DOCUMENT INTEGRATION ===
""")

    print_section("6. TROUBLESHOOTING", """
❌ Problem: ImportError when running analyzer.py directly
✅ Solution: Use test_analyzer_standalone.py instead

❌ Problem: "No module named 'cross_document_relationships'"  
✅ Solution: Run from correct directory or add to sys.path

❌ Problem: "attempted relative import with no known parent package"
✅ Solution: Don't run src files directly, use integration module

❌ Problem: No Neo4j connection
✅ Solution: Make sure main backend is configured with Neo4j

❌ Problem: No Gemini API access
✅ Solution: Configure .env file with valid API keys
""")

    print_section("7. QUICK START COMMANDS", """
# Test if everything works:
cd C:\\edu\\task1\\llm-graph-builder\\cross-document-relationships
python test_analyzer_standalone.py

# View complete documentation:
python HOW_TO_RUN.py

# Test from main project:
cd C:\\edu\\task1\\llm-graph-builder
python -c "
import sys, os
sys.path.append('./cross-document-relationships')
try:
    from integration import CrossDocumentIntegration
    print('✅ Integration ready!')
except Exception as e:
    print(f'⚠️  Integration needs setup: {e}')
"
""")

    print(f"\n{'🎉'*20}")
    print("Cross-Document Relationships is ready to use!")
    print("Start with the test scripts to verify functionality")
    print(f"{'🎉'*20}")

if __name__ == "__main__":
    main()
