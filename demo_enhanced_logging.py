"""
Demo script showing how to use the enhanced logging system
Run this script to see the logging system in action
"""

import sys
import os
import time

# Add the backend/src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

def demo_basic_logging():
    """Demo basic logging functionality"""
    print("🔍 Demo: Basic Logging Functionality")
    print("=" * 50)
    
    try:
        from custom_logging_config import create_development_logger
        
        # Create a development logger
        logger = create_development_logger()
        
        # Start a process
        logger.start_process(
            "demo_document.pdf",
            "gemini-pro",
            "local",
            {
                "user_id": "demo_user",
                "chunk_size": 512,
                "overlap": 50
            }
        )
        
        # Log various processing steps
        logger.log_step("DOCUMENT_LOADING", "Loading document from filesystem", {
            "file_path": "/demo/demo_document.pdf",
            "file_size": "2.5MB",
            "pages": 45
        })
        
        time.sleep(0.5)
        
        logger.log_step("CHUNKING", "Breaking document into chunks", {
            "chunk_size": 512,
            "overlap": 50,
            "total_chunks": 25
        })
        
        # Simulate data transformation
        input_text = "This is a sample document with important information about artificial intelligence."
        chunks = ["This is a sample document", "with important information", "about artificial intelligence."]
        
        logger.log_data_flow("CHUNKING", input_text, chunks, 0.3, {
            "strategy": "sentence_based",
            "quality_score": 0.95
        })
        
        time.sleep(1)
        
        # Simulate entity extraction
        entities = [
            {"text": "artificial intelligence", "type": "CONCEPT", "confidence": 0.95},
            {"text": "document", "type": "OBJECT", "confidence": 0.88}
        ]
        
        logger.log_step("ENTITY_EXTRACTION", "Extracting entities using LLM", {
            "model": "gemini-pro",
            "entities_extracted": len(entities),
            "avg_confidence": 0.915
        })
        
        # Log custom metrics
        logger.log_custom_metric("entities_per_chunk", len(entities) / len(chunks))
        logger.log_custom_metric("processing_speed", 25 / 1.8)  # chunks per second
        
        # Complete the process
        logger.end_process("SUCCESS", {
            "total_entities": len(entities),
            "total_chunks": len(chunks),
            "final_quality": 0.92
        })
        
        print("\n✅ Basic logging demo completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the project root directory")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_performance_monitoring():
    """Demo performance monitoring"""
    print("\n⚡ Demo: Performance Monitoring")
    print("=" * 50)
    
    try:
        from custom_logging_config import create_debugging_logger
        
        # Create a debugging logger
        logger = create_debugging_logger()
        
        logger.start_process("performance_demo.pdf", "gemini-pro", "local")
        
        # Fast operation
        logger.log_step("FAST_OPERATION", "Quick processing", {"items": 100})
        time.sleep(0.1)
        
        # Slow operation (will trigger performance alert)
        logger.log_step("SLOW_OPERATION", "Complex processing", {"items": 1000})
        time.sleep(3)  # Simulate slow processing
        
        # Very slow operation (will trigger critical alert)
        logger.log_step("VERY_SLOW_OPERATION", "Heavy AI processing", {"items": 5000})
        time.sleep(1)  # Simulate very slow processing
        
        # Log performance bottleneck
        logger.log_performance_bottleneck("API_CALL", "TIMEOUT", {
            "endpoint": "external_api",
            "timeout_seconds": 30,
            "retry_count": 3
        })
        
        logger.end_process("SUCCESS")
        
        print("\n✅ Performance monitoring demo completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_data_quality_monitoring():
    """Demo data quality monitoring"""
    print("\n📊 Demo: Data Quality Monitoring")
    print("=" * 50)
    
    try:
        from custom_logging_config import create_development_logger
        
        logger = create_development_logger()
        
        logger.start_process("quality_demo.pdf", "gemini-pro", "local")
        
        # High quality data transformation
        input_data = ["sentence1", "sentence2", "sentence3", "sentence4"]
        high_quality_output = ["entity1", "entity2", "entity3", "entity4"]
        
        logger.log_data_flow("HIGH_QUALITY_EXTRACTION", input_data, high_quality_output, 1.2, {
            "extraction_method": "advanced_nlp",
            "confidence_threshold": 0.9
        })
        
        # Medium quality data transformation
        medium_quality_output = ["entity1", "entity2"]
        
        logger.log_data_flow("MEDIUM_QUALITY_EXTRACTION", input_data, medium_quality_output, 0.8, {
            "extraction_method": "basic_nlp",
            "confidence_threshold": 0.7
        })
        
        # Low quality data transformation
        low_quality_output = ["entity1"]
        
        logger.log_data_flow("LOW_QUALITY_EXTRACTION", input_data, low_quality_output, 0.5, {
            "extraction_method": "regex",
            "confidence_threshold": 0.5
        })
        
        logger.end_process("SUCCESS")
        
        print("\n✅ Data quality monitoring demo completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_custom_hooks():
    """Demo custom hooks"""
    print("\n🎣 Demo: Custom Hooks")
    print("=" * 50)
    
    try:
        from custom_logging_config import create_development_logger
        
        logger = create_development_logger()
        
        # Add a custom hook
        def custom_alert_hook(data):
            if data.get("step_name") == "CRITICAL_STEP":
                print(f"🚨 CUSTOM ALERT: Critical step executed with data: {data}")
        
        logger.add_custom_hook("custom_alert", custom_alert_hook)
        
        logger.start_process("hooks_demo.pdf", "gemini-pro", "local")
        
        # Regular step
        logger.log_step("REGULAR_STEP", "Normal processing", {"value": 42})
        
        # Critical step (will trigger custom hook)
        logger.log_step("CRITICAL_STEP", "Critical processing", {"value": 999})
        
        # Log with high entity extraction (will trigger entity extraction hook)
        logger.log_step("ENTITY_EXTRACTION", "Extracting many entities", {
            "entities_extracted": 150,
            "input_chunks": 10
        })
        
        logger.end_process("SUCCESS")
        
        print("\n✅ Custom hooks demo completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def show_log_files():
    """Show generated log files"""
    print("\n📁 Generated Log Files:")
    print("=" * 50)
    
    logs_dir = "logs"
    if os.path.exists(logs_dir):
        files = os.listdir(logs_dir)
        for file in files:
            file_path = os.path.join(logs_dir, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"  📄 {file} ({size} bytes)")
    else:
        print("  ℹ️  No log files found (logs directory doesn't exist)")

def main():
    """Run all demos"""
    print("🚀 Enhanced Logging System Demo")
    print("=" * 60)
    
    try:
        demo_basic_logging()
        demo_performance_monitoring()
        demo_data_quality_monitoring()
        demo_custom_hooks()
        show_log_files()
        
        print("\n🎉 All demos completed successfully!")
        print("\n💡 Tips for customization:")
        print("   1. Edit backend/src/custom_logging_config.py to change thresholds")
        print("   2. Add your own custom formatters and hooks")
        print("   3. Set ENVIRONMENT=production for production logging")
        print("   4. Check the logs/ directory for generated files")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
