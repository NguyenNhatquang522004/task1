# 📚 CONSTANTS.PY - DETAILED CODE EXPLANATION

## 📋 Tổng quan
File `constants.py` chứa tất cả các constants, queries và cấu hình cho hệ thống LLM Graph Builder. Đây là file trung tâm điều khiển các hoạt động của hệ thống từ LLM models đến GraphRAG queries.

---

## 🤖 **LLM MODEL CONFIGURATIONS**

### Model Lists
```python
OPENAI_MODELS = ["openai-gpt-3.5", "openai-gpt-4o", "openai-gpt-4o-mini"]
GEMINI_MODELS = ["gemini-1.0-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
GROQ_MODELS = ["groq-llama3"]
```

**Giải thích:**
- **`OPENAI_MODELS`**: Danh sách các model OpenAI được hỗ trợ
  - `openai-gpt-3.5`: GPT-3.5 Turbo model
  - `openai-gpt-4o`: GPT-4 Omni model (latest)
  - `openai-gpt-4o-mini`: GPT-4 Omni Mini (lightweight)
- **`GEMINI_MODELS`**: Danh sách Google Gemini models
  - `gemini-1.0-pro`: Gemini Pro v1.0
  - `gemini-1.5-pro`: Gemini Pro v1.5 (enhanced)
  - `gemini-1.5-flash`: Gemini Flash (faster inference)
- **`GROQ_MODELS`**: Groq hardware accelerated models
  - `groq-llama3`: Llama 3 running on Groq chips

---

## ☁️ **CLOUD STORAGE CONFIGURATIONS**

```python
BUCKET_UPLOAD = 'llm-graph-builder-upload'
BUCKET_FAILED_FILE = 'llm-graph-builder-failed'
PROJECT_ID = 'llm-experiments-387609'
```

**Giải thích:**
- **`BUCKET_UPLOAD`**: Google Cloud Storage bucket name cho file uploads
- **`BUCKET_FAILED_FILE`**: Bucket name cho failed file processing
- **`PROJECT_ID`**: Google Cloud Project ID để authenticate services

---

## 📊 **GRAPH DISPLAY CONFIGURATION**

```python
GRAPH_CHUNK_LIMIT = 50
```

**Giải thích:**
- **`GRAPH_CHUNK_LIMIT`**: Giới hạn số lượng chunks được hiển thị trong graph visualization (50 chunks) để tránh overload UI

---

## 🔍 **MAIN GRAPH QUERY**

### Graph Query Structure
```python
GRAPH_QUERY = """
MATCH docs = (d:Document) 
WHERE d.fileName IN $document_names
WITH docs, d 
ORDER BY d.createdAt DESC
```

**Giải thích từng phần:**

#### 1. Document Matching
```cypher
MATCH docs = (d:Document) 
WHERE d.fileName IN $document_names
```
- **`MATCH docs = (d:Document)`**: Tìm tất cả Document nodes
- **`WHERE d.fileName IN $document_names`**: Filter theo danh sách filename được truyền vào
- **`$document_names`**: Parameter được inject từ API call

#### 2. Document Ordering
```cypher
WITH docs, d 
ORDER BY d.createdAt DESC
```
- **`WITH docs, d`**: Pass variables sang phần tiếp theo
- **`ORDER BY d.createdAt DESC`**: Sắp xếp documents theo thời gian tạo (mới nhất trước)

#### 3. Chunk Fetching with Limit
```cypher
CALL {{
  WITH d
  OPTIONAL MATCH chunks = (d)<-[:PART_OF|FIRST_CHUNK]-(c:Chunk)
  RETURN c, chunks LIMIT {graph_chunk_limit}
}}
```
- **`CALL {{ WITH d ... }}`**: Subquery để xử lý từng document riêng biệt
- **`OPTIONAL MATCH`**: Cho phép documents không có chunks
- **`(d)<-[:PART_OF|FIRST_CHUNK]-(c:Chunk)`**: Tìm chunks thuộc document
  - `PART_OF`: Relationship từ chunk đến document
  - `FIRST_CHUNK`: Relationship cho chunk đầu tiên
- **`LIMIT {graph_chunk_limit}`**: Giới hạn chunks (50 chunks)

#### 4. Data Aggregation
```cypher
WITH collect(distinct docs) AS docs, 
     collect(distinct chunks) AS chunks, 
     collect(distinct c) AS selectedChunks
```
- **`collect(distinct ...)`**: Aggregate distinct values thành arrays
- **`selectedChunks`**: Array chứa chunk nodes để sử dụng sau

#### 5. Chunk Relationships
```cypher
WITH *, 
     [c IN selectedChunks | 
       [p = (c)-[:NEXT_CHUNK|SIMILAR]-(other) 
       WHERE other IN selectedChunks | p]] AS chunkRels
```
- **`[c IN selectedChunks | ...]`**: List comprehension cho từng chunk
- **`(c)-[:NEXT_CHUNK|SIMILAR]-(other)`**: Tìm relationships:
  - `NEXT_CHUNK`: Sequential chunk relationships
  - `SIMILAR`: Similarity relationships
- **`WHERE other IN selectedChunks`**: Chỉ lấy relationships trong selected chunks
- **`chunkRels`**: Array chứa chunk relationship paths

