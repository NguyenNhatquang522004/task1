# Cross-Document Entity Relationships

Mô-đun phân tích mối quan hệ giữa các entity từ các tài liệu khác nhau trong hệ thống LLM Graph Builder.

## Tổng quan

Module này cung cấp khả năng phân tích và tạo mối quan hệ giữa các entity từ các tài liệu khác nhau, sử dụng:
- Vector similarity để tìm các entity cặp tương đồng
- LLM để phân tích mối quan hệ ngữ nghĩa  
- 5 loại mối quan hệ: PREREQUISITE, EQUIVALENT, RELATED, CONTAINS, UNRELATED

## Cấu trúc thư mục

```
cross-document-relationships/
├── src/
│   ├── constants.py          # Hằng số và queries
│   ├── api/
│   │   └── routes.py         # FastAPI endpoints
│   ├── core/
│   │   └── analyzer.py       # Logic phân tích chính
│   └── utils/
│       └── helpers.py        # Utility functions
├── config/
│   └── settings.py           # Cấu hình
├── tests/
│   ├── conftest.py          # Test fixtures
│   └── test_analyzer.py     # Unit tests
├── integration.py           # Tích hợp với ứng dụng chính
└── README.md
```

## Các loại mối quan hệ

1. **PREREQUISITE** - Entity1 là tiên quyết cho Entity2
2. **EQUIVALENT** - Hai entity đại diện cho cùng một khái niệm
3. **RELATED** - Có liên quan về mặt khái niệm nhưng riêng biệt
4. **CONTAINS** - Entity1 bao quát/chứa Entity2
5. **UNRELATED** - Không có mối quan hệ có nghĩa

## API Endpoints

### POST /cross-document/analyze
Bắt đầu phân tích mối quan hệ cross-document

```json
{
  "similarity_threshold": 0.75,
  "confidence_threshold": 0.6,
  "batch_size": 50,
  "max_pairs": 1000
}
```

### GET /cross-document/relationships
Lấy danh sách mối quan hệ đã tạo với filtering

Query parameters:
- `document1`: Filter theo document 1
- `document2`: Filter theo document 2  
- `relationship_type`: Filter theo loại mối quan hệ

### GET /cross-document/similar-entities
Tìm các entity pairs tương đồng mà chưa phân tích

Query parameters:
- `similarity_threshold`: Ngưỡng similarity (default: 0.75)
- `limit`: Số lượng pairs tối đa (default: 100)

### DELETE /cross-document/relationships
Xóa mối quan hệ cross-document với filtering

### GET /cross-document/llm-status
Kiểm tra trạng thái LLM client (đặc biệt hữu ích cho Gemini key rotation)

### POST /cross-document/reset-failed-keys  
Reset các API keys đã bị đánh dấu lỗi (hữu ích khi keys khả dụng trở lại)

### GET /cross-document/stats
Thống kê về mối quan hệ cross-document

### GET /cross-document/documents
Danh sách documents có mối quan hệ cross-document

## Cấu hình Gemini 2.0 Flash

Module đã được tối ưu để sử dụng Gemini 2.0 Flash với multiple API keys luân phiên:

```bash
# Multiple Gemini API Keys (ngăn cách bằng dấu phẩy)
GEMINI_API_KEYS=key1,key2,key3,key4,key5

# Fallback single key
GEMINI_API_KEY=your_single_key

# Model Gemini
CROSS_DOC_LLM_MODEL=gemini-2.0-flash
CROSS_DOC_LLM_TEMPERATURE=0.1
CROSS_DOC_LLM_MAX_TOKENS=2048

# Retry và error handling
CROSS_DOC_MAX_RETRIES=3
CROSS_DOC_RETRY_DELAY=1.0

# Cấu hình logging
CROSS_DOC_LOG_LEVEL=INFO
CROSS_DOC_LOG_FILE=cross_document_analysis.log
```

## 🔥 Gemini 2.0 Flash Features

### ✅ Multiple API Key Rotation
- Tự động luân phiên multiple API keys
- Fail-over khi key bị rate limit/quota exceeded
- Reset failed keys thông qua API endpoint

