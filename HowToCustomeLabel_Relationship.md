# 📚 Hướng Dẫn Custom Node Labels và Relationships trong LLM Graph Builder

## 🎯 Mục Tiêu
Hướng dẫn này giúp bạn tùy chỉnh node labels và relationships để tạo cấu trúc phân cấp như sách (Chapter, Section, Subsection) hoặc bất kỳ domain-specific schema nào khác.

## 📁 Files và Code Sections Cần Chỉnh Sửa

### 1. 🔧 BACKEND - Schema & Processing

#### A. `backend/src/shared/constants.py`
**Vị trí**: Dòng 891-897
**Mục đích**: Cập nhật hướng dẫn cho LLM để extract hierarchical entities

```python
ADDITIONAL_INSTRUCTIONS = """Your goal is to identify and categorize entities while ensuring that specific data 
types such as dates, numbers, revenues, and other non-entity information are not extracted as separate nodes.
Instead, treat these as properties associated with the relevant entities.

FOR BOOK/DOCUMENT STRUCTURE:
- Extract hierarchical entities: Book, Chapter, Section, Subsection, Page, Paragraph
- Create relationships: CONTAINS, PART_OF, FOLLOWS, REFERENCES, CITES
- Maintain document structure and numbering (e.g., Chapter 1, Section 1.1, Subsection 1.1.1)
- Extract figures, tables, and references as separate entities
- Link content to its hierarchical parent (Paragraph PART_OF Section)

FOR CUSTOM DOMAIN SCHEMAS:
- Identify domain-specific entities and their hierarchical relationships
- Maintain proper entity types and relationship semantics
- Use consistent naming conventions for labels and relationships
"""
```

#### B. `backend/src/shared/schema_extraction.py`
**Vị trí**: Dòng 12-25 (cập nhật prompt templates)
**Mục đích**: Thêm support cho hierarchical schema extraction

```python
PROMPT_TEMPLATE_FOR_BOOK_STRUCTURE = """
You are an expert in document structure analysis and knowledge graph modeling.
Analyze the following text and extract hierarchical entities following this pattern:

HIERARCHICAL LEVELS:
- Book level: Main document/publication
- Chapter level: Major sections (numbered: Chapter 1, Chapter 2, etc.)
- Section level: Subsections (numbered: 1.1, 1.2, 2.1, 2.2, etc.)
- Subsection level: Sub-subsections (numbered: 1.1.1, 1.1.2, 1.2.1, etc.)
- Page level: Physical or logical pages
- Paragraph level: Content blocks
- Figure/Table level: Visual elements
- Reference level: Citations and references

RELATIONSHIP PATTERNS:
- Book-CONTAINS->Chapter
- Chapter-CONTAINS->Section  
- Section-CONTAINS->Subsection
- Section-FOLLOWS->Section (sequential order)
- Chapter-FOLLOWS->Chapter (sequential order)
- Paragraph-PART_OF->Section
- Figure-BELONGS_TO->Section
- Reference-CITED_BY->Paragraph

Return the result in the triplet format: ["NodeType1-RELATIONSHIP_TYPE->NodeType2"]
Maintain proper hierarchy and sequential relationships.
"""

PROMPT_TEMPLATE_FOR_CUSTOM_DOMAIN = """
You are an expert in domain-specific knowledge graph modeling.
Based on the provided domain description and example text, extract:

1. Domain-specific entity types (nodes)
2. Meaningful relationships between entities
3. Hierarchical structures if applicable

Guidelines:
- Use domain-appropriate terminology
- Maintain semantic accuracy
- Create logical entity hierarchies
- Ensure relationship consistency

Return structured triplets: ["EntityType1-RELATIONSHIP->EntityType2"]
"""
```

#### C. `backend/src/llm.py`
**Vị trí**: Dòng 207-215 (LLMGraphTransformer initialization)
**Mục đích**: Nơi system áp dụng custom nodes và relationships

```python
# Code hiện tại đã support allowed_nodes và allowed_relationships
# Cần đảm bảo logic xử lý hierarchical relationships
llm_transformer = LLMGraphTransformer(
    llm=llm,
    node_properties=node_properties,
    relationship_properties=relationship_properties,
    allowed_nodes=allowedNodes,  # Từ frontend
    allowed_relationships=allowedRelationship,  # Từ frontend
    ignore_tool_usage=ignore_tool_usage,
    additional_instructions=ADDITIONAL_INSTRUCTIONS + (additional_instructions if additional_instructions else "")
)
```

**Vị trí**: Dòng 231-247 (relationship validation logic)
**Mục đích**: Validate hierarchical relationships

