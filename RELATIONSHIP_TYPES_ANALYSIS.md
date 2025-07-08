# 🔗 LLM Graph Builder - Relationship Types Analysis

## 📊 **Tổng số loại RelationshipType trong project:**

Dựa trên phân tích toàn bộ codebase, tôi đã tìm thấy **12 loại relationshipType** chính được sử dụng:

---

## 🏗️ **System Relationship Types (8 loại):**

### 1. **Document-Chunk Relationships:**
- **`PART_OF`** - Liên kết từ Chunk tới Document
- **`FIRST_CHUNK`** - Liên kết từ Document tới chunk đầu tiên

### 2. **Chunk-Chunk Relationships:**
- **`NEXT_CHUNK`** - Liên kết sequential giữa các chunks
- **`SIMILAR`** - Liên kết giữa các chunks tương tự (dựa trên embedding)

### 3. **Chunk-Entity Relationships:**
- **`HAS_ENTITY`** - Liên kết từ Chunk tới Entities được extract

### 4. **Community Relationships:**
- **`IN_COMMUNITY`** - Entity thuộc về Community
- **`PARENT_COMMUNITY`** - Hierarchy giữa các communities

### 5. **System Internal:**
- **`_Bloom_Perspective_`** - Neo4j Bloom visualization

---

## 🎯 **Application-Specific Relationship Types (4 loại):**

### 6. **Chat/Session Relationships:**
- **`NEXT`** - Liên kết trong chat sessions
- **`LAST_MESSAGE`** - Liên kết tới message cuối cùng

### 7. **Dynamic Entity Relationships:**
- **`*` (Wildcard)** - Các relationships được LLM tự động tạo
- **Custom relationship types** - Được extract từ content bởi LLM

---

## 📋 **Chi tiết từ Code:**

### **File: `graphDB_dataAccess.py` (Line 565):**
```python
relation_query = """
    CALL db.relationshipTypes() yield relationshipType
    WHERE NOT relationshipType  IN [
        'PART_OF', 'NEXT_CHUNK', 'HAS_ENTITY', '_Bloom_Perspective_',
        'FIRST_CHUNK','SIMILAR','IN_COMMUNITY','PARENT_COMMUNITY'
    ] 
    return relationshipType order by relationshipType
    """
```

### **File: `main.py` (Lines 670-671):**
```python
excluded_relationships = [
    'PART_OF', 'HAS_ENTITY', '__Entity__', 'Session',
    'NEXT_CHUNK', '_Bloom_Perspective_', 'FIRST_CHUNK',
    'SIMILAR', 'IN_COMMUNITY', 'PARENT_COMMUNITY', 'NEXT', 'LAST_MESSAGE'
]
```

---

## 🔄 **Relationship Usage Patterns:**

### **1. Document Structure:**
```
Document --[FIRST_CHUNK]--> First Chunk
    ↑
[PART_OF]
    ↑
All Chunks --[NEXT_CHUNK]--> Next Chunk
```

### **2. Semantic Relationships:**
```
Chunk --[HAS_ENTITY]--> Entity
Chunk --[SIMILAR]--> Similar Chunk (similarity score)
```

**📁 Files thực hiện so sánh chunk SIMILAR:**

#### **1. `backend/src/graphDB_dataAccess.py` - Main Implementation:**
```python
def update_KNN_graph(self):
    """
    Update the graph node with SIMILAR relationship where embedding score match
    """
    knn_min_score = os.environ.get('KNN_MIN_SCORE')  # 0.94 từ .env
    if len(index) > 0:
        self.graph.query("""
            MATCH (c:Chunk)
            WHERE c.embedding IS NOT NULL AND count { (c)-[:SIMILAR]-() } < 5
            CALL db.index.vector.queryNodes('vector', 6, c.embedding) yield node, score
            WHERE node <> c and score >= $score 
            MERGE (c)-[rel:SIMILAR]-(node) SET rel.score = score
        """, {"score":float(knn_min_score)})
```

#### **2. `backend/src/main.py` - Trigger Function:**
```python
def update_graph(graph):
    """Update the graph node with SIMILAR relationship where embedding score match"""
    graph_DB_dataAccess = graphDBdataAccess(graph)
    graph_DB_dataAccess.update_KNN_graph()  # Calls the similarity comparison
```

#### **3. Configuration trong `.env`:**
```properties
KNN_MIN_SCORE = "0.94"  # Minimum similarity score threshold
```

**🔍 Cách thức hoạt động:**
1. **Vector Index**: Sử dụng Neo4j vector index với cosine similarity
2. **K-Nearest Neighbors**: Tìm 6 chunks gần nhất cho mỗi chunk
3. **Threshold**: Chỉ tạo relationship nếu similarity score >= 0.94
4. **Limit**: Mỗi chunk tối đa 5 SIMILAR relationships
5. **Bidirectional**: Tạo relationship 2 chiều giữa similar chunks

### **3. Community Structure:**
```
Entity --[IN_COMMUNITY]--> Community Level 0
Community Level 0 --[PARENT_COMMUNITY]--> Community Level 1
Community Level 1 --[PARENT_COMMUNITY]--> Community Level 2
```

### **4. Dynamic Content Relationships:**
```
Entity --[CUSTOM_REL]--> Entity (extracted by LLM)
Examples: WORKS_FOR, LOCATED_IN, RELATED_TO, etc.
```

---

## ⚙️ **Configuration Impact:**

### **Excluded from User Queries:**
Trong function `get_nodelabels_relationships()`, các system relationships được exclude:
- Document management: `PART_OF`, `FIRST_CHUNK`, `NEXT_CHUNK`
- System internal: `_Bloom_Perspective_`, `HAS_ENTITY`
- Similarity: `SIMILAR`
- Communities: `IN_COMMUNITY`, `PARENT_COMMUNITY`

### **Available for User Analysis:**
- Custom relationships extracted by LLM từ document content
- Domain-specific relationships (business logic)

---

## 📈 **Relationship Statistics:**

### **System Relationships (Fixed):** 8 types
### **Dynamic Relationships (Variable):** Unlimited
- Tùy thuộc vào content được extract bởi LLM
- Examples: `WORKS_FOR`, `LIVES_IN`, `PART_OF_COMPANY`, etc.

### **Total Count:** 8 System + N Dynamic = **8 + N relationship types**

---

## 🎯 **Summary:**

**Có tối thiểu 12 loại relationshipType** được định nghĩa trong code:

1. `PART_OF` ✅
2. `FIRST_CHUNK` ✅  
3. `NEXT_CHUNK` ✅
4. `SIMILAR` ✅
5. `HAS_ENTITY` ✅
6. `IN_COMMUNITY` ✅
7. `PARENT_COMMUNITY` ✅
8. `_Bloom_Perspective_` ✅
9. `NEXT` ✅
10. `LAST_MESSAGE` ✅
11. **Dynamic LLM-extracted relationships** (unlimited) ✅
12. **Wildcard relationships** (`*`) ✅

**Actual number trong database sẽ nhiều hơn** vì LLM sẽ tạo thêm các relationship types based on document content!
