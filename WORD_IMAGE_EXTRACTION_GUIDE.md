# Hướng dẫn Trích xuất Hình ảnh từ File Word và Lưu vào Neo4j

## 🎯 Mục tiêu
Trích xuất hình ảnh từ file Word (.docx) và lưu trữ trong Neo4j database để hiển thị trong knowledge graph.

## 🔧 Chuẩn bị

### 1. Cài đặt thư viện cần thiết
```bash
pip install python-docx pillow base64 io zipfile
```

### 2. Cấu trúc thư mục lưu ảnh
```
backend/
├── src/
│   ├── image_extraction/
│   │   ├── __init__.py
│   │   ├── docx_image_extractor.py
│   │   └── image_storage.py
│   └── static/
│       └── extracted_images/
```

## 📝 Các bước thực hiện

### Bước 1: Tạo module trích xuất ảnh từ DOCX

**File: `backend/src/image_extraction/docx_image_extractor.py`**
```python
import os
import zipfile
import base64
from io import BytesIO
from PIL import Image
from docx import Document
from docx.shared import Inches
import logging

class DocxImageExtractor:
    def __init__(self, docx_file_path, output_dir="src/static/extracted_images"):
        self.docx_file_path = docx_file_path
        self.output_dir = output_dir
        self.images = []
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """Tạo thư mục output nếu chưa tồn tại"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def extract_images_from_docx(self):
        """Trích xuất tất cả hình ảnh từ file DOCX"""
        try:
            # Method 1: Sử dụng zipfile để trích xuất ảnh
            with zipfile.ZipFile(self.docx_file_path, 'r') as docx_zip:
                image_files = [f for f in docx_zip.namelist() if f.startswith('word/media/')]
                
                for i, image_file in enumerate(image_files):
                    # Đọc dữ liệu ảnh
                    image_data = docx_zip.read(image_file)
                    
                    # Lấy extension của file
                    file_extension = os.path.splitext(image_file)[1]
                    if not file_extension:
                        file_extension = '.png'  # Default extension
                    
                    # Tạo tên file mới
                    image_filename = f"image_{i+1}{file_extension}"
                    image_path = os.path.join(self.output_dir, image_filename)
                    
                    # Lưu ảnh
                    with open(image_path, 'wb') as img_file:
                        img_file.write(image_data)
                    
                    # Convert to base64 for database storage
                    base64_data = base64.b64encode(image_data).decode('utf-8')
                    
                    self.images.append({
                        'filename': image_filename,
                        'path': image_path,
                        'base64': base64_data,
                        'mime_type': self.get_mime_type(file_extension),
                        'size': len(image_data)
                    })
                    
                    logging.info(f"Extracted image: {image_filename}")
            
            # Method 2: Sử dụng python-docx để lấy context ảnh
            self.extract_image_context()
            
            return self.images
            
        except Exception as e:
            logging.error(f"Error extracting images: {e}")
            return []
    
    def extract_image_context(self):
        """Trích xuất context xung quanh ảnh trong document"""
        try:
            doc = Document(self.docx_file_path)
            
            for i, paragraph in enumerate(doc.paragraphs):
                # Tìm ảnh trong paragraph
                for run in paragraph.runs:
                    if run._element.xpath('.//a:blip'):
                        # Tìm context trước và sau ảnh
                        context_before = ""
                        context_after = ""
                        
                        # Lấy 2 paragraph trước
                        if i >= 2:
                            context_before = doc.paragraphs[i-2].text + " " + doc.paragraphs[i-1].text
                        elif i >= 1:
                            context_before = doc.paragraphs[i-1].text
                        
                        # Lấy 2 paragraph sau
                        if i + 2 < len(doc.paragraphs):
                            context_after = doc.paragraphs[i+1].text + " " + doc.paragraphs[i+2].text
                        elif i + 1 < len(doc.paragraphs):
                            context_after = doc.paragraphs[i+1].text
                        
                        # Cập nhật context cho ảnh tương ứng
                        if len(self.images) > 0:
                            self.images[-1]['context_before'] = context_before.strip()
                            self.images[-1]['context_after'] = context_after.strip()
                            self.images[-1]['paragraph_index'] = i
                            
        except Exception as e:
            logging.error(f"Error extracting image context: {e}")
    
    def get_mime_type(self, file_extension):
        """Xác định MIME type từ file extension"""
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff'
        }
        return mime_types.get(file_extension.lower(), 'image/png')
```

### Bước 2: Tạo module lưu trữ ảnh vào Neo4j

