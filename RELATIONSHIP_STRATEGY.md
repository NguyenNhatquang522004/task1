# Chiến lược Gán Mối Quan Hệ Giữa Entities Trong LLM Graph Builder

## 📋 Tổng quan

Project LLM Graph Builder sử dụng một chiến lược phức hợp để gán mối quan hệ giữa các entities được trích xuất từ documents và các entities trong curriculum framework. Đây là một hệ thống linking thông minh kết hợp nhiều phương pháp để tạo ra knowledge graph có ý nghĩa.

---

## 🎯 Mục tiêu Chính

### 1. **Entity Linking Strategy**
- **Mục đích**: Kết nối entities được trích xuất từ documents với curriculum framework
- **Phạm vi**: Tạo relationships giữa extracted entities và course structures
- **Kết quả**: Knowledge graph tích hợp đa chiều

### 2. **Cross-Document Relationships**
- **Mục đích**: Tìm và tạo relationships giữa entities từ các documents khác nhau
- **Phạm vi**: Entities thuộc cùng domain hoặc có semantic similarity
- **Kết quả**: Mạng lưới connections phong phú giữa các documents

---

## 🏗️ Kiến trúc Hệ thống

### **Layer 1: Document Processing**
```
PDF Documents → Text Extraction → Chunking → Entity Extraction
```

### **Layer 2: Curriculum Integration** 
```
Course Framework + Extracted Entities → CurriculumLink → Structured Knowledge
```

### **Layer 3: Cross-Document Analysis**
```
Multiple Documents → Semantic Analysis → Cross-Document Relationships
```

---

## 🔧 Chi Tiết Chiến Lược

## 1. **Curriculum Entity Linking**

### **A. Course Code Matching Strategy**

**Nguyên tắc**: Đơn giản hóa logic linking
```python
# Logic cũ (phức tạp)
if course_exists AND has_curriculum_framework AND entities_match_concepts:
    create_curriculum_link()

# Logic mới (đơn giản)
if course_exists:
    create_curriculum_link()  # Tạo ngay lập tức
```

**Quy trình**:
1. **Extract Course Code** từ filename pattern `[CMP170]`
2. **Find Course Node** trong Neo4j database
3. **Create CurriculumLink** nếu course tồn tại
4. **Link All Entities** từ document đến CurriculumLink

### **B. Relationship Structure**

```cypher
# Cấu trúc relationships
(Course)-[:POINT_TO]->(CurriculumLink)-[:HAVE]->(ExtractedEntity)
(Document)-[:FIRST_CHUNK]->(Chunk)-[:HAS_ENTITY]->(ExtractedEntity)
```

**Ý nghĩa**:
- `POINT_TO`: Course framework "trỏ đến" CurriculumLink
- `HAVE`: CurriculumLink "có" tất cả entities liên quan
- `HAS_ENTITY`: Chunk "chứa" entity được trích xuất

### **C. Multi-Document Handling**

**Vấn đề**: Nhiều documents cùng course code
```
[COS141] Giáo trình HP Phát triển ứng dụng với J2EE.pdf
[COS141] Giáo trình HP Lập trình ứng dụng với Java.pdf
```

**Giải pháp**: Một CurriculumLink per course code
- 2 documents → 1 CurriculumLink node
- CurriculumLink nhận entities từ TẤT CẢ documents cùng course

---

## 2. **Cross-Document Relationship Strategy**

### **A. Semantic Similarity Detection**

**Phương pháp 1: Embedding-based Similarity**
```python
# Sử dụng sentence transformers hoặc OpenAI embeddings
entity1_embedding = get_embedding(entity1.text)
entity2_embedding = get_embedding(entity2.text)
similarity = cosine_similarity(entity1_embedding, entity2_embedding)

if similarity > THRESHOLD:
    create_relationship(entity1, entity2, "SIMILAR_TO")
```

**Phương pháp 2: Named Entity Recognition**
```python
# Entities cùng type và tương tự
if entity1.type == entity2.type and are_similar(entity1.name, entity2.name):
    create_relationship(entity1, entity2, "RELATES_TO")
```

