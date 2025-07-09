# 📋 LLM Graph Builder - Complete Processing Workflow Documentation

## 🔍 **OVERVIEW**
This document provides a comprehensive overview of the LLM Graph Builder processing workflow, showing the exact sequence of operations, data flow, and timing for each step.

## 🚀 **MAIN PROCESSING PIPELINE**

### **📊 ENTRY POINT: `processing_source()` Function**
**Location**: `backend/src/main.py` (Line ~279)  
**Purpose**: Main orchestrator for document processing pipeline

---

## 📋 **STEP-BY-STEP PROCESSING WORKFLOW**

### **🔥 STEP 1: Process Initialization**
**Function**: `process_logger.start_process()`
- **Input**: `file_name`, `model`, `source_type`
- **Output**: Logging system initialization
- **Data**: Process metadata, timestamps
- **Code Location**: Line ~297

### **🔗 STEP 2: Database Connection Setup**
**Function**: `create_graph_database_connection()`
- **Input**: `uri`, `userName`, `password`, `database`
- **Output**: `Neo4jGraph` connection object
- **Data**: Connection time, graph object type
- **Code Location**: Line ~315
- **Processing Time**: ~0.1-0.5 seconds

### **📊 STEP 3: Data Access Layer Initialization**
**Function**: `graphDBdataAccess(graph)`
- **Input**: Graph connection object
- **Output**: Database access layer instance
- **Data**: Data access object type
- **Code Location**: Line ~332

### **🔍 STEP 4: Vector Index Creation**
**Function**: `create_chunk_vector_index(graph)`
- **Input**: Graph connection
- **Output**: Vector index for similarity search
- **Data**: Index type, purpose
- **Code Location**: Line ~343

### **📄 STEP 5: Document Chunking Process**
**Function**: `get_chunkId_chunkDoc_list()`
- **Input**: 
  - `graph`: Neo4j connection
  - `file_name`: Document name
  - `pages`: Document pages
  - `token_chunk_size`: Chunk size limit
  - `chunk_overlap`: Overlap between chunks
- **Output**: 
  - `total_chunks`: Number of chunks created
  - `chunkId_chunkDoc_list`: List of chunk objects
- **Data**: Chunking parameters, chunk count, processing time
- **Code Location**: Line ~355
- **Processing Time**: ~1-10 seconds (depends on document size)

### **📊 STEP 6: Document Status Check**
**Function**: `get_current_status_document_node()`
- **Input**: `file_name`
- **Output**: Document processing status
- **Data**: Current status, processed chunks, node/relationship counts
- **Code Location**: Line ~376
- **Processing Time**: ~0.1-0.3 seconds

### **🔄 STEP 7: Status Update to Processing**
**Function**: `update_source_node()`
- **Input**: `sourceNode` object with status = "Processing"
- **Output**: Updated document node
- **Data**: Status change, retry configuration
- **Code Location**: Line ~398

### **🔄 STEP 8: Batch Processing Configuration**
**Environment Variable**: `UPDATE_GRAPH_CHUNKS_PROCESSED`
- **Input**: Environment configuration
- **Output**: Batch size for processing
- **Data**: Chunks per batch, expected batches
- **Code Location**: Line ~431

### **🔄 STEP 9-12: Main Processing Loop**
**Function**: `processing_chunks()` (called in loop)
- **Input**: 
  - `selected_chunks`: Batch of chunks to process
  - `graph`: Database connection
  - `model`: LLM model name
  - `allowedNodes`: Allowed entity types
  - `allowedRelationship`: Allowed relationship types
- **Output**: 
  - `node_count`: Updated node count
  - `rel_count`: Updated relationship count
  - `latency_processed_chunk`: Processing metrics
- **Processing Time**: ~10-60 seconds per batch

---

## 🤖 **CHUNK PROCESSING PIPELINE (`processing_chunks()` Function)**

### **🔗 STEP A: Initialize Chunk Processing**
- **Input**: Chunk list, database connection, model parameters
- **Output**: Processing initialization
- **Code Location**: Line ~620

### **🔗 STEP B: Database Connection Check**
- **Input**: Current graph connection
- **Output**: Valid database connection
- **Data**: Connection status, reconnection if needed
- **Code Location**: Line ~638

### **🔍 STEP C: Embedding Creation**
**Function**: `create_chunk_embeddings()`
- **Input**: Graph, chunk list, file name
- **Output**: Vector embeddings for chunks
- **Data**: Embedding time, chunks processed
- **Code Location**: Line ~658
- **Processing Time**: ~2-5 seconds per batch

### **🤖 STEP D: LLM Entity Extraction**
**Function**: `get_graph_from_llm()`
- **Input**: 
  - `model`: LLM model (Gemini, OpenAI, etc.)
  - `chunkId_chunkDoc_list`: Chunks to process
  - `allowedNodes`: Entity types allowed
  - `allowedRelationship`: Relationship types allowed
  - `chunks_to_combine`: Chunk combination strategy
- **Output**: `graph_documents` with entities and relationships
- **Data**: Entities extracted, relationships found
- **Code Location**: Line ~680
- **Processing Time**: ~5-30 seconds (depends on LLM speed)

