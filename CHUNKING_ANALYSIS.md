# 📄 LLM Graph Builder - Chunking System Analysis

## 🔍 **Files thực hiện chức năng Chunking:**

### 1. **Core Chunking Files:**

#### **📁 `backend/src/create_chunks.py`** - Main Chunking Implementation
- **Class:** `CreateChunksofDocument`
- **Method:** `split_file_into_chunks(token_chunk_size, chunk_overlap)`
- **Chức năng:** Chia tài liệu thành các chunks nhỏ hơn

#### **📁 `backend/src/make_relationships.py`** 
- **Function:** `create_relation_between_chunks()`
- **Chức năng:** Tạo relationships giữa các chunks

#### **📁 `backend/src/llm.py`**
- **Function:** `get_combined_chunks()` - Kết hợp nhiều chunks
- **Function:** `get_chunk_id_as_doc_metadata()` - Xử lý metadata

### 2. **Supporting Files:**
- **`backend/src/chunkid_entities.py`** - Xử lý entities trong chunks
- **`backend/src/main.py`** - Processing logic và workflow
- **Frontend files:** Hiển thị và quản lý chunks

---

## ⚙️ **Cách thức Chunking hoạt động:**

### **🎯 Step 1: Document Input Processing**
```python
# File: create_chunks.py
class CreateChunksofDocument:
    def __init__(self, pages: list[Document], graph: Neo4jGraph):
        self.pages = pages  # Input documents
        self.graph = graph  # Neo4j connection
```

### **🔪 Step 2: Text Splitting với TokenTextSplitter**
```python
# Sử dụng LangChain TokenTextSplitter
text_splitter = TokenTextSplitter(
    chunk_size=token_chunk_size,      # Kích thước chunk (tokens)
    chunk_overlap=chunk_overlap       # Overlap giữa các chunks
)

# Tính toán số lượng chunks tối đa
MAX_TOKEN_CHUNK_SIZE = int(os.getenv('MAX_TOKEN_CHUNK_SIZE', 10000))
chunk_to_be_created = int(MAX_TOKEN_CHUNK_SIZE / token_chunk_size)
```

### **📑 Step 3: Chunking Strategy theo loại document**

#### **A. PDF Documents (có 'page' metadata):**
```python
if 'page' in self.pages[0].metadata:
    chunks = []
    for i, document in enumerate(self.pages):
        page_number = i + 1
        if len(chunks) >= chunk_to_be_created:
            break
        for chunk in text_splitter.split_documents([document]):
            chunks.append(Document(
                page_content=chunk.page_content, 
                metadata={'page_number': page_number}
            ))
```

#### **B. YouTube Videos (có 'length' metadata):**
```python
elif 'length' in self.pages[0].metadata:
    # Xử lý transcript YouTube
    chunks_without_time_range = text_splitter.split_documents([self.pages[0]])
    chunks = get_calculated_timestamps(chunks_without_time_range, youtube_id)
```

#### **C. Other Documents:**
```python
else:
    chunks = text_splitter.split_documents(self.pages)
```

### **🔗 Step 4: Creating Chunk Relationships**
```python
# File: make_relationships.py
def create_relation_between_chunks(graph, file_name, chunks):
    for i, chunk in enumerate(chunks):
        # Tạo unique ID cho chunk
        page_content_sha1 = hashlib.sha1(chunk.page_content.encode())
        current_chunk_id = page_content_sha1.hexdigest()
        
        # Tạo relationships
        if i == 0:
            relationships.append({"type": "FIRST_CHUNK", "chunk_id": current_chunk_id})
        else:
            relationships.append({
                "type": "NEXT_CHUNK",
                "from": previous_chunk_id,
                "to": current_chunk_id
            })
```

### **🎯 Step 5: Chunk Combination Strategy**
```python
# File: llm.py
def get_combined_chunks(chunkId_chunkDoc_list, chunks_to_combine):
    # Kết hợp nhiều chunks thành 1 để xử lý
    combined_chunks_page_content = [
        "".join(
            document["chunk_doc"].page_content
            for document in chunkId_chunkDoc_list[i : i + chunks_to_combine]
        )
        for i in range(0, len(chunkId_chunkDoc_list), chunks_to_combine)
    ]
```