```python
# Thêm validation logic cho hierarchical relationships
def validate_hierarchical_relationships(allowed_relationships, allowed_nodes):
    """Validate that hierarchical relationships maintain proper structure"""
    hierarchical_patterns = [
        ("Book", "CONTAINS", "Chapter"),
        ("Chapter", "CONTAINS", "Section"),
        ("Section", "CONTAINS", "Subsection"),
        ("Section", "FOLLOWS", "Section"),
        ("Chapter", "FOLLOWS", "Chapter")
    ]
    
    for source, relation, target in allowed_relationships:
        if (source, relation, target) in hierarchical_patterns:
            logging.info(f"Validated hierarchical relationship: {source}-{relation}->{target}")
    
    return allowed_relationships
```

### 2. 🎨 FRONTEND - UI & Schema Selection

#### A. `frontend/src/assets/schemas.json`
**Vị trí**: Toàn bộ file
**Mục đích**: Thêm predefined schemas cho book structure và custom domains

```json
{
  "labels": [
    "Book",
    "Chapter", 
    "Section",
    "Subsection",
    "Page",
    "Paragraph",
    "Figure",
    "Table",
    "Reference",
    "Citation",
    "Author",
    "Publisher"
  ],
  "relationshipTypes": [
    "CONTAINS",
    "PART_OF", 
    "FOLLOWS",
    "REFERENCES",
    "CITES",
    "INCLUDES",
    "BELONGS_TO",
    "AUTHORED_BY",
    "PUBLISHED_BY",
    "APPEARS_IN",
    "DESCRIBES"
  ],
  "schema": "book_structure"
},
{
  "labels": [
    "Course",
    "Module",
    "Lesson",
    "Topic",
    "Exercise",
    "Assignment",
    "Student",
    "Instructor",
    "Resource"
  ],
  "relationshipTypes": [
    "CONTAINS",
    "PART_OF",
    "TEACHES",
    "LEARNS",
    "ASSIGNS",
    "COMPLETES",
    "REQUIRES",
    "USES",
    "REFERENCES"
  ],
  "schema": "education"
},
{
  "labels": [
    "Organization",
    "Department",
    "Team",
    "Employee",
    "Project",
    "Task",
    "Meeting",
    "Document",
    "Process"
  ],
  "relationshipTypes": [
    "BELONGS_TO",
    "MANAGES",
    "WORKS_ON",
    "REPORTS_TO",
    "PARTICIPATES_IN",
    "CREATES",
    "FOLLOWS",
    "DEPENDS_ON",
    "DOCUMENTS"
  ],
  "schema": "organization"
}
```

#### B. `frontend/src/context/UsersFiles.tsx`
**Vị trí**: Dòng 35-36 (state management)
**Mục đích**: Quản lý selected nodes và relationships

```typescript
// State cho custom schema management
const [selectedNodes, setSelectedNodes] = useState<readonly OptionType[]>([]);
const [selectedRels, setSelectedRels] = useState<readonly OptionType[]>([]);
const [customSchemaName, setCustomSchemaName] = useState<string>('');
const [isCustomSchema, setIsCustomSchema] = useState<boolean>(false);

// Thêm functions để handle custom schema
const saveCustomSchema = (name: string, nodes: OptionType[], rels: OptionType[]) => {
  const customSchema = {
    name,
    labels: nodes.map(n => n.value),
    relationshipTypes: rels.map(r => r.value),
    schema: name.toLowerCase().replace(' ', '_')
  };
  
  // Save to localStorage or send to backend
  localStorage.setItem(`custom_schema_${name}`, JSON.stringify(customSchema));
};

const loadCustomSchema = (schemaName: string) => {
  const saved = localStorage.getItem(`custom_schema_${schemaName}`);
  if (saved) {
    const schema = JSON.parse(saved);
    setSelectedNodes(schema.labels.map((label: string) => ({ value: label, label })));
    setSelectedRels(schema.relationshipTypes.map((rel: string) => ({ value: rel, label: rel })));
  }
};
```

#### C. `frontend/src/utils/FileAPI.ts`
**Vị trí**: Dòng 32-33, 53-54, 67-68, 84-85
**Mục đích**: Type definitions và API calls

```typescript
// Type definitions
interface ProcessingParams {
  allowedNodes?: string[];
  allowedRelationship?: string[];
  additional_instructions?: string;
  schema_type?: 'predefined' | 'custom' | 'generated';
  hierarchical_mode?: boolean;
}

// Enhanced API call functions
export const processWithCustomSchema = async (
  params: ProcessingParams & {
    files: File[];
    model: string;
  }
) => {
  const formData = new FormData();
  
  // Add files
  params.files.forEach(file => formData.append('files', file));
  
  // Add schema parameters
  if (params.allowedNodes) {
    formData.append('allowedNodes', params.allowedNodes.join(','));
  }
  
  if (params.allowedRelationship) {
    formData.append('allowedRelationship', params.allowedRelationship.join(','));
  }
  
  // Add hierarchical processing instructions
  if (params.hierarchical_mode) {
    const hierarchicalInstructions = `
      Process content maintaining hierarchical structure.
      Extract sequential relationships (FOLLOWS).
      Maintain parent-child relationships (CONTAINS, PART_OF).
    `;
    formData.append('additional_instructions', hierarchicalInstructions);
  }
  
  return await api.post('/extract', formData);
};
```

