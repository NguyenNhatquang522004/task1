# Hệ thống Logging Nâng cao - Hướng dẫn Sử dụng và Tùy chỉnh

## Tổng quan

Tôi đã cải tiến hệ thống logging của LLM Graph Builder để cung cấp cái nhìn sâu sắc về quy trình xử lý tài liệu và cho phép bạn tùy chỉnh dễ dàng theo nhu cầu. Hệ thống mới có các tính năng:

### 🔍 **Theo dõi chi tiết quy trình**
- **Ghi lại từng bước**: Mỗi bước xử lý được ghi lại với timestamp, tóm tắt dữ liệu, và metrics hiệu suất
- **Theo dõi luồng dữ liệu**: Trace hoàn chỉnh cách dữ liệu chuyển đổi qua pipeline
- **Giám sát hiệu suất**: Tự động phát hiện các điểm nghẽn và hoạt động chậm
- **Theo dõi bộ nhớ**: Giám sát mức tiêu thụ bộ nhớ qua các bước xử lý

### 🎛️ **Tùy chỉnh linh hoạt**
- **Cấu hình sẵn**: Các setting được cấu hình trước cho development, production, debugging
- **Custom formatters**: Định nghĩa cách hiển thị và format log messages
- **Custom hooks**: Thêm logic tùy chỉnh được thực thi trong các sự kiện xử lý cụ thể
- **Ẩn danh hóa dữ liệu**: Tự động ẩn thông tin nhạy cảm khỏi logs
- **Tùy chọn output**: Log ra console, file, hoặc cả hai với format tùy chỉnh

## Cách sử dụng cơ bản

### 1. Cấu hình môi trường

Bạn có thể thiết lập biến môi trường để tự động chọn cấu hình:

```bash
# Cho development
set ENVIRONMENT=development

# Cho production
set ENVIRONMENT=production
```

### 2. Tùy chỉnh cấu hình

Chỉnh sửa file `backend/src/custom_logging_config.py`:

```python
# Cấu hình cơ bản
LOG_LEVEL = logging.INFO  # DEBUG cho chi tiết hơn, WARNING cho minimal
LOG_DIRECTORY = "logs"    # Thư mục lưu log files
ENABLE_CONSOLE_LOGGING = True    # Hiển thị logs trên console
ENABLE_FILE_LOGGING = True       # Lưu logs vào files
ENABLE_PERFORMANCE_TRACKING = True  # Theo dõi hiệu suất
ENABLE_DATA_ANONYMIZATION = False   # Ẩn danh hóa dữ liệu nhạy cảm
MAX_DATA_PREVIEW_LENGTH = 300       # Độ dài tối đa cho preview dữ liệu

# Ngưỡng hiệu suất (tính bằng giây)
SLOW_STEP_THRESHOLD = 30      # Cảnh báo nếu bước này chậm hơn
VERY_SLOW_STEP_THRESHOLD = 60 # Báo lỗi nếu bước này chậm hơn
MEMORY_THRESHOLD_MB = 1000    # Cảnh báo nếu bộ nhớ vượt quá
```

### 3. Thêm Custom Formatters

Định nghĩa cách hiển thị messages:

```python
def performance_formatter(message: str, data: Dict[str, Any]) -> str:
    """Custom formatter cho performance messages"""
    if data and "processing_time" in data:
        processing_time = data["processing_time"]
        if isinstance(processing_time, str) and processing_time.endswith('s'):
            time_value = float(processing_time[:-1])
            if time_value > 60:
                return f"🚨 RẤT CHẬM: {message} ({processing_time})"
            elif time_value > 30:
                return f"⚠️ CHẬM: {message} ({processing_time})"
            else:
                return f"🚀 NHANH: {message} ({processing_time})"
    return message
```

### 4. Thêm Custom Hooks

Thêm logic tùy chỉnh cho monitoring và alerting:

```python
def performance_monitoring_hook(data: Dict[str, Any]):
    """Monitor hiệu suất và tạo alerts"""
    if "processing_time" in data:
        processing_time = data["processing_time"]
        if isinstance(processing_time, str) and processing_time.endswith('s'):
            time_value = float(processing_time[:-1])
            if time_value > 60:
                # Thêm logic alerting của bạn ở đây
                send_slack_alert(f"Phát hiện xử lý chậm: {processing_time}")
                send_email_alert(f"Vấn đề hiệu suất: {data}")
```

## Các outputs được tạo ra

### 1. Log Files hàng ngày
- `logs/process_detailed_YYYYMMDD.log`: Tất cả log messages với timestamps
- Format có thể tùy chỉnh và mức độ chi tiết

### 2. Báo cáo Process
- `logs/process_report_filename_timestamp.json`: Báo cáo JSON toàn diện
- Bao gồm timeline, data lineage, và performance metrics

### 3. Tóm tắt dễ đọc
- `logs/process_summary_filename_timestamp.txt`: Tóm tắt dễ đọc
- Performance bottlenecks và data quality scores

## Ví dụ về cấu trúc báo cáo

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

## Cách tùy chỉnh cho nhu cầu cụ thể

### 1. Theo dõi các bước cụ thể

