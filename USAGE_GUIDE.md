# 📚 Hướng Dẫn Sử Dụng LLM Graph Builder

## 🎯 Tổng Quan

LLM Graph Builder là một hệ thống tự động tạo knowledge graph từ documents PDF, tích hợp với curriculum framework và tạo relationships giữa các entities. Hệ thống sử dụng AI/LLM để trích xuất thông tin và tạo ra một mạng lưới kiến thức có cấu trúc.

---

## 🚀 Quick Start

### **Bước 1: Environment Setup**

```bash
# Clone repository
git clone <repository-url>
cd llm-graph-builder

# Tạo virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### **Bước 2: Database Setup**

```bash
# Khởi động Neo4j (Docker)
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/12345678 \
  neo4j:latest

# Hoặc sử dụng Neo4j Desktop
# Tạo database mới với password: 12345678
```

### **Bước 3: Configuration**

```bash
# Copy environment template
cp backend/example.env backend/.env

# Chỉnh sửa .env file
nano backend/.env
```

```properties
# backend/.env
NEO4J_URI=neo4j://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=12345678
NEO4J_DATABASE=neo4j

# Gemini API (for LLM processing)
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 📖 Hướng Dẫn Sử Dụng Chi Tiết

## 1. **Xử Lý Documents cơ bản**

### **A. Khởi động Backend Server**

```bash
cd backend
python -m uvicorn score:app --reload --host 0.0.0.0 --port 8000
```

Hoặc sử dụng VS Code task:
```bash
# Ctrl+Shift+P → "Tasks: Run Task" → "Run Backend Development Server"
```

### **B. Upload và Process Documents**

**Via Web Interface:**
1. Mở browser: `http://localhost:8000`
2. Upload PDF files
3. Chọn processing options
4. Start processing

**Via API:**
```bash
# Upload document
curl -X POST "http://localhost:8000/upload" \
  -F "file=@path/to/document.pdf"

# Start processing
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{"file_name": "document.pdf", "mode": "entities"}'
```

### **C. Processing Modes**

| Mode | Mô tả | Sử dụng khi |
|------|-------|-------------|
| `entities` | Trích xuất entities cơ bản | Document đầu tiên |
| `communities` | Phân tích community structure | Cần hiểu relationships |
| `hybrid` | Kết hợp entities + communities | Phân tích sâu |

---

## 2. **Curriculum Integration**

### **A. Setup Curriculum Framework**

```bash
cd curriculum-entity-linker

# Load curriculum framework vào Neo4j
python -c "
from curriculum_linker import CurriculumEntityLinker
linker = CurriculumEntityLinker('neo4j://127.0.0.1:7687', 'neo4j', '12345678')
# Framework sẽ được load tự động từ curriculum-syllabus-example.cql
"
```

### **B. Link Documents với Curriculum**

```bash
# Auto-link tất cả documents với curriculum
cd curriculum-entity-linker
python curriculum_linker.py

# Force relink nếu cần
python curriculum_linker.py --force
```

**Output mong đợi:**
```
✅ Linked documents: 15
🔗 Total links created: 15
📊 Total entities linked: 1,273
```

### **C. Verify Curriculum Links**

```bash
# Kiểm tra linking status
python verify_entity_linking.py

# Debug linking issues
python debug_curriculum_links.py
```

---

## 3. **Cross-Document Relationships**

### **A. Setup Cross-Document Analysis**

```bash
cd cross-document-relationships

# Copy environment config
cp ../.env .env

# Chỉnh sửa config cho cross-document analysis
nano .env
```

**cross-document-relationships/.env:**
```properties
# === Neo4j Database Configuration ===
NEO4J_URI=neo4j://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=12345678
NEO4J_DATABASE=neo4j

# === Gemini API Keys (Multiple keys for rate limiting) ===
GEMINI_API_KEY_1=your_primary_gemini_key
GEMINI_API_KEY_2=your_secondary_gemini_key  
GEMINI_API_KEY_3=your_tertiary_gemini_key

# === Analysis Parameters ===
CONFIDENCE_THRESHOLD=0.7              # Minimum confidence for relationships
MAX_RELATIONSHIPS_PER_ENTITY=15       # Limit relationships per entity
BATCH_SIZE=50                         # Entities processed per batch
SIMILARITY_THRESHOLD=0.8              # Semantic similarity threshold

# === Rate Limiting (Important for API costs) ===
REQUESTS_PER_MINUTE=15                # Max API requests per minute
CONCURRENT_REQUESTS=3                 # Parallel API calls
RETRY_ATTEMPTS=3                      # Retry failed requests
RETRY_DELAY=5                         # Delay between retries (seconds)

# === Processing Options ===
ENABLE_CACHING=true                   # Cache API responses
CACHE_DURATION=86400                  # Cache duration (24 hours)
SKIP_EXISTING_RELATIONSHIPS=true      # Skip already processed pairs
ENABLE_DETAILED_LOGGING=true          # Detailed progress logs

# === Quality Control ===
MIN_ENTITY_LENGTH=3                   # Minimum entity text length
MAX_ENTITY_LENGTH=200                 # Maximum entity text length
EXCLUDE_STOP_WORDS=true               # Filter out stop words
ENABLE_SPELL_CHECK=false              # Spell checking (optional)

# === Output Configuration ===
EXPORT_RESULTS=true                   # Export results to files
EXPORT_FORMAT=json                    # json, csv, or both
RESULTS_DIRECTORY=./results           # Output directory
ENABLE_PROGRESS_REPORTS=true          # Progress monitoring
```

