# PHÂN TÍCH CHI TIẾT: CÁCH TẠO RELATIONSHIPS GIỮA CÁC CHUNKS

## 🚫 TRĂNG ĐÁP CÂU HỎI: KHÔNG PHẢI TẤT CẢ RELATIONSHIPS ĐỀU PHỤ THUỘC VÀO SENTENCE EMBEDDING

Relationships giữa các chunks được tạo theo **2 phương thức khác nhau**:

---

## 📍 PHƯƠNG THỨC 1: RELATIONSHIPS DỰA TRÊN VỊ TRÍ TUẦN TỰ (KHÔNG PHỤ THUỘC EMBEDDING)

### File: `backend/src/make_relationships.py` → `create_relation_between_chunks()`

### Các relationships được tạo dựa trên **thứ tự xuất hiện** trong document:

#### 1. **PART_OF** - Chunk thuộc về Document
```python
# Được tạo cho TẤT CẢ chunks, không cần embedding
MERGE (c:Chunk {id: data.id})
MERGE (c)-[:PART_OF]->(d:Document)
```
- **Điều kiện**: Mọi chunk đều có relationship này
- **Phụ thuộc**: Chỉ phụ thuộc vào `file_name`
- **Embedding**: KHÔNG cần

#### 2. **FIRST_CHUNK** - Document → Chunk đầu tiên
```python
if i == 0:  # Chunk đầu tiên
    firstChunk = True
    relationships.append({"type": "FIRST_CHUNK", "chunk_id": current_chunk_id})
```
- **Điều kiện**: `position == 1` (chunk đầu tiên)
- **Phụ thuộc**: Thứ tự trong document
- **Embedding**: KHÔNG cần

#### 3. **NEXT_CHUNK** - Chunk trước → Chunk sau
```python
else:  # Các chunk tiếp theo
    relationships.append({
        "type": "NEXT_CHUNK",
        "previous_chunk_id": previous_chunk_id,
        "current_chunk_id": current_chunk_id
    })
```
- **Điều kiện**: `position > 1` (tuần tự theo thứ tự)
- **Phụ thuộc**: Vị trí liền kề trong document
- **Embedding**: KHÔNG cần

### 🎯 **QUAN TRỌNG**: Các relationships này được tạo **TRƯỚC KHI** có embeddings!

---

## 📍 PHƯƠNG THỨC 2: RELATIONSHIPS DỰA TRÊN EMBEDDING SIMILARITY

### File: `backend/src/graphDB_dataAccess.py` → `update_KNN_graph()`

#### 4. **SIMILAR** - Chunk ↔ Chunk (dựa trên embedding similarity)
```python
def update_KNN_graph(self):
    knn_min_score = os.environ.get('KNN_MIN_SCORE')  # default: 0.8
    
    self.graph.query("""
        MATCH (c:Chunk)
        WHERE c.embedding IS NOT NULL AND count { (c)-[:SIMILAR]-() } < 5
        CALL db.index.vector.queryNodes('vector', 6, c.embedding) 
        YIELD node, score
        WHERE node <> c and score >= $score 
        MERGE (c)-[rel:SIMILAR]-(node) 
        SET rel.score = score
    """, {"score": float(knn_min_score)})
```

**Đặc điểm**:
- **Điều kiện**: `c.embedding IS NOT NULL` - BẮT BUỘC phải có embedding
- **Phụ thuộc**: Cosine similarity score ≥ threshold
- **Embedding**: **CẦN THIẾT**
- **Giới hạn**: Tối đa 5 SIMILAR relationships per chunk

---

## 🔄 TIMELINE THỰC THI

### Giai đoạn 1: Tạo Structural Relationships (KHÔNG cần embedding)
```python
# 1. Tạo chunks và basic relationships
create_relation_between_chunks(graph, file_name, chunks)
# → Tạo: PART_OF, FIRST_CHUNK, NEXT_CHUNK
```

### Giai đoạn 2: Tạo Embeddings
```python
# 2. Tạo embeddings cho chunks
create_chunk_embeddings(graph, chunkId_chunkDoc_list, file_name)
# → Cập nhật property: c.embedding
```

### Giai đoạn 3: Tạo Similarity Relationships (CẦN embedding)
```python
# 3. Tạo SIMILAR relationships
graphDb_data_Access.update_KNN_graph()
# → Tạo: SIMILAR (dựa trên vector similarity)
```

---

## 📊 BẢNG SO SÁNH CÁC RELATIONSHIPS

| Relationship Type | Phụ thuộc Embedding? | Điều kiện tạo | Thời điểm tạo |
|-------------------|---------------------|---------------|---------------|
| **PART_OF** | ❌ KHÔNG | Mọi chunk | Giai đoạn 1 |
| **FIRST_CHUNK** | ❌ KHÔNG | position == 1 | Giai đoạn 1 |
| **NEXT_CHUNK** | ❌ KHÔNG | position > 1, liền kề | Giai đoạn 1 |
| **HAS_ENTITY** | ❌ KHÔNG | Chunk có entities | Sau LLM extraction |
| **SIMILAR** | ✅ CÓ | cosine similarity ≥ threshold | Giai đoạn 3 |

---

## 🎯 KẾT LUẬN

### Câu trả lời cho câu hỏi:
**"Tạo ra các relationship giữa các chunk phụ thuộc vào sentence embedding có phải không?"**

### ✅ **Trả lời**: **KHÔNG HOÀN TOÀN ĐÚNG**

### Chi tiết:
1. **80% relationships KHÔNG phụ thuộc embedding**:
   - PART_OF, FIRST_CHUNK, NEXT_CHUNK, HAS_ENTITY
   - Được tạo dựa trên **vị trí tuần tự** và **cấu trúc document**

2. **20% relationships PHỤ THUỘC embedding**:
   - Chỉ có SIMILAR relationships
   - Được tạo dựa trên **vector similarity**

### 🔍 **Insight quan trọng**:
- **Structural relationships** (PART_OF, FIRST_CHUNK, NEXT_CHUNK) được tạo **trước** khi có embeddings
- **Semantic relationships** (SIMILAR) được tạo **sau** khi có embeddings
- Hệ thống đảm bảo có **basic graph structure** ngay cả khi embedding generation fails

### 📈 **Ưu điểm của approach này**:
1. **Resilience**: Graph vẫn hoạt động nếu embedding fails
2. **Performance**: Structural relationships rất nhanh
3. **Semantic Enhancement**: SIMILAR relationships bổ sung thêm semantic connections
4. **Flexibility**: Có thể disable embedding mà vẫn có basic graph
