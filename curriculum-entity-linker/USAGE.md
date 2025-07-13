# Curriculum Entity Linker - Hướng dẫn sử dụng

## Tổng quan

Project này tạo liên kết giữa curriculum framework (khung sườn giáo trình) và các entities được extract từ documents bởi LLM Graph Builder.

### Kiến trúc dữ liệu

```
Course Framework (khung sườn)
        ↓ POINT_TO
CurriculumLink (Node A: schema + filename)
        ↓ HAVE_TO  
Extracted Entities (từ document)
```

## Workflow chi tiết

### 1. Input Data
- **Document nodes**: Có filename chứa course code trong dấu `[]`
- **Course framework**: Từ file `curriculum-syllabus-example.cql`
- **Schema**: Từ Document.schema property

### 2. Processing Steps

#### Bước 1: Extract Course Code
```python
filename = "[CMP170] Đề cương HP Lap Trinh Tren Moi Truong Windows"
course_code = "CMP170"  # Extracted từ pattern [A-Z]{3}\d{3,4}
```

#### Bước 2: Find Course Framework
```cypher
MATCH (c:Course {code: 'CMP170'})
WHERE NOT c:__Entity__  // Không phải entity được extract
RETURN c
```

#### Bước 3: Create Intermediate Node (Node A)
```cypher
MERGE (a:CurriculumLink {name: 'giáo_trình_CMP170_Đề_cương_HP_Lap_Trinh_Tren_Moi_Truong_Windows'})
```

#### Bước 4: Create POINT_TO Relationship
```cypher
MATCH (c:Course {code: 'CMP170'}), (a:CurriculumLink)
MERGE (c)-[:POINT_TO]->(a)
```

#### Bước 5: Create HAVE_TO Relationships
```cypher
MATCH (d:Document)-[:HAS_ENTITY]->(e)
WHERE d.fileName CONTAINS '[CMP170]'
MATCH (a:CurriculumLink) WHERE a.name CONTAINS 'CMP170'
MERGE (a)-[:HAVE_TO]->(e)
```

## Cài đặt và Sử dụng

### 1. Setup
```bash
cd curriculum-entity-linker
python setup.py
```

### 2. Configuration
Cập nhật file `.env`:
```
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
```

### 3. Test
```bash
python query_utils.py      # Test regex patterns và preview data
python test_linker.py      # Test connection và basic functionality
```

### 4. Load Curriculum Framework
```bash
# Chạy curriculum-syllabus-example.cql trong Neo4j Browser trước
# Hoặc script sẽ tự động load
```

### 5. Run Main Process
```bash
python curriculum_linker.py
```

## Kết quả mong đợi

### Trước khi chạy:
```
Document: "[CMP170] Đề cương HP..."
    ↓ HAS_ENTITY
Entities: Concept, Topic, etc.

Course: {code: "CMP170", name: "Lập trình trên môi trường Windows"}
```

### Sau khi chạy:
```
Course: {code: "CMP170"} 
    ↓ POINT_TO
CurriculumLink: {name: "giáo_trình_CMP170_..."}
    ↓ HAVE_TO
Entities: All entities từ CMP170 document
```

## Queries để kiểm tra kết quả

### 1. Xem tất cả liên kết đã tạo
```cypher
MATCH (c:Course)-[:POINT_TO]->(a:CurriculumLink)-[:HAVE_TO]->(e)
RETURN c.code, c.name, a.name, labels(e), count(e) as entity_count
ORDER BY c.code
```

### 2. Xem chi tiết cho một course
```cypher
MATCH (c:Course {code: 'CMP170'})-[:POINT_TO]->(a:CurriculumLink)-[:HAVE_TO]->(e)
RETURN c.name, a.name, e.id, labels(e)
```

### 3. Thống kê
```cypher
MATCH (a:CurriculumLink)
RETURN count(a) as total_links, 
       count{(a)-[:HAVE_TO]->(:__Entity__)} as total_entity_connections
```

## Xử lý lỗi thường gặp

### 1. Không tìm thấy Course Framework
```
Warning: No course framework found for CMP170, skipping...
```
**Giải pháp**: Kiểm tra curriculum-syllabus-example.cql đã được load chưa

### 2. Không có entities
```
Created 0 HAVE_TO relationships
```
**Giải pháp**: Kiểm tra Document có relationship HAS_ENTITY không

### 3. Connection Error
```
Neo4j connection error
```
**Giải pháp**: Kiểm tra .env file và Neo4j server

## File Structure

```
curriculum-entity-linker/
├── curriculum_linker.py      # Main script
├── query_utils.py           # Query utilities & testing
├── test_linker.py          # Test suite
├── setup.py                # Setup script
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
└── README.md             # This file
```

## Dependencies

- neo4j==5.14.1
- python-dotenv==1.0.0

## Notes

- Script này không thay đổi gì ở LLM Graph Builder project chính
- Chỉ tạo thêm CurriculumLink nodes và relationships
- Có thể chạy nhiều lần (sử dụng MERGE)
- Có thể clean up bằng query DELETE CurriculumLink nodes
