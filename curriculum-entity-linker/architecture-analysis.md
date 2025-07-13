# Curriculum Entity Linker - Architecture Analysis & Improvements

## 📋 Tổng quan

Document này phân tích kiến trúc hiện tại của Curriculum Entity Linker và đề xuất các kiến trúc cải tiến để tận dụng tốt hơn các chức năng search của LLM Graph Builder.

---

## 🏗️ Kiến trúc hiện tại (Current Architecture)

### Cấu trúc nodes & relationships
```
Course (Framework) → POINT_TO → CurriculumLink → HAVE_TO → __Entity__ (Extracted)
                                     ↑
                                Document (HAS_ENTITY → __Entity__)
```

### Ưu điểm
✅ **Đơn giản và dễ hiểu**
- Workflow rõ ràng: Course → Intermediate → Entities
- Dễ debug và maintain

✅ **Tách biệt framework và extracted data**
- Framework Course nodes độc lập
- Extracted entities không bị ảnh hưởng

✅ **Duplicate prevention**
- Kiểm tra document đã link chưa
- Force relink option

### Nhược điểm
❌ **Không tận dụng search capabilities**
- Không sử dụng vector embeddings
- Không có semantic search
- Missing similarity scoring

❌ **Static mapping dựa trên filename**
- Chỉ dựa vào course code trong filename
- Không kiểm tra content relevance

❌ **No content validation**
- Không verify entities có thực sự liên quan đến course không
- Có thể link sai entities

---

## 🚀 Kiến trúc cải tiến đề xuất

### 1. 🎯 Semantic-Aware Linker Architecture

```
Course (Framework) 
    ↓ (SEMANTIC_MATCH with confidence score)
CurriculumLink {
    confidence: float,
    method: "semantic|filename|hybrid",
    created_at: datetime
}
    ↓ (HAVE_TO with relevance score)
__Entity__ (Extracted) {
    relevance_score: float,
    match_reason: string
}
```

#### Improvements:
- **Vector embeddings comparison** giữa course description và entity content
- **Confidence scores** cho mỗi relationship
- **Multiple matching methods**: filename, semantic, hybrid
- **Relevance scoring** cho từng entity

### 2. 🔍 Search-Enhanced Linker Architecture

```
Course (Framework)
    ↓ (SEARCH_BASED_LINK)
SearchBasedLink {
    search_query: string,
    search_method: "vector|text|hybrid",
    match_score: float,
    search_results_count: int
}
    ↓ (CONTAINS with score)
__Entity__ (Top N relevant entities)
```

#### Features:
- **Sử dụng existing search API** của LLM Graph Builder
- **Vector search** cho entities tương tự
- **Text search** cho keyword matching
- **Hybrid search** kết hợp cả hai
- **Top-K selection** thay vì link tất cả entities

### 3. 🧠 AI-Powered Curriculum Mapper

```
Course (Framework)
    ↓ (AI_MAPPED)
IntelligentLink {
    llm_confidence: float,
    reasoning: string,
    validation_status: "validated|pending|rejected",
    ai_model: string
}
    ↓ (CURRICULUM_RELEVANCE)
__Entity__ (AI-validated relevant entities)
```

#### Advanced Features:
- **LLM-based content analysis** để validate relevance
- **Reasoning storage** - tại sao entity được chọn
- **Human validation workflow**
- **Continuous learning** từ feedback

---

## 🔧 Implementation Strategies

### Strategy 1: Enhanced Search Integration

```python
class SearchEnhancedLinker(CurriculumEntityLinker):
    def __init__(self, llm_graph_builder_api: str):
        super().__init__()
        self.search_api = llm_graph_builder_api
    
    def find_relevant_entities_by_search(self, course_description: str, 
                                       search_method: str = "hybrid") -> List[Dict]:
        """
        Sử dụng search API của LLM Graph Builder để tìm entities
        """
        # Vector search cho semantic similarity
        if search_method in ["vector", "hybrid"]:
            vector_results = self.search_api.vector_search(
                query=course_description,
                node_types=["__Entity__"],
                limit=50
            )
        
        # Text search cho keyword matching  
        if search_method in ["text", "hybrid"]:
            text_results = self.search_api.text_search(
                query=course_description,
                node_types=["__Entity__"],
                limit=50
            )
        
        # Combine và rank results
        return self.combine_and_rank_results(vector_results, text_results)
    
    def calculate_relevance_score(self, entity: Dict, course: Dict) -> float:
        """
        Tính relevance score giữa entity và course
        """
        # Vector similarity
        vector_score = self.calculate_vector_similarity(entity, course)
        
        # Keyword overlap
        keyword_score = self.calculate_keyword_overlap(entity, course)
        
        # Domain relevance
        domain_score = self.calculate_domain_relevance(entity, course)
        
        return (vector_score * 0.5 + keyword_score * 0.3 + domain_score * 0.2)
```

