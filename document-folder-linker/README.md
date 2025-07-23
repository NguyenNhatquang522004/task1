# Document-Folder Linker

## Mục tiêu
Tạo relationships HAVE giữa folder nodes và entity nodes của documents dựa trên điều kiện:
- `name` (folder node) = `folder_name` (document node)  
- `course_code` (folder node) = `course_code` (document node)

## Architecture
```
folder_name node (name='đề cương', course_code='CMP170') 
    -[:HAVE]-> 
entity node (của document có folder_name='đề cương', course_code='CMP170')
```

## Điều kiện liên kết
- Document node có properties: `folder_name`, `course_code`
- Folder node có properties: `name`, `course_code`  
- Liên kết khi: `folder.name == document.folder_name` AND `folder.course_code == document.course_code`
- Relationship: `(folder)-[:HAVE]->(entity_of_document)`

## Cách sử dụng
```bash
cd c:\edu\task1\llm-graph-builder\document-folder-linker
python main.py
```
