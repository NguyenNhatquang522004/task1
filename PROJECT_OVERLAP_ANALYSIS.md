# THÔNG TIN OVERLAP CỦA PROJECT LLM GRAPH BUILDER

## 🎯 OVERLAP HIỆN TẠI CỦA PROJECT

### 📊 **Giá trị Overlap: 20**

---

## 🔍 NGUỒN CẤU HÌNH

### 1. **Frontend Configuration**
**File**: `frontend/.env`
```properties
VITE_CHUNK_OVERLAP=20
```

### 2. **Frontend Constants**
**File**: `frontend/src/utils/Constants.ts`
```typescript
export const chunkOverlap = process.env.VITE_CHUNK_OVERLAP ? Number(process.env.VITE_CHUNK_OVERLAP) : 20;
```

**Logic**:
- Nếu có biến `VITE_CHUNK_OVERLAP` trong .env → sử dụng giá trị đó
- Nếu không có → sử dụng **default value: 20**

---

## 🔄 LUỒNG TRUYỀN OVERLAP VALUE

### Frontend → Backend Flow:
```
1. frontend/.env: VITE_CHUNK_OVERLAP=20
   ↓
2. Constants.ts: chunkOverlap = 20
   ↓
3. User Context: selectedChunk_overlap = 20
   ↓
4. API Call: FileAPI.ts gửi chunk_overlap=20
   ↓
5. Backend receives: chunk_overlap parameter
   ↓
6. main.py: split_file_into_chunks(token_chunk_size, chunk_overlap)
   ↓
7. create_chunks.py: TokenTextSplitter(chunk_overlap=20)
```

---

## 📝 CHI TIẾT KỸ THUẬT

### Overlap trong TokenTextSplitter:
```python
# File: backend/src/create_chunks.py
text_splitter = TokenTextSplitter(
    chunk_size=token_chunk_size,      # Thường là 100 tokens
    chunk_overlap=chunk_overlap       # 20 tokens
)
```

### Ý nghĩa Overlap = 20:
- **Chunk 1**: tokens 1-100
- **Chunk 2**: tokens 81-180 (overlap 20 tokens: 81-100)
- **Chunk 3**: tokens 161-260 (overlap 20 tokens: 161-180)

---

## 🎛️ CÁC THAM SỐ CHUNKING KHÁC

### Từ frontend/.env:
```properties
VITE_CHUNK_SIZE=5242880           # File chunk size (5MB)
VITE_CHUNK_OVERLAP=20             # Token overlap: 20
VITE_TOKENS_PER_CHUNK=100         # Tokens per chunk: 100
VITE_CHUNK_TO_COMBINE=1           # Chunks to combine: 1
```

### Từ Constants.ts defaults:
```typescript
chunkSize = 1 * 1024 * 1024       // 1MB (nếu không có VITE_CHUNK_SIZE)
tokenchunkSize = 100              // 100 tokens (nếu không có VITE_TOKENS_PER_CHUNK)
chunkOverlap = 20                 // 20 tokens (nếu không có VITE_CHUNK_OVERLAP)
chunksToCombine = 1               // 1 chunk (nếu không có VITE_CHUNK_TO_COMBINE)
```

---

## 📈 PHÂN TÍCH OVERLAP = 20

### ✅ **Ưu điểm**:
1. **Context Preservation**: Giữ lại ngữ cảnh giữa các chunks
2. **Moderate Overlap**: Không quá nhiều (tốn memory) cũng không quá ít (mất context)
3. **Good for Entity Recognition**: LLM có thể nhận diện entities span across chunk boundaries

### ⚖️ **Trade-offs**:
- **Token Usage**: 20% overhead (20/100 = 20%)
- **Processing Time**: Slightly more chunks to process
- **Storage**: More total tokens stored

### 🎯 **Tối ưu cho**:
- **Token chunk size**: 100 tokens
- **Overlap ratio**: 20% (20/100)
- **Use case**: Balanced performance và quality

---

## 🔧 CÁCH THAY ĐỔI OVERLAP

### 1. **Thay đổi trong Frontend .env**:
```properties
# Tăng overlap cho documents phức tạp
VITE_CHUNK_OVERLAP=30

# Giảm overlap để tiết kiệm tokens
VITE_CHUNK_OVERLAP=10
```

### 2. **Thay đổi default trong Constants.ts**:
```typescript
export const chunkOverlap = process.env.VITE_CHUNK_OVERLAP ? Number(process.env.VITE_CHUNK_OVERLAP) : 30;
```

### 3. **User có thể điều chỉnh**:
Frontend UI cho phép user chọn overlap value khác nhau qua:
- `selectedChunk_overlap` state
- Local storage persistence
- Dynamic API calls

---

## 📊 SO SÁNH VỚI INDUSTRY STANDARDS

| System | Chunk Size | Overlap | Overlap Ratio |
|--------|------------|---------|---------------|
| **LLM Graph Builder** | 100 tokens | 20 tokens | **20%** |
| LangChain Default | 1000 chars | 200 chars | 20% |
| OpenAI Recommended | 512 tokens | 50-100 tokens | 10-20% |
| RAG Best Practice | 256-512 tokens | 25-50 tokens | 10-20% |

**Kết luận**: Project sử dụng overlap ratio **20%** - phù hợp với industry best practices.

---

## 🎯 TÓM TẮT

- **Current Overlap**: **20 tokens**
- **Chunk Size**: **100 tokens** 
- **Overlap Ratio**: **20%**
- **Configuration Source**: `frontend/.env` → `VITE_CHUNK_OVERLAP=20`
- **Fallback Default**: 20 tokens (trong Constants.ts)
- **Industry Standard**: ✅ Phù hợp với best practices