### **B. Domain-Specific Relationships**

**Programming Concepts**:
```cypher
# Ví dụ: Java concepts trong different documents
(Entity1 {id: "Java OOP"})-[:BUILDS_UPON]->(Entity2 {id: "Java Basics"})
(Entity1 {id: "Spring Framework"})-[:USES]->(Entity2 {id: "Java Annotations"})
```

**Academic Relationships**:
```cypher
# Course prerequisites và dependencies
(Course1)-[:PREREQUISITE]->(Course2)
(Concept1)-[:REQUIRES]->(Concept2)
```

### **C. Content-Based Relationship Mining**

**Co-occurrence Analysis**:
```python
# Entities xuất hiện cùng nhau trong contexts
def find_co_occurring_entities(documents):
    for doc in documents:
        entities_in_doc = extract_entities(doc)
        for entity1 in entities_in_doc:
            for entity2 in entities_in_doc:
                if are_related(entity1, entity2):
                    create_relationship(entity1, entity2, "CO_OCCURS")
```

**Topic Modeling**:
```python
# Entities thuộc cùng topic
def group_by_topics(entities):
    topics = run_lda_analysis(entities)
    for topic in topics:
        entities_in_topic = get_entities_for_topic(topic)
        create_topic_relationships(entities_in_topic)
```

---

## 3. **Advanced Relationship Strategies**

### **A. Temporal Relationships**

**Learning Progression**:
```cypher
# Sequence trong curriculum
(Topic1)-[:LEADS_TO]->(Topic2)-[:LEADS_TO]->(Topic3)
(BasicConcept)-[:PREREQUISITE_FOR]->(AdvancedConcept)
```

**Document Timeline**:
```cypher
# Version evolution của course materials
(Document2024)-[:UPDATES]->(Document2023)
(NewSyllabus)-[:REPLACES]->(OldSyllabus)
```

### **B. Hierarchical Relationships**

**Taxonomy Structure**:
```cypher
# Concept hierarchy
(Programming)-[:HAS_SUBCATEGORY]->(OOP)
(OOP)-[:HAS_SUBCATEGORY]->(Inheritance)
(Inheritance)-[:IMPLEMENTED_IN]->(Java)
```

**Academic Structure**:
```cypher
# Course structure hierarchy  
(Program)-[:CONTAINS]->(Course)
(Course)-[:HAS_TOPIC]->(Topic)
(Topic)-[:HAS_CONCEPT]->(Concept)
```

### **C. Functional Relationships**

**Tool-Usage Relationships**:
```cypher
# Technologies và applications
(IDE)-[:USED_FOR]->(Programming)
(Framework)-[:FACILITATES]->(Development)
(Library)-[:PROVIDES]->(Functionality)
```

**Assessment Relationships**:
```cypher
# Learning outcomes và assessments
(Assessment)-[:EVALUATES]->(CLO)
(CLO)-[:MEASURED_BY]->(PI)
(PI)-[:PART_OF]->(PLO)
```

---

## 4. **Implementation Details**

### **A. Entity Extraction Pipeline**

```python
class EntityExtractionPipeline:
    def __init__(self):
        self.nlp_model = load_model()
        self.embedding_model = load_embedding_model()
    
    def extract_entities(self, document):
        # 1. Text preprocessing
        clean_text = preprocess(document.text)
        
        # 2. Named Entity Recognition
        named_entities = self.nlp_model(clean_text)
        
        # 3. Custom entity extraction
        domain_entities = extract_domain_specific_entities(clean_text)
        
        # 4. Entity normalization
        normalized_entities = normalize_entities(named_entities + domain_entities)
        
        return normalized_entities
```

### **B. Relationship Discovery**

