# Auto-Fix Failed Documents Script

## 🎯 Mục đích
Script này tự động sửa các document bị Failed trong database để có thể reprocess.

## 🔧 Cách sử dụng

### Sửa một file cụ thể:
```bash
c:\edu\task1\llm-graph-builder\.venv\Scripts\python.exe c:\edu\task1\llm-graph-builder\backend\fix_failed_document.py
```

### Tìm và sửa tất cả files bị Failed:
Chỉnh sửa file `fix_failed_document.py` và thay đổi:
```python
file_name = "[CMP177] beginningflutter.pdf"  # File cụ thể
```
thành:
```python
file_name = None  # Sửa tất cả files Failed
```

## 📊 Kết quả có thể có:

### ✅ Case 1: Document có chunks
- **Vấn đề**: Document status bị "Failed" nhưng chunks vẫn tồn tại
- **Giải pháp**: Reset status về "New" để có thể reprocess
- **Kết quả**: Có thể sử dụng Reprocess Options

### ❌ Case 2: Document không có chunks (như trường hợp của bạn)
- **Vấn đề**: Document status "Failed" và không có chunks
- **Giải pháp**: Xóa document node hoàn toàn
- **Kết quả**: Phải upload lại từ đầu

## 🔍 Nguyên nhân Files bị Failed

1. **Lỗi trong quá trình tạo chunks**:
   - File PDF bị hỏng hoặc không đọc được
   - Token chunk size quá nhỏ/lớn
   - Lỗi memory khi xử lý file lớn

2. **Lỗi trong quá trình extract entities**:
   - API key không hợp lệ
   - Model không phản hồi
   - Relationship validation lỗi (đã fix)

3. **Lỗi kết nối database**:
   - Neo4j timeout
   - Network issues

## 🛡️ Phòng tránh tương lai

1. **Kiểm tra file quality** trước khi upload
2. **Sử dụng chunk size phù hợp** (mặc định: token_chunk_size=512)
3. **Để trống allowedNodes/allowedRelationship** nếu không chắc chắn
4. **Monitor logs** trong quá trình processing

## 📝 Log Files để debug

- `backend/logs/` - Application logs
- Terminal output từ server - Real-time processing logs
- Neo4j browser - Database status