```python
# Cấu hình chi tiết logging cho các bước cụ thể
DETAILED_LOGGING_STEPS = [
    "ENTITY_EXTRACTION",
    "RELATIONSHIP_EXTRACTION", 
    "CHUNKING",
    "EMBEDDING_CREATION",
    "NEO4J_SAVE"
]
```

### 2. Giám sát hiệu suất cho bước cụ thể

```python
PERFORMANCE_MONITORED_STEPS = [
    "ENTITY_EXTRACTION",
    "CHUNKING",
    "EMBEDDING_CREATION",
    "NEO4J_SAVE"
]
```

### 3. Theo dõi chất lượng dữ liệu

```python
DATA_QUALITY_MONITORED_STEPS = [
    "ENTITY_EXTRACTION",
    "RELATIONSHIP_EXTRACTION",
    "DATA_CLEANING"
]
```

## Ví dụ tích hợp vào code hiện tại

### Cách tích hợp tối thiểu (không thay đổi logic hiện tại):

```python
from backend.src.process_logger import process_logger

def existing_function(data):
    # Thêm logging mà không thay đổi logic
    process_logger.log_step("PROCESSING_START", "Bắt đầu xử lý", {
        "input_size": len(data),
        "processing_type": "existing_logic"
    })
    
    # Logic hiện tại (không thay đổi)
    result = your_existing_logic(data)
    
    process_logger.log_step("PROCESSING_COMPLETE", "Hoàn thành xử lý", {
        "output_size": len(result),
        "success": True
    })
    
    return result
```

### Tích hợp đầy đủ với data flow tracking:

```python
def comprehensive_processing(input_data):
    # Bắt đầu process
    process_logger.start_process("my_document.pdf", "gemini-pro", "local")
    
    try:
        # Bước 1: Xử lý đầu vào
        process_logger.log_step("INPUT_PROCESSING", "Xử lý đầu vào")
        processed_input = process_input(input_data)
        
        # Ghi lại data transformation
        process_logger.log_data_flow("INPUT_PROCESSING", input_data, processed_input, processing_time)
        
        # Bước 2: Trích xuất thông tin
        process_logger.log_step("EXTRACTION", "Trích xuất thông tin")
        extracted_data = extract_information(processed_input)
        
        # Kiểm tra chất lượng và ghi lại
        quality_score = calculate_quality_score(extracted_data)
        process_logger.log_data_flow("EXTRACTION", processed_input, extracted_data, processing_time, {
            "quality_score": quality_score,
            "extraction_method": "advanced_nlp"
        })
        
        # Kết thúc process
        process_logger.end_process("SUCCESS", {
            "total_items": len(extracted_data),
            "quality_score": quality_score
        })
        
        return extracted_data
        
    except Exception as e:
        process_logger.log_step("PROCESSING_ERROR", f"Lỗi: {str(e)}", {
            "error_type": type(e).__name__,
            "error_message": str(e)
        }, level="ERROR")
        
        process_logger.end_process("ERROR", {"error": str(e)})
        raise
```

## Chạy demo để xem logging hoạt động

```bash
# Chạy demo từ thư mục gốc của project
python demo_enhanced_logging.py
```

Script này sẽ:
1. Tạo các log files mẫu
2. Hiển thị các tính năng khác nhau
3. Tạo báo cáo chi tiết
4. Cho thấy cách tùy chỉnh hooks và formatters

## Các tính năng nâng cao

### 1. Export metrics

```python
# Export dữ liệu dưới dạng JSON
json_data = logger.export_metrics("json")

# Export dưới dạng CSV
csv_data = logger.export_metrics("csv")
```

### 2. Realtime insights

```python
# Lấy thông tin về process hiện tại
insights = logger.get_process_insights()
print(f"Current step: {insights['current_step']}")
print(f"Elapsed time: {insights['elapsed_time']}")
```

### 3. Custom metrics

```python
# Ghi lại custom metrics
logger.log_custom_metric("entities_per_second", 25.5)
logger.log_custom_metric("api_calls_count", 10)
logger.log_custom_metric("memory_usage_mb", 512)
```

## Troubleshooting

### 1. Lỗi import
- Đảm bảo chạy script từ thư mục gốc của project
- Kiểm tra đường dẫn Python path

### 2. Lỗi permission
- Đảm bảo quyền write cho thư mục logs
- Tạo thư mục logs nếu chưa tồn tại

### 3. Hiệu suất
- Sử dụng log level phù hợp (INFO cho production)
- Tắt console logging trong production
- Giới hạn độ dài preview dữ liệu

## Kết luận

Hệ thống logging nâng cao này cung cấp:

1. **Cái nhìn sâu sắc**: Hiểu rõ quy trình xử lý từng bước
2. **Tùy chỉnh dễ dàng**: Thay đổi cấu hình, formatters, hooks theo nhu cầu
3. **Monitoring tự động**: Phát hiện vấn đề hiệu suất và chất lượng dữ liệu
4. **Báo cáo chi tiết**: Tạo báo cáo toàn diện cho analysis
5. **Tích hợp linh hoạt**: Có thể tích hợp với code hiện tại mà không thay đổi logic

Bạn có thể bắt đầu với cấu hình cơ bản và dần dần thêm các tính năng tùy chỉnh theo nhu cầu cụ thể của mình.
