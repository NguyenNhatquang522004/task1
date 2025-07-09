# Advanced Logging System Documentation

## Overview

The LLM Graph Builder now includes a comprehensive, customizable logging system that provides deep insights into the document processing workflow. This enhanced logging system tracks every step of the process, monitors performance, analyzes data transformations, and provides extensive customization options.

## Key Features

### 🔍 **Deep Process Insights**
- **Step-by-step tracking**: Every processing step is logged with timestamps, data summaries, and performance metrics
- **Data lineage tracking**: Complete trace of how data transforms throughout the pipeline
- **Performance monitoring**: Automatic detection of bottlenecks and slow operations
- **Memory usage tracking**: Monitor memory consumption across processing steps

### 🎛️ **Extensive Customization**
- **Configuration presets**: Pre-configured settings for development, production, debugging, and minimal logging
- **Custom formatters**: Define how log messages are formatted and displayed
- **Custom hooks**: Add custom logic that executes during specific processing events
- **Data anonymization**: Automatically redact sensitive information from logs
- **Flexible output options**: Log to console, files, or both with customizable formats

### 📊 **Advanced Analytics**
- **Data quality scoring**: Automatic assessment of data quality at each transformation step
- **Processing statistics**: Comprehensive metrics about the entire processing pipeline
- **Export capabilities**: Export logs and metrics in JSON or CSV formats
- **Human-readable reports**: Generate detailed, easy-to-read process summaries

## Quick Start

### Basic Usage

```python
from backend.src.process_logger import create_process_logger

# Create a logger with default settings
logger = create_process_logger()

# Start a process
logger.start_process("document.pdf", "gemini-pro", "local")

# Log processing steps
logger.log_step("DOCUMENT_LOADING", "Loading document from file", {
    "file_path": "/path/to/document.pdf",
    "file_size": "2.5MB"
})

# Log data transformations
logger.log_data_flow("CHUNKING", input_text, chunks, processing_time)

# End the process
logger.end_process("SUCCESS", {"entities_extracted": 150})
```

### Using Configuration Presets

```python
from backend.src.logging_config import create_development_config, create_production_config

# Development configuration (verbose logging)
dev_config = create_development_config()
logger = create_process_logger(
    log_level=dev_config.get_config()["log_level"],
    log_directory=dev_config.get_config()["log_directory"],
    enable_performance_tracking=True
)

# Production configuration (minimal logging, data anonymization)
prod_config = create_production_config()
logger = create_process_logger(
    log_level=prod_config.get_config()["log_level"],
    enable_data_anonymization=True
)
```

### Decorator-Based Logging

```python
from backend.src.process_logger import log_process_step

@log_process_step("ENTITY_EXTRACTION", "Extracting entities using LLM")
def extract_entities(text: str, model: str):
    # Your processing logic here
    entities = process_text(text, model)
    return entities

# The decorator automatically logs:
# - Function start and completion
# - Processing time
# - Input/output data summaries
# - Any errors that occur
```

## Configuration Options

### Logging Presets

| Preset | Description | Use Case |
|--------|-------------|----------|
| `development` | Verbose logging with performance tracking | Local development and debugging |
| `production` | Minimal logging with data anonymization | Production deployment |
| `debugging` | Maximum verbosity with detailed data | Troubleshooting issues |
| `minimal` | Warnings and errors only | Lightweight monitoring |

### Custom Configuration

```python
from backend.src.logging_config import create_custom_config

config = create_custom_config(
    log_level=logging.DEBUG,           # Logging level
    enable_console=True,               # Console output
    enable_file=True,                  # File output
    enable_performance=True,           # Performance tracking
    enable_anonymization=False,        # Data anonymization
    max_preview_length=200,           # Data preview length
    log_directory="custom_logs"        # Log directory
)
```

## Advanced Features

### Custom Hooks

Add custom logic that executes during specific events:

```python
# Performance monitoring hook
def performance_alert(data):
    if "processing_time" in data:
        time_str = data["processing_time"]
        if time_str.endswith('s'):
            time_value = float(time_str[:-1])
            if time_value > 30:
                send_alert(f"Slow processing detected: {time_value}s")

logger.add_custom_hook("performance_monitor", performance_alert)
```

### Custom Formatters

Define how log messages are formatted:

