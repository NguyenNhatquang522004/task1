"""
Advanced Logging System Demo - LLM Graph Builder
Demonstrates the enhanced logging capabilities with deep insights and customization
"""

import sys
import os
import time
import json
from pathlib import Path

# Add the src directory to the path
backend_src_path = os.path.join(os.path.dirname(__file__), 'backend', 'src')
sys.path.insert(0, backend_src_path)

try:
    from process_logger import create_process_logger, log_process_step, log_processing_step, log_data_transformation
    from logging_config import create_development_config, create_production_config, create_custom_config
except ImportError as e:
    print(f"⚠️ Warning: Could not import logging modules: {e}")
    print(f"📁 Looking for modules in: {backend_src_path}")
    print("📁 Expected directory structure:")
    print("   project_root/")
    print("   ├── advanced_logging_demo.py")
    print("   └── backend/")
    print("       └── src/")
    print("           ├── process_logger.py")
    print("           └── logging_config.py")
    
    # List what's actually in the directory
    if os.path.exists(backend_src_path):
        print(f"📂 Files in {backend_src_path}:")
        for file in os.listdir(backend_src_path):
            if file.endswith('.py'):
                print(f"   - {file}")
    else:
        print(f"❌ Directory {backend_src_path} does not exist")
    
    sys.exit(1)

def demonstrate_basic_logging():
    """Demonstrate basic logging functionality"""
    print("🔍 DEMO 1: Basic Logging Functionality")
    print("=" * 50)
    
    # Create a development logger
    logger = create_process_logger(
        log_directory="demo_logs",
        enable_performance_tracking=True,
        enable_data_anonymization=False
    )
    
    # Start a process
    logger.start_process(
        file_name="demo_document.pdf",
        model="gemini-pro",
        source_type="local",
        custom_metadata={
            "user_id": "demo_user",
            "session_id": "demo_session_001",
            "experiment_name": "advanced_logging_demo"
        }
    )
    
    # Log various steps
    logger.log_step("DOCUMENT_LOADING", "Loading document from file system", {
        "file_path": "/demo/demo_document.pdf",
        "file_size": "2.5MB",
        "pages": 45
    })
    
    time.sleep(1)
    
    logger.log_step("DOCUMENT_PARSING", "Parsing document content", {
        "parser": "PyPDF2",
        "text_length": 15000,
        "images_found": 3,
        "tables_found": 2
    })
    
    time.sleep(0.5)
    
    # Log data transformation
    input_text = "This is a sample document with multiple paragraphs and sections."
    chunks = ["This is a sample document", "with multiple paragraphs", "and sections."]
    
    logger.log_data_flow("CHUNKING", input_text, chunks, 0.3, {
        "chunking_strategy": "sentence_based",
        "chunk_size": 512,
        "overlap": 50
    })
    
    # Log custom metrics
    logger.log_custom_metric("tokens_processed", 1250, "DOCUMENT_PARSING", {"model": "gemini-pro"})
    logger.log_custom_metric("api_calls_made", 5, "ENTITY_EXTRACTION", {"provider": "google"})
    
    # Simulate a performance bottleneck
    logger.log_performance_bottleneck("ENTITY_EXTRACTION", "SLOW_API_RESPONSE", {
        "api_endpoint": "gemini-pro",
        "response_time": 15.5,
        "expected_time": 3.0,
        "retry_count": 2
    })
    
    # End process
    stats = logger.end_process("SUCCESS", {
        "entities_extracted": 125,
        "relationships_created": 78,
        "nodes_created": 125,
        "edges_created": 78
    })
    
    print(f"\n✅ Process completed with statistics: {json.dumps(stats, indent=2)}")
    
