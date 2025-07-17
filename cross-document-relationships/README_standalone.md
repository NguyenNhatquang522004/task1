# Cross-Document Relationships - Standalone System

## 🎯 Mục đích chính
Hệ thống này **tách biệt hoàn toàn** với backend chính, tập trung vào việc **gán mối quan hệ cho các entity ở document khác nhau**.

### Core Functionality
- 🔍 **Tìm entity pairs**: Phát hiện entities tương tự từ documents khác nhau
- 🧠 **Phân tích LLM**: Sử dụng Gemini để xác định semantic relationships
- 🔗 **Gán relationships**: Tạo relationships trong Neo4j graph
- 📊 **Thống kê**: Monitoring và reporting chi tiết

## 🏗️ Kiến trúc Standalone

```
Backend (Port 8000)          Cross-Document System (Port 8001)
     │                                    │
     ├─ PDF Processing                    ├─ Entity Pair Discovery
     ├─ Entity Extraction                 ├─ LLM Relationship Analysis  
     ├─ Graph Building                    ├─ Cross-Document Assignment
     └─ Question Answering                └─ Statistics & Monitoring
                    │                     │
                    └───── Neo4j DB ──────┘
                      (Shared Data Layer)
```

## 🚀 Khởi động nhanh

### 1. Setup môi trường
```bash
cd cross-document-relationships
pip install -r requirements_standalone.txt
```

### 2. Cấu hình environment
Tạo file `.env`:
```env
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

GEMINI_API_KEY_1=your_key_1
GEMINI_API_KEY_2=your_key_2
GEMINI_API_KEY_3=your_key_3
```

### 3. Khởi động server
```bash
# Windows
start_server.bat

# Linux/Mac
./start_server.sh

# Manual
python standalone_server.py
```

### 4. Test hệ thống
```bash
python test_cross_document_demo.py
```

## 📋 API Endpoints

### Core Analysis
- **POST /analyze** - Chạy phân tích cross-document relationships
- **GET /entity-pairs** - Preview entity pairs tiềm năng
- **GET /cross-document-stats** - Thống kê relationships hiện tại

### Monitoring
- **GET /health** - Health check
- **GET /status** - System status chi tiết
- **POST /reset-llm-keys** - Reset LLM keys khi gặp lỗi

## 🔧 Sử dụng API

### Chạy phân tích cross-document
```bash
curl -X POST "http://localhost:8001/analyze" \
  -F "max_pairs=1000" \
  -F "batch_size=10" \
  -F "similarity_threshold=0.75" \
  -F "confidence_threshold=0.6"
```

### Lấy thống kê
```bash
curl "http://localhost:8001/cross-document-stats"
```

### Preview entity pairs
```bash
curl "http://localhost:8001/entity-pairs?limit=50&similarity_threshold=0.75"
```

## 📊 Output Examples

### Cross-Document Statistics
```json
{
  "status": "success",
  "data": {
    "cross_document_relationships": 1250,
    "documents_with_cross_connections": 45,
    "relationship_types": {
      "RELATED": 680,
      "PREREQUISITE": 230,
      "EQUIVALENT": 180,
      "CONTAINS": 160
    },
    "top_connected_entities": [
      {"entity": "Machine Learning", "connections": 89},
      {"entity": "Data Science", "connections": 67}
    ]
  }
}
```

### Entity Pairs Discovery
```json
{
  "status": "success",
  "data": {
    "entity_pairs": [
      {
        "entity1": "Artificial Intelligence",
        "entity2": "AI",
        "similarity": 0.89,
        "document1": "AI_Overview.pdf",
        "document2": "Tech_Trends.pdf"
      }
    ],
    "total_found": 456,
    "similarity_threshold": 0.75
  }
}
```

## 🔍 Core Algorithm

### 1. Entity Pair Discovery
```python
# Tìm entities từ documents khác nhau có similarity cao
pairs = await assigner.find_cross_document_entity_pairs(
    max_pairs=1000,
    similarity_threshold=0.75
)
```

### 2. LLM Relationship Analysis
```python
# Phân tích semantic relationship bằng Gemini
relationship = await assigner.analyze_entity_relationship(
    entity1, entity2, 
    context1, context2
)
```

### 3. Graph Assignment
```python
# Gán relationship vào Neo4j
await assigner.create_cross_document_relationship(
    entity1, entity2, 
    relationship_type, 
    confidence_score
)
```

## 🎛️ Configuration

### Similarity Thresholds
- **0.85+**: Very high similarity (likely same concept)
- **0.75-0.84**: High similarity (strong relationship)
- **0.65-0.74**: Medium similarity (potential relationship)
- **<0.65**: Low similarity (unlikely relationship)

### Relationship Types
- **RELATED**: General semantic relationship
- **PREREQUISITE**: One concept requires another
- **EQUIVALENT**: Same or very similar concepts
- **CONTAINS**: One concept includes another
- **OPPOSITE**: Contrasting concepts
- **CAUSES**: Causal relationship

## 📈 Performance Metrics

### Typical Processing Stats
- **Entity pair discovery**: ~1000 pairs/minute
- **LLM analysis**: ~50 pairs/minute (limited by API)
- **Graph assignment**: ~500 relationships/minute
- **Memory usage**: ~200MB for 10K entities

### Optimization Tips
- Adjust `batch_size` for LLM calls (default: 10)
- Use higher `similarity_threshold` for precision
- Monitor API key rotation for Gemini

## 🔧 Troubleshooting

### Common Issues
1. **LLM API limits**: Server automatically rotates keys
2. **Neo4j connection**: Check connection string and credentials
3. **Memory issues**: Reduce `max_pairs` parameter

### Debug Mode
```bash
# Enable debug logging
PYTHONPATH=. python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
exec(open('standalone_server.py').read())
"
```

## 📁 File Structure
```
cross-document-relationships/
├── standalone_server.py              # Main FastAPI server
├── cross_document_relationship_assigner.py  # Core algorithm
├── test_cross_document_demo.py       # Testing script
├── requirements_standalone.txt       # Dependencies
├── start_server.bat/.sh             # Startup scripts
├── src/
│   ├── core/analyzer.py             # Base analyzer
│   ├── llm/gemini_client.py         # LLM integration
│   └── config/settings.py           # Configuration
└── README.md                        # This file
```

## 🎯 Key Benefits

### ✅ Complete Independence
- Chạy tách biệt hoàn toàn với backend
- Port 8001 (khác với backend port 8000)
- Không ảnh hưởng đến backend workflow

### ✅ Focused Functionality
- Tập trung 100% vào cross-document relationships
- Không bị phân tâm bởi PDF processing hay QA
- Tối ưu cho entity relationship analysis

### ✅ Scalable Architecture
- Async processing cho performance cao
- Batch processing cho LLM efficiency
- Memory-efficient entity handling

### ✅ Production Ready
- Comprehensive error handling
- Health checks và monitoring
- API key rotation và failover

---

## 🚀 Bắt đầu ngay!

1. **Setup**: `pip install -r requirements_standalone.txt`
2. **Config**: Tạo `.env` với Neo4j và Gemini keys
3. **Start**: `python standalone_server.py`
4. **Test**: `python test_cross_document_demo.py`
5. **Monitor**: `http://localhost:8001/docs`

**Hệ thống sẽ tự động phân tích và gán mối quan hệ cho entities từ các documents khác nhau một cách hoàn toàn độc lập!** 🎯