### Strategy 2: Multi-Modal Content Analysis

```python
class MultiModalLinker(CurriculumEntityLinker):
    def analyze_document_content(self, doc_id: int) -> Dict:
        """
        Phân tích content của document để hiểu topic
        """
        # Extract text content
        content = self.extract_document_content(doc_id)
        
        # Topic modeling
        topics = self.extract_topics(content)
        
        # Key concepts extraction
        concepts = self.extract_key_concepts(content)
        
        # Learning objectives identification
        objectives = self.identify_learning_objectives(content)
        
        return {
            "topics": topics,
            "concepts": concepts, 
            "objectives": objectives,
            "content_summary": self.summarize_content(content)
        }
    
    def create_intelligent_links(self, course: Dict, content_analysis: Dict):
        """
        Tạo links thông minh dựa trên content analysis
        """
        # Find entities matching topics
        topic_entities = self.find_entities_by_topics(content_analysis["topics"])
        
        # Find entities matching concepts
        concept_entities = self.find_entities_by_concepts(content_analysis["concepts"])
        
        # Combine và filter duplicates
        relevant_entities = self.merge_and_deduplicate(topic_entities, concept_entities)
        
        # Create links with confidence scores
        return self.create_scored_links(course, relevant_entities)
```

### Strategy 3: Hierarchical Curriculum Structure

```
Program → Semester → Course → Module → Topic → __Entity__
    ↓        ↓         ↓        ↓       ↓
CourseProgram → SemesterPlan → CurriculumModule → TopicMap → EntityLink
```

```python
class HierarchicalLinker(CurriculumEntityLinker):
    def create_hierarchical_structure(self):
        """
        Tạo cấu trúc phân cấp cho curriculum
        """
        # Program level
        programs = self.create_program_nodes()
        
        # Semester level  
        semesters = self.create_semester_nodes(programs)
        
        # Course level
        courses = self.create_course_nodes(semesters)
        
        # Module level (topics within course)
        modules = self.create_module_nodes(courses)
        
        # Link entities to appropriate level
        self.link_entities_hierarchically(modules)
    
    def find_optimal_linking_level(self, entity: Dict) -> str:
        """
        Xác định level tối ưu để link entity
        """
        specificity = self.calculate_entity_specificity(entity)
        
        if specificity > 0.8:
            return "module"  # Very specific topic
        elif specificity > 0.5:
            return "course"  # Course-level concept
        else:
            return "program"  # General concept
```

---

## 🎯 Recommended Architecture: Hybrid Smart Linker

### Core Components

#### 1. **Multi-Method Matcher**
```python
class HybridMatcher:
    methods = ["filename", "semantic", "search", "ai_validation"]
    
    def match_entities(self, course: Dict, method: str = "hybrid") -> List[Dict]:
        results = {}
        
        # Method 1: Filename-based (existing)
        if method in ["filename", "hybrid"]:
            results["filename"] = self.filename_based_match(course)
        
        # Method 2: Semantic similarity
        if method in ["semantic", "hybrid"]:
            results["semantic"] = self.semantic_similarity_match(course)
        
        # Method 3: Search API integration
        if method in ["search", "hybrid"]:
            results["search"] = self.search_api_match(course)
        
        # Method 4: AI validation
        if method in ["ai", "hybrid"]:
            results["ai"] = self.ai_validation_match(course)
        
        return self.combine_match_results(results)
```

#### 2. **Confidence-Based Relationships**
```cypher
// Enhanced relationship với metadata
MERGE (course:Course)-[r:SMART_LINK]->(entity:__Entity__)
SET r.confidence = $confidence_score,
    r.method = $matching_method,
    r.reasoning = $ai_reasoning,
    r.created_at = datetime(),
    r.validated = $human_validated
```

#### 3. **Search Integration Layer**
```python
class SearchIntegration:
    def __init__(self, llm_api_endpoint: str):
        self.api = LLMGraphBuilderAPI(llm_api_endpoint)
    
    def enhanced_entity_search(self, query: str, filters: Dict = None) -> List[Dict]:
        """
        Sử dụng search capabilities của LLM Graph Builder
        """
        # Vector search
        vector_results = self.api.vector_search(
            query=query,
            filters=filters,
            similarity_threshold=0.7
        )
        
        # Fulltext search
        text_results = self.api.fulltext_search(
            query=query,
            node_labels=["__Entity__"],
            property_keys=["id", "description", "name"]
        )
        
        # Cypher-based search cho complex patterns
        pattern_results = self.api.pattern_search(
            pattern=self.generate_search_pattern(query),
            parameters=filters
        )
        
        return self.merge_search_results(vector_results, text_results, pattern_results)
```