---

## 🏗️ **Chunk Relationships trong Neo4j:**

### **Graph Structure:**
```
Document Node
    ↓ PART_OF
Chunk Nodes
    ↓ FIRST_CHUNK (Document → First Chunk)
    ↓ NEXT_CHUNK (Chunk → Next Chunk)
    ↓ HAS_ENTITY (Chunk → Entities)
    ↓ SIMILAR (Chunk ↔ Similar Chunks)
```

### **Chunk Properties:**
```python
chunk_data = {
    "id": current_chunk_id,           # SHA1 hash của content
    "pg_content": chunk.page_content, # Nội dung chunk
    "position": position,             # Vị trí trong document
    "length": len(chunk.page_content), # Độ dài
    "f_name": file_name,             # File name
    "content_offset": offset,         # Offset trong document
    "page_number": page_number        # Số trang (nếu có)
}
```

---

## ⚙️ **Configuration Parameters:**

### **Environment Variables:**
```properties
# Backend chunking settings
MAX_TOKEN_CHUNK_SIZE=2000           # Token limit cho mỗi chunk  
NUMBER_OF_CHUNKS_TO_COMBINE=6       # Số chunks kết hợp khi processing
UPDATE_GRAPH_CHUNKS_PROCESSED=20    # Chunks processed trước khi update

# Frontend chunking settings
VITE_CHUNK_SIZE=5242880             # File upload chunk size
VITE_CHUNK_OVERLAP=20               # Overlap giữa chunks
VITE_TOKENS_PER_CHUNK=100           # Tokens per chunk
VITE_CHUNK_TO_COMBINE=1             # Chunks to combine cho parallel processing
```

### **Function Parameters:**
```python
async def processing_source(
    # ... other params
    token_chunk_size,     # Kích thước token cho mỗi chunk
    chunk_overlap,        # Overlap giữa chunks
    chunks_to_combine,    # Số chunks kết hợp khi xử lý
):
```

---

## 🚀 **Chunking Workflow:**

### **Complete Process Flow:**
```
1. Document Input → Pages/Content
    ↓
2. CreateChunksofDocument.split_file_into_chunks()
    ↓
3. TokenTextSplitter → Split into chunks
    ↓ 
4. create_relation_between_chunks() → Create relationships
    ↓
5. Store chunks in Neo4j với metadata
    ↓
6. get_combined_chunks() → Combine cho LLM processing
    ↓
7. Extract entities và relationships từ chunks
    ↓
8. Create HAS_ENTITY relationships
    ↓
9. Update embeddings cho chunks
    ↓
10. Create SIMILAR relationships giữa similar chunks
```

---

## 🎯 **Optimization Strategies:**

### **1. Parallel Processing:**
- Combine multiple chunks trước khi gửi tới LLM
- Sử dụng ThreadPoolExecutor để xử lý parallel
- Batch processing theo `UPDATE_GRAPH_CHUNKS_PROCESSED`

### **2. Memory Management:**
- Limit chunk count với `MAX_TOKEN_CHUNK_SIZE`
- Clean up processed chunks
- Incremental processing

### **3. Context Preservation:**
- `chunk_overlap` giữ context giữa chunks
- Sequential numbering và positioning
- NEXT_CHUNK relationships maintain order

---

## 📊 **Performance Metrics:**

### **Chunking có thể được optimize bằng:**
- **Chunk size:** Smaller = more granular, larger = more context
- **Overlap:** Higher overlap = better context preservation
- **Combination:** More chunks combined = better LLM context
- **Parallel processing:** ThreadPool size optimization

### **Trade-offs:**
- **Small chunks:** Faster processing, có thể mất context
- **Large chunks:** Better context, slower processing
- **High overlap:** Better coherence, more redundancy
- **Chunk combination:** Better LLM results, higher memory usage

---

**Tóm lại:** Chunking system trong LLM Graph Builder rất sophisticated, sử dụng LangChain TokenTextSplitter và tạo complex relationships trong Neo4j để preserve context và optimize LLM processing performance!