### **B. Run Cross-Document Analysis**

```bash
# Phân tích relationships giữa documents
python cross_document_analyzer.py

# Chỉ phân tích documents mới
python cross_document_analyzer.py --mode incremental

# Phân tích tất cả documents
python cross_document_analyzer.py --mode full
```

### **C. Monitor Progress**

```bash
# Real-time monitoring
tail -f cross_document_analysis.log

# Check statistics
python relationship_stats.py
```

---

## 4. **Frontend Interface**

### **A. Khởi động Frontend**

```bash
cd frontend
npm install
npm run dev
```

Hoặc sử dụng VS Code task:
```bash
# Ctrl+Shift+P → "Tasks: Run Task" → "Run Frontend Development Server"
```

### **B. Graph Visualization**

**Truy cập**: `http://localhost:3000`

**Tính năng chính:**
- 📊 Interactive graph visualization
- 🔍 Entity search và filtering
- 🎯 Relationship exploration
- 📈 Analytics dashboard

### **C. Query Interface**

**Cypher Query Console:**
```cypher
-- Tìm tất cả documents liên quan đến Java
MATCH (d:Document)-[:FIRST_CHUNK]->(chunk:Chunk)-[:HAS_ENTITY]->(e:__Entity__)
WHERE e.id CONTAINS "Java"
RETURN d.fileName, collect(e.id) as entities

-- Xem curriculum links
MATCH (c:Course)-[:POINT_TO]->(cl:CurriculumLink)-[:HAVE]->(e:__Entity__)
RETURN c.code, c.name, count(e) as entity_count
ORDER BY entity_count DESC

-- Cross-document relationships
MATCH (e1:__Entity__)-[r:RELATES_TO]->(e2:__Entity__)
WHERE r.confidence > 0.8
RETURN e1.id, e2.id, r.confidence
```

---

## 5. **Advanced Usage**

### **A. Custom Document Processing**

```python
# custom_processor.py
from backend.src.main import create_graph_from_file

def process_custom_document(file_path, custom_config):
    config = {
        "chunk_size": custom_config.get("chunk_size", 1000),
        "chunk_overlap": custom_config.get("chunk_overlap", 200),
        "entity_extraction_mode": custom_config.get("mode", "entities"),
        "llm_model": custom_config.get("model", "gemini-2.0-flash")
    }
    
    result = create_graph_from_file(file_path, config)
    return result

# Usage
result = process_custom_document(
    "my_document.pdf", 
    {"chunk_size": 1500, "mode": "hybrid"}
)
```

### **B. Batch Processing**

```python
# batch_processor.py
import os
from pathlib import Path

def process_directory(directory_path):
    pdf_files = Path(directory_path).glob("*.pdf")
    
    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file}")
        try:
            process_custom_document(str(pdf_file), {})
            print(f"✅ Completed: {pdf_file}")
        except Exception as e:
            print(f"❌ Failed: {pdf_file} - {e}")

# Usage
process_directory("/path/to/pdf/directory")
```

### **C. Custom Relationship Rules**

```python
# custom_relationships.py
class CustomRelationshipExtractor:
    def __init__(self):
        self.custom_rules = {
            "programming_concepts": {
                "patterns": ["implements", "extends", "inherits"],
                "relationship": "PROGRAMMING_RELATION",
                "confidence_boost": 0.2
            },
            "academic_prerequisites": {
                "patterns": ["prerequisite", "required", "before"],
                "relationship": "PREREQUISITE",
                "confidence_boost": 0.3
            }
        }
    
    def extract_relationships(self, entity1, entity2, context):
        for rule_name, rule in self.custom_rules.items():
            if self.matches_pattern(context, rule["patterns"]):
                return {
                    "type": rule["relationship"],
                    "confidence": base_confidence + rule["confidence_boost"]
                }
        return None
```

---

## 6. **Maintenance & Monitoring**

### **A. Database Maintenance**

```bash
# Backup Neo4j database
neo4j-admin database dump --to-path=/backup/location neo4j

# Restore database
neo4j-admin database load --from-path=/backup/location neo4j

# Database stats
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('neo4j://127.0.0.1:7687', auth=('neo4j', '12345678'))
with driver.session() as session:
    result = session.run('CALL db.stats.retrieve(\"GRAPH\") YIELD data RETURN data')
    print(result.single()['data'])
"
```

### **B. Cleanup Operations**

```bash
# Xóa tất cả processed data (giữ lại raw documents)
cd curriculum-entity-linker
python cleanup_curriculum_links.py

# Xóa specific document data
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('neo4j://127.0.0.1:7687', auth=('neo4j', '12345678'))
with driver.session() as session:
    session.run('MATCH (d:Document {fileName: \"document_name.pdf\"}) DETACH DELETE d')
"
```

### **C. Performance Monitoring**

```bash
# System resources
htop

# Neo4j performance
neo4j-admin memrec

# Application logs
tail -f backend/logs/application.log
tail -f curriculum-entity-linker/curriculum_linking.log
```

---

## 7. **Troubleshooting**

### **A. Common Issues**