```python
class RelationshipDiscovery:
    def __init__(self):
        self.similarity_threshold = 0.8
        self.relationship_rules = load_relationship_rules()
    
    def discover_relationships(self, entity1, entity2):
        relationships = []
        
        # 1. Similarity-based relationships
        if self.compute_similarity(entity1, entity2) > self.similarity_threshold:
            relationships.append(("SIMILAR_TO", self.compute_similarity(entity1, entity2)))
        
        # 2. Rule-based relationships
        for rule in self.relationship_rules:
            if rule.matches(entity1, entity2):
                relationships.append((rule.relationship_type, rule.confidence))
        
        # 3. Context-based relationships
        if self.share_context(entity1, entity2):
            relationships.append(("CONTEXTUALLY_RELATED", self.context_score(entity1, entity2)))
        
        return relationships
```

### **C. Cross-Document Analysis**

```python
class CrossDocumentAnalyzer:
    def __init__(self):
        self.documents = []
        self.entity_index = {}
    
    def analyze_cross_document_relationships(self):
        # 1. Build entity index
        for doc in self.documents:
            entities = extract_entities(doc)
            for entity in entities:
                self.entity_index[entity.id] = entity
        
        # 2. Find potential relationships
        relationships = []
        for entity1_id in self.entity_index:
            for entity2_id in self.entity_index:
                if entity1_id != entity2_id:
                    entity1 = self.entity_index[entity1_id]
                    entity2 = self.entity_index[entity2_id]
                    
                    # Different documents only
                    if entity1.document_id != entity2.document_id:
                        potential_rels = self.discover_relationships(entity1, entity2)
                        relationships.extend(potential_rels)
        
        return relationships
```

---

## 5. **Quality Control & Validation**

### **A. Relationship Confidence Scoring**

```python
def calculate_relationship_confidence(entity1, entity2, relationship_type):
    confidence_factors = {
        'semantic_similarity': compute_semantic_similarity(entity1, entity2),
        'context_overlap': compute_context_overlap(entity1, entity2),
        'domain_relevance': compute_domain_relevance(entity1, entity2),
        'co_occurrence_frequency': get_co_occurrence_count(entity1, entity2)
    }
    
    # Weighted combination
    confidence = (
        0.4 * confidence_factors['semantic_similarity'] +
        0.3 * confidence_factors['context_overlap'] +
        0.2 * confidence_factors['domain_relevance'] +
        0.1 * confidence_factors['co_occurrence_frequency']
    )
    
    return confidence
```

### **B. Relationship Validation Rules**

```python
class RelationshipValidator:
    def __init__(self):
        self.validation_rules = [
            self.check_semantic_consistency,
            self.check_domain_appropriateness,
            self.check_circular_dependencies,
            self.check_relationship_multiplicity
        ]
    
    def validate_relationship(self, entity1, entity2, relationship_type):
        for rule in self.validation_rules:
            if not rule(entity1, entity2, relationship_type):
                return False
        return True
    
    def check_semantic_consistency(self, entity1, entity2, rel_type):
        # Ensure relationship makes semantic sense
        return self.is_semantically_valid(entity1, entity2, rel_type)
    
    def check_circular_dependencies(self, entity1, entity2, rel_type):
        # Prevent circular relationships that don't make sense
        return not self.creates_invalid_cycle(entity1, entity2, rel_type)
```

---

## 6. **Performance Optimization**

### **A. Caching Strategy**

```python
class RelationshipCache:
    def __init__(self):
        self.embedding_cache = {}
        self.similarity_cache = {}
        self.relationship_cache = {}
    
    def get_cached_similarity(self, entity1_id, entity2_id):
        cache_key = f"{entity1_id}_{entity2_id}"
        return self.similarity_cache.get(cache_key)
    
    def cache_similarity(self, entity1_id, entity2_id, similarity):
        cache_key = f"{entity1_id}_{entity2_id}"
        self.similarity_cache[cache_key] = similarity
```

### **B. Batch Processing**