def demonstrate_custom_configuration():
    """Demonstrate custom configuration options"""
    print("\n🔧 DEMO 2: Custom Configuration")
    print("=" * 50)
    
    # Create custom configuration
    config = create_custom_config(
        log_level=10,  # DEBUG level
        enable_console=True,
        enable_file=True,
        enable_performance=True,
        enable_anonymization=True,  # Enable data anonymization
        max_preview_length=100,
        log_directory="custom_logs"
    )
    
    # Create logger with custom configuration
    logger = create_process_logger(
        log_level=config.get_config()["log_level"],
        log_directory=config.get_config()["log_directory"],
        enable_performance_tracking=config.get_config()["enable_performance_tracking"],
        enable_data_anonymization=config.get_config()["enable_data_anonymization"],
        custom_formatters=config.get_custom_formatters()
    )
    
    # Add custom hooks
    for hook_name, hook_func in config.get_custom_hooks().items():
        logger.add_custom_hook(hook_name, hook_func)
    
    # Start process with sensitive data
    logger.start_process(
        file_name="sensitive_document.pdf",
        model="gemini-pro",
        source_type="encrypted",
        custom_metadata={
            "api_key": "secret_key_12345",  # This will be anonymized
            "user_token": "token_abcdef",   # This will be anonymized
            "user_name": "John Doe",        # This will not be anonymized
            "department": "Research"
        }
    )
    
    # Log step with sensitive data
    logger.log_step("API_CALL", "Making API call to external service", {
        "endpoint": "https://api.example.com/process",
        "api_key": "secret_api_key_xyz",  # This will be anonymized
        "payload_size": 1024,
        "timeout": 30
    })
    
    # Log data with performance tracking
    large_data = list(range(10000))
    processed_data = [x * 2 for x in large_data]
    
    logger.log_data_flow("DATA_PROCESSING", large_data, processed_data, 0.8, {
        "processing_type": "multiplication",
        "batch_size": 1000,
        "parallel_processing": True
    })
    
    logger.end_process("SUCCESS")
    
def demonstrate_decorator_usage():
    """Demonstrate decorator-based logging"""
    print("\n🎭 DEMO 3: Decorator-Based Logging")
    print("=" * 50)
    
    @log_process_step("DOCUMENT_PROCESSING", "Processing document with advanced features")
    def process_document(file_path: str, options: dict):
        """Simulate document processing"""
        time.sleep(1)  # Simulate processing time
        
        # Simulate some processing
        return {
            "processed_pages": 10,
            "extracted_text": "Sample extracted text...",
            "entities": ["Person", "Organization", "Location"],
            "processing_time": 1.0
        }
    
    @log_process_step("ENTITY_EXTRACTION", "Extracting entities using LLM", track_data_flow=True)
    def extract_entities(text: str, model: str):
        """Simulate entity extraction"""
        time.sleep(0.5)
        
        # Simulate entity extraction
        entities = [
            {"text": "John Doe", "type": "PERSON", "confidence": 0.95},
            {"text": "Microsoft", "type": "ORGANIZATION", "confidence": 0.88},
            {"text": "Seattle", "type": "LOCATION", "confidence": 0.92}
        ]
        
        return entities
    
    @log_process_step("RELATIONSHIP_EXTRACTION", "Extracting relationships between entities")
    def extract_relationships(entities: list):
        """Simulate relationship extraction"""
        time.sleep(0.3)
        
        # Simulate relationship extraction
        relationships = [
            {"source": "John Doe", "relation": "WORKS_FOR", "target": "Microsoft"},
            {"source": "Microsoft", "relation": "LOCATED_IN", "target": "Seattle"}
        ]
        
        return relationships
    
    # Use the decorated functions
    doc_result = process_document("demo_document.pdf", {"extract_images": True})
    entities = extract_entities(doc_result["extracted_text"], "gemini-pro")
    relationships = extract_relationships(entities)
    
    print(f"\n✅ Final results: {len(entities)} entities, {len(relationships)} relationships")

