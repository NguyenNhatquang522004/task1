# GIẢI THÍCH ĐOẠN CODE: MAX_TOKEN_CHUNK_SIZE VÀ chunk_to_be_created

## 📝 ĐOẠN CODE ĐƯỢC HỎI

```python
MAX_TOKEN_CHUNK_SIZE = int(os.getenv('MAX_TOKEN_CHUNK_SIZE', 10000))
chunk_to_be_created = int(MAX_TOKEN_CHUNK_SIZE / token_chunk_size)
```

---

## 🔍 PHÂN TÍCH TỪNG DÒNG

### Dòng 1: `MAX_TOKEN_CHUNK_SIZE = int(os.getenv('MAX_TOKEN_CHUNK_SIZE', 10000))`

**Ý nghĩa**: Lấy giá trị từ environment variable `MAX_TOKEN_CHUNK_SIZE`

**Chi tiết**:
- `os.getenv('MAX_TOKEN_CHUNK_SIZE', 10000)`: Đọc biến môi trường `MAX_TOKEN_CHUNK_SIZE`
- Nếu biến này **không tồn tại** → sử dụng giá trị mặc định `10000`
- `int(...)`: Chuyển đổi thành số nguyên

**Ví dụ**:
```python
# Nếu trong .env có: MAX_TOKEN_CHUNK_SIZE=15000
MAX_TOKEN_CHUNK_SIZE = 15000

# Nếu không có trong .env
MAX_TOKEN_CHUNK_SIZE = 10000  # Giá trị mặc định
```

### Dòng 2: `chunk_to_be_created = int(MAX_TOKEN_CHUNK_SIZE / token_chunk_size)`

**Ý nghĩa**: Tính số chunk tối đa được phép tạo ra

**Chi tiết**:
- `token_chunk_size`: Kích thước mỗi chunk (thường là 512)
- `MAX_TOKEN_CHUNK_SIZE / token_chunk_size`: Chia tổng token limit cho kích thước mỗi chunk
- `int(...)`: Làm tròn xuống thành số nguyên

**Ví dụ tính toán**:
```python
# Trường hợp 1:
MAX_TOKEN_CHUNK_SIZE = 10000
token_chunk_size = 512
chunk_to_be_created = int(10000 / 512) = int(19.53) = 19

# Trường hợp 2:
MAX_TOKEN_CHUNK_SIZE = 10000  
token_chunk_size = 1000
chunk_to_be_created = int(10000 / 1000) = int(10.0) = 10
```

---

## 🎯 MỤC ĐÍCH CỦA LOGIC NÀY

### 1. **Giới hạn tài nguyên (Resource Limiting)**
```python
# Đảm bảo không tạo quá nhiều chunks → tránh:
# - Tốn quá nhiều memory
# - Quá nhiều API calls tới LLM
# - Database overload
# - Processing time quá lâu
```

### 2. **Kiểm soát chi phí (Cost Control)**
```python
# LLM API thường tính phí theo tokens
# Giới hạn số chunks = Giới hạn chi phí API calls
```

### 3. **Performance Optimization**
```python
# Nhiều chunks = nhiều embeddings = nhiều vector operations
# Giới hạn hợp lý để đảm bảo performance
```

---

## 📊 VÍ DỤ THỰC TẾ

### Scenario 1: Document nhỏ
```python
MAX_TOKEN_CHUNK_SIZE = 10000
token_chunk_size = 512

# Document có 3000 tokens
# Chia thành chunks 512 tokens = 6 chunks
# chunk_to_be_created = 19 (limit)
# Thực tế tạo = 6 chunks (< 19) ✅ OK
```

### Scenario 2: Document lớn
```python
MAX_TOKEN_CHUNK_SIZE = 10000  
token_chunk_size = 512

# Document có 50000 tokens
# Có thể chia thành 97 chunks
# chunk_to_be_created = 19 (limit)
# Thực tế tạo = 19 chunks (bị giới hạn) ⚠️ Truncated
```

### Scenario 3: Chunk size lớn
```python
MAX_TOKEN_CHUNK_SIZE = 10000
token_chunk_size = 2000

# chunk_to_be_created = int(10000/2000) = 5
# Chỉ tạo tối đa 5 chunks dù document có lớn đến đâu
```

---

## 🔧 SỬ DỤNG TRONG CODE

### Trong file `create_chunks.py`:
```python
# Sau khi tính chunk_to_be_created
if 'page' in self.pages[0].metadata:
    chunks = []
    for i, document in enumerate(self.pages):
        page_number = i + 1
        if len(chunks) >= chunk_to_be_created:  # ⚠️ GIỚI HẠN Ở ĐÂY
            break
        # ...

# Ở cuối function
chunks = chunks[:chunk_to_be_created]  # ⚠️ CẮT BỚTI Ở ĐÂY
return chunks
```

---

## ⚙️ CẤU HÌNH TRONG .ENV

### Trong file `.env`:
```bash
# Tăng giới hạn chunks cho documents lớn
MAX_TOKEN_CHUNK_SIZE=20000

# Hoặc giảm để tiết kiệm tài nguyên
MAX_TOKEN_CHUNK_SIZE=5000
```

### Tác động:
```python
# Với token_chunk_size=512:

# MAX_TOKEN_CHUNK_SIZE=5000  → chunk_to_be_created=9
# MAX_TOKEN_CHUNK_SIZE=10000 → chunk_to_be_created=19  
# MAX_TOKEN_CHUNK_SIZE=20000 → chunk_to_be_created=39
```

---

## 🚨 LƯU Ý QUAN TRỌNG

### 1. **Truncation Risk**
```python
# Document lớn có thể bị cắt bớt thông tin
# Cần cân nhắc giữa performance và completeness
```

### 2. **Token vs Character**
```python
# MAX_TOKEN_CHUNK_SIZE: đơn vị là TOKENS
# token_chunk_size: đơn vị là TOKENS  
# 1 token ≈ 4 characters (tiếng Anh)
```

### 3. **Business Logic**
```python
# Đây là business rule để kiểm soát:
# - Chi phí xử lý
# - Thời gian xử lý  
# - Tài nguyên hệ thống
```

---

## 🎯 TÓM TẮT

**`MAX_TOKEN_CHUNK_SIZE`**: Tổng số tokens tối đa cho tất cả chunks
**`chunk_to_be_created`**: Số chunks tối đa được phép tạo
**Mục đích**: Giới hạn tài nguyên, kiểm soát chi phí, tối ưu performance

**Công thức**: `Số chunks tối đa = Tổng token limit / Kích thước mỗi chunk`