#### 6. Entity and Entity Relationships (🚶‍♂️ **GRAPH TRAVERSAL #1**)
```cypher
CALL {{
  WITH selectedChunks
  UNWIND selectedChunks AS c
  OPTIONAL MATCH entities = (c:Chunk)-[:HAS_ENTITY]->(e)
  OPTIONAL MATCH entityRels = (e)--(e2:!Chunk) 
  WHERE exists {{
    (e2)<-[:HAS_ENTITY]-(other) WHERE other IN selectedChunks
  }}
  RETURN entities, entityRels, collect(DISTINCT e) AS entity
}}
```
**🔍 Graph Traversal Logic:**
- **`UNWIND selectedChunks AS c`**: Expand array thành individual rows
- **`(c:Chunk)-[:HAS_ENTITY]->(e)`**: **Traversal step 1**: Từ chunks → entities
- **`(e)--(e2:!Chunk)`**: **Traversal step 2**: Từ entities → connected entities
  - `--`: Undirected relationship (both directions)
  - `!Chunk`: Exclude Chunk nodes để tránh back-tracking
- **`WHERE exists {{ ... }}`**: Filter entities trong selected scope
- **`collect(DISTINCT e) AS entity`**: Aggregate distinct entities

**📍 Traversal Pattern**: `Chunk → Entity → Connected_Entity`

#### 7. Community Detection (🚶‍♂️ **GRAPH TRAVERSAL #2**)
```cypher
CALL {{
  With entity
  UNWIND entity AS n
  OPTIONAL MATCH community = (n:__Entity__)-[:IN_COMMUNITY]->(p:__Community__)
  OPTIONAL MATCH parentcommunity = (p)-[:PARENT_COMMUNITY*]->(p2:__Community__) 
  RETURN collect(community) AS communities, 
         collect(parentcommunity) AS parentCommunities
}}
```
**🔍 Graph Traversal Logic:**
- **`(n:__Entity__)-[:IN_COMMUNITY]->(p:__Community__)`**: **Traversal step 1**: Entity → Base Community
- **`(p)-[:PARENT_COMMUNITY*]->(p2:__Community__)`**: **Traversal step 2**: Community → Parent Communities
  - `*`: **Variable length path** - traverses multiple levels
  - **Multi-hop traversal**: Base → Parent → Grandparent → Great-grandparent communities
- **Community hierarchy traversal**: Follows hierarchical structure

**📍 Traversal Pattern**: `Entity → Community → Parent_Community → Grandparent_Community → ...`

#### 8. Path Flattening
```cypher
WITH apoc.coll.flatten(docs + chunks + chunkRels + entities + entityRels + communities + parentCommunities, true) AS paths
```
- **`apoc.coll.flatten(..., true)`**: Flatten nested arrays into single array
- **`true`**: Deep flatten (recursive)
- **`paths`**: Combined array of all graph paths

#### 9. Node Extraction
```cypher
CALL {{
  WITH paths 
  UNWIND paths AS path 
  UNWIND nodes(path) AS node 
  WITH distinct node 
  RETURN collect(node) AS nodes 
}}
```
- **`UNWIND paths AS path`**: Expand paths array
- **`UNWIND nodes(path) AS node`**: Extract all nodes from each path
- **`WITH distinct node`**: Remove duplicate nodes
- **`collect(node) AS nodes`**: Aggregate unique nodes

#### 10. Relationship Extraction
```cypher
CALL {{
  WITH paths 
  UNWIND paths AS path 
  UNWIND relationships(path) AS rel 
  RETURN collect(distinct rel) AS rels 
}}  
```
- **`relationships(path)`**: Extract relationships from path
- **`collect(distinct rel)`**: Aggregate unique relationships

#### 11. Final Return
```cypher
RETURN nodes, rels
```
- **Return**: Final nodes và relationships cho graph visualization

---

## 📋 **CHUNK QUERY**

```python
CHUNK_QUERY = """
MATCH (chunk:Chunk)
WHERE chunk.id IN $chunksIds
MATCH (chunk)-[:PART_OF]->(d:Document)
```

**Giải thích:**

#### 1. Chunk Selection
```cypher
MATCH (chunk:Chunk)
WHERE chunk.id IN $chunksIds
```
- **Purpose**: Tìm specific chunks theo IDs
- **`$chunksIds`**: Array of chunk IDs từ client

#### 2. Document Association
```cypher
MATCH (chunk)-[:PART_OF]->(d:Document)
```
- **Purpose**: Tìm document chứa chunks
- **`PART_OF`**: Relationship từ chunk to document

#### 3. Data Aggregation
```cypher
WITH d, 
     collect(distinct chunk) AS chunks
```
- **Purpose**: Group chunks theo document

#### 4. Related Data Collection
```cypher
WITH d, chunks, 
     collect {
         MATCH ()-[r]->() 
         WHERE elementId(r) IN $relationshipIds
         RETURN r
     } AS rels,
     collect {
         MATCH (e) 
         WHERE elementId(e) IN $entityIds
         RETURN e
     } AS nodes
```
- **`elementId(r) IN $relationshipIds`**: Tìm specific relationships
- **`elementId(e) IN $entityIds`**: Tìm specific entities
- **Purpose**: Lấy related data cho chunk details

#### 5. Data Formatting
```cypher
RETURN 
    d AS doc, 
    [chunk IN chunks | 
        chunk {.*, embedding: null, element_id: elementId(chunk)}
    ] AS chunks,
```
- **`chunk {.*}`**: All chunk properties
- **`embedding: null`**: Remove embedding data (too large)
- **`elementId(chunk)`**: Neo4j internal element ID

---

