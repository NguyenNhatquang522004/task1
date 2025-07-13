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
