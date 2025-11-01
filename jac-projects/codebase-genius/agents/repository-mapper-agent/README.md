# Codebase Genius - Repository Mapper Agent

A comprehensive JAC-based implementation for analyzing and mapping GitHub repositories. This agent clones repositories, generates file trees, and provides README summaries as part of the Codebase Genius multi-agent system.

## 🏗️ Architecture Overview

The Repository Mapper Agent follows the **Walker-based Architecture** pattern from JAC language, implementing Object-Spatial Programming (OSP) for multi-agent systems.

### Core Components

```
�� Repository Mapper Agent
├── 🏃 Walker: map_repository (Main processing)
├── 🌐 HTTP API: api_map_repository (Endpoint handler)
├── 🔧 Support: validate_github_url, clone_repository
├── 📊 Analysis: generate_file_tree, summarize_readme
├── 🧹 Cleanup: cleanup_repository (Resource management)
└── ⚡ Utilities: Language detection, File filtering
```

## 🚀 Features

### ✅ Repository Analysis
- **Git Clone**: Automatic repository cloning with error handling
- **File Tree Generation**: Recursive directory traversal with filtering
- **Language Detection**: Automatic programming language identification
- **Size Analysis**: File size tracking and limits
- **README Extraction**: Smart README file detection and summarization

### 🛡️ Error Handling
- **URL Validation**: GitHub URL format validation
- **Authentication**: Private repository detection
- **Network Failures**: Robust retry and timeout handling
- **File System**: Safe file operations with cleanup
- **Resource Management**: Automatic temporary directory cleanup

### ⚙️ Configuration
- **File Size Limits**: Configurable maximum file sizes
- **Ignore Patterns**: Customizable file exclusion rules
- **Language Mapping**: Extensible language detection
- **Timeout Settings**: Processing timeout configuration

### 🌐 HTTP API
- **RESTful Endpoints**: Standard HTTP API interface
- **JSON Responses**: Structured data output
- **Error Responses**: Detailed error information
- **Health Check**: Service monitoring endpoint

## 📦 Installation

### Prerequisites
- Python 3.12 or higher
- Git installed on system
- JAC language runtime (`jaclang`)

### Quick Setup

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd repository-mapper
   python setup.py
   ```

2. **Activate Environment**:
   ```bash
   # On Unix/Linux/macOS
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate
   ```

3. **Install JAC Runtime**:
   ```bash
   pip install jaclang jac-cloud
   ```

4. **Start Service**:
   ```bash
   jac serve main.jac
   ```

## 🐳 Docker Deployment

### Using Docker Compose
```bash
docker-compose up -d
```

### Manual Docker Build
```bash
docker build -t repo-mapper .
docker run -p 8080:8080 repo-mapper
```

## 🔧 Configuration

The agent uses `config/config.json` for configuration:

```json
{
  "repository_mapper": {
    "max_file_size": 10485760,
    "max_file_preview": 5000,
    "timeout_seconds": 300,
    "temp_dir": "/tmp/codebase_genius",
    "allowed_domains": ["github.com", "gitlab.com"],
    "ignore_patterns": [
      ".git",
      "node_modules",
      "__pycache__",
      "*.pyc"
    ]
  }
}
```

## 📚 API Usage

### Health Check
```bash
curl http://localhost:8080/api/health
```

### Repository Mapping
```bash
curl -X POST http://localhost:8080/api/map-repository \\
  -H "Content-Type: application/json" \\
  -d '{
    "repository_url": "https://github.com/microsoft/vscode",
    "max_file_size": 10485760
  }'
```

### Python Client Example
```python
import requests

# Map a repository
response = requests.post('http://localhost:8080/api/map-repository', json={
    'repository_url': 'https://github.com/microsoft/vscode',
    'max_file_size': 10485760
})

if response.status_code == 200:
    result = response.json()
    print(f"Found {result['file_tree']['statistics']['total_files']} files")
    print(f"Repository: {result['repository_url']}")
```

## 🧪 Testing

### Run Test Suite
```bash
# Ensure service is running
python tests/test_api.py

# Manual testing with JAC
jac run main.jac walker:test_repository_mapping
```

### Expected Test Results
```
✅ Health check passed
✅ Repository mapping test passed
   - Found 150 files
   - Repository URL: https://github.com/microsoft/vscode