## 📊 **COUNT QUERIES**

### Chunk Count Query
```python
COUNT_CHUNKS_QUERY = """
MATCH (d:Document {fileName: $file_name})<-[:PART_OF]-(c:Chunk)
RETURN count(c) AS total_chunks
"""
```

**Giải thích:**
- **Purpose**: Đếm số chunks trong một document
- **`{fileName: $file_name}`**: Filter theo filename
- **`count(c)`**: Đếm chunk nodes

### Chunk Text Query
```python
CHUNK_TEXT_QUERY = """
MATCH (d:Document {fileName: $file_name})<-[:PART_OF]-(c:Chunk)
RETURN c.text AS chunk_text, c.position AS chunk_position, c.page_number AS page_number
ORDER BY c.position
SKIP $skip
LIMIT $limit
"""
```

**Giải thích:**
- **Purpose**: Lấy text content của chunks với pagination
- **`ORDER BY c.position`**: Sắp xếp theo vị trí trong document
- **`SKIP $skip`**: Pagination offset
- **`LIMIT $limit`**: Pagination limit

---

## 📈 **NODE/RELATIONSHIP COUNT QUERIES**

### With Community Query
```python
NODEREL_COUNT_QUERY_WITH_COMMUNITY = """
MATCH (d:Document)
WHERE d.fileName IS NOT NULL
OPTIONAL MATCH (d)<-[po:PART_OF]-(c:Chunk)
OPTIONAL MATCH (c)-[he:HAS_ENTITY]->(e:__Entity__)
OPTIONAL MATCH (c)-[sim:SIMILAR]->(c2:Chunk)
OPTIONAL MATCH (c)-[nc:NEXT_CHUNK]->(c3:Chunk)
OPTIONAL MATCH (e)-[ic:IN_COMMUNITY]->(comm:__Community__)
OPTIONAL MATCH (comm)-[pc1:PARENT_COMMUNITY]->(first_level:__Community__)
OPTIONAL MATCH (first_level)-[pc2:PARENT_COMMUNITY]->(second_level:__Community__)
OPTIONAL MATCH (second_level)-[pc3:PARENT_COMMUNITY]->(third_level:__Community__)
```

**Giải thích từng OPTIONAL MATCH:**

1. **`(d)<-[po:PART_OF]-(c:Chunk)`**: Document-Chunk relationships
2. **`(c)-[he:HAS_ENTITY]->(e:__Entity__)`**: Chunk-Entity relationships
3. **`(c)-[sim:SIMILAR]->(c2:Chunk)`**: Chunk similarity relationships
4. **`(c)-[nc:NEXT_CHUNK]->(c3:Chunk)`**: Sequential chunk relationships
5. **`(e)-[ic:IN_COMMUNITY]->(comm:__Community__)`**: Entity-Community relationships
6. **`(comm)-[pc1:PARENT_COMMUNITY]->(first_level:__Community__)`**: Community hierarchy level 1
7. **`(first_level)-[pc2:PARENT_COMMUNITY]->(second_level:__Community__)`**: Community hierarchy level 2
8. **`(second_level)-[pc3:PARENT_COMMUNITY]->(third_level:__Community__)`**: Community hierarchy level 3

#### Counting Logic
```cypher
WITH
  d.fileName AS filename,
  count(DISTINCT c) AS chunkNodeCount,
  count(DISTINCT po) AS partOfRelCount,
  count(DISTINCT he) AS hasEntityRelCount,
  count(DISTINCT sim) AS similarRelCount,
  count(DISTINCT nc) AS nextChunkRelCount,
  count(DISTINCT e) AS entityNodeCount,
  collect(DISTINCT e) AS entities,
  count(DISTINCT comm) AS baseCommunityCount,
  count(DISTINCT first_level) AS firstlevelcommCount,
  count(DISTINCT second_level) AS secondlevelcommCount,
  count(DISTINCT third_level) AS thirdlevelcommCount,
  count(DISTINCT ic) AS inCommunityCount,
  count(DISTINCT pc1) AS parentCommunityRelCount1,
  count(DISTINCT pc2) AS parentCommunityRelCount2,
  count(DISTINCT pc3) AS parentCommunityRelCount3
```

**Purpose**: Đếm tất cả nodes và relationships cho statistics dashboard

---

## 💬 **CHAT SYSTEM CONFIGURATIONS**

### Basic Chat Settings
```python
CHAT_MAX_TOKENS = 1000
CHAT_SEARCH_KWARG_SCORE_THRESHOLD = 0.5
CHAT_DOC_SPLIT_SIZE = 3000
CHAT_EMBEDDING_FILTER_SCORE_THRESHOLD = 0.10
```

**Giải thích:**
- **`CHAT_MAX_TOKENS`**: Maximum tokens cho chat responses (1000 tokens)
- **`CHAT_SEARCH_KWARG_SCORE_THRESHOLD`**: Minimum score cho search results (0.5)
- **`CHAT_DOC_SPLIT_SIZE`**: Document chunk size cho processing (3000 characters)
- **`CHAT_EMBEDDING_FILTER_SCORE_THRESHOLD`**: Minimum embedding similarity (0.10)

### Token Cut-off Configuration
```python
CHAT_TOKEN_CUT_OFF = {
     ('openai_gpt_3.5','azure_ai_gpt_35',"gemini_1.0_pro","gemini_1.5_pro", "gemini_1.5_flash","groq-llama3",'groq_llama3_70b','anthropic_claude_3_5_sonnet','fireworks_llama_v3_70b','bedrock_claude_3_5_sonnet', ) : 4, 
     ("openai-gpt-4","diffbot" ,'azure_ai_gpt_4o',"openai_gpt_4o", "openai_gpt_4o_mini") : 28,
     ("ollama_llama3") : 2  
}
```

