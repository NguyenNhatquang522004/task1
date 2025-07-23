# Schema Properties Validation Implementation

## Mục tiêu
Khi tạo graph, hệ thống sẽ kiểm tra node Document đã có các properties `schema`, `triplet`, `additional_instructions` hay chưa:
- **Nếu chưa có**: Lấy từ giao diện (interface parameters)
- **Nếu có rồi**: Phải sử dụng đúng schema, triplet và additional_instructions từ document đó

## Các thay đổi đã thực hiện

### 1. Cập nhật Database Access Layer

#### File: `backend/src/graphDB_dataAccess.py`

**`get_current_status_document_node()`**:
- ✅ Thêm trả về properties: `schema`, `triplet`, `additional_instructions`
- ✅ Query đã cập nhật để lấy các properties mới

**`update_source_node()`**:
- ✅ Thêm logic cập nhật `triplet` và `additional_instructions`
- ✅ Properties được lưu vào database khi update

### 2. Cập nhật Main Processing Logic

#### File: `backend/src/main.py`

**`processing_source()`**:
- ✅ Thêm **STEP 6.1: Schema Properties Check**
- ✅ Logic kiểm tra existing schema properties từ document
- ✅ Sử dụng effective values (document hoặc interface)
- ✅ Logging chi tiết cho debugging

**Schema Resolution Logic**:
```python
# Ưu tiên: Document schema > Interface schema
if existing_schema and valid:
    effective_schema = existing_schema  # Từ document
    effective_triplet = existing_triplet
    effective_additional_instructions = existing_additional_instructions
else:
    effective_schema = interface_schema  # Từ giao diện
```

**`processing_chunks()`**:
- ✅ Thêm parameters: `schema=None, triplet=None`
- ✅ Truyền effective values đến LLM processing

### 3. Cập nhật LLM Processing

#### File: `backend/src/llm.py`

**`get_graph_from_llm()`**:
- ✅ Thêm parameters: `schema=None, triplet=None`
- ✅ Truyền schema context đến graph generation

**`get_graph_document_list()`**:
- ✅ Logic load schema-specific triplets từ `newSchema.json`
- ✅ Convert triplet format sang allowed_relationships
- ✅ Schema-aware LLMGraphTransformer configuration

**Schema Triplet Loading**:
```python
# Load từ frontend/src/assets/newSchema.json
if schema and triplet and schema != 'default':
    # Tìm matching schema trong newSchema.json
    # Convert triplets thành allowed_relationships format
    # Sử dụng cho LLMGraphTransformer
```

### 4. Entity Source Node Updates

#### File: `backend/src/entities/source_node.py`

**Properties đã có sẵn**:
- ✅ `schema:str=None`
- ✅ `triplet:str=None` 
- ✅ `additional_instructions:str=None`

### 5. Test Script

#### File: `backend/test_schema_logic.py`
- ✅ Test cases cho schema detection
- ✅ Simulation logic kiểm tra document properties
- ✅ Validation effective values resolution

## Flow xử lý mới

### 1. Document Processing Start
```
User uploads file → processing_source()
```

### 2. Schema Properties Check
```
get_current_status_document_node() 
→ Kiểm tra existing schema, triplet, additional_instructions
→ So sánh với interface parameters
→ Quyết định effective values
```

### 3. Effective Values Usage
```
effective_schema, effective_triplet, effective_additional_instructions
→ Truyền vào processing_chunks()
→ Truyền vào get_graph_from_llm()
→ Configure LLMGraphTransformer with schema-specific settings
```

### 4. Schema-Aware Graph Generation
```
Load triplets từ newSchema.json based on effective_schema
→ Convert thành allowed_relationships
→ LLMGraphTransformer sử dụng schema-specific rules
→ Generate graph theo đúng schema pattern
```

## Behavior Examples

### Case 1: Document chưa tồn tại
```
Interface input: schema="giaotrinh", additional_instructions="Custom instructions"
Document status: Not exists
→ Effective values: schema="giaotrinh", additional_instructions="Custom instructions"
```

### Case 2: Document đã có schema properties
```
Document properties: schema="decuong", triplet="decuong", additional_instructions="Document instructions"
Interface input: schema="giaotrinh", additional_instructions="Interface instructions"
→ Effective values: schema="decuong", triplet="decuong", additional_instructions="Document instructions"
```

### Case 3: Document có schema empty/invalid
```
Document properties: schema="", triplet=None, additional_instructions=""
Interface input: schema="ebook", additional_instructions="Interface instructions"
→ Effective values: schema="ebook", additional_instructions="Interface instructions"
```

## Logging & Debugging

### Schema Check Logs
```
🔍 STEP 6.1: SCHEMA_PROPERTIES_CHECK
✅ Using existing schema from document: decuong
✅ Using existing triplet from document: decuong
✅ Using existing additional_instructions from document (length: 1234 chars)
🎯 Final effective values applied to processing
```

### Schema Loading Logs
```
📊 Using schema-specific triplets for schema: decuong
📊 Found 150 triplets for schema 'decuong'
📊 Using 150 relationships from schema 'decuong'
```

## Integration với newSchema.json

Schema-aware processing sử dụng triplets định nghĩa trong:
- `frontend/src/assets/newSchema.json`
- Format: `["NodeType1-RELATIONSHIP->NodeType2"]`
- Automatic conversion sang LangChain allowed_relationships format

## Error Handling

- ✅ Fallback to interface values nếu document schema invalid
- ✅ Graceful handling khi newSchema.json không tồn tại
- ✅ Detailed error logging cho debugging
- ✅ Safe handling các edge cases (None, empty strings)

## Backward Compatibility

- ✅ Existing documents without schema properties vẫn hoạt động bình thường
- ✅ Interface parameters vẫn được respect khi document chưa có schema
- ✅ Default fallback behavior maintained
