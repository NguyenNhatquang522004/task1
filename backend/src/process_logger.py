"""
LLM Graph Builder - Advanced Process Logging System
Tracks the complete document processing workflow with deep insights and customization
"""

import logging
import time
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
import functools
import traceback
from pathlib import Path

class ProcessLogger:
    """Advanced process logger for LLM Graph Builder with deep insights and customization"""
    
    def __init__(self, 
                 log_level=logging.INFO,
                 log_directory: str = "logs",
                 enable_file_logging: bool = True,
                 enable_console_logging: bool = True,
                 custom_formatters: Dict[str, Callable] = None,
                 data_anonymization: bool = False,
                 max_data_preview_length: int = 200):
        
        self.log_directory = Path(log_directory)
        self.enable_file_logging = enable_file_logging
        self.enable_console_logging = enable_console_logging
        self.custom_formatters = custom_formatters or {}
        self.data_anonymization = data_anonymization
        self.max_data_preview_length = max_data_preview_length
        
        # Create logs directory
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        self.setup_logging(log_level)
        self.process_start_time = None
        self.step_times = {}
        self.process_data = {}
        self.step_counter = 0
        self.performance_metrics = {}
        self.data_lineage = []
        self.custom_hooks = {}
        
        
    def setup_logging(self, log_level):
        """Setup advanced logging configuration with customization options"""
        
        # Create a custom formatter that handles missing step_num gracefully
        class SafeFormatter(logging.Formatter):
            def format(self, record):
                # Provide default step_num if not present
                if not hasattr(record, 'step_num'):
                    record.step_num = '-'
                return super().format(record)
        
        handlers = []
        
        # File handler
        if self.enable_file_logging:
            file_handler = logging.FileHandler(
                self.log_directory / f'process_detailed_{datetime.now().strftime("%Y%m%d")}.log',
                encoding='utf-8'
            )
            file_handler.setFormatter(SafeFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - [STEP %(step_num)s] %(message)s'
            ))
            handlers.append(file_handler)
            
        # Console handler
        if self.enable_console_logging:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(SafeFormatter(
                '%(asctime)s - [STEP %(step_num)s] %(levelname)s - %(message)s'
            ))
            handlers.append(console_handler)
        
        logging.basicConfig(
            level=log_level,
            handlers=handlers,
            force=True
        )
        
        # Create custom logger
        self.logger = logging.getLogger('LLMGraphBuilder')
        
    def add_custom_hook(self, hook_name: str, hook_function: Callable):
        """Add custom hook for processing steps"""
        self.custom_hooks[hook_name] = hook_function
        
    def remove_custom_hook(self, hook_name: str):
        """Remove custom hook"""
        if hook_name in self.custom_hooks:
            del self.custom_hooks[hook_name]
            
    def _execute_hooks(self, hook_type: str, data: Dict[str, Any]):
        """Execute registered hooks"""
        for hook_name, hook_function in self.custom_hooks.items():
            if hook_type in hook_name:
                try:
                    hook_function(data)
                except Exception as e:
                    self.logger.warning(f"Hook {hook_name} failed: {str(e)}")
                    
    def _anonymize_data(self, data: Any) -> Any:
        """Anonymize sensitive data if enabled"""
        if not self.data_anonymization:
            return data
            
        if isinstance(data, dict):
            anonymized = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in ['password', 'token', 'key', 'secret']):
                    anonymized[key] = "***REDACTED***"
                else:
                    anonymized[key] = self._anonymize_data(value)
            return anonymized
        elif isinstance(data, list):
            return [self._anonymize_data(item) for item in data]
        else:
            return data
        
    def start_process(self, file_name: str, model: str, source_type: str, custom_metadata: Dict[str, Any] = None):
        """Initialize advanced process logging with custom metadata"""
        self.process_start_time = time.time()
        self.step_counter = 0
        self.process_data = {
            'file_name': file_name,
            'model': model,
            'source_type': source_type,
            'start_time': datetime.now().isoformat(),
            'custom_metadata': custom_metadata or {},
            'steps': [],
            'performance_metrics': {},
            'data_lineage': []
        }
        
        # Initialize performance tracking
        self.performance_metrics = {
            'memory_usage': [],
            'processing_speeds': {},
            'bottlenecks': []
        }
        
        start_data = {
            'file_name': file_name,
            'model': model,
            'source_type': source_type,
            'custom_metadata': custom_metadata or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.log_step(
            "PROCESS_START",
            f"🚀 Starting document processing for: {file_name}",
            start_data
        )
        
        # Execute start hooks
        self._execute_hooks("start", start_data)
        
    def log_step(self, step_name: str, message: str, data: Dict[str, Any] = None, level: str = "INFO", 
                 custom_formatter: str = None, track_performance: bool = True):
        """Log a processing step with advanced features"""
        self.step_counter += 1
        step_time = time.time()
        
        # Apply custom formatter if specified
        if custom_formatter and custom_formatter in self.custom_formatters:
            message = self.custom_formatters[custom_formatter](message, data)
            
        # Anonymize data if enabled
        processed_data = self._anonymize_data(data) if data else {}
        
        step_info = {
            'step_number': self.step_counter,
            'step_name': step_name,
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'data': processed_data,
            'elapsed_time': step_time - self.process_start_time if self.process_start_time else 0,
            'level': level
        }
        
        # Track performance if enabled
        if track_performance:
            step_info['performance'] = self._capture_performance_metrics(step_name)
            
        self.process_data['steps'].append(step_info)
        
        # Enhanced log message
        log_message = f"[{step_name}] {message}"
        if processed_data:
            data_summary = self._create_data_summary(processed_data)
            log_message += f" | {data_summary}"
            
        # Add step number to logger context
        extra = {'step_num': self.step_counter}
        
        if level == "ERROR":
            self.logger.error(log_message, extra=extra)
        elif level == "WARNING":
            self.logger.warning(log_message, extra=extra)
        elif level == "DEBUG":
            self.logger.debug(log_message, extra=extra)
        else:
            self.logger.info(log_message, extra=extra)
            
        self.step_times[step_name] = step_time
        
        # Execute step hooks
        self._execute_hooks("step", step_info)
        
    def _capture_performance_metrics(self, step_name: str) -> Dict[str, Any]:
        """Capture performance metrics for a step"""
        import psutil
        import os
        
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            metrics = {
                'memory_mb': memory_info.rss / 1024 / 1024,
                'cpu_percent': process.cpu_percent(),
                'step_duration': time.time() - self.step_times.get(step_name, time.time())
            }
            
            self.performance_metrics['memory_usage'].append({
                'step': step_name,
                'memory_mb': metrics['memory_mb'],
                'timestamp': datetime.now().isoformat()
            })
            
            return metrics
        except Exception as e:
            return {'error': f"Could not capture metrics: {str(e)}"}
            
    def _create_data_summary(self, data: Dict[str, Any]) -> str:
        """Create a concise data summary for logging"""
        if not data:
            return "No data"
            
        summary_parts = []
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                summary_parts.append(f"{key}: {type(value).__name__}({len(value)})")
            elif isinstance(value, str):
                preview = value[:50] + "..." if len(value) > 50 else value
                summary_parts.append(f"{key}: '{preview}'")
            else:
                summary_parts.append(f"{key}: {value}")
                
        return " | ".join(summary_parts[:5])  # Limit to 5 items for readability
        
    def log_data_flow(self, step_name: str, input_data: Any, output_data: Any, processing_time: float, 
                     transformation_details: Dict[str, Any] = None):
        """Log data flow between processing steps with enhanced analysis"""
        
        # Create data lineage entry
        lineage_entry = {
            'step': step_name,
            'timestamp': datetime.now().isoformat(),
            'input_summary': self._summarize_data(input_data),
            'output_summary': self._summarize_data(output_data),
            'processing_time': processing_time,
            'transformation_type': self._analyze_transformation(input_data, output_data),
            'transformation_details': transformation_details or {}
        }
        
        self.data_lineage.append(lineage_entry)
        
        self.log_step(
            f"{step_name}_DATA_FLOW",
            f"📊 Data flow for {step_name} - {lineage_entry['transformation_type']}",
            {
                'input_summary': lineage_entry['input_summary'],
                'output_summary': lineage_entry['output_summary'],
                'processing_time': f"{processing_time:.2f}s",
                'transformation_type': lineage_entry['transformation_type'],
                'transformation_details': transformation_details or {},
                'data_quality_score': self._calculate_data_quality_score(input_data, output_data)
            }
        )
        
    def _calculate_data_quality_score(self, input_data: Any, output_data: Any) -> float:
        """Calculate a simple data quality score"""
        try:
            input_size = len(input_data) if hasattr(input_data, '__len__') else 1
            output_size = len(output_data) if hasattr(output_data, '__len__') else 1
            
            if input_size == 0:
                return 0.0
                
            # Simple quality score based on data retention
            retention_score = min(output_size / input_size, 1.0)
            
            # Check for empty or null outputs
            if output_size == 0 or output_data is None:
                return 0.0
                
            return retention_score
        except:
            return 0.5  # Default score if calculation fails
            
    def log_performance_bottleneck(self, step_name: str, bottleneck_type: str, details: Dict[str, Any]):
        """Log performance bottlenecks for optimization"""
        bottleneck_info = {
            'step': step_name,
            'type': bottleneck_type,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        
        self.performance_metrics['bottlenecks'].append(bottleneck_info)
        
        self.log_step(
            f"{step_name}_BOTTLENECK",
            f"⚠️ Performance bottleneck detected in {step_name}: {bottleneck_type}",
            bottleneck_info,
            level="WARNING"
        )
        
    def log_custom_metric(self, metric_name: str, value: Any, step_name: str = None, tags: Dict[str, str] = None):
        """Log custom metrics for monitoring"""
        metric_info = {
            'metric_name': metric_name,
            'value': value,
            'step_name': step_name,
            'timestamp': datetime.now().isoformat(),
            'tags': tags or {}
        }
        
        if 'custom_metrics' not in self.process_data:
            self.process_data['custom_metrics'] = []
            
        self.process_data['custom_metrics'].append(metric_info)
        
        self.log_step(
            f"CUSTOM_METRIC_{metric_name.upper()}",
            f"📈 Custom metric: {metric_name} = {value}",
            metric_info,
            level="DEBUG"
        )
        
    def _summarize_data(self, data: Any) -> Dict[str, Any]:
        """Create an enhanced summary of data for logging"""
        if data is None:
            return {'type': 'None', 'value': None}
            
        if isinstance(data, list):
            summary = {
                'type': 'list',
                'length': len(data),
                'is_empty': len(data) == 0,
                'first_item_type': type(data[0]).__name__ if len(data) > 0 else None
            }
            
            # Add sample data
            if len(data) > 0:
                sample_size = min(3, len(data))
                summary['sample'] = [self._get_item_preview(item) for item in data[:sample_size]]
                
            # Add type distribution for mixed lists
            if len(data) > 1:
                type_counts = {}
                for item in data[:100]:  # Sample first 100 items
                    item_type = type(item).__name__
                    type_counts[item_type] = type_counts.get(item_type, 0) + 1
                summary['type_distribution'] = type_counts
                
            return summary
            
        elif isinstance(data, dict):
            summary = {
                'type': 'dict',
                'size': len(data),
                'is_empty': len(data) == 0,
                'keys': list(data.keys())[:10]
            }
            
            # Add value type distribution
            if data:
                value_types = {}
                for key, value in list(data.items())[:50]:  # Sample first 50 items
                    value_type = type(value).__name__
                    value_types[value_type] = value_types.get(value_type, 0) + 1
                summary['value_type_distribution'] = value_types
                
            return summary
            
        elif isinstance(data, str):
            return {
                'type': 'string',
                'length': len(data),
                'is_empty': len(data) == 0,
                'preview': data[:self.max_data_preview_length] + "..." if len(data) > self.max_data_preview_length else data,
                'word_count': len(data.split()) if data else 0
            }
            
        elif isinstance(data, (int, float)):
            return {
                'type': type(data).__name__,
                'value': data,
                'is_positive': data > 0,
                'is_zero': data == 0
            }
            
        else:
            return {
                'type': type(data).__name__,
                'str_representation': str(data)[:self.max_data_preview_length],
                'size': len(str(data))
            }
            
    def _get_item_preview(self, item: Any) -> Any:
        """Get a preview of an item for logging"""
        if isinstance(item, str):
            return item[:50] + "..." if len(item) > 50 else item
        elif isinstance(item, dict):
            return {k: "..." for k in list(item.keys())[:3]}
        elif isinstance(item, list):
            return f"[{len(item)} items]"
        else:
            return str(item)[:100]
            
    def _analyze_transformation(self, input_data: Any, output_data: Any) -> str:
        """Analyze how data was transformed with enhanced detail"""
        input_type = type(input_data).__name__
        output_type = type(output_data).__name__
        
        # Basic type transformation
        if input_type != output_type:
            return f"Type change: {input_type} -> {output_type}"
            
        # Same type transformations
        if isinstance(input_data, (list, dict, str)):
            input_size = len(input_data) if hasattr(input_data, '__len__') else 0
            output_size = len(output_data) if hasattr(output_data, '__len__') else 0
            
            if input_size == output_size:
                return f"Same size {input_type} transformation ({input_size} items)"
            elif output_size > input_size:
                return f"Expansion: {input_type} {input_size} -> {output_size} items"
            else:
                return f"Reduction: {input_type} {input_size} -> {output_size} items"
                
        return f"Same type transformation: {input_type}"
            
    def end_process(self, status: str, final_data: Dict[str, Any] = None, generate_report: bool = True):
        """End process logging with comprehensive analysis"""
        total_time = time.time() - self.process_start_time if self.process_start_time else 0
        
        # Calculate process statistics
        process_stats = self._calculate_process_statistics(total_time)
        
        self.process_data.update({
            'end_time': datetime.now().isoformat(),
            'total_processing_time': f"{total_time:.2f}s",
            'final_status': status,
            'final_data': final_data or {},
            'total_steps': self.step_counter,
            'process_statistics': process_stats,
            'data_lineage': self.data_lineage,
            'performance_metrics': self.performance_metrics
        })
        
        end_data = {
            'total_time': f"{total_time:.2f}s",
            'total_steps': self.step_counter,
            'final_data': final_data or {},
            'status': status,
            'process_statistics': process_stats
        }
        
        self.log_step(
            "PROCESS_END",
            f"✅ Process completed with status: {status}",
            end_data
        )
        
        # Execute end hooks
        self._execute_hooks("end", end_data)
        
        # Generate comprehensive report
        if generate_report:
            self._generate_comprehensive_report()
            
        return process_stats
        
    def _calculate_process_statistics(self, total_time: float) -> Dict[str, Any]:
        """Calculate comprehensive process statistics"""
        stats = {
            'total_time': total_time,
            'total_steps': self.step_counter,
            'average_step_time': total_time / self.step_counter if self.step_counter > 0 else 0,
            'step_distribution': {},
            'error_count': 0,
            'warning_count': 0,
            'data_quality_scores': []
        }
        
        # Analyze step distribution
        step_types = {}
        for step in self.process_data['steps']:
            step_type = step['step_name'].split('_')[0]
            step_types[step_type] = step_types.get(step_type, 0) + 1
            
            # Count errors and warnings
            if step.get('level') == 'ERROR':
                stats['error_count'] += 1
            elif step.get('level') == 'WARNING':
                stats['warning_count'] += 1
                
        stats['step_distribution'] = step_types
        
        # Calculate data quality scores
        for lineage in self.data_lineage:
            if 'data_quality_score' in lineage:
                stats['data_quality_scores'].append(lineage['data_quality_score'])
                
        if stats['data_quality_scores']:
            stats['average_data_quality'] = sum(stats['data_quality_scores']) / len(stats['data_quality_scores'])
        else:
            stats['average_data_quality'] = 1.0
            
        return stats
        
    def _generate_comprehensive_report(self):
        """Generate a comprehensive process report"""
        report_filename = f"process_report_{self.process_data['file_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.log_directory / report_filename
        
        # Create detailed report
        report = {
            'process_summary': {
                'file_name': self.process_data['file_name'],
                'model': self.process_data['model'],
                'source_type': self.process_data['source_type'],
                'status': self.process_data['final_status'],
                'duration': self.process_data['total_processing_time'],
                'total_steps': self.step_counter
            },
            'timeline': [
                {
                    'step': step['step_number'],
                    'name': step['step_name'],
                    'timestamp': step['timestamp'],
                    'message': step['message'],
                    'elapsed_time': step['elapsed_time']
                }
                for step in self.process_data['steps']
            ],
            'data_lineage': self.data_lineage,
            'performance_analysis': {
                'bottlenecks': self.performance_metrics.get('bottlenecks', []),
                'memory_usage': self.performance_metrics.get('memory_usage', []),
                'processing_speeds': self.performance_metrics.get('processing_speeds', {})
            },
            'statistics': self.process_data.get('process_statistics', {}),
            'custom_metrics': self.process_data.get('custom_metrics', [])
        }
        
        # Save detailed report
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
        # Generate human-readable summary
        self._generate_human_readable_summary(report)
        
        self.logger.info(f"📊 Comprehensive process report saved to: {report_path}")
        
    def _generate_human_readable_summary(self, report: Dict[str, Any]):
        """Generate human-readable process summary"""
        summary = f"""
        
🔍 COMPREHENSIVE PROCESS REPORT FOR: {report['process_summary']['file_name']}
{'='*80}
📄 File: {report['process_summary']['file_name']}
🤖 Model: {report['process_summary']['model']}
📊 Source Type: {report['process_summary']['source_type']}
⏱️  Total Duration: {report['process_summary']['duration']}
📈 Final Status: {report['process_summary']['status']}
� Total Steps: {report['process_summary']['total_steps']}

📋 TIMELINE SUMMARY:
"""
        
        # Add timeline
        for item in report['timeline']:
            status_emoji = "✅" if "COMPLETE" in item['name'] else "❌" if "ERROR" in item['name'] else "🔄"
            summary += f"  {item['step']:2d}. {status_emoji} [{item['name']}] {item['message']}\n"
            
        # Add performance analysis
        if report['performance_analysis']['bottlenecks']:
            summary += f"\n⚠️  PERFORMANCE BOTTLENECKS DETECTED:\n"
            for bottleneck in report['performance_analysis']['bottlenecks']:
                summary += f"  - {bottleneck['step']}: {bottleneck['type']}\n"
                
        # Add data quality summary
        stats = report['statistics']
        if stats.get('average_data_quality') is not None:
            quality_score = stats['average_data_quality']
            quality_emoji = "🟢" if quality_score > 0.8 else "🟡" if quality_score > 0.6 else "🔴"
            summary += f"\n{quality_emoji} DATA QUALITY SCORE: {quality_score:.2f}\n"
            
        summary += f"\n{'='*80}\n"
        
        # Save human-readable summary
        summary_path = self.log_directory / f"process_summary_{report['process_summary']['file_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        self.logger.info(summary)
        
    def export_metrics(self, format: str = "json") -> str:
        """Export process metrics in various formats"""
        if format == "json":
            return json.dumps(self.process_data, indent=2)
        elif format == "csv":
            return self._export_to_csv()
        else:
            raise ValueError(f"Unsupported export format: {format}")
            
    def _export_to_csv(self) -> str:
        """Export process data to CSV format"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['Step', 'Name', 'Timestamp', 'Message', 'Elapsed Time', 'Level'])
        
        # Write data
        for step in self.process_data['steps']:
            writer.writerow([
                step['step_number'],
                step['step_name'],
                step['timestamp'],
                step['message'],
                step['elapsed_time'],
                step.get('level', 'INFO')
            ])
            
        return output.getvalue()
        
    def get_process_insights(self) -> Dict[str, Any]:
        """Get insights about the current process"""
        return {
            'current_step': self.step_counter,
            'elapsed_time': time.time() - self.process_start_time if self.process_start_time else 0,
            'recent_steps': self.process_data['steps'][-5:] if len(self.process_data['steps']) > 0 else [],
            'performance_summary': {
                'bottlenecks': len(self.performance_metrics.get('bottlenecks', [])),
                'memory_usage': self.performance_metrics.get('memory_usage', [])[-1] if self.performance_metrics.get('memory_usage') else None
            }
        }

def log_process_step(step_name: str, description: str = "", track_data_flow: bool = True):
    """Enhanced decorator to automatically log function execution with data flow tracking"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a new logger instance for this function
            logger = ProcessLogger()
            
            # Initialize the process data if not already done
            if not hasattr(logger, 'process_data') or not logger.process_data:
                logger.process_data = {
                    'steps': [],
                    'file_name': f"{func.__name__}_execution",
                    'model': 'decorator',
                    'source_type': 'function',
                    'custom_metadata': {},
                    'start_time': time.time()
                }
            
            start_time = time.time()
            
            # Capture input data for analysis
            input_data = {'args': args, 'kwargs': kwargs} if track_data_flow else None
            
            # Log function start
            logger.log_step(
                f"{step_name}_START",
                f"🔄 Starting {description or func.__name__}",
                {
                    'function': func.__name__,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys()),
                    'input_preview': logger._summarize_data(input_data) if input_data else None
                }
            )
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Log function completion
                processing_time = time.time() - start_time
                
                completion_data = {
                    'function': func.__name__,
                    'processing_time': f"{processing_time:.2f}s",
                    'result_type': type(result).__name__,
                    'success': True,
                    'result_preview': logger._summarize_data(result) if track_data_flow else None
                }
                
                logger.log_step(
                    f"{step_name}_COMPLETE",
                    f"✅ Completed {description or func.__name__}",
                    completion_data
                )
                
                # Log data flow if enabled
                if track_data_flow and input_data:
                    logger.log_data_flow(
                        step_name,
                        input_data,
                        result,
                        processing_time
                    )
                
                # Check for performance issues
                if processing_time > 30:  # 30 seconds threshold
                    logger.log_performance_bottleneck(
                        step_name,
                        "SLOW_EXECUTION",
                        {
                            'function': func.__name__,
                            'processing_time': processing_time,
                            'threshold': 30
                        }
                    )
                
                return result
                
            except Exception as e:
                # Log function error
                processing_time = time.time() - start_time
                error_data = {
                    'function': func.__name__,
                    'processing_time': f"{processing_time:.2f}s",
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'traceback': traceback.format_exc(),
                    'success': False
                }
                
                logger.log_step(
                    f"{step_name}_ERROR",
                    f"❌ Error in {description or func.__name__}: {str(e)}",
                    error_data,
                    level="ERROR"
                )
                
                # Log as bottleneck if it's a performance-related error
                if any(keyword in str(e).lower() for keyword in ['timeout', 'memory', 'resource']):
                    logger.log_performance_bottleneck(
                        step_name,
                        "ERROR_BOTTLENECK",
                        error_data
                    )
                
                raise
                
        return wrapper
    return decorator

# Enhanced global process logger with configuration options
def create_process_logger(
    log_level=logging.INFO,
    log_directory: str = "logs",
    enable_performance_tracking: bool = True,
    enable_data_anonymization: bool = False,
    custom_formatters: Dict[str, Callable] = None
) -> ProcessLogger:
    """Create a configured process logger instance"""
    
    logger = ProcessLogger(
        log_level=log_level,
        log_directory=log_directory,
        enable_file_logging=True,
        enable_console_logging=True,
        custom_formatters=custom_formatters,
        data_anonymization=enable_data_anonymization
    )
    
    # Add default custom formatters
    if not custom_formatters:
        logger.add_custom_hook("performance_alert", lambda data: print(f"⚠️ Performance Alert: {data}"))
        logger.add_custom_hook("data_quality_check", lambda data: print(f"📊 Data Quality: {data}"))
    
    return logger

# Utility functions for easy integration
def log_processing_step(step_name: str, message: str, data: Dict[str, Any] = None):
    """Quick logging function for processing steps"""
    # Create a temporary logger if one doesn't exist
    temp_logger = create_process_logger()
    
    # Initialize the process data if not already done
    if not hasattr(temp_logger, 'process_data') or not temp_logger.process_data:
        temp_logger.process_data = {
            'steps': [],
            'file_name': f"{step_name}_processing",
            'model': 'global_function',
            'source_type': 'processing_step',
            'custom_metadata': {},
            'start_time': time.time()
        }
    
    temp_logger.log_step(step_name, message, data or {})

def log_data_transformation(step_name: str, input_data: Any, output_data: Any, processing_time: float):
    """Quick logging function for data transformations"""
    # Create a temporary logger if one doesn't exist
    temp_logger = create_process_logger()
    
    # Initialize the process data if not already done
    if not hasattr(temp_logger, 'process_data') or not temp_logger.process_data:
        temp_logger.process_data = {
            'steps': [],
            'file_name': f"{step_name}_transformation",
            'model': 'global_function',
            'source_type': 'data_transformation',
            'custom_metadata': {},
            'start_time': time.time()
        }
    
    temp_logger.log_data_flow(step_name, input_data, output_data, processing_time)

def log_performance_issue(step_name: str, issue_type: str, details: Dict[str, Any]):
    """Quick logging function for performance issues"""
    # Create a temporary logger if one doesn't exist
    temp_logger = create_process_logger()
    
    # Initialize the process data if not already done
    if not hasattr(temp_logger, 'process_data') or not temp_logger.process_data:
        temp_logger.process_data = {
            'steps': [],
            'file_name': f"{step_name}_performance",
            'model': 'global_function',
            'source_type': 'performance_issue',
            'custom_metadata': {},
            'start_time': time.time()
        }
    
    temp_logger.log_performance_bottleneck(step_name, issue_type, details)

def get_current_process_status() -> Dict[str, Any]:
    """Get current process status and insights"""
    # Create a temporary logger if one doesn't exist
    temp_logger = create_process_logger()
    
    # Initialize the process data if not already done
    if not hasattr(temp_logger, 'process_data') or not temp_logger.process_data:
        return {'status': 'no_process_started', 'message': 'No process is currently running'}
    
    return temp_logger.get_process_insights()
