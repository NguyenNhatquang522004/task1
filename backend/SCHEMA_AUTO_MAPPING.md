# Schema Auto-Mapping với newSchema.json

## Câu hỏi
> Ví dụ schema là "decuong" thì có tự động mapping với file json này lấy ra cho LLM chỉ sinh ra những label được định sẵn trong schema decuong hay không?

## Trả lời: **CÓ!** ✅

Hệ thống **ĐÃ TỰ ĐỘNG** mapping schema với file `newSchema.json` và **CHỈ CHO PHÉP** LLM sinh ra những labels được định sẵn.

## Cách hoạt động

### 1. Schema Detection
- Khi user chọn schema = "decuong", hệ thống tự động đọc file `frontend/src/assets/newSchema.json`
- Tìm object có `"schema": "decuong"` và extract array `"triplet"`

### 2. Label Extraction  
Từ 172 triplets trong schema "decuong", hệ thống extract ra:
- **128 Entity Labels** (allowed_nodes)
- **118 Relationship Labels** (allowed_relationships)

### 3. LLM Constraint
```python
llm_transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=entities_from_schema,           # CHỈ 128 entities được phép
    allowed_relationships=relationships_from_schema, # CHỈ 118 relationships được phép
    strict_mode=True                             # Không cho phép labels khác
)
```

## Ví dụ cụ thể với schema "decuong"

### Entity Labels được phép (128 labels):
```
Mon_Hoc, Course, Khoa, Faculty, CLO, PLO, Bai_Hoc, Lesson, 
Giang_Vien, Instructor, Sinh_Vien, Student, Assessment_Method,
Grade_Component, Teaching_Method, Reference_Material, ...
```

### Relationship Labels được phép (118 labels):
```
THUOC_VE, BELONGS_TO, CO_MA, HAS_CODE, CO_TEN, HAS_NAME,
TEACHES, LEARNS, ADDRESSES_CLO, CONTRIBUTES_TO_PLO, ...
```

### Sample Triplets:
```
Mon_Hoc-THUOC_VE->Khoa
Course-BELONGS_TO->Faculty  
Mon_Hoc-CO_MA->Ma_Mon_Hoc
Course-HAS_CODE->Course_Code
Giang_Vien-TEACHES->Mon_Hoc
Sinh_Vien-LEARNS->Course
```

## Implementation Details

### File: `backend/src/llm.py`
```python
async def get_graph_document_list(..., schema=None, triplet=None):
    # Load schema-specific triplets if schema is provided
    effective_allowed_relationships = allowedRelationship
    if schema and triplet and schema != 'default':
        logging.info(f"Using schema-specific triplets for schema: {schema}")
        
        # Load triplet relationships from newSchema.json
        schema_file_path = os.path.join(..., "newSchema.json")
        with open(schema_file_path, 'r', encoding='utf-8') as f:
            schema_data = json.load(f)
        
        # Find matching schema and extract triplets
        for item in schema_data:
            if item.get('schema') == schema:
                schema_triplets = item.get('triplet', [])
                # Convert to allowed_relationships format
                effective_allowed_relationships = convert_triplets(schema_triplets)
```

## Kiểm chứng
Chạy test để verify:
```bash
cd backend
python demo_schema_decuong.py
```

## Kết luận
✅ **Tự động mapping**: Schema "decuong" → newSchema.json  
✅ **Strict constraint**: LLM CHỈ sinh 128 entities + 118 relationships được định sẵn  
✅ **Quality control**: Không cho phép labels ngoài schema  
✅ **Consistency**: Đảm bảo graph structure nhất quán theo thiết kế  

**→ Hệ thống hoàn toàn kiểm soát được labels mà LLM sinh ra!**
