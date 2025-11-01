#!/usr/bin/env python3
"""
Repository Mapper Setup Script
Initializes the environment and dependencies for Codebase Genius Repository Mapper
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def create_directories():
    """Create necessary directories for the project"""
    directories = [
        "logs",
        "temp_repos",
        "output",
        "config",
        "tests"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Created directory: {directory}")

def setup_environment():
    """Set up Python virtual environment and install dependencies"""
    try:
        # Check if virtual environment exists
        if not os.path.exists("venv"):
            print("Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        
        # Activate virtual environment
        if os.name == 'nt':  # Windows
            activate_script = "venv\\Scripts\\activate"
            python_executable = "venv\\Scripts\\python.exe"
        else:  # Unix/Linux/macOS
            activate_script = "source venv/bin/activate"
            python_executable = "venv/bin/python"
        
        # Install dependencies
        print("Installing dependencies...")
        subprocess.run([
            python_executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        
        print("Dependencies installed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Error setting up environment: {e}")
        return False
    
    return True

def create_config_files():
    """Create configuration files"""
    
    # Default configuration
    config = {
        "repository_mapper": {
            "max_file_size": 10485760,
            "max_file_preview": 5000,
            "timeout_seconds": 300,
            "temp_dir": "/tmp/codebase_genius",
            "allowed_domains": ["github.com", "gitlab.com"],
            "ignore_patterns": [
                ".git",
                ".svn",
                ".hg",
                "node_modules",
                "__pycache__",
                ".pytest_cache",
                "target",
                "build",
                "dist",
                "out",
                ".DS_Store",
                "Thumbs.db"
            ],
            "language_extensions": {
                ".py": "Python",
                ".js": "JavaScript",
                ".ts": "TypeScript",
                ".java": "Java",
                ".cpp": "C++",
                ".c": "C",
                ".h": "C/C++ Header",
                ".cs": "C#",
                ".php": "PHP",
                ".rb": "Ruby",
                ".go": "Go",
                ".rs": "Rust",
                ".swift": "Swift",
                ".kt": "Kotlin",
                ".scala": "Scala",
                ".sh": "Shell",
                ".bat": "Batch",
                ".ps1": "PowerShell",
                ".html": "HTML",
                ".css": "CSS",
                ".scss": "SCSS",
                ".less": "LESS",
                ".vue": "Vue.js",
                ".jsx": "React JSX",
                ".tsx": "React TSX",
                ".md": "Markdown",
                ".txt": "Plain Text",
                ".yml": "YAML",
                ".yaml": "YAML",
                ".json": "JSON",
                ".xml": "XML",
                ".toml": "TOML",
                ".ini": "INI",
                ".cfg": "Configuration",
                ".conf": "Configuration"
            }
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "logs/repo_mapper.log"
        }
    }
    
    with open("config/config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("Created configuration file: config/config.json")

def create_docker_files():
    """Create Dockerfile for containerized deployment"""
    
    dockerfile_content = """# Dockerfile for Repository Mapper
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.jac .
COPY config/ config/

# Create necessary directories
RUN mkdir -p logs temp_repos output

# Expose port for API
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/api/health || exit 1

# Start the application (assumes jac command is available)
CMD ["jac", "serve", "main.jac"]
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)
    
    # Create docker-compose.yml
    compose_content = """version: '3.8'

services:
  repository-mapper:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./logs:/app/logs
      - ./temp_repos:/app/temp_repos
      - ./output:/app/output
    environment:
      - JAC_SERVE_HOST=0.0.0.0
      - JAC_SERVE_PORT=8080
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
"""
    
    with open("docker-compose.yml", "w") as f:
        f.write(compose_content)
    
    print("Created Docker deployment files")