**1. Connection Issues:**
```bash
# Test Neo4j connection
python -c "
from neo4j import GraphDatabase
try:
    driver = GraphDatabase.driver('neo4j://127.0.0.1:7687', auth=('neo4j', '12345678'))
    driver.verify_connectivity()
    print('✅ Neo4j connection successful')
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

**2. Memory Issues:**
```bash
# Increase Java heap size for Neo4j
# Edit neo4j.conf:
server.memory.heap.initial_size=2G
server.memory.heap.max_size=4G
```

**3. API Rate Limits:**
```bash
# Check API usage
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Gemini API Key:', os.getenv('GEMINI_API_KEY')[:10] + '...')
"
```

### **B. Debugging Tools**

```bash
# Debug curriculum linking
cd curriculum-entity-linker
python debug_curriculum_links.py

# Test entity extraction
python test_entity_extraction.py --file "sample.pdf"

# Validate relationships
python validate_relationships.py --confidence-threshold 0.7
```

### **C. Performance Optimization**

```python
# optimize_processing.py
def optimize_for_large_datasets():
    config = {
        "chunk_size": 2000,  # Larger chunks = fewer API calls
        "batch_size": 100,   # Process more entities per batch
        "parallel_workers": 4,  # Parallel processing
        "cache_embeddings": True,  # Cache similarity calculations
        "skip_low_confidence": True  # Skip relationships < threshold
    }
    return config
```

---

## 8. **Best Practices**

### **A. Document Preparation**

1. **File Naming Convention:**
   ```
   [COURSE_CODE] Document_Title.pdf
   Example: [CMP170] Lập trình trên môi trường Windows.pdf
   ```

2. **Document Quality:**
   - Sử dụng OCR cho scanned PDFs
   - Ensure proper text encoding (UTF-8)
   - Remove password protection

3. **Batch Size:**
   - Process 5-10 documents per batch
   - Monitor memory usage
   - Use incremental processing for large datasets

### **B. Configuration Optimization**

```properties
# Optimized .env for production
CHUNK_SIZE=1500
CHUNK_OVERLAP=200
CONFIDENCE_THRESHOLD=0.75
MAX_RELATIONSHIPS_PER_ENTITY=20
ENABLE_CACHING=true
LOG_LEVEL=INFO
```

### **C. Workflow Recommendations**

1. **Development Phase:**
   ```bash
   # Test với 1-2 documents nhỏ
   python curriculum_linker.py --test-mode
   ```

2. **Production Phase:**
   ```bash
   # Full processing pipeline
   python curriculum_linker.py
   python cross_document_analyzer.py --mode incremental
   ```

3. **Maintenance Phase:**
   ```bash
   # Weekly cleanup và optimization
   python cleanup_old_data.py --older-than 30days
   python optimize_graph.py
   ```

---

## 9. **Integration Examples**

### **A. API Integration**

```python
# api_client.py
import requests

class LLMGraphAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def upload_document(self, file_path):
        with open(file_path, 'rb') as f:
            response = requests.post(
                f"{self.base_url}/upload",
                files={"file": f}
            )
        return response.json()
    
    def process_document(self, file_name, mode="entities"):
        response = requests.post(
            f"{self.base_url}/process",
            json={"file_name": file_name, "mode": mode}
        )
        return response.json()
    
    def get_graph_data(self, query_params=None):
        response = requests.get(
            f"{self.base_url}/graph",
            params=query_params or {}
        )
        return response.json()

# Usage
api = LLMGraphAPI()
result = api.upload_document("document.pdf")
process_result = api.process_document("document.pdf", "hybrid")
```

### **B. Database Integration**

```python
# db_integration.py
from neo4j import GraphDatabase

class GraphQueryManager:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def get_document_entities(self, document_name):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Document {fileName: $doc_name})-[:FIRST_CHUNK]->(chunk:Chunk)-[:HAS_ENTITY]->(e:__Entity__)
                RETURN e.id as entity, e.type as entity_type
            """, doc_name=document_name)
            return [record.data() for record in result]
    
    def get_cross_document_relationships(self, confidence_threshold=0.7):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e1:__Entity__)-[r:RELATES_TO]->(e2:__Entity__)
                WHERE r.confidence >= $threshold
                RETURN e1.id as entity1, e2.id as entity2, r.confidence as confidence
            """, threshold=confidence_threshold)
            return [record.data() for record in result]

# Usage
graph_manager = GraphQueryManager("neo4j://127.0.0.1:7687", "neo4j", "12345678")
entities = graph_manager.get_document_entities("sample.pdf")
relationships = graph_manager.get_cross_document_relationships(0.8)
```

---

## 10. **Deployment**

### **A. Development Deployment**

```bash
# All-in-one development setup
docker-compose up -d

# Hoặc manual setup
# Terminal 1: Neo4j
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/12345678 neo4j

# Terminal 2: Backend
cd backend && python -m uvicorn score:app --reload --port 8000

# Terminal 3: Frontend  
cd frontend && npm run dev
```

### **B. Production Deployment**

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "score:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.production.yml
version: '3.8'
services:
  neo4j:
    image: neo4j:latest
    environment:
      NEO4J_AUTH: neo4j/production_password
    volumes:
      - neo4j_data:/data
    ports:
      - "7687:7687"
  
  backend:
    build: ./backend
    environment:
      NEO4J_URI: neo4j://neo4j:7687
      NEO4J_PASSWORD: production_password
    ports:
      - "8000:8000"
    depends_on:
      - neo4j
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  neo4j_data:
```