```python
def performance_formatter(message, data):
    if data and "processing_time" in data:
        time_str = data["processing_time"]
        if time_str.endswith('s') and float(time_str[:-1]) > 10:
            return f"⚠️ SLOW: {message}"
    return message

logger = create_process_logger(
    custom_formatters={"performance": performance_formatter}
)
```

### Data Anonymization

Automatically redact sensitive information:

```python
logger = create_process_logger(enable_data_anonymization=True)

# This data will be anonymized
logger.log_step("API_CALL", "Making API request", {
    "endpoint": "https://api.example.com",
    "api_key": "secret_key_123",      # Will become "***REDACTED***"
    "user_token": "token_abc",        # Will become "***REDACTED***"
    "payload_size": 1024              # Will remain as-is
})
```

## Integration with Existing Code

### Minimal Integration

Add logging to existing functions without changing their logic:

```python
# Before
def process_chunks(chunks, model):
    # existing logic
    return processed_chunks

# After
from backend.src.process_logger import process_logger

def process_chunks(chunks, model):
    process_logger.log_step("CHUNK_PROCESSING", f"Processing {len(chunks)} chunks", {
        "chunk_count": len(chunks),
        "model": model
    })
    
    # existing logic (unchanged)
    processed_chunks = existing_processing_logic(chunks, model)
    
    process_logger.log_step("CHUNK_PROCESSING_COMPLETE", "Chunk processing completed", {
        "processed_count": len(processed_chunks)
    })
    
    return processed_chunks
```

### Full Integration

For comprehensive logging throughout the workflow:

```python
from backend.src.process_logger import process_logger

def main_processing_workflow(file_path, model):
    # Start process logging
    process_logger.start_process(file_path, model, "local")
    
    try:
        # Step 1: Load document
        process_logger.log_step("DOCUMENT_LOADING", "Loading document")
        document = load_document(file_path)
        
        # Step 2: Process chunks
        process_logger.log_step("CHUNKING", "Creating chunks")
        chunks = create_chunks(document)
        
        # Log data transformation
        process_logger.log_data_flow("CHUNKING", document, chunks, processing_time)
        
        # Step 3: Extract entities
        process_logger.log_step("ENTITY_EXTRACTION", "Extracting entities")
        entities = extract_entities(chunks, model)
        
        # End process
        process_logger.end_process("SUCCESS", {
            "entities_extracted": len(entities),
            "chunks_processed": len(chunks)
        })
        
        return entities
        
    except Exception as e:
        process_logger.log_step("PROCESSING_ERROR", f"Error: {str(e)}", {
            "error_type": type(e).__name__,
            "error_message": str(e)
        }, level="ERROR")
        
        process_logger.end_process("ERROR", {"error": str(e)})
        raise
```

## Generated Outputs

### Log Files

The system generates several types of output files:

1. **Daily Log Files**: `logs/process_detailed_YYYYMMDD.log`
   - All log messages with timestamps and step numbers
   - Configurable format and detail level

2. **Process Reports**: `logs/process_report_filename_timestamp.json`
   - Comprehensive JSON report with all process data
   - Includes timeline, data lineage, and performance metrics

3. **Human-Readable Summaries**: `logs/process_summary_filename_timestamp.txt`
   - Easy-to-read process summary with statistics
   - Performance bottlenecks and data quality scores

### Report Structure

```json
{
  "process_summary": {
    "file_name": "document.pdf",
    "model": "gemini-pro",
    "status": "SUCCESS",
    "duration": "45.2s",
    "total_steps": 12
  },
  "timeline": [
    {
      "step": 1,
      "name": "DOCUMENT_LOADING",
      "timestamp": "2024-01-15T10:30:00",
      "message": "Loading document from file",
      "elapsed_time": 0.5
    }
  ],
  "data_lineage": [
    {
      "step": "CHUNKING",
      "input_summary": {"type": "string", "length": 15000},
      "output_summary": {"type": "list", "length": 25},
      "processing_time": 2.3,
      "data_quality_score": 0.95
    }
  ],
  "performance_analysis": {
    "bottlenecks": [],
    "memory_usage": [],
    "processing_speeds": {}
  }
}
```

## Performance Monitoring

### Automatic Bottleneck Detection

The system automatically detects performance issues:

- **Slow operations**: Functions taking longer than expected
- **Memory usage**: High memory consumption alerts
- **API timeouts**: External service issues
- **Data quality issues**: Low data quality scores

### Custom Performance Metrics

