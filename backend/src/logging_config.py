"""
LLM Graph Builder - Advanced Logging Configuration
Provides configuration options and presets for the logging system
"""

import logging
from typing import Dict, Any, Callable, Optional
from pathlib import Path
import json
from datetime import datetime

# Logging configuration presets
LOGGING_PRESETS = {
    "development": {
        "log_level": logging.DEBUG,
        "enable_console_logging": True,
        "enable_file_logging": True,
        "enable_performance_tracking": True,
        "enable_data_anonymization": False,
        "max_data_preview_length": 500,
        "track_memory_usage": True
    },
    "production": {
        "log_level": logging.INFO,
        "enable_console_logging": False,
        "enable_file_logging": True,
        "enable_performance_tracking": True,
        "enable_data_anonymization": True,
        "max_data_preview_length": 100,
        "track_memory_usage": False
    },
    "debugging": {
        "log_level": logging.DEBUG,
        "enable_console_logging": True,
        "enable_file_logging": True,
        "enable_performance_tracking": True,
        "enable_data_anonymization": False,
        "max_data_preview_length": 1000,
        "track_memory_usage": True
    },
    "minimal": {
        "log_level": logging.WARNING,
        "enable_console_logging": True,
        "enable_file_logging": False,
        "enable_performance_tracking": False,
        "enable_data_anonymization": False,
        "max_data_preview_length": 50,
        "track_memory_usage": False
    }
}

class LoggingConfig:
    """Advanced logging configuration manager"""
    
    def __init__(self, preset: str = "development", custom_config: Dict[str, Any] = None):
        self.preset = preset
        self.config = LOGGING_PRESETS.get(preset, LOGGING_PRESETS["development"]).copy()
        
        # Apply custom configuration
        if custom_config:
            self.config.update(custom_config)
            
        # Setup paths
        self.log_directory = Path(self.config.get("log_directory", "logs"))
        self.log_directory.mkdir(exist_ok=True)
        
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration"""
        return self.config.copy()
        
    def update_config(self, updates: Dict[str, Any]):
        """Update the configuration"""
        self.config.update(updates)
        
    def save_config(self, filepath: str = None):
        """Save current configuration to file"""
        if not filepath:
            filepath = self.log_directory / "logging_config.json"
            
        config_to_save = self.config.copy()
        config_to_save["preset"] = self.preset
        config_to_save["created_at"] = datetime.now().isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(config_to_save, f, indent=2)
            
    def load_config(self, filepath: str):
        """Load configuration from file"""
        with open(filepath, 'r') as f:
            loaded_config = json.load(f)
            
        self.preset = loaded_config.get("preset", "custom")
        self.config = loaded_config
        
    def get_custom_formatters(self) -> Dict[str, Callable]:
        """Get custom formatters based on configuration"""
        formatters = {}
        
        # Add performance formatter
        if self.config.get("enable_performance_tracking", False):
            formatters["performance"] = self._performance_formatter
            
        # Add data quality formatter
        if self.config.get("track_data_quality", True):
            formatters["data_quality"] = self._data_quality_formatter
            
        return formatters
        
    def _performance_formatter(self, message: str, data: Dict[str, Any]) -> str:
        """Format performance-related messages"""
        if data and "processing_time" in data:
            processing_time = data["processing_time"]
            if isinstance(processing_time, str) and processing_time.endswith('s'):
                time_value = float(processing_time[:-1])
                if time_value > 10:
                    return f"⚠️ SLOW: {message} ({processing_time})"
                elif time_value > 5:
                    return f"⚡ MODERATE: {message} ({processing_time})"
                else:
                    return f"🚀 FAST: {message} ({processing_time})"
        return message
        
    def _data_quality_formatter(self, message: str, data: Dict[str, Any]) -> str:
        """Format data quality messages"""
        if data and "data_quality_score" in data:
            score = data["data_quality_score"]
            if score > 0.8:
                return f"🟢 HIGH QUALITY: {message} (score: {score:.2f})"
            elif score > 0.6:
                return f"🟡 MEDIUM QUALITY: {message} (score: {score:.2f})"
            else:
                return f"🔴 LOW QUALITY: {message} (score: {score:.2f})"
        return message
        
    def get_custom_hooks(self) -> Dict[str, Callable]:
        """Get custom hooks based on configuration"""
        hooks = {}
        
        # Performance monitoring hook
        if self.config.get("enable_performance_tracking", False):
            hooks["performance_monitor"] = self._performance_monitor_hook
            
        # Data quality monitoring hook
        if self.config.get("track_data_quality", True):
            hooks["data_quality_monitor"] = self._data_quality_monitor_hook
            
        # Memory usage monitoring hook
        if self.config.get("track_memory_usage", False):
            hooks["memory_monitor"] = self._memory_monitor_hook
            
        return hooks
        
    def _performance_monitor_hook(self, data: Dict[str, Any]):
        """Monitor performance metrics"""
        if "processing_time" in data:
            processing_time = data["processing_time"]
            if isinstance(processing_time, str) and processing_time.endswith('s'):
                time_value = float(processing_time[:-1])
                if time_value > 30:
                    print(f"🚨 PERFORMANCE ALERT: Step took {processing_time} - Consider optimization")
                    
    def _data_quality_monitor_hook(self, data: Dict[str, Any]):
        """Monitor data quality"""
        if "data_quality_score" in data:
            score = data["data_quality_score"]
            if score < 0.5:
                print(f"🚨 DATA QUALITY ALERT: Low quality score ({score:.2f}) - Check data processing")
                
    def _memory_monitor_hook(self, data: Dict[str, Any]):
        """Monitor memory usage"""
        if "performance" in data and "memory_mb" in data["performance"]:
            memory_mb = data["performance"]["memory_mb"]
            if memory_mb > 1000:  # 1GB threshold
                print(f"🚨 MEMORY ALERT: High memory usage ({memory_mb:.1f}MB)")

# Configuration factory functions
def create_development_config() -> LoggingConfig:
    """Create development configuration"""
    return LoggingConfig("development")

def create_production_config() -> LoggingConfig:
    """Create production configuration"""
    return LoggingConfig("production")

def create_debugging_config() -> LoggingConfig:
    """Create debugging configuration"""
    return LoggingConfig("debugging")

def create_minimal_config() -> LoggingConfig:
    """Create minimal configuration"""
    return LoggingConfig("minimal")

def create_custom_config(
    log_level: int = logging.INFO,
    enable_console: bool = True,
    enable_file: bool = True,
    enable_performance: bool = True,
    enable_anonymization: bool = False,
    max_preview_length: int = 200,
    log_directory: str = "logs"
) -> LoggingConfig:
    """Create custom configuration"""
    custom_config = {
        "log_level": log_level,
        "enable_console_logging": enable_console,
        "enable_file_logging": enable_file,
        "enable_performance_tracking": enable_performance,
        "enable_data_anonymization": enable_anonymization,
        "max_data_preview_length": max_preview_length,
        "log_directory": log_directory
    }
    
    return LoggingConfig("custom", custom_config)

# Default configuration
default_config = create_development_config()