---

## 📋 Quick Reference

### **Essential Commands**

```bash
# Start full system
docker-compose up -d

# Process documents
cd curriculum-entity-linker && python curriculum_linker.py

# Cross-document analysis
cd cross-document-relationships && python cross_document_analyzer.py

# View results
open http://localhost:3000
```

### **Key Files**

| File | Purpose |
|------|---------|
| `backend/score.py` | Main API server |
| `curriculum-entity-linker/curriculum_linker.py` | Curriculum integration |
| `cross-document-relationships/cross_document_analyzer.py` | Cross-document analysis |
| `frontend/` | Web interface |
| `.env` files | Configuration |

### **Important URLs**

- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Neo4j Browser: `http://localhost:7474`
- API Documentation: `http://localhost:8000/docs`

---

*Hướng dẫn này cung cấp tất cả thông tin cần thiết để sử dụng LLM Graph Builder hiệu quả. Để biết thêm chi tiết, tham khảo các file README trong từng module.*

---

## 📊 Cross-Document Relationships Module - Detailed Guide

### **Tổng quan Module**

Module `cross-document-relationships` là thành phần chuyên biệt để phân tích và tạo relationships giữa entities từ các documents khác nhau. Module này sử dụng AI/LLM để:

- 🔍 Phát hiện semantic similarities giữa entities
- 🔗 Tạo meaningful relationships across documents  
- 📈 Phân tích confidence scores và quality metrics
- 🎯 Tối ưu hóa performance với rate limiting và caching

### **Architecture Overview**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Document A    │    │   Document B    │    │   Document C    │
│   ┌─────────┐   │    │   ┌─────────┐   │    │   ┌─────────┐   │
│   │Entity 1 │   │    │   │Entity 3 │   │    │   │Entity 5 │   │
│   │Entity 2 │   │    │   │Entity 4 │   │    │   │Entity 6 │   │
│   └─────────┘   │    │   └─────────┘   │    │   └─────────┘   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                │
                ┌───────────────────────────┐
                │ Cross-Document Analyzer   │
                │ ┌─────────────────────┐   │
                │ │ Semantic Analysis   │   │
                │ │ Confidence Scoring  │   │
                │ │ Relationship Mining │   │
                │ └─────────────────────┘   │
                └───────────────────────────┘
                                │
                    ┌─────────────────────┐
                    │   Neo4j Graph DB    │
                    │ Entity1--RELATES_TO │
                    │    │     (conf:0.85) │
                    │ Entity3             │
                    └─────────────────────┘
```

---

## 🚀 Setup & Configuration

### **1. Environment Setup**

```bash
cd cross-document-relationships

# Tạo environment file từ template
cp .env.example .env

# Chỉnh sửa configuration
nano .env
```

**Detailed .env Configuration:**
```properties
# === Neo4j Database Configuration ===
NEO4J_URI=neo4j://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=12345678
NEO4J_DATABASE=neo4j

# === Gemini API Keys (Multiple keys for rate limiting) ===
GEMINI_API_KEY_1=your_primary_gemini_key
GEMINI_API_KEY_2=your_secondary_gemini_key  
GEMINI_API_KEY_3=your_tertiary_gemini_key

# === Analysis Parameters ===
CONFIDENCE_THRESHOLD=0.7              # Minimum confidence for relationships
MAX_RELATIONSHIPS_PER_ENTITY=15       # Limit relationships per entity
BATCH_SIZE=50                         # Entities processed per batch
SIMILARITY_THRESHOLD=0.8              # Semantic similarity threshold

# === Rate Limiting (Important for API costs) ===
REQUESTS_PER_MINUTE=15                # Max API requests per minute
CONCURRENT_REQUESTS=3                 # Parallel API calls
RETRY_ATTEMPTS=3                      # Retry failed requests
RETRY_DELAY=5                         # Delay between retries (seconds)

# === Processing Options ===
ENABLE_CACHING=true                   # Cache API responses
CACHE_DURATION=86400                  # Cache duration (24 hours)
SKIP_EXISTING_RELATIONSHIPS=true      # Skip already processed pairs
ENABLE_DETAILED_LOGGING=true          # Detailed progress logs

# === Quality Control ===
MIN_ENTITY_LENGTH=3                   # Minimum entity text length
MAX_ENTITY_LENGTH=200                 # Maximum entity text length
EXCLUDE_STOP_WORDS=true               # Filter out stop words
ENABLE_SPELL_CHECK=false              # Spell checking (optional)

# === Output Configuration ===
EXPORT_RESULTS=true                   # Export results to files
EXPORT_FORMAT=json                    # json, csv, or both
RESULTS_DIRECTORY=./results           # Output directory
ENABLE_PROGRESS_REPORTS=true          # Progress monitoring
```

### **2. Dependency Installation**

```bash
# Install specific dependencies for cross-document analysis
pip install -r requirements.txt

# Key dependencies include:
# - google-generativeai (Gemini API)
# - neo4j (Database driver)
# - pandas (Data processing)
# - numpy (Mathematical operations)
# - scikit-learn (ML utilities)
# - python-dotenv (Environment management)
```

---

## 📖 Core Functionality

### **1. Main Analysis Script**

```bash
# Basic usage - analyze all documents
python cross_document_analyzer.py

