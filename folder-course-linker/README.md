# Folder Course Linker

## Mô tả dự án
Project riêng biệt để tạo và liên kết folder nodes với course khung sườn.

## Chức năng chính
1. **Phân tích Course khung sườn**: Lấy các node có chỉ 1 label là `Course`
2. **Thu thập folder_name**: Lấy tất cả folder_name từ các Document nodes  
3. **Tạo folder nodes**: Tạo nodes với label = folder_name
4. **Liên kết**: Tạo relationship `POINT_TO` từ course khung sườn đến folder nodes

## Nguyên tắc hoạt động
- Mỗi course khung sườn sẽ POINT_TO tất cả folder nodes
- Folder nodes có label = folder_name và properties: name, course_code
- Không ảnh hưởng đến dữ liệu hiện có

## Cấu trúc thư mục
```
folder-course-linker/
├── README.md
├── requirements.txt
├── config.py
├── main.py
├── data_analyzer.py
├── folder_node_creator.py
├── relationship_builder.py
└── queries/
    ├── analyze.cql
    ├── create_nodes.cql
    └── create_relationships.cql
```

## Installation
```bash
cd folder-course-linker
pip install -r requirements.txt
```

## Usage
```bash
# Cài đặt
cd folder-course-linker
cp .env.example .env
# Chỉnh sửa .env với thông tin Neo4j
pip install -r requirements.txt

# Chạy tự động (khuyến nghị)
python main.py

# Hoặc chạy với menu interactive
python main_interactive.py
```