def demonstrate_data_lineage_tracking():
    """Demonstrate data lineage and transformation tracking"""
    print("\n🔄 DEMO 4: Data Lineage and Transformation Tracking")
    print("=" * 50)
    
    logger = create_process_logger(
        log_directory="lineage_logs",
        enable_performance_tracking=True
    )
    
    logger.start_process("lineage_demo.pdf", "gemini-pro", "local")
    
    # Stage 1: Raw text
    raw_text = "This is a sample document about artificial intelligence and machine learning. AI is transforming industries."
    
    # Stage 2: Tokenization
    tokens = ["This", "is", "a", "sample", "document", "about", "artificial", "intelligence", "and", "machine", "learning", "AI", "is", "transforming", "industries"]
    log_data_transformation("TOKENIZATION", raw_text, tokens, 0.1)
    
    # Stage 3: Chunking
    chunks = [
        "This is a sample document about artificial intelligence",
        "and machine learning. AI is transforming industries."
    ]
    log_data_transformation("CHUNKING", tokens, chunks, 0.2)
    
    # Stage 4: Entity extraction
    entities = [
        {"text": "artificial intelligence", "type": "CONCEPT"},
        {"text": "machine learning", "type": "CONCEPT"},
        {"text": "AI", "type": "CONCEPT"},
        {"text": "industries", "type": "SECTOR"}
    ]
    log_data_transformation("ENTITY_EXTRACTION", chunks, entities, 1.5)
    
    # Stage 5: Relationship extraction
    relationships = [
        {"source": "AI", "relation": "SAME_AS", "target": "artificial intelligence"},
        {"source": "AI", "relation": "INCLUDES", "target": "machine learning"},
        {"source": "AI", "relation": "TRANSFORMS", "target": "industries"}
    ]
    log_data_transformation("RELATIONSHIP_EXTRACTION", entities, relationships, 2.1)
    
    # Get current process insights
    insights = logger.get_process_insights()
    print(f"\n📊 Current process insights: {json.dumps(insights, indent=2)}")
    
    logger.end_process("SUCCESS", {
        "total_entities": len(entities),
        "total_relationships": len(relationships),
        "data_lineage_steps": 5
    })

def demonstrate_performance_monitoring():
    """Demonstrate performance monitoring and bottleneck detection"""
    print("\n⚡ DEMO 5: Performance Monitoring")
    print("=" * 50)
    
    logger = create_process_logger(
        log_directory="performance_logs",
        enable_performance_tracking=True
    )
    
    # Add performance monitoring hooks
    logger.add_custom_hook("performance_alert", lambda data: 
        print(f"🚨 Performance Alert: {data.get('step_name', 'Unknown')} took {data.get('processing_time', 'Unknown')}"))
    
    logger.start_process("performance_demo.pdf", "gemini-pro", "local")
    
    # Simulate fast operation
    logger.log_step("FAST_OPERATION", "Quick data processing", {"items_processed": 100})
    time.sleep(0.1)
    
    # Simulate moderate operation
    logger.log_step("MODERATE_OPERATION", "Medium complexity processing", {"items_processed": 500})
    time.sleep(2)
    
    # Simulate slow operation (will trigger bottleneck detection)
    logger.log_step("SLOW_OPERATION", "Complex AI processing", {"items_processed": 1000})
    time.sleep(5)
    
    # Log performance bottleneck manually
    logger.log_performance_bottleneck("API_CALL", "TIMEOUT", {
        "endpoint": "external_api",
        "timeout_duration": 30,
        "retry_attempts": 3
    })
    
    # Export metrics
    metrics_json = logger.export_metrics("json")
    print(f"\n📈 Exported metrics preview: {metrics_json[:200]}...")
    
    logger.end_process("SUCCESS")

def main():
    """Run all demonstrations"""
    print("🚀 LLM Graph Builder - Advanced Logging System Demo")
    print("=" * 60)
    
    try:
        demonstrate_basic_logging()
        demonstrate_custom_configuration()
        demonstrate_decorator_usage()
        demonstrate_data_lineage_tracking()
        demonstrate_performance_monitoring()
        
        print("\n🎉 All demonstrations completed successfully!")
        print("📁 Check the following directories for generated logs:")
        print("   - demo_logs/")
        print("   - custom_logs/")
        print("   - lineage_logs/")
        print("   - performance_logs/")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