### ✅ Enhanced Error Handling
- Exponential backoff cho retries
- Phân biệt lỗi authentication vs temporary errors
- Graceful degradation khi tất cả keys fail

### ✅ Performance Optimization
- Async processing với retry logic
- Batch processing với error recovery
- Real-time monitoring của key status

### ✅ Safety & Content Filtering
- Built-in Gemini safety settings
- Proper handling của content filtering
- Fallback strategies cho blocked content

## Tích hợp với LLM Graph Builder

### 1. Setup với Gemini (Recommended)

```python
from cross_document_relationships.integration import setup_cross_document_analysis

# Trong main FastAPI app
app = FastAPI()

# Setup với Gemini 2.0 Flash (auto key rotation)
setup_cross_document_analysis(app, neo4j_driver=neo4j_driver, use_gemini=True)

# Hoặc setup với LLM client riêng
setup_cross_document_analysis(app, llm_client=your_llm_client, neo4j_driver=neo4j_driver, use_gemini=False)
```

### 2. Environment Setup

```bash
# Copy và edit .env file
cp cross-document-relationships/.env.example .env

# Thêm Gemini API keys
GEMINI_API_KEYS=AIzaSyA...,AIzaSyB...,AIzaSyC...
```

### 3. Sử dụng analyzer

```python
from cross_document_relationships.integration import get_cross_document_analyzer

analyzer = get_cross_document_analyzer()
if analyzer:
    result = await analyzer.analyze_all_relationships()
```

## Workflow phân tích

1. **Tìm entity pairs**: Sử dụng vector similarity để tìm các entity từ documents khác nhau có độ tương đồng cao
2. **Lấy context**: Thu thập context của mỗi entity từ chunks và descriptions
3. **Phân tích LLM**: Sử dụng LLM để phân tích mối quan hệ giữa entity pairs
4. **Tạo relationships**: Lưu kết quả phân tích vào Neo4j với confidence score
5. **Filtering**: Chỉ tạo relationships có confidence >= threshold

## Neo4j Schema

```cypher
# Relationship pattern
(Entity1)-[:CROSS_DOC_RELATIONSHIP {
  type: "PREREQUISITE|EQUIVALENT|RELATED|CONTAINS|UNRELATED",
  confidence: 0.85,
  explanation: "Explanation text",
  direction: "entity1_to_entity2|entity2_to_entity1|bidirectional",
  created_at: datetime(),
  analysis_version: "1.0"
}]->(Entity2)
```

## Testing

Chạy tests:

```bash
cd cross-document-relationships
python -m pytest tests/ -v
```

Test coverage bao gồm:
- Unit tests cho analyzer core logic
- Mock tests cho LLM và Neo4j interactions
- Integration tests cho API endpoints

## Performance Considerations

- **Batch processing**: Xử lý entity pairs theo batches để tránh memory overflow
- **Similarity threshold**: Ngưỡng cao hơn = ít pairs hơn nhưng chất lượng tốt hơn
- **Confidence filtering**: Chỉ lưu relationships có confidence cao
- **Context limiting**: Giới hạn độ dài context để tối ưu LLM calls

## Monitoring

- Logs được lưu vào file cấu hình
- Processing statistics sau mỗi analysis run
- Health check endpoint cho monitoring
- Error tracking và reporting

## Troubleshooting

### Lỗi thường gặp

1. **No similar entities found**: Kiểm tra similarity_threshold, có thể cần giảm xuống
2. **LLM errors**: Kiểm tra API keys và network connectivity  
3. **Neo4j errors**: Verify database connection và schema
4. **Low confidence results**: Có thể cần adjust confidence_threshold hoặc improve entity contexts

### Debug mode

```bash
CROSS_DOC_LOG_LEVEL=DEBUG
```

Sẽ hiển thị chi tiết về:
- Entity pairs được tìm thấy
- LLM prompts và responses
- Confidence scores và filtering decisions
- Database operations

## Future Enhancements

- [ ] Parallel processing cho large datasets
- [ ] Caching LLM responses để tránh duplicate calls
- [ ] Advanced relationship types
- [ ] Confidence calibration
- [ ] Relationship quality metrics
- [ ] Export/import functionality
- [ ] Visualization của relationship networks