🎉 All tests passed!
```

## 🔄 Workflow

### Processing Pipeline

1. **URL Validation** 
   - Parse GitHub URL format
   - Extract owner/repository information

2. **Repository Cloning**
   - Shallow clone for performance
   - Fallback to master branch if main doesn't exist

3. **File Tree Generation**
   - Recursive directory traversal
   - Language detection by file extension
   - Apply ignore patterns
   - Calculate statistics

4. **README Analysis**
   - Detect README files (README.md, README.txt, etc.)
   - Extract title, description, installation, usage

5. **Resource Cleanup**
   - Remove temporary repository files
   - Clean up resources

### Walker Pattern Implementation

The agent uses JAC's **Walker-based Architecture**:

```jac
walker map_repository {
    has repository_url: str;
    
    with entry {
        # Main entry point
        result = spawn validate_github_url;
        result = spawn clone_repository;
        result = spawn generate_file_tree;
        result = spawn summarize_readme;
        spawn cleanup_repository;
        
        report result;
    }
}
```

## 🎯 Response Format

### Success Response
```json
{
  "status": "success",
  "repository_url": "https://github.com/owner/repo",
  "validation": {
    "status": "valid",
    "username": "owner",
    "repository": "repo"
  },
  "cloning": {
    "status": "success",
    "clone_path": "/tmp/codebase_genius_1234567890",
    "repository_info": {
      "name": "repo",
      "remote_url": "https://github.com/owner/repo.git",
      "commit_hash": "abc123...",
      "branch": "main"
    }
  },
  "file_tree": {
    "statistics": {
      "total_files": 150,
      "total_directories": 25,
      "total_size_bytes": 2048576,
      "language_distribution": {
        "Python": 45,
        "JavaScript": 30,
        "Markdown": 15
      }
    }
  },
  "readme": {
    "status": "success",
    "file_found": "README.md",
    "summary": {
      "title": "Repository Name",
      "description": "Repository description...",
      "installation_instructions": "Install steps...",
      "usage_instructions": "Usage examples..."
    }
  }
}
```

### Error Response
```json
{
  "error": "Repository cloning failed",
  "details": "Authentication failed - repository may be private",
  "timestamp": "2025-10-31T07:07:35"
}
```

## 🔧 Development

### Adding New Language Support
Edit `config/config.json` to add language mappings:

```json
{
  "language_extensions": {
    ".newlang": "New Language"
  }
}
```

### Custom Ignore Patterns
Add patterns to the `ignore_patterns` array in configuration:

```json
{
  "ignore_patterns": [
    "my_custom_folder",
    "*.custom_extension"
  ]
}
```

### Testing with Sample Repositories
```bash
# Test with public repositories
jac run main.jac walker:api_map_repository {
    repository_url: "https://github.com/microsoft/vscode"
}
```

## 📈 Performance

### Optimization Features
- **Shallow Cloning**: Fast repository downloads
- **File Size Limits**: Prevent memory issues
- **Async Processing**: Non-blocking operations
- **Resource Cleanup**: Automatic cleanup

### Limits
- Maximum repository size: 100MB uncompressed
- Maximum file count: 10,000 files per repository
- File size limit: Configurable (default: 10MB)
- Processing timeout: 5 minutes default

## 🔍 Monitoring

### Health Check Endpoint
```bash
curl http://localhost:8080/api/health
```

### Log Files
- Application logs: `logs/repo_mapper.log`
- Configuration: `config/config.json`
- Test results: `tests/test_results.json`

## 🤝 Integration

### Multi-Agent System Integration
The Repository Mapper integrates with other Codebase Genius agents:

```jac
# Supervisor delegates to Repository Mapper
walker supervisor_process_repo {
    can map_repository with entry {
        result = spawn map_repository {
            repository_url: input_url
        };
        # Pass results to next agent...
    }
}
```

### API Compatibility
- RESTful HTTP API
- JSON request/response format
- Standard HTTP status codes
- CORS enabled for web frontend integration

## 📝 License

This implementation follows the same license as the Codebase Genius project.

## 🆘 Troubleshooting

### Common Issues

1. **"JAC not found"**
   ```bash
   pip install jaclang jac-cloud
   ```

2. **"Git clone failed"**
   - Check repository URL format
   - Verify repository is public
   - Check network connectivity

3. **"Permission denied"**
   - Ensure temp directory permissions
   - Check available disk space
   - Verify Git is installed

4. **"Service not responding"**
   ```bash
   # Check if service is running
   ps aux | grep jac
   # View logs
   tail -f logs/repo_mapper.log
   ```

### Debug Mode
```bash
# Run with verbose logging
JAC_LOG_LEVEL=DEBUG jac serve main.jac
```

## 🚀 Future Enhancements

- [ ] Support for private repositories (GitHub API)
- [ ] Incremental analysis for large repositories
- [ ] Multiple file format support (tar.gz, zip)
- [ ] Git history analysis
- [ ] License detection
- [ ] Security vulnerability scanning
- [ ] Performance metrics dashboard

---

**Created by:** Cavin Otieno  
**Last Updated:** 2025-10-31  
**Version:** 1.0.0