**File: `backend/src/image_extraction/image_storage.py`**
```python
import logging
from src.shared.common_fn import create_graph_database_connection

class ImageNeo4jStorage:
    def __init__(self, uri, username, password, database):
        self.graph = create_graph_database_connection(uri, username, password, database)
    
    def create_image_node(self, image_data, document_filename, chunk_id=None):
        """Tạo node Image trong Neo4j"""
        try:
            query = """
            MERGE (img:Image {filename: $filename})
            SET img.base64_data = $base64_data,
                img.mime_type = $mime_type,
                img.size = $size,
                img.context_before = $context_before,
                img.context_after = $context_after,
                img.paragraph_index = $paragraph_index,
                img.document_source = $document_source,
                img.created_at = datetime()
            RETURN img
            """
            
            params = {
                'filename': image_data['filename'],
                'base64_data': image_data['base64'],
                'mime_type': image_data['mime_type'],
                'size': image_data['size'],
                'context_before': image_data.get('context_before', ''),
                'context_after': image_data.get('context_after', ''),
                'paragraph_index': image_data.get('paragraph_index', 0),
                'document_source': document_filename
            }
            
            result = self.graph.query(query, params)
            
            # Liên kết với Document node
            self.link_image_to_document(image_data['filename'], document_filename)
            
            # Liên kết với Chunk node nếu có
            if chunk_id:
                self.link_image_to_chunk(image_data['filename'], chunk_id)
            
            logging.info(f"Created image node: {image_data['filename']}")
            return result
            
        except Exception as e:
            logging.error(f"Error creating image node: {e}")
            return None
    
    def link_image_to_document(self, image_filename, document_filename):
        """Liên kết Image với Document"""
        try:
            query = """
            MATCH (img:Image {filename: $image_filename})
            MATCH (doc:Document {fileName: $document_filename})
            MERGE (doc)-[:CONTAINS_IMAGE]->(img)
            """
            
            params = {
                'image_filename': image_filename,
                'document_filename': document_filename
            }
            
            self.graph.query(query, params)
            logging.info(f"Linked image {image_filename} to document {document_filename}")
            
        except Exception as e:
            logging.error(f"Error linking image to document: {e}")
    
    def link_image_to_chunk(self, image_filename, chunk_id):
        """Liên kết Image với Chunk"""
        try:
            query = """
            MATCH (img:Image {filename: $image_filename})
            MATCH (chunk:Chunk {id: $chunk_id})
            MERGE (chunk)-[:CONTAINS_IMAGE]->(img)
            """
            
            params = {
                'image_filename': image_filename,
                'chunk_id': chunk_id
            }
            
            self.graph.query(query, params)
            logging.info(f"Linked image {image_filename} to chunk {chunk_id}")
            
        except Exception as e:
            logging.error(f"Error linking image to chunk: {e}")
    
    def get_images_for_document(self, document_filename):
        """Lấy tất cả ảnh của một document"""
        try:
            query = """
            MATCH (doc:Document {fileName: $document_filename})-[:CONTAINS_IMAGE]->(img:Image)
            RETURN img.filename as filename,
                   img.base64_data as base64_data,
                   img.mime_type as mime_type,
                   img.context_before as context_before,
                   img.context_after as context_after
            ORDER BY img.paragraph_index
            """
            
            params = {'document_filename': document_filename}
            result = self.graph.query(query, params)
            
            return result
            
        except Exception as e:
            logging.error(f"Error getting images for document: {e}")
            return []
```

### Bước 3: Cập nhật local_file.py để tích hợp trích xuất ảnh

**File: `backend/src/document_sources/local_file.py`** (thêm vào cuối file)
```python
# Thêm import
from src.image_extraction.docx_image_extractor import DocxImageExtractor
from src.image_extraction.image_storage import ImageNeo4jStorage

def extract_and_store_images(file_path, file_name, uri, username, password, database):
    """Trích xuất và lưu ảnh từ file Word vào Neo4j"""
    if not file_path.suffix.lower() == '.docx':
        return []
    
    try:
        # Trích xuất ảnh
        extractor = DocxImageExtractor(str(file_path))
        images = extractor.extract_images_from_docx()
        
        if not images:
            logging.info(f"No images found in {file_name}")
            return []
        
        # Lưu vào Neo4j
        storage = ImageNeo4jStorage(uri, username, password, database)
        
        for image_data in images:
            storage.create_image_node(image_data, file_name)
        
        logging.info(f"Extracted and stored {len(images)} images from {file_name}")
        return images
        
    except Exception as e:
        logging.error(f"Error processing images for {file_name}: {e}")
        return []
```

