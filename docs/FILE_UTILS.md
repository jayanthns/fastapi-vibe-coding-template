# File Utilities Documentation

## Overview

The FastAPI Vibe Coding file utilities provide a comprehensive solution for handling various file operations including text files, JSON files, CSV files, and general file management. The utilities include built-in error handling, validation, logging integration, and security features.

## Features

- **Multiple File Formats**: Support for text, JSON, and CSV files
- **Error Handling**: Comprehensive exception handling with custom `FileUtilsError`
- **Security**: Path traversal protection and validation
- **Logging Integration**: Full trace ID support for debugging and monitoring
- **Convenience Functions**: Simple one-line functions for common operations
- **File Management**: Copy, delete, list, and get information about files
- **Encoding Support**: Configurable encoding for all text-based operations

## Architecture

### Core Classes

```python
FileUtils              # Main utility class with comprehensive file operations
FileUtilsError        # Custom exception for file operation errors
```

### Key Components

- **Text Operations**: Read, write, append text files with encoding support
- **JSON Operations**: Read/write JSON with custom serialization
- **CSV Operations**: Read/write CSV files as dictionaries or lists
- **File Management**: Copy, delete, list files and directories
- **Validation**: Path validation and security checks
- **Logging**: Integrated logging with trace ID support

## Installation & Setup

The file utilities use standard Python libraries and are included in the project:

```python
# Core dependencies (already included)
import csv
import json
from pathlib import Path
from datetime import datetime, timezone
```

## Usage Examples

### 1. Text File Operations

```python
from src.utils.file_utils import FileUtils, write_text, read_text

# Using the FileUtils class
file_utils = FileUtils(trace_id="example-001")

# Write a text file
content = "Hello, World!\nThis is a sample text file."
file_utils.write_text_file("data/example.txt", content)

# Read a text file
content = file_utils.read_text_file("data/example.txt")
print(content)

# Read lines as a list
lines = file_utils.read_lines("data/example.txt")
print(f"File has {len(lines)} lines")

# Append to file
file_utils.write_text_file("data/example.txt", "\nAppended content!", append=True)

# Using convenience functions
write_text("data/quick.txt", "Quick text content", trace_id="quick-001")
content = read_text("data/quick.txt", trace_id="quick-001")
```

### 2. JSON File Operations

```python
from src.utils.file_utils import FileUtils, write_json, read_json

file_utils = FileUtils(trace_id="json-example")

# Sample data
data = {
    "users": [
        {"id": 1, "name": "Alice Smith", "email": "alice@example.com", "active": True},
        {"id": 2, "name": "Bob Johnson", "email": "bob@example.com", "active": False},
    ],
    "metadata": {
        "created_at": "2024-01-01T10:00:00Z",
        "version": "1.0",
        "total_users": 2
    },
    "settings": {"theme": "dark", "notifications": True}
}

# Write JSON file
file_utils.write_json_file("data/users.json", data, indent=2)

# Read JSON file
read_data = file_utils.read_json_file("data/users.json")
print(f"Loaded {len(read_data['users'])} users")

# Using convenience functions
write_json("data/config.json", {"debug": True, "port": 8000}, trace_id="config-001")
config = read_json("data/config.json", trace_id="config-001")
```

### 3. CSV File Operations

```python
from src.utils.file_utils import FileUtils, write_csv, read_csv

file_utils = FileUtils(trace_id="csv-example")

# Sample employee data
employees = [
    {"id": "1", "name": "Alice Smith", "department": "Engineering", "salary": "75000"},
    {"id": "2", "name": "Bob Johnson", "department": "Marketing", "salary": "65000"},
    {"id": "3", "name": "Charlie Brown", "department": "Engineering", "salary": "80000"},
]

# Write CSV file
file_utils.write_csv_file("data/employees.csv", employees)

# Read CSV file as dictionaries
employees_data = file_utils.read_csv_file("data/employees.csv")
print(f"Loaded {len(employees_data)} employees")

# Filter and write new CSV
engineering_employees = [emp for emp in employees_data if emp["department"] == "Engineering"]
file_utils.write_csv_file("data/engineering.csv", engineering_employees)

# Read CSV as list of lists (raw data)
csv_data = file_utils.read_csv_as_list("data/employees.csv")
print(f"CSV has {len(csv_data)} rows including header")

# Using convenience functions
csv_data = [
    {"product": "Laptop", "price": "999.99", "stock": "5"},
    {"product": "Mouse", "price": "29.99", "stock": "50"}
]
write_csv("data/products.csv", csv_data, trace_id="products-001")
products = read_csv("data/products.csv", trace_id="products-001")
```