```python
# Log custom metrics
logger.log_custom_metric("tokens_processed", 1250, "ENTITY_EXTRACTION")
logger.log_custom_metric("api_calls_made", 5, "LLM_PROCESSING")

# Log performance bottlenecks
logger.log_performance_bottleneck("API_CALL", "SLOW_RESPONSE", {
    "response_time": 15.5,
    "expected_time": 3.0,
    "endpoint": "gemini-pro"
})
```

## Best Practices

### 1. Use Appropriate Log Levels

```python
# For debugging detailed information
logger.log_step("DETAIL", "Processing item X", data, level="DEBUG")

# For normal operations
logger.log_step("PROCESSING", "Processing chunks", data, level="INFO")

# For warnings
logger.log_step("WARNING", "Slow response detected", data, level="WARNING")

# For errors
logger.log_step("ERROR", "Failed to process", data, level="ERROR")
```

### 2. Structure Your Data

```python
# Good: Structured data
logger.log_step("ENTITY_EXTRACTION", "Extracting entities", {
    "model": "gemini-pro",
    "chunk_count": 25,
    "expected_entities": 100,
    "timeout": 30
})

# Avoid: Unstructured data
logger.log_step("ENTITY_EXTRACTION", "Extracting entities with gemini-pro from 25 chunks")
```

### 3. Use Data Flow Logging

```python
# Track data transformations
logger.log_data_flow("PROCESSING_STEP", input_data, output_data, processing_time, {
    "transformation_type": "entity_extraction",
    "confidence_threshold": 0.8
})
```

### 4. Monitor Performance

```python
# Add performance monitoring
if processing_time > expected_time:
    logger.log_performance_bottleneck("STEP_NAME", "SLOW_PROCESSING", {
        "actual_time": processing_time,
        "expected_time": expected_time,
        "difference": processing_time - expected_time
    })
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure the Python path includes the `backend/src` directory
2. **Permission Errors**: Ensure write permissions for the log directory
3. **Memory Issues**: Use data anonymization and limit preview lengths for large datasets
4. **Performance Impact**: Use appropriate log levels and disable console logging in production

### Debug Mode

Enable debug mode for maximum verbosity:

```python
config = create_debugging_config()
logger = create_process_logger(
    log_level=config.get_config()["log_level"],
    enable_performance_tracking=True,
    max_data_preview_length=1000
)
```

## Migration Guide

### From Basic Logging

If you're currently using the basic logging system:

1. Replace `ProcessLogger()` with `create_process_logger()`
2. Add configuration options as needed
3. Use the new data flow logging methods
4. Add custom hooks for specific monitoring needs

### Configuration Migration

```python
# Old way
logger = ProcessLogger()

# New way
logger = create_process_logger(
    log_level=logging.INFO,
    enable_performance_tracking=True,
    log_directory="logs"
)
```

## API Reference

### ProcessLogger Class

#### Methods

- `start_process(file_name, model, source_type, custom_metadata=None)`
- `log_step(step_name, message, data=None, level="INFO", custom_formatter=None)`
- `log_data_flow(step_name, input_data, output_data, processing_time, transformation_details=None)`
- `log_performance_bottleneck(step_name, bottleneck_type, details)`
- `log_custom_metric(metric_name, value, step_name=None, tags=None)`
- `end_process(status, final_data=None, generate_report=True)`
- `export_metrics(format="json")`
- `get_process_insights()`

### Configuration Classes

#### LoggingConfig

- `get_config()`: Get current configuration
- `update_config(updates)`: Update configuration
- `save_config(filepath)`: Save configuration to file
- `load_config(filepath)`: Load configuration from file

### Factory Functions

- `create_process_logger(**kwargs)`: Create configured logger
- `create_development_config()`: Development preset
- `create_production_config()`: Production preset
- `create_debugging_config()`: Debugging preset
- `create_minimal_config()`: Minimal preset
- `create_custom_config(**kwargs)`: Custom configuration

## Examples

See `advanced_logging_demo.py` for comprehensive examples of all features.

## Support

For issues or questions about the logging system:

1. Check the generated log files for error messages
2. Use debug mode for detailed troubleshooting
3. Review the data lineage for data transformation issues
4. Monitor performance metrics for bottlenecks

The enhanced logging system provides deep insights into your document processing pipeline while maintaining flexibility and performance. Use it to understand, optimize, and monitor your LLM Graph Builder workflows.