### **🧹 STEP E: Data Cleaning**
**Function**: `handle_backticks_nodes_relationship_id_type()`
- **Input**: Raw graph documents
- **Output**: Cleaned graph documents
- **Data**: Cleaning operations applied
- **Code Location**: Line ~704

### **💾 STEP F: Save to Neo4j**
**Function**: `save_graphDocuments_in_neo4j()`
- **Input**: Graph connection, cleaned documents
- **Output**: Entities and relationships saved to database
- **Data**: Save time, documents saved
- **Code Location**: Line ~722
- **Processing Time**: ~1-5 seconds

### **🔗 STEP G: Chunk-Entity Relationship Creation**
**Function**: `merge_relationship_between_chunk_and_entites()`
- **Input**: Graph, chunk-entity mappings
- **Output**: HAS_ENTITY relationships created
- **Data**: Relationships created
- **Code Location**: Line ~750
- **Processing Time**: ~1-3 seconds

### **📊 STEP H: Count Updates**
**Function**: `update_node_relationship_count()`
- **Input**: File name
- **Output**: Updated node and relationship counts
- **Data**: Final counts
- **Code Location**: Line ~773

---

## 📊 **DATA FLOW SUMMARY**

### **INPUT DATA**:
```
Document File → Pages → Chunks → LLM Processing → Entities & Relationships → Neo4j Graph
```

### **OUTPUT DATA**:
```json
{
  "fileName": "document.pdf",
  "nodeCount": 150,
  "relationshipCount": 200,
  "total_processing_time": 45.67,
  "status": "Completed",
  "model": "gemini-1.5-flash",
  "success_count": 1
}
```

---

## ⏱️ **TIMING BREAKDOWN**

### **Typical Processing Times**:
1. **Database Connection**: 0.1-0.5s
2. **Document Chunking**: 1-10s (depends on document size)
3. **Status Check**: 0.1-0.3s
4. **Chunk Processing** (per batch):
   - Embedding Creation: 2-5s
   - LLM Entity Extraction: 5-30s
   - Data Cleaning: 0.1-0.5s
   - Neo4j Save: 1-5s
   - Relationship Creation: 1-3s
5. **Final Updates**: 0.5-1s

### **Total Processing Time**: 15 seconds - 10 minutes (depends on document size and complexity)

---

## 🔄 **PROCESSING SEQUENCE**

```
START → DB Connect → Chunking → Status Check → Batch Loop:
  ├── Embedding Creation
  ├── LLM Entity Extraction  
  ├── Data Cleaning
  ├── Neo4j Save
  ├── Relationship Creation
  └── Progress Update
→ Final Status Update → Cleanup → END
```

---

## 📈 **PERFORMANCE METRICS**

### **Key Metrics Tracked**:
- **Total Processing Time**: End-to-end processing duration
- **Chunks Processed**: Number of document chunks processed
- **Entities Extracted**: Number of entities identified by LLM
- **Relationships Created**: Number of relationships established
- **Node Count**: Final number of nodes in graph
- **Relationship Count**: Final number of relationships in graph
- **Per-entity Latency**: Average time per entity processed

### **Latency Data Structure**:
```json
{
  "create_connection": "0.12s",
  "create_list_chunk_and_document": "2.45s",
  "get_status_document_node": "0.08s",
  "update_source_node": "0.15s",
  "processed_combine_chunk_0-20": "15.67s",
  "processed_chunk_detail_0-20": {
    "update_embedding": "2.34s",
    "entity_extraction": "12.45s",
    "save_graphDocuments": "0.67s",
    "relationship_between_chunk_entity": "0.21s"
  },
  "Processed_source": "23.45s",
  "Per_entity_latency": "0.156s"
}
```

---

## 🎯 **CRITICAL SUCCESS FACTORS**

### **For Successful Processing**:
1. **Database Connection**: Must be stable throughout processing
2. **LLM Model**: Must be available and responsive
3. **Memory Management**: Efficient chunk processing to avoid memory issues
4. **Error Handling**: Robust error recovery for network/API issues
5. **Cancellation Support**: Ability to stop processing if needed

### **Common Failure Points**:
1. **LLM API Failures**: Rate limiting, authentication issues
2. **Database Connection Loss**: Network interruptions
3. **Memory Overflow**: Large documents causing memory issues
4. **Invalid Data**: Malformed documents or unsupported formats

---

## 🛠️ **MONITORING & DEBUGGING**

### **Log Files Generated**:
- `process_detailed.log`: Comprehensive step-by-step logging
- `process_log_{filename}_{timestamp}.json`: Detailed process data in JSON format

### **Key Logging Points**:
- Process start/end timestamps
- Each step duration and data flow
- Error conditions and recovery attempts
- Performance metrics and bottlenecks

### **Debugging Commands**:
```bash
# View detailed process logs
tail -f process_detailed.log

# Check specific file processing
grep "filename.pdf" process_detailed.log

# Monitor performance metrics
grep "elapsed_time" process_detailed.log
```

---

This documentation provides a complete understanding of the LLM Graph Builder processing workflow, enabling effective monitoring, debugging, and optimization of the system.