### 4. File Management Operations

```python
from src.utils.file_utils import FileUtils, file_exists, get_file_info

file_utils = FileUtils(trace_id="file-ops")

# Check if file exists
if file_utils.file_exists("data/example.txt"):
    print("File exists!")

# Get file information
info = file_utils.get_file_info("data/example.txt")
print(f"File: {info['name']}")
print(f"Size: {info['size_human']}")
print(f"Modified: {info['modified']}")
print(f"Permissions: {info['permissions']}")

# Copy a file
file_utils.copy_file("data/example.txt", "backup/example_backup.txt")

# List files in directory
txt_files = file_utils.list_files("data/", pattern="*.txt")
print(f"Found {len(txt_files)} text files:")
for file in txt_files:
    print(f"  - {file.name}")

# List all files recursively
all_files = file_utils.list_files("data/", pattern="*", recursive=True)
print(f"Total files in data/: {len(all_files)}")

# Delete a file
file_utils.delete_file("temp/old_file.txt")

# Using convenience functions
exists = file_exists("data/config.json")
info = get_file_info("data/config.json", trace_id="info-001")
```

### 5. Error Handling

```python
from src.utils.file_utils import FileUtils, FileUtilsError

file_utils = FileUtils(trace_id="error-handling")

# Handle file not found
try:
    content = file_utils.read_text_file("nonexistent.txt")
except FileUtilsError as e:
    print(f"File error: {e}")

# Handle invalid JSON
try:
    file_utils.write_text_file("invalid.json", "{ invalid json")
    data = file_utils.read_json_file("invalid.json")
except FileUtilsError as e:
    print(f"JSON error: {e}")

# Handle invalid CSV data
try:
    file_utils.write_csv_file("invalid.csv", "not a list")
except FileUtilsError as e:
    print(f"CSV error: {e}")

# Validate recipients before processing
from src.utils.file_utils import NotificationRecipient

recipient = NotificationRecipient(id="1", email="invalid-email")
if not email_notifier.validate_recipient(recipient):
    print("Invalid recipient email format")
```

## Advanced Usage

### Custom JSON Serialization

The file utilities include custom JSON serialization for common Python types:

```python
from datetime import datetime
from src.utils.file_utils import FileUtils

file_utils = FileUtils()

# Data with datetime objects
data = {
    "created_at": datetime.now(),
    "updated_at": datetime(2024, 1, 1, 12, 0, 0),
    "user": {"name": "John", "active": True}
}

# Automatically serializes datetime objects
file_utils.write_json_file("data/timestamps.json", data)

# Custom objects with __dict__ are also supported
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.created_at = datetime.now()

user = User("Alice", "alice@example.com")
file_utils.write_json_file("data/user.json", {"user": user})
```

### Working with Different Encodings

```python
file_utils = FileUtils()

# Read file with specific encoding
content = file_utils.read_text_file("data/unicode.txt", encoding="utf-16")

# Write file with specific encoding
file_utils.write_text_file("data/output.txt", "Content with émojis 🎉", encoding="utf-8")

# CSV with different encoding
csv_data = file_utils.read_csv_file("data/international.csv", encoding="iso-8859-1")
```

### Batch File Operations

```python
file_utils = FileUtils(trace_id="batch-ops")

# Process multiple files
source_dir = "input/"
output_dir = "output/"

for file_path in file_utils.list_files(source_dir, pattern="*.txt"):
    # Read, process, and write
    content = file_utils.read_text_file(file_path)
    processed_content = content.upper()  # Example processing

    output_path = f"{output_dir}/{file_path.stem}_processed.txt"
    file_utils.write_text_file(output_path, processed_content)

print("Batch processing completed!")
```

## Integration with FastAPI

### File Upload Handler

```python
from fastapi import APIRouter, UploadFile, File, HTTPException
from src.utils.file_utils import FileUtils, FileUtilsError
from src.middleware.trace import get_trace_id

router = APIRouter()

@router.post("/upload-csv")
async def upload_csv_file(file: UploadFile = File(...)):
    """Upload and process a CSV file."""
    trace_id = get_trace_id()
    file_utils = FileUtils(trace_id=trace_id)

    try:
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        content = await file.read()
        file_utils.write_text_file(file_path, content.decode('utf-8'))

        # Process CSV
        csv_data = file_utils.read_csv_file(file_path)
        record_count = len(csv_data)

        # Save processing result
        result = {
            "filename": file.filename,
            "records": record_count,
            "processed_at": datetime.now().isoformat()
        }

        result_path = f"results/{file.filename}.json"
        file_utils.write_json_file(result_path, result)

        return {"message": f"Processed {record_count} records", "result_file": result_path}

    except FileUtilsError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Configuration Management

```python
from fastapi import FastAPI
from src.utils.file_utils import read_json, write_json, FileUtilsError