**Giải thích:**
- **Dictionary mapping**: Model names → Token cut-off ratios
- **Ratio 4**: Smaller models get less context (4x cut-off)
- **Ratio 28**: Larger models get more context (28x cut-off)
- **Ratio 2**: Local models get minimal context (2x cut-off)

---

## 🤖 **CHAT SYSTEM TEMPLATE**

```python
CHAT_SYSTEM_TEMPLATE = """
You are an AI-powered question-answering agent. Your task is to provide accurate and comprehensive responses to user queries based on the given context, chat history, and available resources.

### Response Guidelines:
1. **Direct Answers**: Provide clear and thorough answers to the user's queries without headers unless requested. Avoid speculative responses.
2. **Utilize History and Context**: Leverage relevant information from previous interactions, the current user input, and the context provided below.
3. **No Greetings in Follow-ups**: Start with a greeting in initial interactions. Avoid greetings in subsequent responses unless there's a significant break or the chat restarts.
4. **Admit Unknowns**: Clearly state if an answer is unknown. Avoid making unsupported statements.
5. **Avoid Hallucination**: Only provide information based on the context provided. Do not invent information.
6. **Response Length**: Keep responses concise and relevant. Aim for clarity and completeness within 4-5 sentences unless more detail is requested.
7. **Tone and Style**: Maintain a professional and informative tone. Be friendly and approachable.
8. **Error Handling**: If a query is ambiguous or unclear, ask for clarification rather than providing a potentially incorrect answer.
9. **Fallback Options**: If the required information is not available in the provided context, provide a polite and helpful response. Example: "I don't have that information right now." or "I'm sorry, but I don't have that information. Is there something else I can help with?"
10. **Context Availability**: If the context is empty, do not provide answers based solely on internal knowledge. Instead, respond appropriately by indicating the lack of information.


**IMPORTANT** : DO NOT ANSWER FROM YOUR KNOWLEDGE BASE USE THE BELOW CONTEXT

### Context:
<context>
{context}
</context>
```

**Purpose**: System prompt template cho AI chat agent với strict guidelines về:
- **Context-only responses**: Không sử dụng knowledge base riêng
- **Conversation flow**: Greeting patterns và follow-up behavior
- **Error handling**: Cách xử lý unknown queries
- **Response format**: Length và style guidelines

### Question Transform Template
```python
QUESTION_TRANSFORM_TEMPLATE = "Given the below conversation, generate a search query to look up in order to get information relevant to the conversation. Only respond with the query, nothing else."
```

**Purpose**: Template để transform conversation thành search queries cho retrieval

---

## 🔍 **VECTOR SEARCH CONFIGURATION**

### Basic Vector Search
```python
VECTOR_SEARCH_TOP_K = 5

VECTOR_SEARCH_QUERY = """
WITH node AS chunk, score
MATCH (chunk)-[:PART_OF]->(d:Document)
WITH d, 
     collect(distinct {chunk: chunk, score: score}) AS chunks, 
     avg(score) AS avg_score

WITH d, avg_score, 
     [c IN chunks | c.chunk.text] AS texts, 
     [c IN chunks | {id: c.chunk.id, score: c.score}] AS chunkdetails

WITH d, avg_score, chunkdetails, 
     apoc.text.join(texts, "\n----\n") AS text

RETURN text, 
       avg_score AS score, 
       {source: COALESCE(CASE WHEN d.url CONTAINS "None" 
                             THEN d.fileName 
                             ELSE d.url 
                       END, 
                       d.fileName), 
        chunkdetails: chunkdetails} AS metadata
"""
```

**Giải thích Vector Search Query:**

#### 1. Input Processing
```cypher
WITH node AS chunk, score
```
- **Input**: Vector search results từ Neo4j vector index
- **`node`**: Chunk node from vector search
- **`score`**: Similarity score

#### 2. Document Association
```cypher
MATCH (chunk)-[:PART_OF]->(d:Document)
```
- **Purpose**: Tìm document chứa chunk

#### 3. Chunk Aggregation
```cypher
WITH d, 
     collect(distinct {chunk: chunk, score: score}) AS chunks, 
     avg(score) AS avg_score
```
- **Purpose**: Group chunks theo document
- **`avg(score)`**: Average similarity score cho document

#### 4. Text Extraction
```cypher
WITH d, avg_score, 
     [c IN chunks | c.chunk.text] AS texts, 
     [c IN chunks | {id: c.chunk.id, score: c.score}] AS chunkdetails
```
- **`[c IN chunks | c.chunk.text]`**: Extract text từ chunks
- **`chunkdetails`**: Metadata với IDs và scores

#### 5. Text Joining
```cypher
WITH d, avg_score, chunkdetails, 
     apoc.text.join(texts, "\n----\n") AS text
```
- **`apoc.text.join(..., "\n----\n")`**: Join texts với separator
- **Purpose**: Combine multiple chunks thành single text

#### 6. Metadata Creation
```cypher
RETURN text, 
       avg_score AS score, 
       {source: COALESCE(CASE WHEN d.url CONTAINS "None" 
                             THEN d.fileName 
                             ELSE d.url 
                       END, 
                       d.fileName), 
        chunkdetails: chunkdetails} AS metadata
```
- **`COALESCE(...)`**: Fallback logic cho source field
- **Source priority**: URL → fileName fallback
- **Metadata**: Source information và chunk details