# Incremental mode - only new relationships
python cross_document_analyzer.py --mode incremental

# Full mode - reanalyze everything
python cross_document_analyzer.py --mode full

# Specific confidence threshold
python cross_document_analyzer.py --confidence-threshold 0.8

# Custom batch size
python cross_document_analyzer.py --batch-size 25

# Dry run - analyze without saving
python cross_document_analyzer.py --dry-run
```

### **2. Processing Modes Explained**

**Incremental Mode (Recommended):**
```bash
python cross_document_analyzer.py --mode incremental
```
- ✅ Chỉ phân tích entity pairs chưa được xử lý
- ✅ Tiết kiệm API calls và thời gian
- ✅ Ideal cho daily/weekly updates

**Full Mode:**
```bash
python cross_document_analyzer.py --mode full
```
- 🔄 Phân tích lại tất cả entity pairs
- 🔄 Cập nhật confidence scores
- ⚠️ Expensive - sử dụng nhiều API calls

**Custom Analysis:**
```bash
# Chỉ phân tích specific documents
python cross_document_analyzer.py --documents "doc1.pdf,doc2.pdf"

# Chỉ phân tích specific course codes
python cross_document_analyzer.py --course-codes "CMP170,CMP175"

# Phân tích với custom parameters
python cross_document_analyzer.py \
  --confidence-threshold 0.85 \
  --max-relationships 10 \
  --batch-size 30
```

---

## 🔧 Advanced Usage

### **1. Relationship Quality Analysis**

```bash
# Analyze relationship quality distribution
python relationship_analyzer.py

# Generate quality report
python relationship_analyzer.py --report --output-file quality_report.json

# Filter by confidence levels
python relationship_analyzer.py --min-confidence 0.8 --max-confidence 1.0
```

**Sample Quality Report:**
```json
{
  "total_relationships": 1247,
  "confidence_distribution": {
    "high_confidence (0.8-1.0)": 342,
    "medium_confidence (0.6-0.8)": 651,
    "low_confidence (0.4-0.6)": 254
  },
  "relationship_types": {
    "RELATES_TO": 892,
    "SIMILAR_TO": 234,
    "DEPENDS_ON": 121
  },
  "top_connected_entities": [
    {"entity": "Java Programming", "connections": 45},
    {"entity": "Object-Oriented Programming", "connections": 38}
  ]
}
```

### **2. Performance Monitoring**

```bash
# Real-time monitoring during analysis
python monitor_analysis.py

# Check current progress
python check_progress.py

# Performance statistics
python performance_stats.py
```

**Monitor Output:**
```
🔄 CROSS-DOCUMENT ANALYSIS MONITORING
====================================
⏰ Started: 2025-07-15 10:30:00
📊 Progress: 342/1250 entity pairs (27.4%)
⚡ Speed: 15.3 pairs/minute
🎯 Confidence: Avg 0.73, High-quality: 68%
💰 API Usage: 1,247 calls, $12.45 estimated cost
⏱️ ETA: 59 minutes remaining

Recent relationships found:
✅ "Java OOP" → "Object Inheritance" (confidence: 0.87)
✅ "Database Design" → "Normalization" (confidence: 0.82)
✅ "Web Development" → "HTML Structure" (confidence: 0.79)
```

### **3. Batch Processing Scripts**

```python
# batch_processor.py - Custom batch processing
import os
from cross_document_analyzer import CrossDocumentAnalyzer

def process_course_batch(course_codes, config_overrides=None):
    """Process specific courses in batch"""
    analyzer = CrossDocumentAnalyzer()
    
    if config_overrides:
        analyzer.update_config(config_overrides)
    
    for course_code in course_codes:
        print(f"🎯 Processing course: {course_code}")
        
        # Get documents for this course
        documents = analyzer.get_documents_by_course(course_code)
        print(f"📄 Found {len(documents)} documents")
        
        # Analyze relationships within course
        results = analyzer.analyze_course_relationships(course_code)
        
        print(f"✅ Found {results['relationships_found']} relationships")
        print(f"💰 API calls used: {results['api_calls']}")
        print(f"⏱️ Processing time: {results['duration']:.2f} seconds\n")

