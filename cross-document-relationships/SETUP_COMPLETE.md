# 🎯 CROSS-DOCUMENT RELATIONSHIPS - HOÀN TOÀN ĐỘC LẬP

## ✅ ĐÃ HOÀN THÀNH

Bạn đã có **Cross-Document Relationships** chạy **hoàn toàn độc lập** với backend chính!

### 📁 Files đã tạo:
- `standalone_server.py` - Server chính (FastAPI)
- `requirements_standalone.txt` - Dependencies riêng
- `start_server.bat` - Script khởi động Windows
- `start_server.ps1` - Script khởi động PowerShell  
- `simple_demo.py` - Demo test functionality
- `STANDALONE_README.md` - Hướng dẫn chi tiết

## 🚀 CÁCH CHẠY

### Option 1: Script tự động
```bash
cd C:\edu\task1\llm-graph-builder\cross-document-relationships
start_server.bat
```

### Option 2: Thủ công
```bash
cd C:\edu\task1\llm-graph-builder\cross-document-relationships
pip install -r requirements_standalone.txt
python standalone_server.py
```

### Option 3: Test đơn giản
```bash
cd C:\edu\task1\llm-graph-builder\cross-document-relationships
python simple_demo.py
```

## 🌐 SERVER ENDPOINTS

**Server URL**: http://localhost:8001 (Port khác backend chính)

### API Endpoints:
- `GET /` - Thông tin server
- `GET /health` - Health check
- `GET /status` - Status chi tiết
- `GET /similar-entities` - Lấy entity pairs tương tự
- `POST /analyze` - Chạy phân tích cross-document
- `POST /reset-llm-keys` - Reset API keys failed

### API Documentation:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## ⚙️ CẤU HÌNH

### 1. Environment Variables (.env)
```env
# Neo4j (dùng chung với backend chính)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j

# Gemini API Keys
GEMINI_API_KEYS=key1,key2,key3

# Analysis Settings
CROSS_DOC_SIMILARITY_THRESHOLD=0.75
CROSS_DOC_CONFIDENCE_THRESHOLD=0.6
CROSS_DOC_BATCH_SIZE=50
CROSS_DOC_MAX_PAIRS=1000
```

### 2. Dependencies
Server có `requirements_standalone.txt` riêng với các packages cần thiết:
- FastAPI + Uvicorn (web framework)
- Neo4j driver
- Google Generative AI
- Python-dotenv

## 🏗️ KIẾN TRÚC HOÀN TOÀN ĐỘC LẬP

```
┌─────────────────────────────────────────────────────────────┐
│                   LLM GRAPH BUILDER                        │
├─────────────────────────────────────────────────────────────┤
│ Backend Chính (Port 8000)    │ Cross-Document (Port 8001)  │
│ ├── Document Processing      │ ├── Standalone FastAPI      │
│ ├── Entity Extraction        │ ├── CrossDocumentAnalyzer   │
│ ├── Graph Creation           │ ├── Gemini LLM Client       │
│ ├── Main APIs                │ ├── Independent APIs        │
│ └── score.py (KHÔNG SỬA)     │ └── standalone_server.py    │
├─────────────────────────────────────────────────────────────┤
│                    Neo4j Database                          │
│              (Shared data source)                          │
└─────────────────────────────────────────────────────────────┘
```

## ✅ ƯU ĐIỂM

1. **Không ảnh hưởng backend**: Không cần sửa code backend hiện tại
2. **Chạy độc lập**: Server riêng biệt trên port khác  
3. **Dễ maintain**: Stop/start riêng biệt
4. **Scalable**: Có thể deploy trên server khác
5. **API documentation**: Swagger UI riêng
6. **Error isolation**: Lỗi không ảnh hưởng backend chính

## 📊 WORKFLOW SỬ DỤNG

1. **Start backend chính**: `python backend/score.py` (Port 8000)
2. **Start cross-document**: `python standalone_server.py` (Port 8001)
3. **Upload documents**: Qua backend chính
4. **Analyze relationships**: Qua cross-document server
5. **View results**: API endpoints hoặc Neo4j Browser

## 🔧 EXAMPLE API CALLS

```bash
# Health check
curl http://localhost:8001/health

# Get system status  
curl http://localhost:8001/status

# Find similar entities
curl "http://localhost:8001/similar-entities?limit=100"

# Run analysis
curl -X POST http://localhost:8001/analyze \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "max_pairs=500&batch_size=25&similarity_threshold=0.8"
```

## 🚦 STATUS CHECK

✅ **Simple Demo**: `python simple_demo.py` - WORKING  
✅ **Imports**: All modules imported successfully  
✅ **Analyzer**: CrossDocumentAnalyzer created  
✅ **Config**: Settings loaded correctly  

## 🎉 KẾT QUẢ

**Cross-Document Relationships giờ đây chạy hoàn toàn độc lập!**

- ✅ Không cần sửa backend chính
- ✅ Server riêng biệt (Port 8001)  
- ✅ API documentation đầy đủ
- ✅ Dễ dàng maintenance và scaling
- ✅ Error isolation hoàn toàn

**Ready to use! 🚀**