app = FastAPI()

@app.on_event("startup")
async def load_config():
    """Load application configuration from JSON file."""
    try:
        config = read_json("config/app_config.json", trace_id="startup")
        app.state.config = config
        print(f"Loaded configuration: {config}")
    except FileUtilsError as e:
        print(f"Failed to load config: {e}")
        # Use default configuration
        default_config = {"debug": False, "port": 8000}
        app.state.config = default_config

@app.post("/config/update")
async def update_config(new_config: dict):
    """Update application configuration."""
    try:
        write_json("config/app_config.json", new_config, trace_id="config-update")
        app.state.config = new_config
        return {"message": "Configuration updated successfully"}
    except FileUtilsError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Report Generation

```python
@router.get("/reports/generate/{report_type}")
async def generate_report(report_type: str):
    """Generate and save a report."""
    trace_id = get_trace_id()
    file_utils = FileUtils(trace_id=trace_id)

    try:
        # Generate report data (example)
        if report_type == "users":
            # Get users from database
            users_data = get_users_from_db()
            report_data = [
                {"id": user.id, "name": user.name, "email": user.email}
                for user in users_data
            ]
        else:
            raise HTTPException(status_code=400, detail="Invalid report type")

        # Save as CSV
        csv_path = f"reports/{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_utils.write_csv_file(csv_path, report_data)

        # Save metadata as JSON
        metadata = {
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "record_count": len(report_data),
            "file_path": csv_path
        }

        json_path = csv_path.replace('.csv', '_metadata.json')
        file_utils.write_json_file(json_path, metadata)

        return {
            "message": f"Report generated successfully",
            "csv_file": csv_path,
            "metadata_file": json_path,
            "records": len(report_data)
        }

    except FileUtilsError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Common Use Cases

### 1. Configuration Files

```python
# Load application settings
settings = read_json("config/settings.json")

# Update settings
settings["debug"] = False
write_json("config/settings.json", settings, indent=2)
```

### 2. Data Export/Import

```python
# Export database data to CSV
users = get_all_users()
user_data = [{"id": u.id, "name": u.name, "email": u.email} for u in users]
write_csv("exports/users.csv", user_data)

# Import CSV data
imported_users = read_csv("imports/new_users.csv")
for user_data in imported_users:
    create_user(user_data)
```

### 3. Log File Processing

```python
# Read and process log files
log_content = read_text("logs/app.log")
error_lines = [line for line in log_content.split('\n') if 'ERROR' in line]

# Save processed logs
write_text("logs/errors_only.log", '\n'.join(error_lines))
```

### 4. Backup and Archive

```python
file_utils = FileUtils(trace_id="backup")

# Create backup of important files
important_files = file_utils.list_files("data/", pattern="*.json")
for file_path in important_files:
    backup_path = f"backup/{file_path.name}"
    file_utils.copy_file(file_path, backup_path)

# Archive old files
import shutil
shutil.make_archive("archive/data_backup", 'zip', "backup/")
```

## API Reference

### FileUtils Class

#### Constructor
```python
FileUtils(trace_id: str = None)
```

#### Text File Methods
- `read_text_file(file_path, encoding="utf-8", strip_whitespace=True) -> str`
- `write_text_file(file_path, content, encoding="utf-8", create_dirs=True, append=False) -> bool`
- `read_lines(file_path, encoding="utf-8", strip_whitespace=True, skip_empty=False) -> List[str]`

#### JSON File Methods
- `read_json_file(file_path, encoding="utf-8") -> Union[Dict, List, Any]`
- `write_json_file(file_path, data, encoding="utf-8", indent=2, ensure_ascii=False, create_dirs=True) -> bool`

#### CSV File Methods
- `read_csv_file(file_path, encoding="utf-8", delimiter=",", has_header=True, skip_empty_rows=True) -> List[Dict[str, str]]`
- `write_csv_file(file_path, data, encoding="utf-8", delimiter=",", write_header=True, create_dirs=True) -> bool`
- `read_csv_as_list(file_path, encoding="utf-8", delimiter=",", skip_empty_rows=True) -> List[List[str]]`

#### File Management Methods
- `file_exists(file_path) -> bool`
- `directory_exists(dir_path) -> bool`
- `get_file_info(file_path) -> Dict[str, Any]`
- `delete_file(file_path) -> bool`
- `copy_file(source_path, destination_path, create_dirs=True) -> bool`
- `list_files(directory_path, pattern="*", recursive=False, files_only=True) -> List[Path]`

### Convenience Functions

```python
# Text operations
read_text(file_path, trace_id=None, **kwargs) -> str
write_text(file_path, content, trace_id=None, **kwargs) -> bool