# Usage
programming_courses = ["CMP170", "CMP175", "CMP177", "COS141"]
process_course_batch(programming_courses, {
    "confidence_threshold": 0.75,
    "max_relationships_per_entity": 20
})
```

### **4. Custom Relationship Rules**

```python
# custom_rules.py - Define domain-specific relationship rules
class CustomRelationshipRules:
    def __init__(self):
        self.programming_patterns = {
            "inheritance": {
                "keywords": ["extends", "inherits", "subclass", "parent class"],
                "relationship_type": "INHERITS_FROM",
                "confidence_boost": 0.15
            },
            "composition": {
                "keywords": ["contains", "has-a", "composed of"],
                "relationship_type": "CONTAINS",
                "confidence_boost": 0.12
            },
            "implementation": {
                "keywords": ["implements", "interface", "contract"],
                "relationship_type": "IMPLEMENTS",
                "confidence_boost": 0.18
            }
        }
        
        self.academic_patterns = {
            "prerequisite": {
                "keywords": ["prerequisite", "required before", "must complete"],
                "relationship_type": "PREREQUISITE_FOR",
                "confidence_boost": 0.20
            },
            "assessment": {
                "keywords": ["evaluated by", "tested through", "assessed via"],
                "relationship_type": "EVALUATED_BY",
                "confidence_boost": 0.14
            }
        }
    
    def apply_rules(self, entity1, entity2, context, base_confidence):
        """Apply custom rules to boost confidence"""
        boosted_confidence = base_confidence
        relationship_type = "RELATES_TO"  # default
        
        context_lower = context.lower()
        
        # Check programming patterns
        for pattern_name, pattern in self.programming_patterns.items():
            if any(keyword in context_lower for keyword in pattern["keywords"]):
                boosted_confidence += pattern["confidence_boost"]
                relationship_type = pattern["relationship_type"]
                break
        
        # Check academic patterns
        for pattern_name, pattern in self.academic_patterns.items():
            if any(keyword in context_lower for keyword in pattern["keywords"]):
                boosted_confidence += pattern["confidence_boost"]
                relationship_type = pattern["relationship_type"]
                break
        
        return min(boosted_confidence, 1.0), relationship_type

# Integration with main analyzer
analyzer = CrossDocumentAnalyzer()
analyzer.add_custom_rules(CustomRelationshipRules())
```

---

## 📊 Data Analysis & Reporting

### **1. Relationship Statistics**

```bash
# Generate comprehensive statistics
python generate_stats.py

# Export statistics to different formats
python generate_stats.py --format json --output stats.json
python generate_stats.py --format csv --output stats.csv
python generate_stats.py --format html --output report.html
```

### **2. Network Analysis**

```python
# network_analyzer.py - Analyze network properties
import networkx as nx
from neo4j import GraphDatabase

class NetworkAnalyzer:
    def __init__(self, neo4j_uri, username, password):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(username, password))
    
    def build_networkx_graph(self):
        """Convert Neo4j graph to NetworkX for analysis"""
        G = nx.Graph()
        
        with self.driver.session() as session:
            # Add nodes (entities)
            result = session.run("MATCH (e:__Entity__) RETURN e.id as entity")
            for record in result:
                G.add_node(record["entity"])
            
            # Add edges (relationships)
            result = session.run("""
                MATCH (e1:__Entity__)-[r:RELATES_TO]->(e2:__Entity__)
                RETURN e1.id as source, e2.id as target, r.confidence as weight
            """)
            for record in result:
                G.add_edge(
                    record["source"], 
                    record["target"], 
                    weight=record["weight"]
                )
        
        return G
    
    def analyze_network_properties(self):
        """Analyze network structure"""
        G = self.build_networkx_graph()
        
        analysis = {
            "basic_stats": {
                "nodes": G.number_of_nodes(),
                "edges": G.number_of_edges(),
                "density": nx.density(G),
                "average_clustering": nx.average_clustering(G)
            },
            "centrality_measures": {
                "degree_centrality": nx.degree_centrality(G),
                "betweenness_centrality": nx.betweenness_centrality(G),
                "closeness_centrality": nx.closeness_centrality(G),
                "eigenvector_centrality": nx.eigenvector_centrality(G)
            },
            "community_detection": {
                "communities": list(nx.community.greedy_modularity_communities(G)),
                "modularity": nx.community.modularity(G, nx.community.greedy_modularity_communities(G))
            }
        }
        
        return analysis

# Usage
analyzer = NetworkAnalyzer("neo4j://127.0.0.1:7687", "neo4j", "12345678")
network_props = analyzer.analyze_network_properties()
print(f"Network has {network_props['basic_stats']['nodes']} entities")
print(f"Average clustering coefficient: {network_props['basic_stats']['average_clustering']:.3f}")
```

### **3. Visualization Tools**

```python
# visualizer.py - Create network visualizations
import matplotlib.pyplot as plt
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px

class NetworkVisualizer:
    def __init__(self, network_analyzer):
        self.analyzer = network_analyzer
        self.graph = network_analyzer.build_networkx_graph()
    
    def create_static_visualization(self, output_file="network.png"):
        """Create static network visualization"""
        plt.figure(figsize=(15, 10))
        
        # Position nodes using spring layout
        pos = nx.spring_layout(self.graph, k=1, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(
            self.graph, pos, 
            node_color='lightblue',
            node_size=300,
            alpha=0.7
        )
        
        # Draw edges with weight-based width
        edges = self.graph.edges(data=True)
        weights = [edge[2]['weight'] * 3 for edge in edges]
        
        nx.draw_networkx_edges(
            self.graph, pos,
            width=weights,
            alpha=0.5,
            edge_color='gray'
        )
        
        # Add labels for high-degree nodes
        high_degree_nodes = [node for node, degree in self.graph.degree() if degree > 5]
        labels = {node: node for node in high_degree_nodes}
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8)
        
        plt.title("Cross-Document Entity Relationship Network")
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_interactive_visualization(self, output_file="network.html"):
        """Create interactive Plotly visualization"""
        pos = nx.spring_layout(self.graph, k=1, iterations=50)
        
        # Prepare edge traces
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in self.graph.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_info.append(f"{edge[0]} → {edge[1]} (confidence: {edge[2]['weight']:.2f})")
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Prepare node traces
        node_x = []
        node_y = []
        node_text = []
        node_info = []
        
        for node in self.graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            
            # Node info
            adjacencies = list(self.graph.neighbors(node))
            node_info.append(f'{node}<br>Connections: {len(adjacencies)}<br>' +
                           f'Connected to: {", ".join(adjacencies[:3])}{"..." if len(adjacencies) > 3 else ""}')
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="middle center",
            hovertext=node_info,
            marker=dict(
                size=10,
                color=[len(list(self.graph.neighbors(node))) for node in self.graph.nodes()],
                colorscale='YlOrRd',
                showscale=True,
                colorbar=dict(title="Number of Connections")
            )
        )
        
        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                        title='Interactive Cross-Document Entity Network',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        annotations=[ dict(
                            text="Entity relationships across documents",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002,
                            xanchor='left', yanchor='bottom',
                            font=dict(size=12)
                        )],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                       )
        
        fig.write_html(output_file)
        print(f"Interactive visualization saved to {output_file}")