```python
def process_relationships_in_batches(entities, batch_size=1000):
    entity_pairs = generate_entity_pairs(entities)
    batches = create_batches(entity_pairs, batch_size)
    
    for batch in batches:
        relationships = []
        for entity1, entity2 in batch:
            rels = discover_relationships(entity1, entity2)
            relationships.extend(rels)
        
        # Bulk insert to Neo4j
        create_relationships_bulk(relationships)
```

---

## 7. **Configuration & Customization**

### **A. Relationship Type Configuration**

```yaml
# relationship_config.yaml
relationship_types:
  semantic:
    - SIMILAR_TO
    - RELATED_TO
    - EQUIVALENT_TO
  
  hierarchical:
    - IS_PART_OF
    - CONTAINS
    - SUBCATEGORY_OF
  
  temporal:
    - PRECEDES
    - FOLLOWS
    - CONCURRENT_WITH
  
  functional:
    - USES
    - PROVIDES
    - ENABLES
    - REQUIRES

similarity_thresholds:
  high_confidence: 0.9
  medium_confidence: 0.7
  low_confidence: 0.5

processing_rules:
  max_relationships_per_entity: 50
  min_confidence_threshold: 0.6
  enable_cross_document: true
  enable_curriculum_linking: true
```

### **B. Domain-Specific Rules**

```python
# domain_rules.py
PROGRAMMING_RELATIONSHIPS = {
    'inheritance': {
        'patterns': ['extends', 'inherits from', 'subclass of'],
        'relationship': 'INHERITS_FROM',
        'confidence_boost': 0.2
    },
    'implementation': {
        'patterns': ['implements', 'realizes'],
        'relationship': 'IMPLEMENTS',
        'confidence_boost': 0.15
    },
    'dependency': {
        'patterns': ['depends on', 'requires', 'uses'],
        'relationship': 'DEPENDS_ON',
        'confidence_boost': 0.1
    }
}

ACADEMIC_RELATIONSHIPS = {
    'prerequisite': {
        'patterns': ['prerequisite', 'required before', 'must complete'],
        'relationship': 'PREREQUISITE_FOR',
        'confidence_boost': 0.25
    },
    'assessment': {
        'patterns': ['evaluates', 'measures', 'assesses'],
        'relationship': 'EVALUATES',
        'confidence_boost': 0.2
    }
}
```

---

## 8. **Monitoring & Analytics**

### **A. Relationship Quality Metrics**

```python
class RelationshipAnalytics:
    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver
    
    def generate_relationship_report(self):
        with self.driver.session() as session:
            # Relationship distribution
            rel_distribution = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as relationship_type, count(r) as count
                ORDER BY count DESC
            """)
            
            # Confidence distribution
            confidence_stats = session.run("""
                MATCH ()-[r]->()
                WHERE r.confidence IS NOT NULL
                RETURN 
                    avg(r.confidence) as avg_confidence,
                    min(r.confidence) as min_confidence,
                    max(r.confidence) as max_confidence,
                    count(r) as total_relationships
            """)
            
            # Entity connectivity
            connectivity_stats = session.run("""
                MATCH (n)
                RETURN 
                    avg(size((n)-[]->())) as avg_outgoing,
                    avg(size((n)<-[]->())) as avg_incoming,
                    max(size((n)-[]->())) as max_connections
            """)
            
            return {
                'relationship_distribution': list(rel_distribution),
                'confidence_statistics': confidence_stats.single(),
                'connectivity_statistics': connectivity_stats.single()
            }
```

### **B. Performance Monitoring**

```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'processing_time': [],
            'relationships_created': [],
            'entities_processed': [],
            'error_count': 0
        }
    
    def track_processing_batch(self, start_time, end_time, entities_count, relationships_count):
        processing_time = end_time - start_time
        self.metrics['processing_time'].append(processing_time)
        self.metrics['relationships_created'].append(relationships_count)
        self.metrics['entities_processed'].append(entities_count)
    
    def get_performance_summary(self):
        return {
            'avg_processing_time': np.mean(self.metrics['processing_time']),
            'total_relationships': sum(self.metrics['relationships_created']),
            'total_entities': sum(self.metrics['entities_processed']),
            'relationships_per_second': sum(self.metrics['relationships_created']) / sum(self.metrics['processing_time']),
            'error_rate': self.metrics['error_count'] / len(self.metrics['processing_time'])
        }
```