---

## 🧠 **VECTOR GRAPH SEARCH (GraphRAG Core)**

### Configuration Parameters
```python
VECTOR_GRAPH_SEARCH_ENTITY_LIMIT = 40
VECTOR_GRAPH_SEARCH_EMBEDDING_MIN_MATCH = 0.3
VECTOR_GRAPH_SEARCH_EMBEDDING_MAX_MATCH = 0.9
VECTOR_GRAPH_SEARCH_ENTITY_LIMIT_MINMAX_CASE = 20
VECTOR_GRAPH_SEARCH_ENTITY_LIMIT_MAX_CASE = 40
```

**Giải thích Parameters:**
    - **`ENTITY_LIMIT = 40`**: Maximum entities per search (performance limit)
    - **`EMBEDDING_MIN_MATCH = 0.3`**: Minimum embedding similarity (30%)
    - **`EMBEDDING_MAX_MATCH = 0.9`**: High similarity threshold (90%)
    - **`ENTITY_LIMIT_MINMAX_CASE = 20`**: Entities for medium similarity (20)
    - **`ENTITY_LIMIT_MAX_CASE = 40`**: Entities for high similarity (40)

### Query Prefix
```python
VECTOR_GRAPH_SEARCH_QUERY_PREFIX = """
WITH node as chunk, score
// find the document of the chunk
MATCH (chunk)-[:PART_OF]->(d:Document)
// aggregate chunk-details
WITH d, collect(DISTINCT {chunk: chunk, score: score}) AS chunks, avg(score) as avg_score
// fetch entities
CALL { WITH chunks
UNWIND chunks as chunkScore
WITH chunkScore.chunk as chunk
"""
```

**Purpose**: Setup phase cho Vector Graph Search
- **Document grouping**: Group chunks theo documents
- **Score aggregation**: Calculate average scores
- **Entity preparation**: Prepare cho entity expansion

### Core Entity Query (GraphRAG Logic)
```python
VECTOR_GRAPH_SEARCH_ENTITY_QUERY = """
    OPTIONAL MATCH (chunk)-[:HAS_ENTITY]->(e)
    WITH e, count(*) AS numChunks 
    ORDER BY numChunks DESC 
    LIMIT {no_of_entites}

    WITH 
    CASE 
        WHEN e.embedding IS NULL OR ({embedding_match_min} <= vector.similarity.cosine($query_vector, e.embedding) AND vector.similarity.cosine($query_vector, e.embedding) <= {embedding_match_max}) THEN 
            collect {{
                OPTIONAL MATCH path=(e)(()-[rels:!HAS_ENTITY&!PART_OF]-()){{0,1}}(:!Chunk&!Document&!__Community__) 
                RETURN path LIMIT {entity_limit_minmax_case}
            }}
        WHEN e.embedding IS NOT NULL AND vector.similarity.cosine($query_vector, e.embedding) >  {embedding_match_max} THEN
            collect {{
                OPTIONAL MATCH path=(e)(()-[rels:!HAS_ENTITY&!PART_OF]-()){{0,2}}(:!Chunk&!Document&!__Community__) 
                RETURN path LIMIT {entity_limit_max_case} 
            }} 
        ELSE 
            collect {{ 
                MATCH path=(e) 
                RETURN path 
            }}
    END AS paths, e
"""
```

**Giải thích Chi tiết GraphRAG Logic:**

#### 1. Entity Discovery
```cypher
OPTIONAL MATCH (chunk)-[:HAS_ENTITY]->(e)
WITH e, count(*) AS numChunks 
ORDER BY numChunks DESC 
LIMIT {no_of_entites}
```
- **Purpose**: Tìm entities liên quan đến chunks
- **`count(*) AS numChunks`**: Đếm chunks chứa entity
- **`ORDER BY numChunks DESC`**: Prioritize entities xuất hiện nhiều
- **`LIMIT {no_of_entites}`**: Giới hạn 40 entities

#### 2. Smart Graph Expansion (Core GraphRAG)
```cypher
CASE 
    WHEN e.embedding IS NULL OR ({embedding_match_min} <= vector.similarity.cosine($query_vector, e.embedding) AND vector.similarity.cosine($query_vector, e.embedding) <= {embedding_match_max}) THEN 
        // Medium similarity: 1-hop expansion with 20 limit
    WHEN e.embedding IS NOT NULL AND vector.similarity.cosine($query_vector, e.embedding) >  {embedding_match_max} THEN
        // High similarity: 2-hop expansion with 40 limit
    ELSE 
        // Low/No similarity: just the entity itself
END
```

**Expansion Strategy:**

### 2. **VECTOR GRAPH SEARCH - Core GraphRAG Traversal (🧠 Trái tim của Graph Traversal)**

**Case 1: Medium Similarity (0.3-0.9) - 1-HOP TRAVERSAL**
```cypher
collect {{
    OPTIONAL MATCH path=(e)(()-[rels:!HAS_ENTITY&!PART_OF]-()){{0,1}}(:!Chunk&!Document&!__Community__) 
    RETURN path LIMIT {entity_limit_minmax_case}
}}
```
**🔍 Graph Traversal Logic:**
- **`(e)(()-[rels:!HAS_ENTITY&!PART_OF]-()){{0,1}}`**: **1-hop graph traversal**
  - `{0,1}`: Traverses 0 to 1 relationship hops
  - `!HAS_ENTITY&!PART_OF`: Excludes system relationships