### 3. 🔗 API ENDPOINTS

#### A. `backend/score.py`
**Vị trí**: Dòng 217-218 (API parameters)
**Mục đích**: Nhận custom schema parameters từ frontend

```python
@app.post("/extract")
async def extract_graph(
    # ...existing parameters...
    allowedNodes=Form(None),
    allowedRelationship=Form(None),
    schema_type=Form("predefined"),  # New parameter
    hierarchical_mode=Form(False),   # New parameter
    additional_instructions=Form(None),
):
    # Enhanced processing logic
    if hierarchical_mode:
        additional_instructions = enhance_hierarchical_instructions(additional_instructions)
    
    # Pass to processing functions
    uri_latency, result = await extract_graph_from_file_local_file(
        uri, userName, password, database, model, merged_file_path, file_name, 
        allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, 
        chunks_to_combine, retry_condition, additional_instructions
    )
```

**Vị trí**: Dòng 777-785 (schema generation API)
**Mục đích**: Generate schema từ text với hierarchical support

```python
@app.post("/populate_graph_schema")
async def populate_graph_schema(
    input_text=Form(None), 
    model=Form(None), 
    is_schema_description_checked=Form(None),
    is_local_storage=Form(None),
    domain_type=Form("general"),  # New parameter
    hierarchical=Form(False),     # New parameter
    email=Form(None)
):
    try:
        result = populate_graph_schema_from_text(
            input_text, model, is_schema_description_checked, 
            is_local_storage, domain_type, hierarchical
        )
        # ...rest of the function
```

### 4. 🔄 PROCESSING WORKFLOW

#### A. `backend/src/main.py`
**Vị trí**: Dòng 333 (processing_source function)
**Mục đích**: Main processing với custom schema support

```python
async def processing_source(
    uri, userName, password, database, model, file_name, pages, 
    allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, 
    chunks_to_combine, is_uploaded_from_local=None, merged_file_path=None, 
    retry_condition=None, additional_instructions=None,
    hierarchical_mode=False  # New parameter
):
    # Enhanced processing logic for hierarchical content
    if hierarchical_mode:
        additional_instructions = add_hierarchical_processing_instructions(additional_instructions)
    
    # Process with custom schema
    graph_document_list = await get_graph_from_llm(
        model, chunkId_chunkDoc_list, allowedNodes, allowedRelationship, 
        chunks_to_combine, additional_instructions
    )
    
    # Post-process for hierarchical relationships
    if hierarchical_mode:
        graph_document_list = enhance_hierarchical_relationships(graph_document_list)
    
    return graph_document_list
```

## 🚀 Hướng Dẫn Sử Dụng Thực Tế

### Bước 1: Tạo Book Structure Schema

1. **Thêm schema vào `frontend/src/assets/schemas.json`:**
```json
{
  "labels": ["Book", "Chapter", "Section", "Subsection", "Page", "Paragraph"],
  "relationshipTypes": ["CONTAINS", "PART_OF", "FOLLOWS", "REFERENCES"],
  "schema": "book_structure"
}
```

2. **Cập nhật LLM instructions trong `backend/src/shared/constants.py`:**
```python
ADDITIONAL_INSTRUCTIONS = """
FOR BOOK STRUCTURE:
- Extract: Chapter (Chapter 1, Chapter 2...)
- Extract: Section (1.1, 1.2, 2.1, 2.2...)  
- Extract: Subsection (1.1.1, 1.1.2, 1.2.1...)
- Create: Chapter-CONTAINS->Section
- Create: Section-CONTAINS->Subsection
- Create: Section-FOLLOWS->Section (sequential)
- Maintain numbering: preserve original section numbers
"""
```

### Bước 2: Frontend Schema Selection

1. **User chọn "book_structure" từ schema dropdown**
2. **System tự động load corresponding nodes và relationships**
3. **User có thể customize thêm nodes/relationships nếu cần**

### Bước 3: Processing với Custom Schema

1. **Frontend gửi allowedNodes và allowedRelationship lên backend**
2. **Backend áp dụng custom schema vào LLMGraphTransformer**
3. **LLM extract entities theo custom schema**
4. **Post-processing để ensure hierarchical consistency**

### Bước 4: Advanced Customization