# JSON operations
read_json(file_path, trace_id=None, **kwargs) -> Any
write_json(file_path, data, trace_id=None, **kwargs) -> bool

# CSV operations
read_csv(file_path, trace_id=None, **kwargs) -> List[Dict[str, str]]
write_csv(file_path, data, trace_id=None, **kwargs) -> bool

# File info
file_exists(file_path) -> bool
get_file_info(file_path, trace_id=None) -> Dict[str, Any]
```

## Error Handling

### FileUtilsError Exception

All file operations can raise `FileUtilsError` for various error conditions:

- **File not found**: When trying to read non-existent files
- **Permission errors**: When lacking read/write permissions
- **Invalid data**: When data cannot be serialized/deserialized
- **Path traversal**: When attempting to access files outside allowed paths
- **Encoding errors**: When file encoding doesn't match specified encoding

### Best Practices for Error Handling

```python
from src.utils.file_utils import FileUtils, FileUtilsError

file_utils = FileUtils(trace_id="error-example")

try:
    data = file_utils.read_json_file("config.json")
except FileUtilsError as e:
    # Log the error with trace ID for debugging
    logger.error(f"Failed to read config: {e}")

    # Provide fallback behavior
    data = {"default": True}

    # Optionally create the missing file
    file_utils.write_json_file("config.json", data)
```

## Security Considerations

### Path Traversal Protection

The file utilities automatically protect against path traversal attacks:

```python
# These will raise FileUtilsError
file_utils.read_text_file("../../../etc/passwd")  # Blocked
file_utils.write_text_file("../../sensitive.txt", "data")  # Blocked
```

### Safe File Operations

- All paths are validated before operations
- Directory creation is optional and controlled
- File permissions are preserved during copy operations
- Temporary files are handled securely

## Performance Considerations

- **Large Files**: For very large files, consider reading in chunks
- **Batch Operations**: Use the FileUtils instance for multiple operations to reuse logging setup
- **Memory Usage**: JSON operations load entire files into memory
- **Encoding**: UTF-8 is the default and most efficient for most use cases

## Testing

The file utilities include comprehensive tests covering:

- Text file operations (read, write, append, lines)
- JSON operations (valid/invalid JSON, custom serialization)
- CSV operations (dictionaries, lists, validation)
- File management (copy, delete, list, info)
- Error handling (file not found, permission errors, invalid data)
- Convenience functions
- Path validation and security

Run tests with:
```bash
pytest tests/test_utils/test_file_utils.py -v
```

## Troubleshooting

### Common Issues

1. **Encoding Errors**
   - Specify the correct encoding when reading files
   - Use UTF-8 for new files unless specific encoding is required

2. **Permission Errors**
   - Check file/directory permissions
   - Ensure the application has write access to target directories

3. **Path Not Found**
   - Use `create_dirs=True` when writing to new directories
   - Verify the path exists before reading

4. **JSON Serialization Errors**
   - Ensure all data is JSON-serializable
   - Use the built-in datetime serialization for date objects

5. **CSV Format Issues**
   - Verify CSV data is a list of dictionaries
   - Check delimiter settings match the file format

### Debugging

Enable detailed logging:

```python
import logging
logging.getLogger("src.file_utils").setLevel(logging.DEBUG)
```

Use trace IDs for request tracking:

```python
file_utils = FileUtils(trace_id="debug-session-001")
# All operations will be logged with this trace ID
```

## Contributing

When extending the file utilities:

1. Follow the existing error handling patterns
2. Add comprehensive tests for new functionality
3. Update documentation with examples
4. Ensure security considerations are addressed
5. Add logging with trace ID support

---

## License

This file utilities module is part of the FastAPI Vibe Coding project.