- **`:!Chunk&!Document&!__Community__`**: Excludes system nodes
- **`LIMIT 20`**: Limited expansion để control performance

**📍 Traversal Pattern**: `Starting_Entity → (1-hop) → Connected_Entity`

**Case 2: High Similarity (>0.9) - 2-HOP TRAVERSAL**
```cypher
collect {{
    OPTIONAL MATCH path=(e)(()-[rels:!HAS_ENTITY&!PART_OF]-()){{0,2}}(:!Chunk&!Document&!__Community__) 
    RETURN path LIMIT {entity_limit_max_case} 
}}
```
**🔍 Graph Traversal Logic:**
- **`{0,2}`**: **2-hop graph traversal** - Deeper exploration
  - Traverses: Entity → Connected_Entity → Second_Degree_Entity
- **Deeper graph exploration**: Khi similarity cao, system explores deeper
- **`LIMIT 40`**: More extensive expansion

**📍 Traversal Pattern**: `Starting_Entity → (1-hop) → Connected_Entity → (2-hop) → Second_Degree_Entity`

**Case 3: Low/No Similarity**
```cypher
collect {{ 
    MATCH path=(e) 
    RETURN path 
}}
```
- **Just the entity**: No expansion

### Query Suffix (Result Processing)
```python
VECTOR_GRAPH_SEARCH_QUERY_SUFFIX = """
   WITH apoc.coll.toSet(apoc.coll.flatten(collect(DISTINCT paths))) AS paths,
        collect(DISTINCT e) AS entities
   // De-duplicate nodes and relationships across chunks
   RETURN
       collect {
           UNWIND paths AS p
           UNWIND relationships(p) AS r
           RETURN DISTINCT r
       } AS rels,
       collect {
           UNWIND paths AS p
           UNWIND nodes(p) AS n
           RETURN DISTINCT n
       } AS nodes,
       entities
}
```

**Giải thích Result Processing:**

#### 1. Path Flattening
```cypher
WITH apoc.coll.toSet(apoc.coll.flatten(collect(DISTINCT paths))) AS paths,
     collect(DISTINCT e) AS entities
```
- **`apoc.coll.flatten`**: Flatten nested path arrays
- **`apoc.coll.toSet`**: Remove duplicates
- **Purpose**: Consolidate paths từ multiple entities

#### 2. Relationship Extraction
```cypher
collect {
    UNWIND paths AS p
    UNWIND relationships(p) AS r
    RETURN DISTINCT r
} AS rels
```
- **Purpose**: Extract all unique relationships từ paths

#### 3. Node Extraction
```cypher
collect {
    UNWIND paths AS p
    UNWIND nodes(p) AS n
    RETURN DISTINCT n
} AS nodes
```
- **Purpose**: Extract all unique nodes từ paths

### Text Generation and Metadata
```cypher
// Generate metadata and text components for chunks, nodes, and relationships
WITH d, avg_score,
    [c IN chunks | c.chunk.text] AS texts,
    [c IN chunks | {id: c.chunk.id, score: c.score}] AS chunkdetails,
    [n IN nodes | elementId(n)] AS entityIds,
    [r IN rels | elementId(r)] AS relIds,
    apoc.coll.sort([
        n IN nodes |
        coalesce(apoc.coll.removeAll(labels(n), ['__Entity__'])[0], "") + ":" +
        coalesce(
            n.id,
            n[head([k IN keys(n) WHERE k =~ "(?i)(name|title|id|description)$"])],
            ""
        ) +
        (CASE WHEN n.description IS NOT NULL THEN " (" + n.description + ")" ELSE "" END)
    ]) AS nodeTexts,
    apoc.coll.sort([
        r IN rels |
        coalesce(apoc.coll.removeAll(labels(startNode(r)), ['__Entity__'])[0], "") + ":" +
        coalesce(
            startNode(r).id,
            startNode(r)[head([k IN keys(startNode(r)) WHERE k =~ "(?i)(name|title|id|description)$"])],
            ""
        ) + " " + type(r) + " " +
        coalesce(apoc.coll.removeAll(labels(endNode(r)), ['__Entity__'])[0], "") + ":" +
        coalesce(
            endNode(r).id,
            endNode(r)[head([k IN keys(endNode(r)) WHERE k =~ "(?i)(name|title|id|description)$"])],
            ""
        )
    ]) AS relTexts,
    entities
```

**Text Generation Logic:**

#### 1. Node Text Generation
```cypher
coalesce(apoc.coll.removeAll(labels(n), ['__Entity__'])[0], "") + ":" +
coalesce(
    n.id,
    n[head([k IN keys(n) WHERE k =~ "(?i)(name|title|id|description)$"])],
    ""
) +
(CASE WHEN n.description IS NOT NULL THEN " (" + n.description + ")" ELSE "" END)
```
- **Label extraction**: Remove `__Entity__`, get first real label
- **Property priority**: `id` → `name` → `title` → `description`
- **Format**: `Label:PropertyValue (description)`

#### 2. Relationship Text Generation
```cypher
startNode + " " + type(r) + " " + endNode
```
- **Format**: `StartNode RELATIONSHIP_TYPE EndNode`
- **Purpose**: Human-readable relationship description