---

## 9. **Best Practices & Guidelines**

### **A. Entity Relationship Design Principles**

1. **Specificity over Generality**
   - Tạo relationships cụ thể thay vì chung chung
   - `INHERITS_FROM` tốt hơn `RELATED_TO`

2. **Bidirectional Consideration**
   - Relationship có thể cần reverse direction
   - `A DEPENDS_ON B` → `B SUPPORTS A`

3. **Confidence-Based Filtering**
   - Chỉ tạo relationships với confidence > threshold
   - Lower confidence = review manually

4. **Contextual Relevance**
   - Relationships phải có ý nghĩa trong domain context
   - Academic relationships vs Technical relationships

### **B. Scalability Guidelines**

1. **Batch Processing**
   - Xử lý entities theo batches để avoid memory issues
   - Bulk operations cho Neo4j

2. **Incremental Updates**
   - Chỉ process entities mới hoặc đã thay đổi
   - Maintain change tracking

3. **Caching Strategy**
   - Cache embeddings và similarity calculations
   - Redis hoặc in-memory cache

4. **Parallel Processing**
   - Multi-threading cho entity processing
   - Async operations cho I/O bound tasks

---

## 10. **Future Enhancements**

### **A. Machine Learning Integration**

```python
# ML-based relationship prediction
class MLRelationshipPredictor:
    def __init__(self):
        self.model = load_pretrained_model('relationship_classifier')
    
    def predict_relationships(self, entity1, entity2):
        features = extract_features(entity1, entity2)
        predictions = self.model.predict([features])
        return predictions
```

### **B. Knowledge Graph Reasoning**

```python
# Graph reasoning for implicit relationships
class GraphReasoner:
    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver
    
    def infer_implicit_relationships(self):
        # If A relates to B and B relates to C, then A might relate to C
        with self.driver.session() as session:
            session.run("""
                MATCH (a)-[:SIMILAR_TO]->(b)-[:SIMILAR_TO]->(c)
                WHERE NOT (a)-[:SIMILAR_TO]->(c)
                AND a.id <> c.id
                CREATE (a)-[:TRANSITIVELY_SIMILAR]->(c)
            """)
```

### **C. Interactive Relationship Validation**

```python
# Human-in-the-loop validation
class InteractiveValidator:
    def __init__(self):
        self.pending_relationships = []
    
    def queue_for_human_review(self, entity1, entity2, relationship, confidence):
        if confidence < HIGH_CONFIDENCE_THRESHOLD:
            self.pending_relationships.append({
                'entity1': entity1,
                'entity2': entity2,
                'relationship': relationship,
                'confidence': confidence
            })
    
    def get_human_feedback(self, relationship_id):
        # Integration with review interface
        return get_human_validation(relationship_id)
```

---

## 📊 Tổng kết

Chiến lược gán mối quan hệ trong LLM Graph Builder sử dụng một approach đa tầng kết hợp:

1. **Curriculum Integration**: Đơn giản nhưng hiệu quả - chỉ cần course code match
2. **Semantic Analysis**: Sử dụng embeddings và NLP để tìm similarities
3. **Domain Rules**: Áp dụng knowledge domain-specific cho accuracy cao
4. **Quality Control**: Multi-layer validation để đảm bảo relationship quality
5. **Performance Optimization**: Caching, batching, và parallel processing

Hệ thống này tạo ra một knowledge graph phong phú và có ý nghĩa, kết nối không chỉ entities trong cùng document mà còn across documents và với curriculum framework, tạo ra một mạng lưới kiến thức tích hợp và có cấu trúc.

---

*Document này mô tả chiến lược hiện tại và roadmap cho việc phát triển relationship strategies trong LLM Graph Builder project.*
