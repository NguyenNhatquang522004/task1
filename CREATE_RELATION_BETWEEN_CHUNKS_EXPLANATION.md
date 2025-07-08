# GIẢI THÍCH CHI TIẾT HÀM `create_relation_between_chunks`

## 📋 TỔNG QUAN HÀM

```python
def create_relation_between_chunks(graph, file_name, chunks: List[Document])->list:
```

**Mục đích**: Tạo các relationships cấu trúc giữa chunks và document trong Neo4j
**Input**: 
- `graph`: Neo4j connection
- `file_name`: Tên file nguồn
- `chunks`: List các Document chunks đã được split

**Output**: `list` chứa chunk_id và chunk_doc để xử lý tiếp

---

## 🔄 LOGIC TỪNG BƯỚC

### BƯỚC 1: KHỞI TẠO VARIABLES
```python
logging.info("creating FIRST_CHUNK and NEXT_CHUNK relationships between chunks")
current_chunk_id = ""
lst_chunks_including_hash = []  # Kết quả trả về
batch_data = []                 # Data cho Neo4j batch insert
relationships = []              # Relationships data
offset = 0                      # Content offset tracking
```

### BƯỚC 2: DỒN QUA TỪNG CHUNK (MAIN LOOP)
```python
for i, chunk in enumerate(chunks):
```

#### 2.1 Tạo Unique Chunk ID
```python
page_content_sha1 = hashlib.sha1(chunk.page_content.encode())
previous_chunk_id = current_chunk_id
current_chunk_id = page_content_sha1.hexdigest()
```
- **SHA1 Hash**: Tạo unique ID dựa trên nội dung chunk
- **Lưu previous_id**: Để tạo NEXT_CHUNK relationship
- **Ví dụ**: "Hello world" → "2aae6c35c94fcfb415dbe95f408b9ce91ee846ed"

#### 2.2 Tính toán Position và Offset
```python
position = i + 1                                    # Vị trí chunk (1-indexed)
if i > 0:
    offset += len(chunks[i-1].page_content)        # Offset tích lũy
```
- **Position**: Thứ tự chunk trong document (1, 2, 3...)
- **Offset**: Vị trí ký tự bắt đầu chunk trong document gốc

#### 2.3 Xác định First Chunk
```python
if i == 0:
    firstChunk = True    # Chunk đầu tiên
else:
    firstChunk = False   # Các chunk tiếp theo
```

#### 2.4 Tạo Metadata
```python
metadata = {
    "position": position,
    "length": len(chunk.page_content),
    "content_offset": offset
}
chunk_document = Document(page_content=chunk.page_content, metadata=metadata)
```

#### 2.5 Chuẩn bị Chunk Data
```python
chunk_data = {
    "id": current_chunk_id,
    "pg_content": chunk_document.page_content,
    "position": position,
    "length": chunk_document.metadata["length"],
    "f_name": file_name,
    "previous_id": previous_chunk_id,
    "content_offset": offset
}
```

#### 2.6 Xử lý Metadata bổ sung (Conditional)
```python
# Cho PDF files
if 'page_number' in chunk.metadata:
    chunk_data['page_number'] = chunk.metadata['page_number']

# Cho YouTube/Audio files 
if 'start_timestamp' in chunk.metadata and 'end_timestamp' in chunk.metadata:
    chunk_data['start_time'] = chunk.metadata['start_timestamp']
    chunk_data['end_time'] = chunk.metadata['end_timestamp']
```

#### 2.7 Lưu Data cho Batch Processing
```python
batch_data.append(chunk_data)
lst_chunks_including_hash.append({'chunk_id': current_chunk_id, 'chunk_doc': chunk})
```

#### 2.8 Tạo Relationship Definitions
```python
if firstChunk:
    relationships.append({"type": "FIRST_CHUNK", "chunk_id": current_chunk_id})
else:
    relationships.append({
        "type": "NEXT_CHUNK",
        "previous_chunk_id": previous_chunk_id,
        "current_chunk_id": current_chunk_id
    })
```

---

## 🏗️ BƯỚC 3: TẠO NODES VÀ RELATIONSHIPS TRONG NEO4J

### 3.1 Tạo Chunk Nodes và PART_OF Relationships
```python
query_to_create_chunk_and_PART_OF_relation = """
    UNWIND $batch_data AS data
    MERGE (c:Chunk {id: data.id})
    SET c.text = data.pg_content, 
        c.position = data.position, 
        c.length = data.length, 
        c.fileName = data.f_name, 
        c.content_offset = data.content_offset
    WITH data, c
    SET c.page_number = CASE WHEN data.page_number IS NOT NULL THEN data.page_number END,
        c.start_time = CASE WHEN data.start_time IS NOT NULL THEN data.start_time END,
        c.end_time = CASE WHEN data.end_time IS NOT NULL THEN data.end_time END
    WITH data, c
    MATCH (d:Document {fileName: data.f_name})
    MERGE (c)-[:PART_OF]->(d)
"""
```