#### 3. Final Text Assembly
```cypher
WITH d, avg_score, chunkdetails, entityIds, relIds,
    "Text Content:\n" + apoc.text.join(texts, "\n----\n") +
    "\n----\nEntities:\n" + apoc.text.join(nodeTexts, "\n") +
    "\n----\nRelationships:\n" + apoc.text.join(relTexts, "\n") AS text,
    entities
```

**Final Format:**
```
Text Content:
[chunk texts separated by ----]
----
Entities:
[entity descriptions]
----
Relationships:
[relationship descriptions]
```

### Complete Query Assembly
```python
VECTOR_GRAPH_SEARCH_QUERY = VECTOR_GRAPH_SEARCH_QUERY_PREFIX + VECTOR_GRAPH_SEARCH_ENTITY_QUERY.format(
    no_of_entites=VECTOR_GRAPH_SEARCH_ENTITY_LIMIT,
    embedding_match_min=VECTOR_GRAPH_SEARCH_EMBEDDING_MIN_MATCH,
    embedding_match_max=VECTOR_GRAPH_SEARCH_EMBEDDING_MAX_MATCH,
    entity_limit_minmax_case=VECTOR_GRAPH_SEARCH_ENTITY_LIMIT_MINMAX_CASE,
    entity_limit_max_case=VECTOR_GRAPH_SEARCH_ENTITY_LIMIT_MAX_CASE
) + VECTOR_GRAPH_SEARCH_QUERY_SUFFIX
```

**Purpose**: Assemble complete GraphRAG query với parameter substitution

---

## 🏘️ **LOCAL COMMUNITY SEARCH**

### Configuration
```python
LOCAL_COMMUNITY_TOP_K = 10
LOCAL_COMMUNITY_TOP_CHUNKS = 3
LOCAL_COMMUNITY_TOP_COMMUNITIES = 3
LOCAL_COMMUNITY_TOP_OUTSIDE_RELS = 10
```

**Parameters:**
- **`TOP_K = 10`**: Top 10 results cho entity search
- **`TOP_CHUNKS = 3`**: Top 3 related chunks
- **`TOP_COMMUNITIES = 3`**: Top 3 communities
- **`TOP_OUTSIDE_RELS = 10`**: Top 10 outside relationships

### Local Community Query
```python
LOCAL_COMMUNITY_SEARCH_QUERY = """
WITH collect(node) AS nodes, 
     avg(score) AS score, 
     collect({{entityids: elementId(node), score: score}}) AS metadata

WITH score, nodes, metadata,

     collect {{
         UNWIND nodes AS n
         MATCH (n)<-[:HAS_ENTITY]->(c:Chunk)
         WITH c, count(distinct n) AS freq
         RETURN c
         ORDER BY freq DESC
         LIMIT {topChunks}
     }} AS chunks,

     collect {{
         UNWIND nodes AS n
         OPTIONAL MATCH (n)-[:IN_COMMUNITY]->(c:__Community__)
         WITH c, c.community_rank AS rank, c.weight AS weight
         RETURN c
         ORDER BY rank, weight DESC
         LIMIT {topCommunities}
     }} AS communities,

     collect {{
         UNWIND nodes AS n
         UNWIND nodes AS m
         MATCH (n)-[r]->(m)
         RETURN DISTINCT r
         // TODO: need to add limit
     }} AS rels,

     collect {{
         UNWIND nodes AS n
         MATCH path = (n)-[r]-(m:__Entity__)
         WHERE NOT m IN nodes
         WITH m, collect(distinct r) AS rels, count(*) AS freq
         ORDER BY freq DESC 
         LIMIT {topOutsideRels}
         WITH collect(m) AS outsideNodes, apoc.coll.flatten(collect(rels)) AS rels
         RETURN {{ nodes: outsideNodes, rels: rels }}
     }} AS outside
"""
```

**Giải thích Local Community Logic:**

#### 1. Input Processing
```cypher
WITH collect(node) AS nodes, 
     avg(score) AS score, 
     collect({{entityids: elementId(node), score: score}}) AS metadata
```
- **Input**: Entity nodes từ vector search
- **Aggregation**: Collect nodes và scores

#### 2. Related Chunks Discovery
```cypher
collect {{
    UNWIND nodes AS n
    MATCH (n)<-[:HAS_ENTITY]->(c:Chunk)
    WITH c, count(distinct n) AS freq
    RETURN c
    ORDER BY freq DESC
    LIMIT {topChunks}
}} AS chunks
```
- **Purpose**: Tìm chunks chứa entities
- **`count(distinct n) AS freq`**: Đếm entities per chunk
- **`ORDER BY freq DESC`**: Prioritize chunks với nhiều entities
- **`LIMIT 3`**: Top 3 most relevant chunks

#### 3. Community Discovery
```cypher
collect {{
    UNWIND nodes AS n
    OPTIONAL MATCH (n)-[:IN_COMMUNITY]->(c:__Community__)
    WITH c, c.community_rank AS rank, c.weight AS weight
    RETURN c
    ORDER BY rank, weight DESC
    LIMIT {topCommunities}
}} AS communities
```
- **Purpose**: Tìm communities chứa entities
- **Ranking**: `community_rank` và `weight`
- **`LIMIT 3`**: Top 3 communities

#### 4. Internal Relationships
```cypher
collect {{
    UNWIND nodes AS n
    UNWIND nodes AS m
    MATCH (n)-[r]->(m)
    RETURN DISTINCT r
}} AS rels
```
- **Purpose**: Relationships between selected entities