**Tạo Custom Schema cho Domain Cụ Thể:**

```python
# Ví dụ: Legal Document Schema
LEGAL_SCHEMA = {
    "labels": [
        "Law", "Article", "Section", "Subsection", "Paragraph",
        "Case", "Court", "Judge", "Lawyer", "Citation"
    ],
    "relationshipTypes": [
        "CONTAINS", "REFERENCES", "CITES", "INTERPRETS",
        "OVERRULES", "SUPPORTS", "CONTRADICTS", "APPLIES_TO"
    ]
}

# Ví dụ: Medical Document Schema  
MEDICAL_SCHEMA = {
    "labels": [
        "Patient", "Doctor", "Diagnosis", "Treatment", "Medicine",
        "Symptom", "Disease", "Hospital", "Test", "Result"
    ],
    "relationshipTypes": [
        "TREATS", "DIAGNOSED_WITH", "PRESCRIBED", "SHOWS",
        "INDICATES", "CAUSED_BY", "LEADS_TO", "ADMINISTERED_BY"
    ]
}
```

## 🔧 Advanced Features

### 1. Dynamic Schema Generation
```python
# Trong backend/src/main.py
def generate_schema_from_content(content: str, domain: str) -> dict:
    """Generate schema based on content analysis"""
    # Analyze content to suggest appropriate schema
    # Return suggested nodes and relationships
    pass
```

### 2. Schema Validation
```python
# Trong backend/src/llm.py
def validate_schema_consistency(nodes: List[str], relationships: List[str]) -> bool:
    """Validate that schema is logically consistent"""
    # Check for orphaned nodes
    # Validate relationship semantics
    # Ensure hierarchical consistency
    pass
```

### 3. Schema Templates
```python
# Trong frontend/src/utils/SchemaTemplates.ts
export const SCHEMA_TEMPLATES = {
    hierarchical: {
        book: ["Book", "Chapter", "Section", "Subsection"],
        organization: ["Company", "Department", "Team", "Employee"],
        education: ["Course", "Module", "Lesson", "Topic"]
    },
    relationships: {
        hierarchical: ["CONTAINS", "PART_OF", "BELONGS_TO"],
        sequential: ["FOLLOWS", "PRECEDES", "NEXT"],
        reference: ["REFERENCES", "CITES", "MENTIONS"]
    }
}
```

## 🎯 Best Practices

### 1. Schema Design
- **Consistency**: Sử dụng naming conventions nhất quán
- **Hierarchy**: Maintain clear parent-child relationships
- **Semantics**: Ensure relationships make semantic sense
- **Scalability**: Design schema có thể mở rộng

### 2. LLM Instructions
- **Specific**: Provide clear, specific instructions
- **Examples**: Include concrete examples
- **Constraints**: Define what NOT to extract
- **Format**: Specify output format requirements

### 3. Processing Optimization
- **Chunking**: Optimize chunk size for hierarchical content
- **Overlap**: Ensure chapter/section boundaries are preserved
- **Validation**: Implement post-processing validation
- **Performance**: Monitor processing time for large documents

### 4. User Experience
- **Templates**: Provide common schema templates
- **Validation**: Real-time schema validation
- **Preview**: Show schema structure before processing
- **Feedback**: Provide clear error messages

## 🔍 Troubleshooting

### Common Issues:

1. **Missing Hierarchical Relationships**
   - Check allowedRelationship format
   - Verify LLM instructions include hierarchy
   - Ensure proper chunk boundaries

2. **Incorrect Entity Extraction**
   - Review additional_instructions
   - Check allowed_nodes configuration
   - Validate schema consistency

3. **Performance Issues**
   - Optimize chunk size
   - Reduce schema complexity
   - Implement caching for repeated schemas

### Debug Steps:

1. **Check Frontend Schema Selection**
2. **Verify Backend Parameter Reception**
3. **Monitor LLM Processing Logs**
4. **Validate Graph Output Structure**
5. **Test with Simple Examples First**

## 📚 Kết Luận

Hệ thống LLM Graph Builder đã có đầy đủ infrastructure để support custom node labels và relationships. Bằng cách:

1. **Cập nhật schemas.json** với custom schemas
2. **Chỉnh sửa LLM instructions** trong constants.py
3. **Customize schema extraction logic** nếu cần
4. **Sử dụng existing API endpoints** để process với custom schema

Bạn có thể tạo ra bất kỳ cấu trúc phân cấp nào, từ book structure (Chapter, Section, Subsection) đến domain-specific schemas cho legal, medical, educational, hoặc bất kỳ lĩnh vực nào khác.

---

*Tài liệu này cung cấp roadmap chi tiết để implement custom schemas. Bắt đầu với simple book structure, sau đó mở rộng cho các domain khác theo nhu cầu.*