def create_test_files():
    """Create test files for the implementation"""
    
    test_content = '''#!/usr/bin/env python3
"""
Test suite for Repository Mapper implementation
"""

import requests
import json
import time
import sys

def test_api_health():
    """Test the health check endpoint"""
    try:
        response = requests.get("http://localhost:8080/api/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_repository_mapping():
    """Test repository mapping with a sample repository"""
    test_repo = "https://github.com/microsoft/vscode"
    
    try:
        # Test the main mapping endpoint
        data = {
            "repository_url": test_repo,
            "max_file_size": 1048576,  # 1MB for testing
            "include_ignored": False
        }
        
        response = requests.post(
            "http://localhost:8080/api/map-repository",
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print("✅ Repository mapping test passed")
                print(f"   - Found {result['file_tree']['statistics']['total_files']} files")
                print(f"   - Repository URL: {result['repository_url']}")
                return True
            else:
                print(f"❌ Repository mapping failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Repository mapping request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Repository mapping test error: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Repository Mapper Implementation")
    print("=" * 50)
    
    # Wait for service to be ready
    print("Waiting for service to be ready...")
    time.sleep(5)
    
    tests_passed = 0
    total_tests = 2
    
    # Run tests
    if test_api_health():
        tests_passed += 1
    
    if test_repository_mapping():
        tests_passed += 1
    
    print("\\n" + "=" * 50)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("💥 Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    with open("tests/test_api.py", "w") as f:
        f.write(test_content)
    
    print("Created test files")

def create_api_docs():
    """Create API documentation"""
    
    docs_content = '''# Repository Mapper API Documentation

## Overview
The Repository Mapper is a JAC-based service that analyzes GitHub repositories and generates comprehensive file trees with README summaries.

## Base URL
```
http://localhost:8080
```

## Endpoints

### Health Check
**GET** `/api/health`

Check if the service is running and healthy.

**Response:**
```json
{
  "service": "Repository Mapper Agent",
  "status": "healthy",
  "timestamp": "2025-10-31T07:07:35",
  "version": "1.0.0"
}
```

### Repository Mapping
**POST** `/api/map-repository`

Analyze and map a GitHub repository.

**Request Body:**
```json
{
  "repository_url": "https://github.com/owner/repo",
  "output_format": "json",
  "max_file_size": 10485760,
  "include_ignored": false
}
```

**Parameters:**
- `repository_url` (string, required): GitHub repository URL
- `output_format` (string, optional): Response format (default: "json")
- `max_file_size` (integer, optional): Maximum file size in bytes (default: 10485760)
- `include_ignored` (boolean, optional): Include ignored files (default: false)

**Response:**
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
      "description": "A brief description of the repository",
      "installation_instructions": "Installation steps...",
      "usage_instructions": "Usage examples..."
    }
  }
}
```

## Error Handling

### HTTP Error Codes
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Repository not found or inaccessible
- `500 Internal Server Error`: Server processing error

### Error Response Format
```json
{
  "error": "Descriptive error message",
  "details": "Additional error details",
  "timestamp": "2025-10-31T07:07:35"
}
```

## Rate Limiting
- Maximum 10 requests per minute per IP
- Repository size limit: 100MB uncompressed
- File count limit: 10,000 files per repository

## Examples

### cURL Example
```bash
curl -X POST http://localhost:8080/api/map-repository \\
  -H "Content-Type: application/json" \\
  -d '{
    "repository_url": "https://github.com/microsoft/vscode",
    "max_file_size": 5242880
  }'
```

### Python Example
```python
import requests

response = requests.post('http://localhost:8080/api/map-repository', json={
    'repository_url': 'https://github.com/microsoft/vscode',
    'max_file_size': 5242880
})

if response.status_code == 200:
    result = response.json()
    print(f"Found {result['file_tree']['statistics']['total_files']} files")
else:
    print(f"Error: {response.json()['error']}")
```

## Configuration

See `config/config.json` for configurable parameters including:
- File size limits
- Timeout settings
- Ignored file patterns
- Language detection settings
'''
    
    with open("docs/API.md", "w") as f:
        f.write(docs_content)
    
    print("Created API documentation")

def main():
    """Main setup function"""
    print("Setting up Codebase Genius Repository Mapper")
    print("=" * 50)
    
    # Create directory structure
    create_directories()
    
    # Set up Python environment
    if not setup_environment():
        print("Failed to set up environment")
        sys.exit(1)
    
    # Create configuration files
    create_config_files()
    
    # Create Docker files
    create_docker_files()
    
    # Create test files
    create_test_files()
    
    # Create documentation
    create_docker_files()  # This creates docs directory and files
    
    print("\\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\\nNext steps:")
    print("1. Activate the virtual environment:")
    if os.name == 'nt':
        print("   source venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("\\n2. Install JAC language:")
    print("   pip install jaclang jac-cloud")
    print("\\n3. Start the service:")
    print("   jac serve main.jac")
    print("\\n4. Run tests:")
    print("   python tests/test_api.py")

if __name__ == "__main__":
    main()