#### 5. Outside Relationships
```cypher
collect {{
    UNWIND nodes AS n
    MATCH path = (n)-[r]-(m:__Entity__)
    WHERE NOT m IN nodes
    WITH m, collect(distinct r) AS rels, count(*) AS freq
    ORDER BY freq DESC 
    LIMIT {topOutsideRels}
    WITH collect(m) AS outsideNodes, apoc.coll.flatten(collect(rels)) AS rels
    RETURN {{ nodes: outsideNodes, rels: rels }}
}} AS outside
```
- **Purpose**: Tìm entities bên ngoài selected set
- **`WHERE NOT m IN nodes`**: Exclude selected entities
- **Ranking**: Frequency of connections
- **`LIMIT 10`**: Top 10 outside relationships

---

## 🚶‍♂️ **GRAPH TRAVERSAL PATTERNS SUMMARY**

### 🎯 **Các Pattern Graph Traversal trong System:**

#### **1. Main Graph Query Traversals:**
- **Chunk → Entity**: `(c:Chunk)-[:HAS_ENTITY]->(e)`
- **Entity → Connected Entity**: `(e)--(e2:!Chunk)`
- **Entity → Community**: `(n:__Entity__)-[:IN_COMMUNITY]->(p:__Community__)`
- **Community Hierarchy**: `(p)-[:PARENT_COMMUNITY*]->(p2:__Community__)` (Multi-hop)

#### **2. Vector Graph Search (GraphRAG) Traversals:**
- **1-hop Traversal**: `{0,1}` - Direct neighbors only
- **2-hop Traversal**: `{0,2}` - Second-degree connections
- **Smart Expansion**: Depth depends on similarity score

#### **3. Local Community Traversals:**
- **Entity → Chunk**: `(n)<-[:HAS_ENTITY]->(c:Chunk)`
- **Entity → Community**: `(n)-[:IN_COMMUNITY]->(c:__Community__)`
- **Internal Entity Relations**: `(n)-[r]->(m)` where both n,m in selected set
- **External Entity Relations**: `(n)-[r]-(m:__Entity__)` where m NOT in selected set

#### **4. Specialized Traversal Features:**
- **Variable Length Paths**: `*` cho community hierarchies
- **Filtered Traversals**: `!HAS_ENTITY&!PART_OF` để exclude system relationships
- **Bidirectional Traversals**: `--` và `-[r]-` cho undirected exploration
- **Depth-Limited Traversals**: `{0,1}` và `{0,2}` cho performance control

### 🎭 **Chat Mode "graph" - Pure Graph Traversal:**
```python
CHAT_GRAPH_MODE = "graph"
```
- **Mode này sử dụng pure graph traversal** không kết hợp vector search
- **Traverses graph structure** based on relationships only
- **Use case**: Khi muốn explore connections without semantic similarity

---

## 🎬 **YOUTUBE & UTILITY CONFIGURATIONS**

### YouTube Processing
```python
YOUTUBE_CHUNK_SIZE_SECONDS = 60
```
- **Purpose**: Split YouTube videos thành 60-second chunks

### Utility Queries
```python
QUERY_TO_GET_CHUNKS = """
            MATCH (d:Document)
            WHERE d.fileName = $filename
            WITH d
            OPTIONAL MATCH (d)<-[:PART_OF|FIRST_CHUNK]-(c:Chunk)
            RETURN c.id as id, c.text as text, c.position as position 
            """
            
QUERY_TO_DELETE_EXISTING_ENTITIES = """
                                MATCH (d:Document {fileName:$filename})
                                WITH d
                                MATCH (d)<-[:PART_OF]-(c:Chunk)
                                WITH d,c
                                MATCH (c)-[:HAS_ENTITY]->(e)
                                WHERE NOT EXISTS { (e)<-[:HAS_ENTITY]-()<-[:PART_OF]-(d2:Document) }
                                DETACH DELETE e
                                """
```

**Utility Purposes:**
- **`QUERY_TO_GET_CHUNKS`**: Get all chunks for a document
- **`QUERY_TO_DELETE_EXISTING_ENTITIES`**: Clean up entities before reprocessing

---

## 🎯 **SUMMARY**

**File `constants.py` là trung tâm của LLM Graph Builder system**, chứa:

### 🔑 **Key Components:**
1. **Model Configurations**: OpenAI, Gemini, Groq models
2. **Graph Queries**: Complex Cypher queries cho visualization
3. **GraphRAG Implementation**: Sophisticated vector+graph hybrid search
4. **Chat System**: Multiple modes từ simple vector đến full GraphRAG
5. **Community Detection**: Local và global search capabilities
6. **Performance Optimization**: Configurable limits và thresholds

### 🚀 **GraphRAG Highlights:**
- **Smart Expansion**: Dynamic graph traversal based on similarity
- **Multi-level Search**: Chunk → Entity → Community hierarchy
- **Hybrid Scoring**: Vector + Graph + Fulltext combination
- **Context Assembly**: Intelligent text generation từ graph data

### 🎭 **Chat Mode Sophistication:**
- **7 different modes**: Từ simple vector đến complex GraphRAG
- **Default mode**: `graph_vector_fulltext` (full GraphRAG)
- **Configurable parameters**: Tailored cho từng use case
- **Performance optimized**: Với appropriate limits và filters

**Overall**: File này thể hiện một implementation rất sophisticated của GraphRAG system với multiple search strategies và intelligent context assembly.