### Bước 4: Cập nhật main.py để gọi trích xuất ảnh

**File: `backend/src/main.py`** (thêm vào hàm `extract_graph_from_file_local_file`)
```python
# Thêm import
from src.document_sources.local_file import extract_and_store_images

# Trong hàm extract_graph_from_file_local_file, thêm sau dòng get_documents_from_file_by_path:
def extract_graph_from_file_local_file(uri, userName, password, database, model, file_path, file_name, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition, additional_instructions):
    # ...existing code...
    
    file_name, pages, file_extension = get_documents_from_file_by_path(file_path, file_name)
    
    # Trích xuất ảnh cho file Word
    if file_extension == '.docx':
        extract_and_store_images(Path(file_path), file_name, uri, userName, password, database)
    
    # ...rest of existing code...
```

### Bước 5: Cập nhật Frontend để hiển thị ảnh

**File: Frontend component để hiển thị ảnh**
```typescript
// Thêm vào component hiển thị graph
const fetchDocumentImages = async (documentName: string) => {
  try {
    const response = await fetch(`/api/documents/${documentName}/images`);
    const images = await response.json();
    return images;
  } catch (error) {
    console.error('Error fetching images:', error);
    return [];
  }
};

// Component hiển thị ảnh
const ImageDisplay = ({ base64Data, mimeType, context }: ImageProps) => {
  return (
    <div className="image-container">
      <img 
        src={`data:${mimeType};base64,${base64Data}`}
        alt="Document image"
        className="document-image"
      />
      {context && (
        <div className="image-context">
          <p><strong>Context:</strong> {context}</p>
        </div>
      )}
    </div>
  );
};
```

### Bước 6: Tạo API endpoint để lấy ảnh

**File: `backend/score.py`** (thêm endpoint)
```python
@app.get("/documents/{document_name}/images")
async def get_document_images(document_name: str, uri: str = Depends(get_neo4j_uri), 
                             userName: str = Depends(get_neo4j_username), 
                             password: str = Depends(get_neo4j_password), 
                             database: str = Depends(get_neo4j_database)):
    try:
        storage = ImageNeo4jStorage(uri, userName, password, database)
        images = storage.get_images_for_document(document_name)
        return {"images": images}
    except Exception as e:
        return {"error": str(e), "images": []}
```

## 🎯 Lưu ý quan trọng

### 1. Dung lượng Database
- Ảnh base64 có thể rất lớn
- Cân nhắc lưu ảnh riêng và chỉ lưu đường dẫn trong Neo4j

### 2. Performance
- Trích xuất ảnh có thể làm chậm quá trình processing
- Chạy trích xuất ảnh trong background thread

### 3. Bảo mật
- Validate file type và size trước khi trích xuất
- Scan malware cho ảnh được trích xuất

### 4. Hiển thị
- Resize ảnh cho phù hợp với UI
- Lazy loading cho ảnh lớn

## 🚀 Cách sử dụng

1. Upload file Word có chứa ảnh
2. Hệ thống tự động trích xuất ảnh và lưu vào Neo4j
3. Ảnh sẽ hiển thị trong knowledge graph với context xung quanh
4. Có thể search và filter theo ảnh

## 🔧 Troubleshooting

### Lỗi thường gặp:

#### 1. Vấn đề trích xuất ảnh:
- **"No images found"**: File Word không có ảnh hoặc ảnh bị corrupt
- **"Permission denied"**: Không có quyền ghi vào thư mục output
- **"Memory error"**: Ảnh quá lớn, cần giảm kích thước

#### 2. Vấn đề Chunk/Token Limits:
- **"integer division result too large for a float"**: Token chunks quá lớn
- **"Chunk overflow error"**: MAX_TOKEN_CHUNK_SIZE vượt quá giới hạn

**Giải pháp cho Chunk/Token Issues:**

1. **Cập nhật file `.env`**:
```env
# Giá trị an toàn cho token limits
MAX_TOKEN_CHUNK_SIZE=60000
TOKENS_PER_CHUNK=5000
CHUNK_OVERLAP=200
```

2. **Kiểm tra và điều chỉnh trong `backend/src/main.py`**:
```python
# Đảm bảo token_chunk_size không vượt quá MAX_TOKEN_CHUNK_SIZE
def validate_token_settings(token_chunk_size, max_token_limit=60000):
    if token_chunk_size > max_token_limit:
        logging.warning(f"token_chunk_size {token_chunk_size} exceeds limit {max_token_limit}, adjusting...")
        return max_token_limit
    return token_chunk_size
```