#### 4. **Quality Assurance System**
```python
class QualityAssurance:
    def validate_link_quality(self, course: Dict, entity: Dict, link_info: Dict) -> Dict:
        """
        Validate chất lượng của link
        """
        scores = {
            "semantic_relevance": self.check_semantic_relevance(course, entity),
            "domain_match": self.check_domain_alignment(course, entity),
            "learning_outcome_fit": self.check_learning_outcome_alignment(course, entity),
            "confidence": link_info.get("confidence", 0.0)
        }
        
        overall_quality = sum(scores.values()) / len(scores)
        
        return {
            "quality_score": overall_quality,
            "individual_scores": scores,
            "recommendation": self.get_quality_recommendation(overall_quality)
        }
```

---

## 📊 Search Capabilities Integration

### 1. Vector Search Enhancement
```python
def leverage_vector_search(self):
    """
    Tận dụng vector embeddings của LLM Graph Builder
    """
    # Get course embedding
    course_embedding = self.get_entity_embedding(course_node)
    
    # Find similar entities using vector search
    similar_entities = self.vector_search(
        embedding=course_embedding,
        node_types=["__Entity__"],
        similarity_threshold=0.75,
        limit=100
    )
    
    # Rank by combined score
    return self.rank_by_multiple_factors(similar_entities)
```

### 2. Graph Pattern Search
```python
def pattern_based_search(self, course_code: str):
    """
    Sử dụng graph patterns để tìm related entities
    """
    pattern_queries = [
        # Entities từ similar courses
        """
        MATCH (c1:Course {code: $course_code})-[:SIMILAR_TO]->(c2:Course)
        MATCH (c2)<-[:POINT_TO]-(link:CurriculumLink)-[:HAVE_TO]->(e:__Entity__)
        RETURN e, count(*) as frequency
        ORDER BY frequency DESC
        """,
        
        # Co-occurrence patterns
        """
        MATCH (e1:__Entity__)<-[:HAS_ENTITY]-(d:Document)-[:HAS_ENTITY]->(e2:__Entity__)
        WHERE e1.domain = $course_domain
        RETURN e2, count(*) as co_occurrence
        ORDER BY co_occurrence DESC
        """
    ]
```

### 3. Semantic Query Enhancement
```python
def semantic_query_expansion(self, course_description: str):
    """
    Mở rộng query sử dụng semantic understanding
    """
    # Extract key terms
    key_terms = self.extract_key_terms(course_description)
    
    # Find synonyms và related terms
    expanded_terms = self.find_related_terms(key_terms)
    
    # Generate multiple search queries
    search_queries = self.generate_search_variants(expanded_terms)
    
    # Execute searches và combine results
    all_results = []
    for query in search_queries:
        results = self.hybrid_search(query)
        all_results.extend(results)
    
    return self.deduplicate_and_rank(all_results)
```

---

## 🔄 Migration Strategy

### Phase 1: Search Integration (2 weeks)
1. **Add search API integration**
   - Connect to LLM Graph Builder search endpoints
   - Implement vector search for entity matching
   - Add semantic similarity scoring

### Phase 2: Enhanced Matching (2 weeks)  
2. **Implement multi-method matching**
   - Keep existing filename-based method
   - Add semantic similarity matching
   - Implement confidence scoring

### Phase 3: Quality Assurance (1 week)
3. **Add validation layer**
   - Implement link quality assessment
   - Add human validation workflow
   - Create feedback mechanism

### Phase 4: Advanced Features (2 weeks)
4. **AI-powered enhancements**
   - LLM-based content analysis
   - Automated reasoning generation
   - Continuous learning system

---

## 🎯 Kết luận

Kiến trúc **Hybrid Smart Linker** được đề xuất sẽ:

✅ **Tận dụng tối đa search capabilities** của LLM Graph Builder
✅ **Cải thiện chất lượng linking** thông qua multiple validation methods  
✅ **Maintain backward compatibility** với kiến trúc hiện tại
✅ **Enable advanced use cases** như semantic search, AI validation
✅ **Provide scalable foundation** cho future enhancements

### Next Steps
1. Implement SearchIntegration layer
2. Add confidence scoring to existing relationships
3. Create validation và feedback mechanisms
4. Integrate với LLM Graph Builder search APIs
5. Test và optimize performance

---

*Document được tạo vào: July 13, 2025*
*Version: 1.0*
*Author: GitHub Copilot Assistant*
