"""
Custom Logging Configuration for LLM Graph Builder
This file allows you to customize the logging behavior according to your needs
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Callable

# =============================================================================
# CONFIGURATION SECTION - Customize these settings according to your needs
# =============================================================================

# Basic Configuration
LOG_LEVEL = logging.INFO  # Change to DEBUG for more detailed logs, WARNING for minimal logs
LOG_DIRECTORY = "logs"  # Directory where log files will be stored
ENABLE_CONSOLE_LOGGING = True  # Show logs in console
ENABLE_FILE_LOGGING = True  # Save logs to files
ENABLE_PERFORMANCE_TRACKING = True  # Track performance metrics
ENABLE_DATA_ANONYMIZATION = False  # Anonymize sensitive data in logs
MAX_DATA_PREVIEW_LENGTH = 300  # Maximum length for data previews in logs

# Advanced Configuration
ENABLE_DETAILED_DATA_FLOW = True  # Log detailed data transformations
ENABLE_MEMORY_MONITORING = True  # Monitor memory usage
ENABLE_CUSTOM_HOOKS = True  # Enable custom monitoring hooks
GENERATE_DETAILED_REPORTS = True  # Generate comprehensive reports
SAVE_METRICS_TO_DATABASE = False  # Save metrics to database (implement your own logic)

# Performance Thresholds (in seconds)
SLOW_STEP_THRESHOLD = 30  # Log warning if step takes longer than this
VERY_SLOW_STEP_THRESHOLD = 60  # Log error if step takes longer than this
MEMORY_THRESHOLD_MB = 1000  # Log warning if memory usage exceeds this

# Data Quality Thresholds
LOW_QUALITY_THRESHOLD = 0.5  # Log warning if data quality score is below this
HIGH_QUALITY_THRESHOLD = 0.8  # Log info if data quality score is above this

# =============================================================================
# CUSTOM FORMATTERS - Add your own message formatting logic
# =============================================================================

def performance_formatter(message: str, data: Dict[str, Any]) -> str:
    """Custom formatter for performance-related messages"""
    if data and "processing_time" in data:
        processing_time = data["processing_time"]
        if isinstance(processing_time, str) and processing_time.endswith('s'):
            time_value = float(processing_time[:-1])
            if time_value > VERY_SLOW_STEP_THRESHOLD:
                return f"🚨 VERY SLOW: {message} ({processing_time})"
            elif time_value > SLOW_STEP_THRESHOLD:
                return f"⚠️ SLOW: {message} ({processing_time})"
            elif time_value > 5:
                return f"⚡ MODERATE: {message} ({processing_time})"
            else:
                return f"🚀 FAST: {message} ({processing_time})"
    return message

def data_quality_formatter(message: str, data: Dict[str, Any]) -> str:
    """Custom formatter for data quality messages"""
    if data and "data_quality_score" in data:
        score = data["data_quality_score"]
        if score > HIGH_QUALITY_THRESHOLD:
            return f"🟢 HIGH QUALITY: {message} (score: {score:.2f})"
        elif score > LOW_QUALITY_THRESHOLD:
            return f"🟡 MEDIUM QUALITY: {message} (score: {score:.2f})"
        else:
            return f"🔴 LOW QUALITY: {message} (score: {score:.2f})"
    return message

def entity_extraction_formatter(message: str, data: Dict[str, Any]) -> str:
    """Custom formatter for entity extraction messages"""
    if data and "entities_extracted" in data:
        count = data["entities_extracted"]
        if count > 100:
            return f"🎯 RICH EXTRACTION: {message} ({count} entities)"
        elif count > 50:
            return f"📊 GOOD EXTRACTION: {message} ({count} entities)"
        elif count > 10:
            return f"📈 MODERATE EXTRACTION: {message} ({count} entities)"
        else:
            return f"📉 SPARSE EXTRACTION: {message} ({count} entities)"
    return message

# =============================================================================
# CUSTOM HOOKS - Add your own monitoring and alerting logic
# =============================================================================

def performance_monitoring_hook(data: Dict[str, Any]):
    """Monitor performance and trigger alerts"""
    if "processing_time" in data:
        processing_time = data["processing_time"]
        if isinstance(processing_time, str) and processing_time.endswith('s'):
            time_value = float(processing_time[:-1])
            if time_value > VERY_SLOW_STEP_THRESHOLD:
                # Add your alerting logic here
                print(f"🚨 CRITICAL PERFORMANCE ALERT: Step took {processing_time}")
                # send_slack_alert(f"Slow processing detected: {processing_time}")
                # send_email_alert(f"Performance issue: {data}")
            elif time_value > SLOW_STEP_THRESHOLD:
                print(f"⚠️ PERFORMANCE WARNING: Step took {processing_time}")

def data_quality_monitoring_hook(data: Dict[str, Any]):
    """Monitor data quality and trigger alerts"""
    if "data_quality_score" in data:
        score = data["data_quality_score"]
        if score < LOW_QUALITY_THRESHOLD:
            print(f"🚨 DATA QUALITY ALERT: Low quality score ({score:.2f})")
            # Add your data quality alerting logic here
            # log_to_monitoring_system(f"Low data quality: {score}")
            # trigger_data_quality_review(data)

def memory_monitoring_hook(data: Dict[str, Any]):
    """Monitor memory usage and trigger alerts"""
    if "performance" in data and "memory_mb" in data["performance"]:
        memory_mb = data["performance"]["memory_mb"]
        if memory_mb > MEMORY_THRESHOLD_MB:
            print(f"🚨 MEMORY ALERT: High memory usage ({memory_mb:.1f}MB)")
            # Add your memory alerting logic here
            # trigger_memory_cleanup()
            # alert_infrastructure_team(f"High memory usage: {memory_mb}MB")

def entity_extraction_monitoring_hook(data: Dict[str, Any]):
    """Monitor entity extraction quality"""
    if "entities_extracted" in data and "input_chunks" in data:
        entities = data["entities_extracted"]
        chunks = data["input_chunks"]
        if chunks > 0:
            entities_per_chunk = entities / chunks
            if entities_per_chunk < 1:
                print(f"⚠️ LOW ENTITY EXTRACTION: {entities_per_chunk:.2f} entities per chunk")
                # Add your entity extraction monitoring logic here
                # review_extraction_quality(data)
            elif entities_per_chunk > 10:
                print(f"🎯 HIGH ENTITY EXTRACTION: {entities_per_chunk:.2f} entities per chunk")

def custom_metric_hook(data: Dict[str, Any]):
    """Process custom metrics"""
    if "metric_name" in data and "value" in data:
        metric_name = data["metric_name"]
        value = data["value"]
        
        # Add your custom metric processing logic here
        # save_metric_to_database(metric_name, value, data.get("timestamp"))
        # send_metric_to_monitoring_service(metric_name, value)
        
        print(f"📊 CUSTOM METRIC: {metric_name} = {value}")

# =============================================================================
# STEP-SPECIFIC CONFIGURATIONS
# =============================================================================

# Configure which steps should have detailed logging
DETAILED_LOGGING_STEPS = [
    "ENTITY_EXTRACTION",
    "RELATIONSHIP_EXTRACTION", 
    "CHUNKING",
    "EMBEDDING_CREATION",
    "NEO4J_SAVE"
]

# Configure which steps should have performance monitoring
PERFORMANCE_MONITORED_STEPS = [
    "ENTITY_EXTRACTION",
    "CHUNKING",
    "EMBEDDING_CREATION",
    "NEO4J_SAVE"
]

# Configure which steps should have data quality monitoring
DATA_QUALITY_MONITORED_STEPS = [
    "ENTITY_EXTRACTION",
    "RELATIONSHIP_EXTRACTION",
    "DATA_CLEANING"
]

# =============================================================================
# EXPORT CONFIGURATION - Create the configuration object
# =============================================================================

def create_custom_logging_config():
    """Create the custom logging configuration"""
    config = {
        "log_level": LOG_LEVEL,
        "log_directory": LOG_DIRECTORY,
        "enable_console_logging": ENABLE_CONSOLE_LOGGING,
        "enable_file_logging": ENABLE_FILE_LOGGING,
        "enable_performance_tracking": ENABLE_PERFORMANCE_TRACKING,
        "enable_data_anonymization": ENABLE_DATA_ANONYMIZATION,
        "max_data_preview_length": MAX_DATA_PREVIEW_LENGTH,
        "track_memory_usage": ENABLE_MEMORY_MONITORING,
        "generate_detailed_reports": GENERATE_DETAILED_REPORTS,
        "detailed_logging_steps": DETAILED_LOGGING_STEPS,
        "performance_monitored_steps": PERFORMANCE_MONITORED_STEPS,
        "data_quality_monitored_steps": DATA_QUALITY_MONITORED_STEPS,
        "thresholds": {
            "slow_step": SLOW_STEP_THRESHOLD,
            "very_slow_step": VERY_SLOW_STEP_THRESHOLD,
            "memory_mb": MEMORY_THRESHOLD_MB,
            "low_quality": LOW_QUALITY_THRESHOLD,
            "high_quality": HIGH_QUALITY_THRESHOLD
        }
    }
    return config

def get_custom_formatters() -> Dict[str, Callable]:
    """Get custom formatters"""
    formatters = {}
    
    if ENABLE_PERFORMANCE_TRACKING:
        formatters["performance"] = performance_formatter
    
    if ENABLE_DETAILED_DATA_FLOW:
        formatters["data_quality"] = data_quality_formatter
        formatters["entity_extraction"] = entity_extraction_formatter
    
    return formatters

def get_custom_hooks() -> Dict[str, Callable]:
    """Get custom hooks"""
    hooks = {}
    
    if ENABLE_CUSTOM_HOOKS:
        if ENABLE_PERFORMANCE_TRACKING:
            hooks["performance_monitor"] = performance_monitoring_hook
        
        if ENABLE_DETAILED_DATA_FLOW:
            hooks["data_quality_monitor"] = data_quality_monitoring_hook
            hooks["entity_extraction_monitor"] = entity_extraction_monitoring_hook
        
        if ENABLE_MEMORY_MONITORING:
            hooks["memory_monitor"] = memory_monitoring_hook
            
        hooks["custom_metric_processor"] = custom_metric_hook
    
    return hooks

# =============================================================================
# USAGE EXAMPLE
# =============================================================================

def example_usage():
    """Example of how to use the custom configuration"""
    from src.process_logger import create_process_logger
    
    # Create logger with custom configuration
    config = create_custom_logging_config()
    logger = create_process_logger(
        log_level=config["log_level"],
        log_directory=config["log_directory"],
        enable_performance_tracking=config["enable_performance_tracking"],
        enable_data_anonymization=config["enable_data_anonymization"],
        custom_formatters=get_custom_formatters()
    )
    
    # Add custom hooks
    for hook_name, hook_func in get_custom_hooks().items():
        logger.add_custom_hook(hook_name, hook_func)
    
    return logger

# =============================================================================
# ADDITIONAL CUSTOMIZATION EXAMPLES
# =============================================================================

def create_development_logger():
    """Create a logger optimized for development"""
    global LOG_LEVEL, ENABLE_CONSOLE_LOGGING, ENABLE_PERFORMANCE_TRACKING, MAX_DATA_PREVIEW_LENGTH
    
    LOG_LEVEL = logging.DEBUG
    ENABLE_CONSOLE_LOGGING = True
    ENABLE_PERFORMANCE_TRACKING = True
    MAX_DATA_PREVIEW_LENGTH = 500
    
    return example_usage()

def create_production_logger():
    """Create a logger optimized for production"""
    global LOG_LEVEL, ENABLE_CONSOLE_LOGGING, ENABLE_DATA_ANONYMIZATION, MAX_DATA_PREVIEW_LENGTH
    
    LOG_LEVEL = logging.INFO
    ENABLE_CONSOLE_LOGGING = False
    ENABLE_DATA_ANONYMIZATION = True
    MAX_DATA_PREVIEW_LENGTH = 100
    
    return example_usage()

def create_debugging_logger():
    """Create a logger optimized for debugging"""
    global LOG_LEVEL, ENABLE_DETAILED_DATA_FLOW, ENABLE_MEMORY_MONITORING, MAX_DATA_PREVIEW_LENGTH
    
    LOG_LEVEL = logging.DEBUG
    ENABLE_DETAILED_DATA_FLOW = True
    ENABLE_MEMORY_MONITORING = True
    MAX_DATA_PREVIEW_LENGTH = 1000
    
    return example_usage()

# Default configuration
default_config = create_custom_logging_config()
default_formatters = get_custom_formatters()
default_hooks = get_custom_hooks()