**Chức năng**:
- Tạo `:Chunk` nodes với properties
- Tạo `(Chunk)-[:PART_OF]->(Document)` relationships

### 3.2 Tạo FIRST_CHUNK Relationships
```python
query_to_create_FIRST_relation = """ 
    UNWIND $relationships AS relationship
    MATCH (d:Document {fileName: $f_name})
    MATCH (c:Chunk {id: relationship.chunk_id})
    FOREACH(r IN CASE WHEN relationship.type = 'FIRST_CHUNK' THEN [1] ELSE [] END |
            MERGE (d)-[:FIRST_CHUNK]->(c))
"""
```

**Chức năng**: Tạo `(Document)-[:FIRST_CHUNK]->(Chunk)` cho chunk đầu tiên

### 3.3 Tạo NEXT_CHUNK Relationships
```python
query_to_create_NEXT_CHUNK_relation = """ 
    UNWIND $relationships AS relationship
    MATCH (c:Chunk {id: relationship.current_chunk_id})
    WITH c, relationship
    MATCH (pc:Chunk {id: relationship.previous_chunk_id})
    FOREACH(r IN CASE WHEN relationship.type = 'NEXT_CHUNK' THEN [1] ELSE [] END |
            MERGE (c)<-[:NEXT_CHUNK]-(pc))
"""
```

**Chức năng**: Tạo `(PreviousChunk)-[:NEXT_CHUNK]->(CurrentChunk)` chains

---

## 📊 VÍ DỤ THỰC TẾ

### Input: Document với 3 chunks
```
Document: "Apple stock during pandemic.pdf"
Chunks: ["Apple Inc. is a technology...", "During the pandemic period...", "Stock performance showed..."]
```

### Processing Result:

#### Chunk 1:
```python
{
    "id": "abc123...",
    "position": 1,
    "content_offset": 0,
    "firstChunk": True
}
→ Relationship: {"type": "FIRST_CHUNK", "chunk_id": "abc123..."}
```

#### Chunk 2:
```python
{
    "id": "def456...",
    "position": 2,
    "content_offset": 25,
    "previous_id": "abc123..."
}
→ Relationship: {"type": "NEXT_CHUNK", "previous_chunk_id": "abc123...", "current_chunk_id": "def456..."}
```

#### Chunk 3:
```python
{
    "id": "ghi789...",
    "position": 3,
    "content_offset": 52,
    "previous_id": "def456..."
}
→ Relationship: {"type": "NEXT_CHUNK", "previous_chunk_id": "def456...", "current_chunk_id": "ghi789..."}
```

### Final Neo4j Graph Structure:
```
(Document "Apple stock...") 
    ├─[:FIRST_CHUNK]→ (Chunk:abc123)
    │                      ├─[:NEXT_CHUNK]→ (Chunk:def456)
    │                      │                    └─[:NEXT_CHUNK]→ (Chunk:ghi789)
    ├─[:PART_OF]←──────────┘
    ├─[:PART_OF]←───────────────────────────────┘
    └─[:PART_OF]←────────────────────────────────────────────────┘
```

---

## 🎯 KEY INSIGHTS

### 1. **Dual Execute Pattern**
```python
execute_graph_query(graph, query, params)
execute_graph_query(graph, query, params)  # Chạy 2 lần
```
- **Lý do**: Đảm bảo data consistency, handle potential transaction conflicts

### 2. **SHA1 Hash cho Chunk ID**
- **Ưu điểm**: Content-based ID, deterministic
- **Nhược điểm**: Same content → same ID (có thể duplicate)

### 3. **Offset Tracking**
- **Mục đích**: Biết exact position của chunk trong document gốc
- **Ứng dụng**: Highlight, navigation, reconstruction

### 4. **Conditional Metadata**
- **PDF**: `page_number`
- **Audio/Video**: `start_time`, `end_time`
- **Flexible**: Hỗ trợ multiple file types

### 5. **Batch Processing**
- **Performance**: Bulk insert thay vì individual queries
- **Efficiency**: Reduce database round-trips

---

## 🔄 RETURN VALUE

```python
return lst_chunks_including_hash
```

**Structure**:
```python
[
    {'chunk_id': 'abc123...', 'chunk_doc': Document(...)},
    {'chunk_id': 'def456...', 'chunk_doc': Document(...)},
    {'chunk_id': 'ghi789...', 'chunk_doc': Document(...)}
]
```

**Usage**: Được sử dụng trong các bước tiếp theo để:
- Tạo embeddings
- Extract entities từ LLM
- Tạo HAS_ENTITY relationships
