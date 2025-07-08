# LLM Graph Builder - Setup Status

## ✅ Cài đặt hoàn tất

### Packages đã được cài đặt:

#### Backend Python Packages:
- ✅ Python virtual environment đã được thiết lập (Python 3.10.0)
- ✅ Tất cả 65 packages từ `requirements.txt` đã được cài đặt thành công
- ✅ Các packages chính:
  - FastAPI 0.115.12 (Web framework)
  - LangChain ecosystem (0.3.x) - AI/LLM frameworks
  - Neo4j drivers (5.28.1) - Graph database
  - Sentence Transformers 4.1.0 - Embeddings
  - Unstructured 0.17.2 - Document processing
  - OpenAI 1.86.0 - LLM integration
  - PyTorch 2.7.1 - Deep learning
  - RAGAS 0.2.15 - RAG evaluation

#### Frontend Node.js Packages:
- ✅ 831 packages đã được cài đặt thành công
- ✅ React 18.3.1 với TypeScript
- ✅ Neo4j visualization libraries
- ✅ Material-UI components
- ✅ Vite build tool
- ✅ TailwindCSS styling

### Files cấu hình:
- ✅ `.env` files được tạo từ `example.env` cho cả backend và frontend
- ✅ VS Code tasks được thiết lập

## 🚀 Cách sử dụng:

### 1. Chạy Backend:
```bash
# Sử dụng VS Code Task
Ctrl+Shift+P → Tasks: Run Task → "Run Backend Development Server"

# Hoặc chạy manual
cd backend
c:/edu/task1/llm-graph-builder/.venv/Scripts/python.exe -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```
Backend sẽ chạy tại: http://localhost:8000

### 2. Chạy Frontend:
```bash
# Sử dụng VS Code Task
Ctrl+Shift+P → Tasks: Run Task → "Run Frontend Development Server"

# Hoặc chạy manual
cd frontend
npm run dev
```
Frontend sẽ chạy tại: http://localhost:5173

### 3. Các Tasks có sẵn trong VS Code:
- **Run Backend Development Server** - Chạy FastAPI backend
- **Run Frontend Development Server** - Chạy React frontend  
- **Build Frontend** - Build production frontend
- **Install Backend Dependencies** - Cài đặt lại Python packages
- **Install Frontend Dependencies** - Cài đặt lại Node.js packages

## ⚙️ Cấu hình cần thiết:

### Neo4j Database:
Bạn cần cấu hình Neo4j database trong file `.env` của backend:
```
NEO4J_URI = "neo4j://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "your_password"
NEO4J_DATABASE = "neo4j"
```

### API Keys (tùy chọn):
Thêm các API keys vào file `.env` nếu muốn sử dụng:
```
OPENAI_API_KEY = "your_openai_key"
DIFFBOT_API_KEY = "your_diffbot_key"
LANGCHAIN_API_KEY = "your_langchain_key"
```

## 📝 Ghi chú:
- Project sử dụng Knowledge Graph để chuyển đổi dữ liệu phi cấu trúc thành cấu trúc
- Hỗ trợ nhiều loại files: PDF, DOC, TXT, YouTube videos, web pages
- Tích hợp với nhiều LLM models: OpenAI, Gemini, Diffbot, etc.
- Có thể chat với dữ liệu đã được xử lý

## 🔧 Troubleshooting:
1. Nếu backend không start được, kiểm tra Neo4j connection
2. Nếu frontend có lỗi, thử `npm audit fix` trong folder frontend
3. Đảm bảo ports 8000 (backend) và 5173 (frontend) không bị chiếm dụng
