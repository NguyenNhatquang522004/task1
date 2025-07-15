# Curriculum Entity Linker

## Mục đích
Project này được tạo để liên kết curriculum framework với các entities đã được extract từ LLM Graph Builder.

## Chức năng chính
1. Trích xuất course code từ document filename (ví dụ: `[CMP170]` từ `[CMP170] Đề cương HP Lap Trinh Tren Moi Truong Windows`)
2. Tìm course khung sườn tương ứng trong database 
3. Tạo node trung gian (schema + filename)
4. Liên kết curriculum framework với extracted entities

## Kiến trúc
```
Document → Course Code → Course Framework
    ↓           ↓              ↓
  Schema   →   Node A   ←   POINT_TO
    ↓           ↓
Extracted   HAVE_TO
Entities   ←
```

## Workflow
1. Load curriculum framework từ `curriculum-syllabus-example.cql`
2. Scan tất cả Document nodes 
3. Extract course code từ filename
4. Match với Course framework nodes
5. Tạo intermediate nodes và relationships

## Requirements
- neo4j
- python 3.8+

## 🔥 Multi-Document Handling (NEW)

### Vấn đề
Khi có nhiều file PDF khác nhau cùng mã môn học (ví dụ: CMP3025), cần xử lý đặc biệt:

```
[CMP3025] GIÁO TRÌNH THỰC HÀNH LẬP TRÌNH JAVA 2024 - 2005.pdf
[CMP3025] Bài tập thực hành Java.pdf  
[CMP3025] Lab exercises.pdf
[CMP3025] Project guidelines.pdf
```

### Giải pháp Multi-Document Linker

#### 1. **Grouped Processing**
- Tự động group các documents theo course code
- Xử lý tất cả documents của cùng một course cùng lúc
- Tạo structure hierarchy phù hợp

#### 2. **Enhanced Graph Structure**
```cypher
Course Framework (CMP3025)
       ↓ [HAS_MATERIALS]
CourseConsolidation (CMP3025_CourseConsolidation)
       ↓ [CONTAINS_DOCUMENT]  
DocumentLink (per file)
       ↓ [EXTRACTED_ENTITY]
__Entity__ (from each file)
```

#### 3. **Key Components**
- **CourseConsolidation**: Node tổng hợp cho tất cả materials của course
- **DocumentLink**: Node riêng cho từng document
- **Enhanced Relationships**: Properly structured hierarchy

### Usage

```python
# Import enhanced linker
from multi_document_linker import MultiDocumentCurriculumLinker

# Initialize 
linker = MultiDocumentCurriculumLinker(uri, username, password)

# Process all courses (including multi-document)
stats = linker.process_all_multi_document_courses()

# Get statistics
final_stats = linker.get_multi_document_statistics()
```

### Demo
```bash
cd curriculum-entity-linker
python demo_multi_document.py
```

### Benefits

1. **Proper Grouping**: All documents của cùng course được link properly
2. **Scalable**: Handle unlimited số documents per course  
3. **Queryable**: Easy queries cho cross-document analysis
4. **Maintainable**: Clear hierarchy và relationships
5. **Compatible**: Works với existing curriculum framework

### Example Queries

**Find all documents for CMP3025:**
```cypher
MATCH (c:Course {code: 'CMP3025'})-[:HAS_MATERIALS]->(cc:CourseConsolidation)
MATCH (cc)-[:CONTAINS_DOCUMENT]->(dl:DocumentLink)
RETURN dl.original_filename as documents
```

**Cross-document entity analysis:**
```cypher
MATCH (c:Course {code: 'CMP3025'})-[:HAS_MATERIALS]->(cc:CourseConsolidation)
MATCH (cc)-[:CONTAINS_DOCUMENT]->(dl1:DocumentLink)
MATCH (cc)-[:CONTAINS_DOCUMENT]->(dl2:DocumentLink)  
MATCH (dl1)-[:EXTRACTED_ENTITY]->(e1:__Entity__)
MATCH (dl2)-[:EXTRACTED_ENTITY]->(e2:__Entity__)
WHERE dl1 <> dl2 AND e1.name = e2.name
RETURN e1.name as shared_entities
```
