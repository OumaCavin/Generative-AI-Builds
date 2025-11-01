# Codebase Genius - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Web Interface Usage](#web-interface-usage)
3. [API Usage](#api-usage)
4. [Repository Analysis](#repository-analysis)
5. [Output Formats](#output-formats)
6. [Workflow Management](#workflow-management)
7. [Best Practices](#best-practices)
8. [Advanced Features](#advanced-features)

## Getting Started

### Quick Start
1. **Start the Application**
   ```bash
   python api-frontend/start.py start
   ```

2. **Open Web Interface**
   Navigate to: http://localhost:8501

3. **Analyze Your First Repository**
   - Enter: `https://github.com/python/cpython`
   - Select format: `Markdown`
   - Click: `🧠 Start Analysis`

### Supported Repository Platforms
- ✅ **GitHub**: `https://github.com/user/repo`
- ✅ **GitLab**: `https://gitlab.com/user/repo`
- ✅ **Bitbucket**: `https://bitbucket.org/user/repo`
- ✅ **Gitee**: `https://gitee.com/user/repo`

### Repository Requirements
- Public repositories (no authentication required)
- Active repositories with recent commits
- Standard git repository structure
- Reasonable file count (recommended <10,000 files)

## Web Interface Usage

### Navigation

The Streamlit interface provides five main sections:

#### 🚀 New Analysis
Start repository analysis with the input form:
- **Repository URL**: Enter full repository URL
- **Branch**: Specify branch (default: main)
- **Analysis Depth**: Choose complexity level
- **Output Format**: Select documentation format
- **Include Diagrams**: Toggle diagram generation

#### 📊 Status
Monitor running analysis workflows:
- Real-time progress updates
- Current step indicators
- Progress charts and metrics
- Auto-refresh every 5 seconds

#### 📋 Results
View completed analysis results:
- Repository overview and statistics
- File type distribution charts
- Generated documentation preview
- Download links for documentation

#### 🗂️ Management
Workflow administration:
- List all active workflows
- View completed workflow history
- Download previous results
- Delete unwanted workflows

#### ℹ️ About
System information:
- Architecture overview
- Feature descriptions
- Technical stack details

### Form Validation

The interface provides real-time validation:
- ✅ **Valid URLs**: Green checkmark for supported platforms
- ❌ **Invalid URLs**: Red error message with guidance
- 🔄 **Network Check**: Automatic repository accessibility verification

### Progress Tracking

#### Visual Indicators
- **Progress Bar**: Shows completion percentage
- **Status Cards**: Color-coded status information
- **Step Indicators**: Current analysis phase
- **Progress Chart**: Circular progress visualization

#### Status States
- ⏳ **Pending**: Workflow created, awaiting processing
- 🔄 **Running**: Analysis in progress
- ✅ **Completed**: Documentation generated successfully
- ❌ **Failed**: Error occurred during processing

## API Usage

### Authentication

The API supports multiple authentication methods:

```bash
# No authentication (development)
curl http://localhost:8000/health

# API Key authentication (production)
curl -H "X-API-Key: your-api-key" http://localhost:8000/health
```

### Basic Endpoints

#### Health Check
```bash
GET /health

# Response
{
  "status": "healthy",
  "timestamp": "2025-10-31T07:57:17Z",
  "active_workflows": 2,
  "completed_workflows": 15
}
```

#### System Information
```bash
GET /

# Response
{
  "success": true,
  "data": {
    "message": "Codebase Genius API is running",
    "version": "1.0.0"
  },
  "timestamp": "2025-10-31T07:57:17Z"
}
```

### Analysis Endpoints

#### Start Repository Analysis
```bash
POST /api/analyze

# Request Body
{
  "repository_url": "https://github.com/user/repo",
  "branch": "main",
  "analysis_depth": "full",
  "include_diagrams": true,
  "format": "markdown"
}

# Response
{
  "workflow_id": "uuid-string",
  "status": "started",
  "message": "Analysis workflow created successfully",
  "estimated_completion": 300
}
```

#### Check Analysis Status
```bash
GET /api/status/{workflow_id}

# Response
{
  "workflow_id": "uuid-string",
  "status": "running",
  "progress": 0.65,
  "current_step": "Analyzing code structure",
  "result": null,
  "error_message": null
}
```

#### Download Documentation
```bash
GET /api/download/{workflow_id}

# Returns: ZIP file with documentation
# Headers: Content-Type: application/zip
# Body: Binary ZIP file
```

### Workflow Management

#### List All Workflows
```bash
GET /api/workflows

# Response
{
  "active_workflows": ["uuid1", "uuid2"],
  "completed_workflows": ["uuid3", "uuid4"],
  "total_active": 2,
  "total_completed": 2
}
```

#### Delete Workflow
```bash
DELETE /api/workflows/{workflow_id}

# Response
{
  "message": "Workflow uuid-string deleted successfully"
}
```

### Configuration Endpoint

#### Get API Configuration
```bash
GET /api/config

# Response
{
  "supported_formats": ["markdown", "html", "pdf"],
  "max_file_size": "100MB",
  "supported_repositories": ["GitHub", "GitLab", "Bitbucket"],
  "analysis_depth_options": ["basic", "full", "comprehensive"],
  "estimated_analysis_time": "2-5 minutes per repository"
}
```

## Repository Analysis

### Analysis Depths

#### Basic Analysis
- **Scope**: Repository structure and key files
- **Files**: Up to 100 files
- **Processing**: 1-2 minutes
- **Output**: Summary and file listing

**Best for**: Large repositories, quick overviews

#### Full Analysis
- **Scope**: Complete codebase with relationships
- **Files**: Up to 1,000 files
- **Processing**: 3-5 minutes
- **Output**: Comprehensive documentation with diagrams

**Best for**: Medium-sized repositories, detailed analysis

#### Comprehensive Analysis
- **Scope**: Deep analysis including edge cases
- **Files**: Up to 5,000 files
- **Processing**: 5-10 minutes
- **Output**: Complete documentation with metrics

**Best for**: Smaller repositories, thorough documentation

### Processing Pipeline

The analysis follows a structured pipeline:

1. **Repository Validation** (10-20 seconds)
   - URL format validation
   - Repository accessibility check
   - Git clone operation

2. **Repository Mapping** (30-60 seconds)
   - File tree generation
   - README extraction
   - Structure analysis

3. **Code Analysis** (60-300 seconds)
   - File type identification
   - Language detection
   - Code structure parsing

4. **Documentation Generation** (30-120 seconds)
   - Markdown creation
   - Diagram generation
   - Cross-referencing

5. **Package Creation** (10-30 seconds)
   - ZIP archive creation
   - Metadata inclusion
   - Download preparation

### File Processing

#### Supported File Types
```python
SUPPORTED_EXTENSIONS = [
    ".py", ".js", ".ts", ".jsx", ".tsx",  # Scripting
    ".java", ".cpp", ".c", ".h",          # System languages
    ".go", ".rs", ".php", ".rb",          # Modern languages
    ".html", ".css", ".scss", ".vue",     # Web technologies
    ".md", ".rst", ".txt", ".json",       # Documentation
    ".yaml", ".yml", ".xml", ".toml"      # Configuration
]
```

#### File Size Limits
- **Maximum file size**: 10MB per file
- **Total repository size**: Configurable
- **Large file handling**: Automatic skipping with logging

#### Binary File Detection
- Automatic binary file identification
- Exclusion of non-text files
- Image and media file handling

## Output Formats

### Markdown Format

**Structure:**
```markdown
# Repository Documentation

## Overview
- Repository information
- Statistics and metrics
- File type distribution

## Code Structure
- Directory tree
- Key files and modules
- Relationship mappings

## Generated Documentation
- API documentation
- Code comments
- Usage examples

## Metadata
- Analysis details
- Processing information
- Generation timestamp
```

**Features:**
- ✅ Code syntax highlighting
- ✅ Table formatting
- ✅ Cross-references
- ✅ Automatic navigation

### HTML Format

**Structure:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Repository Documentation</title>
    <style>
        /* Professional styling */
    </style>
</head>
<body>
    <h1>Repository Documentation</h1>
    <!-- Generated content with styling -->
</body>
</html>
```

**Features:**
- ✅ Responsive design
- ✅ Professional styling
- ✅ Print-friendly formatting
- ✅ Interactive elements

### PDF Format

**Generation:**
- Requires additional dependencies
- High-quality output
- Print-optimized layout
- Professional presentation

**Features:**
- ✅ Vector graphics
- ✅ Page breaks
- ✅ Table of contents
- ✅ Professional typography

## Workflow Management

### Concurrent Workflows

The system supports multiple simultaneous analyses:

#### Default Limits
- **Maximum concurrent**: 5 workflows
- **Queue management**: FIFO processing
- **Resource allocation**: CPU and memory aware

#### Scaling Configuration
```bash
export MAX_CONCURRENT_WORKFLOWS=10
```

### Workflow Lifecycle

#### States
1. **Created**: Workflow ID generated
2. **Queued**: Awaiting processing
3. **Running**: Active analysis
4. **Completed**: Successfully finished
5. **Failed**: Error occurred
6. **Deleted**: Removed from system

#### State Transitions
```
Created → Queued → Running → Completed
                ↓         ↓
                Failed ← Failed
```

#### Cleanup Policy
- **Active workflows**: Unlimited duration
- **Completed workflows**: 7-day retention
- **Failed workflows**: 24-hour retention
- **Automatic cleanup**: Daily garbage collection

### Error Handling

#### Common Error Scenarios

**Network Issues:**
```json
{
  "status": "failed",
  "error_message": "Repository URL is invalid or inaccessible"
}
```

**Resource Limits:**
```json
{
  "status": "failed",
  "error_message": "Repository too large: exceeds file limit"
}
```

**Processing Errors:**
```json
{
  "status": "failed",
  "error_message": "Code parsing failed: unsupported language"
}
```

#### Recovery Mechanisms
- Automatic retry for network errors
- Graceful handling of malformed repositories
- Comprehensive error logging
- User-friendly error messages

## Best Practices

### Repository Selection

#### Optimal Repositories
- ✅ Well-structured projects
- ✅ Clear README files
- ✅ Standard programming languages
- ✅ Reasonable file count (<5,000 files)

#### Challenging Repositories
- ⚠️ Monorepos with many subprojects
- ⚠️ Binary files and media content
- ⚠️ Very large files (>10MB)
- ⚠️ Proprietary or closed-source code

#### Avoid These
- ❌ Private repositories (no access)
- ❌ Empty or archived repositories
- ❌ Repositories with access restrictions
- ❌ Extremely large repositories (>100,000 files)

### Performance Optimization

#### For Fast Analysis
```bash
# Use basic analysis
"analysis_depth": "basic"

# Limit file processing
"max_files_per_repository": 100

# Quick repository selection
"git_clone_depth": 1
```

#### For Comprehensive Results
```bash
# Use full analysis
"analysis_depth": "comprehensive"

# Include diagrams
"include_diagrams": true

# Allow more processing time
```

### Resource Management

#### Memory Optimization
```bash
# Reduce concurrent workflows
export MAX_CONCURRENT_WORKFLOWS=2

# Limit repository size
export MAX_FILES_PER_REPOSITORY=1000

# Enable aggressive cleanup
export WORKFLOW_RETENTION_DAYS=1
```

#### CPU Optimization
```bash
# Increase worker processes
export WORKERS=4

# Optimize analysis depth
"analysis_depth": "full"
```

### Quality Assurance

#### Documentation Validation
- Check generated documentation completeness
- Verify file analysis accuracy
- Validate cross-references
- Test download functionality

#### Performance Monitoring
- Monitor analysis completion times
- Track resource usage patterns
- Identify bottlenecks
- Optimize configuration

## Advanced Features

### Custom Configuration

#### Repository Filtering
```python
# File type filters
TEXT_EXTENSIONS = [".py", ".js", ".java"]
BINARY_EXTENSIONS = [".png", ".jpg", ".pdf"]

# Size limits
MAX_FILE_SIZE = 10485760  # 10MB
MAX_FILES_PER_REPO = 10000
```

#### Analysis Customization
```python
# Language priorities
LANGUAGE_WEIGHTS = {
    "python": 1.0,
    "javascript": 0.8,
    "java": 0.6
}

# Relationship extraction
INCLUDE_RELATIONSHIPS = True
MAX_RELATIONSHIPS_PER_FILE = 100
```

### Integration Examples

#### Python Client
```python
import requests
import time

class CodebaseGenius:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        
    def analyze_repository(self, repo_url, **options):
        # Start analysis
        response = requests.post(f"{self.base_url}/api/analyze", json={
            "repository_url": repo_url,
            **options
        })
        workflow_id = response.json()["workflow_id"]
        
        # Monitor progress
        while True:
            status = requests.get(f"{self.base_url}/api/status/{workflow_id}")
            data = status.json()
            
            if data["status"] == "completed":
                return data["result"]
            elif data["status"] == "failed":
                raise Exception(f"Analysis failed: {data['error_message']}")
                
            time.sleep(5)
            
    def download_documentation(self, workflow_id):
        response = requests.get(f"{self.base_url}/api/download/{workflow_id}")
        return response.content
```

#### JavaScript Client
```javascript
class CodebaseGenius {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async analyzeRepository(repoUrl, options = {}) {
        // Start analysis
        const response = await fetch(`${this.baseUrl}/api/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ repository_url: repoUrl, ...options })
        });
        
        const { workflow_id } = await response.json();
        
        // Monitor progress
        while (true) {
            const status = await fetch(`${this.baseUrl}/api/status/${workflow_id}`);
            const data = await status.json();
            
            if (data.status === 'completed') {
                return data.result;
            } else if (data.status === 'failed') {
                throw new Error(`Analysis failed: ${data.error_message}`);
            }
            
            await new Promise(resolve => setTimeout(resolve, 5000));
        }
    }
}
```

### Batch Processing

#### Multiple Repository Analysis
```python
import asyncio
import aiohttp

async def analyze_multiple_repos(repositories):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for repo in repositories:
            task = analyze_single_repo(session, repo)
            tasks.append(task)
            
        results = await asyncio.gather(*tasks)
        return results

async def analyze_single_repo(session, repo_url):
    # Start analysis
    async with session.post('http://localhost:8000/api/analyze', json={
        'repository_url': repo_url,
        'analysis_depth': 'full'
    }) as response:
        workflow_id = (await response.json())['workflow_id']
        
    # Wait for completion
    while True:
        async with session.get(f'http://localhost:8000/api/status/{workflow_id}') as status:
            data = await status.json()
            
            if data['status'] == 'completed':
                return data['result']
            elif data['status'] == 'failed':
                return None
                
        await asyncio.sleep(5)
```

### Webhook Integration

#### GitHub Webhook Handler
```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    event = request.headers.get('X-GitHub-Event')
    
    if event == 'push':
        data = request.json
        repo_url = data['repository']['html_url']
        branch = data['ref'].split('/')[-1]
        
        # Trigger automatic analysis
        response = requests.post('http://localhost:8000/api/analyze', json={
            'repository_url': repo_url,
            'branch': branch,
            'analysis_depth': 'basic'
        })
        
        return jsonify({'status': 'analysis_triggered'})
        
    return jsonify({'status': 'ignored'})
```

### Custom Templates

#### Markdown Template Customization
```python
# Custom template for Python projects
PYTHON_PROJECT_TEMPLATE = """
# {title}

## Project Overview
{description}

## Installation
```bash
{installation_instructions}
```

## Usage
{usage_examples}

## API Reference
{api_documentation}

## Contributing
{contributing_guidelines}
"""

def generate_python_documentation(structure, template=None):
    template = template or PYTHON_PROJECT_TEMPLATE
    return template.format(**structure)
```

---

## Conclusion

This user guide covers all aspects of using Codebase Genius effectively. For additional help:

- 📖 **Installation**: [INSTALLATION.md](INSTALLATION.md)
- 🔧 **API Reference**: [API Documentation](api-documentation.md)
- 🏗️ **Architecture**: [Architecture Guide](architecture.md)
- 📊 **Samples**: [Sample Outputs](../samples/)

**Happy documenting! 🎉**