# Usage
network_analyzer = NetworkAnalyzer("neo4j://127.0.0.1:7687", "neo4j", "12345678")
visualizer = NetworkVisualizer(network_analyzer)
visualizer.create_static_visualization("network_static.png")
visualizer.create_interactive_visualization("network_interactive.html")
```

---

## 🔍 Troubleshooting & Optimization

### **1. Common Issues & Solutions**

**API Rate Limiting:**
```bash
# Issue: "Rate limit exceeded" errors
# Solution: Adjust rate limiting parameters

# Check current API usage
python check_api_usage.py

# Reduce concurrent requests
export CONCURRENT_REQUESTS=2
export REQUESTS_PER_MINUTE=10

# Use multiple API keys
python cross_document_analyzer.py --use-multiple-keys
```

**Memory Issues:**
```bash
# Issue: Out of memory during large batch processing
# Solution: Reduce batch size and enable garbage collection

# Monitor memory usage
python memory_monitor.py &

# Reduce batch size
python cross_document_analyzer.py --batch-size 25

# Enable aggressive garbage collection
python -c "import gc; gc.set_threshold(100, 10, 10)"
```

**Performance Issues:**
```bash
# Issue: Slow processing speed
# Solutions:

# 1. Enable caching
export ENABLE_CACHING=true

# 2. Skip existing relationships
export SKIP_EXISTING_RELATIONSHIPS=true

# 3. Increase confidence threshold (fewer API calls)
python cross_document_analyzer.py --confidence-threshold 0.8

# 4. Use parallel processing
python cross_document_analyzer.py --parallel-workers 4
```

### **2. Performance Optimization Scripts**

```python
# optimizer.py - Performance optimization utilities
import time
import psutil
import gc
from functools import wraps

