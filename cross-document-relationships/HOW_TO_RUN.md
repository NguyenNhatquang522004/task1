# 🚀 Cách chạy Cross-Document Relationships

## 📋 Hai chế độ hoạt động

### 1️⃣ **Manual Mode** (Mặc định)
```bash
python standalone_server.py
```
- Server khởi động và **CHỜ** API calls
- **KHÔNG** tự động tìm và gán mối quan hệ
- Phải gọi `POST /analyze` để bắt đầu phân tích

### 2️⃣ **Auto Mode** (Tự động)
```bash
# Cấu hình trong .env
AUTO_START_ANALYSIS=true
AUTO_MAX_PAIRS=1000
AUTO_BATCH_SIZE=10
AUTO_SIMILARITY_THRESHOLD=0.75

# Chạy server
python standalone_server.py
```
- Server khởi động và **TỰ ĐỘNG** bắt đầu phân tích
- Tìm và gán mối quan hệ cross-document ngay lập tức
- Hiển thị kết quả trong console

## 🔧 Cấu hình Auto Mode

### Bước 1: Copy .env file
```bash
copy .env.example .env
```

### Bước 2: Cấu hình .env
```env
# Bật chế độ tự động
AUTO_START_ANALYSIS=true

# Tùy chỉnh parameters
AUTO_MAX_PAIRS=1000          # Số entity pairs tối đa
AUTO_BATCH_SIZE=10           # Batch size cho LLM
AUTO_SIMILARITY_THRESHOLD=0.75  # Ngưỡng similarity

# Neo4j connection
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# Gemini API keys
GEMINI_API_KEYS=key1,key2,key3
```

### Bước 3: Chạy server
```bash
python standalone_server.py
```

## 📊 Output trong Auto Mode

```
🚀 Starting Cross-Document Relationships Server
============================================================
✅ Successfully imported cross-document modules
🔗 Setting up Neo4j connection...
✅ Neo4j: Connected!
✅ Neo4j connection established
✅ Cross-document analyzer initialized
📊 Similarity threshold: 0.75
📦 Batch size: 10
🔑 3 Gemini API keys configured
============================================================
🎉 Cross-Document Relationships Server Ready!
📚 API Documentation: http://localhost:8001/docs
============================================================

🤖 AUTO_START_ANALYSIS enabled - Starting automatic relationship assignment...

🔍 Starting automatic cross-document relationship analysis...
⚙️  Auto analysis parameters:
   - Max pairs: 1000
   - Batch size: 10
   - Similarity threshold: 0.75

✅ Automatic analysis completed!
🔗 Created relationships: 156
📊 Processed pairs: 487
📈 Success rate: 32.0%
📋 Total cross-document relationships: 1,234
============================================================
```

## 🎯 Khi nào dùng chế độ nào?

### Manual Mode - Dùng khi:
- ✅ Muốn kiểm soát thời điểm chạy analysis
- ✅ Test và debug system  
- ✅ Chạy với parameters khác nhau
- ✅ Tích hợp với workflow khác

### Auto Mode - Dùng khi:
- ✅ Muốn analysis ngay khi có data mới
- ✅ Chạy automated pipeline
- ✅ Production deployment
- ✅ Scheduled processing

## 🔄 Kết hợp hai chế độ

Ngay cả trong Auto Mode, bạn vẫn có thể:
- Gọi `POST /analyze` để chạy analysis thêm
- Thay đổi parameters qua API
- Monitor qua `/status` và `/cross-document-stats`

## 💡 Tips

1. **Development**: Dùng Manual Mode với `AUTO_START_ANALYSIS=false`
2. **Production**: Dùng Auto Mode với `AUTO_START_ANALYSIS=true`
3. **Testing**: Dùng parameters nhỏ (MAX_PAIRS=50, BATCH_SIZE=5)
4. **Performance**: Tăng BATCH_SIZE nếu có nhiều API keys

---

**Trả lời câu hỏi**: 
- Mặc định: **KHÔNG**, phải gọi API `/analyze`
- Với `AUTO_START_ANALYSIS=true`: **CÓ**, tự động khi khởi động
