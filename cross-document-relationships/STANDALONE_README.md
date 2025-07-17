# Cross-Document Relationships - Standalone Server

## Chạy hoàn toàn độc lập với Backend chính

Đây là hướng dẫn để chạy Cross-Document Relationships như một **server riêng biệt**, không cần sửa đổi code backend hiện tại.

## 🚀 Cách chạy nhanh

### Phương pháp 1: Sử dụng script tự động
```bash
# Windows Command Prompt
start_server.bat

# Windows PowerShell
.\start_server.ps1
```

### Phương pháp 2: Chạy thủ công
```bash
# 1. Cài đặt dependencies
pip install -r requirements_standalone.txt

# 2. Cấu hình environment
copy .env.example .env
# Chỉnh sửa .env với thông tin của bạn

# 3. Chạy server
python standalone_server.py
```

## 📡 Server Information

- **Port**: 8001 (khác với backend chính port 8000)
- **URL**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 🔧 Cấu hình

### 1. Neo4j Database
Chỉnh sửa file `.env`:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
```

### 2. Gemini API Keys
```env
GEMINI_API_KEYS=key1,key2,key3
CROSS_DOC_SIMILARITY_THRESHOLD=0.75
CROSS_DOC_CONFIDENCE_THRESHOLD=0.6
CROSS_DOC_BATCH_SIZE=50
```

## 📋 API Endpoints

### GET /
Thông tin cơ bản về server

### GET /health
Kiểm tra trạng thái server

### GET /status
Thông tin chi tiết về hệ thống

### GET /similar-entities
Lấy các entity pairs tương tự
```bash
curl "http://localhost:8001/similar-entities?limit=100&threshold=0.8"
```

### POST /analyze
Chạy phân tích cross-document relationships
```bash
curl -X POST "http://localhost:8001/analyze" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "max_pairs=1000&batch_size=50&similarity_threshold=0.75"
```

### POST /reset-llm-keys
Reset các API keys đã failed

## 🔄 Workflow

1. **Khởi động server**: Chạy `start_server.bat` hoặc `start_server.ps1`
2. **Kiểm tra health**: Truy cập http://localhost:8001/health
3. **Xem API docs**: Truy cập http://localhost:8001/docs
4. **Chạy phân tích**: POST request đến `/analyze`
5. **Xem kết quả**: GET request đến `/similar-entities`

## 🏗️ Kiến trúc

```
Cross-Document Server (Port 8001)    Backend Chính (Port 8000)
├── FastAPI Application               ├── LLM Graph Builder
├── Cross-Document Analyzer           ├── Document Processing  
├── Neo4j Connection                  ├── Entity Extraction
├── Gemini LLM Client                 ├── Graph Creation
└── Independent APIs                  └── Main APIs
      ↓                                     ↓
  Same Neo4j Database ← Shared Data Source →
```

## ✅ Ưu điểm của phương pháp này

1. **Không ảnh hưởng backend chính**: Không cần sửa code backend
2. **Chạy độc lập**: Server riêng biệt trên port khác
3. **Dễ maintenance**: Có thể stop/start riêng biệt
4. **Scalable**: Có thể deploy trên server khác
5. **API riêng**: Có documentation và endpoints độc lập

## 🔍 Debugging

### Kiểm tra logs
```bash
# Server logs
tail -f cross_document_server.log

# Real-time logs
python standalone_server.py
```

### Test connections
```bash
# Health check
curl http://localhost:8001/health

# Neo4j status
curl http://localhost:8001/status
```

## 📦 Dependencies

Server sử dụng `requirements_standalone.txt` với các packages cần thiết:
- FastAPI & Uvicorn (web server)
- Neo4j driver
- Google Generative AI (Gemini)
- Python-dotenv (environment variables)

## 🚦 Trạng thái Server

- **🟢 Healthy**: Tất cả components hoạt động bình thường
- **🟡 Degraded**: Neo4j connection có vấn đề nhưng server vẫn chạy
- **🔴 Error**: Server không thể khởi động

## 💡 Tips

1. **Port conflicts**: Nếu port 8001 bị chiếm, sửa trong `standalone_server.py`
2. **Memory usage**: Điều chỉnh `batch_size` nếu gặp vấn đề memory
3. **API rate limits**: Sử dụng nhiều Gemini API keys để tránh rate limiting
4. **Performance**: Chạy trên server riêng để tối ưu performance

Bây giờ bạn có thể chạy Cross-Document Relationships hoàn toàn độc lập! 🎉