class PerformanceOptimizer:
    def __init__(self):
        self.stats = {
            'api_calls': 0,
            'cache_hits': 0,
            'processing_time': 0,
            'memory_usage': []
        }
    
    def monitor_performance(self, func):
        """Decorator to monitor function performance"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            result = func(*args, **kwargs)
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            self.stats['processing_time'] += end_time - start_time
            self.stats['memory_usage'].append({
                'function': func.__name__,
                'start_mb': start_memory,
                'end_mb': end_memory,
                'delta_mb': end_memory - start_memory
            })
            
            return result
        return wrapper
    
    def optimize_memory(self):
        """Force garbage collection and memory optimization"""
        gc.collect()
        
        # Clear caches if memory usage is high
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
        if current_memory > 1000:  # > 1GB
            self.clear_caches()
    
    def clear_caches(self):
        """Clear internal caches to free memory"""
        # Implementation depends on your caching strategy
        pass
    
    def get_performance_report(self):
        """Generate performance report"""
        avg_memory = sum(m['delta_mb'] for m in self.stats['memory_usage']) / len(self.stats['memory_usage'])
        
        return {
            'total_api_calls': self.stats['api_calls'],
            'cache_hit_ratio': self.stats['cache_hits'] / max(self.stats['api_calls'], 1),
            'total_processing_time': self.stats['processing_time'],
            'average_memory_delta': avg_memory,
            'peak_memory_usage': max(m['end_mb'] for m in self.stats['memory_usage'])
        }

# Usage in main analyzer
optimizer = PerformanceOptimizer()

@optimizer.monitor_performance
def analyze_entity_pair(entity1, entity2):
    # Your analysis logic here
    pass
```

### **3. Debugging Tools**

```python
# debugger.py - Debugging utilities
class RelationshipDebugger:
    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver
    
    def debug_entity_pair(self, entity1_id, entity2_id):
        """Debug specific entity pair analysis"""
        with self.driver.session() as session:
            # Get entity details
            result = session.run("""
                MATCH (e1:__Entity__ {id: $id1}), (e2:__Entity__ {id: $id2})
                OPTIONAL MATCH (e1)-[r:RELATES_TO]->(e2)
                RETURN e1, e2, r
            """, id1=entity1_id, id2=entity2_id)
            
            record = result.single()
            if record:
                entity1 = record['e1']
                entity2 = record['e2']
                relationship = record['r']
                
                print(f"🔍 DEBUGGING ENTITY PAIR")
                print(f"Entity 1: {entity1_id}")
                print(f"  Properties: {dict(entity1)}")
                print(f"Entity 2: {entity2_id}")
                print(f"  Properties: {dict(entity2)}")
                
                if relationship:
                    print(f"Existing Relationship: {dict(relationship)}")
                else:
                    print("No existing relationship found")
                
                # Simulate analysis
                confidence = self.simulate_analysis(entity1_id, entity2_id)
                print(f"Simulated confidence: {confidence:.3f}")
            else:
                print(f"❌ Entities not found: {entity1_id}, {entity2_id}")
    
    def simulate_analysis(self, entity1_id, entity2_id):
        """Simulate the analysis process for debugging"""
        # This would contain your actual analysis logic
        # Return a simulated confidence score
        return 0.75
    
    def validate_relationships(self, min_confidence=0.5):
        """Validate existing relationships"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e1:__Entity__)-[r:RELATES_TO]->(e2:__Entity__)
                WHERE r.confidence >= $min_conf
                RETURN e1.id as entity1, e2.id as entity2, r.confidence as confidence
                ORDER BY r.confidence DESC
            """, min_conf=min_confidence)
            
            relationships = list(result)
            print(f"📊 RELATIONSHIP VALIDATION")
            print(f"Found {len(relationships)} relationships with confidence >= {min_confidence}")
            
            for rel in relationships[:10]:  # Show top 10
                print(f"  {rel['entity1']} → {rel['entity2']} (confidence: {rel['confidence']:.3f})")
```

---

## 📈 Monitoring & Maintenance

### **1. Automated Monitoring**

```bash
# Start monitoring daemon
python monitoring_daemon.py --interval 300  # Check every 5 minutes

# Monitor specific metrics
python monitor_relationships.py --metric confidence_distribution
python monitor_relationships.py --metric processing_speed
python monitor_relationships.py --metric api_usage
```

### **2. Maintenance Scripts**

```bash
# Clean up low-confidence relationships
python cleanup_relationships.py --confidence-threshold 0.5

# Recompute confidence scores
python recompute_confidence.py

# Archive old analysis logs
python archive_logs.py --older-than 30days

# Database maintenance
python db_maintenance.py --optimize-indexes --vacuum
```

### **3. Health Check**

```python
# health_check.py - System health monitoring
class SystemHealthChecker:
    def __init__(self):
        self.checks = [
            self.check_neo4j_connection,
            self.check_api_keys,
            self.check_disk_space,
            self.check_memory_usage,
            self.check_relationship_quality
        ]
    
    def run_health_check(self):
        """Run comprehensive health check"""
        results = {}
        
        for check in self.checks:
            try:
                result = check()
                results[check.__name__] = {
                    'status': 'healthy' if result['healthy'] else 'unhealthy',
                    'details': result['details']
                }
            except Exception as e:
                results[check.__name__] = {
                    'status': 'error',
                    'details': str(e)
                }
        
        return results
    
    def check_neo4j_connection(self):
        """Check Neo4j database connectivity"""
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", "12345678"))
            driver.verify_connectivity()
            return {'healthy': True, 'details': 'Neo4j connection successful'}
        except Exception as e:
            return {'healthy': False, 'details': f'Neo4j connection failed: {e}'}
    
    def check_api_keys(self):
        """Check API key validity"""
        import os
        keys = [os.getenv(f'GEMINI_API_KEY_{i}') for i in range(1, 4)]
        valid_keys = [key for key in keys if key and len(key) > 20]
        
        return {
            'healthy': len(valid_keys) > 0,
            'details': f'{len(valid_keys)}/3 API keys configured'
        }
    
    def check_disk_space(self):
        """Check available disk space"""
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_gb = free / (1024**3)
        
        return {
            'healthy': free_gb > 5,  # At least 5GB free
            'details': f'{free_gb:.1f}GB free space'
        }
    
    def check_memory_usage(self):
        """Check system memory usage"""
        import psutil
        memory = psutil.virtual_memory()
        
        return {
            'healthy': memory.percent < 90,
            'details': f'{memory.percent:.1f}% memory used'
        }
    
    def check_relationship_quality(self):
        """Check relationship quality metrics"""
        # This would connect to Neo4j and check relationship statistics
        return {
            'healthy': True,
            'details': 'Relationship quality within normal parameters'
        }

# Usage
health_checker = SystemHealthChecker()
health_report = health_checker.run_health_check()

for check_name, result in health_report.items():
    status_icon = "✅" if result['status'] == 'healthy' else "❌"
    print(f"{status_icon} {check_name}: {result['details']}")
```

---

## 🎯 Best Practices

### **1. Configuration Management**
- Use environment-specific .env files
- Set appropriate rate limits to avoid API costs
- Monitor confidence thresholds based on domain
- Regular backup of analysis results

### **2. Quality Assurance**
- Manual review of high-confidence relationships
- Regular validation of relationship types
- Monitoring for false positives/negatives
- A/B testing different analysis parameters

### **3. Performance Optimization**
- Batch processing for large datasets
- Efficient caching strategies
- Memory management for long-running processes
- Load balancing across multiple API keys

### **4. Cost Management**
- Monitor API usage and costs
- Set daily/monthly spending limits
- Use confidence thresholds to reduce unnecessary calls
- Implement smart retry mechanisms

---

*Phần hướng dẫn cross-document-relationships này cung cấp đầy đủ thông tin để sử dụng module một cách hiệu quả và tối ưu.*
