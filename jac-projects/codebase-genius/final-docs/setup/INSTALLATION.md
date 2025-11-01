# Codebase Genius - Complete Setup and Installation Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Quick Start](#quick-start)
4. [Detailed Setup](#detailed-setup)
5. [Configuration](#configuration)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Deployment](#advanced-deployment)

## Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows 10/11
- **Python**: Version 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: Minimum 2GB free space
- **Network**: Internet connection for repository cloning

### Required Software
```bash
# Python 3.8+ with pip
python --version

# Git for repository operations
git --version

# Docker (optional, for containerized deployment)
docker --version

# Docker Compose (optional)
docker-compose --version
```

### Python Dependencies
The system automatically installs these packages:
- FastAPI, Uvicorn (API Server)
- Streamlit (Frontend)
- Tree-sitter (Code Parsing)
- Pandas, Plotly (Data Analysis)
- Markdown, Pygments (Documentation)

## Installation Methods

### Method 1: Quick Installation (Recommended)

1. **Clone the Repository**
```bash
git clone <repository-url>
cd codebase-genius-impl
```

2. **Run Quick Setup**
```bash
cd api-frontend
python start.py install
python start.py start
```

3. **Access the Application**
- Frontend: http://localhost:8501
- API: http://localhost:8000

### Method 2: Manual Installation

1. **Install Dependencies**
```bash
cd api-frontend
pip install -r requirements.txt
```

2. **Start Services Separately**

**Terminal 1 - API Server:**
```bash
cd api-frontend
python -m uvicorn api.main_api:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Streamlit Frontend:**
```bash
cd api-frontend
streamlit run frontend/streamlit_app.py --server.port 8501
```

### Method 3: Docker Deployment

1. **Build and Run with Docker Compose**
```bash
docker-compose up --build
```

2. **Access Services**
- Frontend: http://localhost:8501
- API: http://localhost:8000
- Health Check: http://localhost:8000/health

## Quick Start

### Using the Web Interface

1. **Start the Application**
```bash
python api-frontend/start.py start
```

2. **Open Web Interface**
Navigate to: http://localhost:8501

3. **Analyze a Repository**
   - Enter repository URL: `https://github.com/python/cpython`
   - Select output format: `Markdown`
   - Click "🧠 Start Analysis"
   - Monitor progress in real-time
   - Download generated documentation

### Using the API Directly

1. **Start Analysis**
```bash
curl -X POST "http://localhost:8000/api/analyze" \\
     -H "Content-Type: application/json" \\
     -d '{
       "repository_url": "https://github.com/python/cpython",
       "analysis_depth": "full",
       "format": "markdown"
     }'
```

2. **Check Status**
```bash
curl "http://localhost:8000/api/status/{workflow_id}"
```

3. **Download Results**
```bash
curl -o documentation.zip "http://localhost:8000/api/download/{workflow_id}"
```

## Detailed Setup

### Environment Configuration

Create `.env` file in `api-frontend/` directory:
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
WORKERS=1

# Frontend Configuration
STREAMLIT_PORT=8501
STREAMLIT_HOST=0.0.0.0
STREAMLIT_DEBUG=false

# Repository Settings
GIT_CLONE_DEPTH=1
GIT_CLONE_TIMEOUT=300
MAX_FILES_PER_REPOSITORY=10000
MAX_FILE_SIZE_BYTES=10485760

# Workflow Management
MAX_CONCURRENT_WORKFLOWS=5
MAX_WORKFLOW_DURATION=1800
WORKFLOW_RETENTION_DAYS=7

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/codebase_genius.log
ENABLE_JSON_LOGS=false

# Security
REQUIRE_API_KEY=false
RATE_LIMIT_PER_MINUTE=60
```

### Performance Tuning

For better performance, adjust these settings:

**High-Performance Configuration:**
```bash
MAX_CONCURRENT_WORKFLOWS=10
MAX_FILES_PER_REPOSITORY=20000
WORKERS=4
```

**Resource-Constrained Environment:**
```bash
MAX_CONCURRENT_WORKFLOWS=2
MAX_FILES_PER_REPOSITORY=5000
WORKERS=1
```

### Security Configuration

**Production Settings:**
```bash
ENVIRONMENT=production
REQUIRE_API_KEY=true
ENABLE_RATE_LIMITING=true
CORS_ALLOW_ORIGINS=["https://yourdomain.com"]
```

## Configuration

### API Configuration

The API server can be configured through environment variables:

```bash
# Server Settings
API_HOST=0.0.0.0              # Server host
API_PORT=8000                 # Server port
DEBUG=false                   # Debug mode
WORKERS=1                     # Number of worker processes

# CORS Settings
CORS_ORIGINS=["*"]           # Allowed origins
CORS_ALLOW_CREDENTIALS=true   # Allow credentials

# Rate Limiting
RATE_LIMIT_REQUESTS=100       # Requests per window
RATE_LIMIT_WINDOW=60          # Window in seconds
```

### Repository Processing Settings

```bash
# Clone Settings
GIT_CLONE_DEPTH=1             # Shallow clone depth
GIT_CLONE_TIMEOUT=300         # Timeout in seconds

# File Processing
MAX_FILES_PER_REPOSITORY=10000
MAX_FILE_SIZE_BYTES=10485760  # 10MB
SUPPORTED_FILE_EXTENSIONS=[".py",".js",".java",".cpp",".c",".h"]

# Analysis Settings
TREE_SITTER_LANGUAGES=["python","javascript","java","cpp","c"]
ANALYSIS_LEVELS=["basic","full","comprehensive"]
```

### Frontend Configuration

```bash
# Streamlit Settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HOST=0.0.0.0
STREAMLIT_DEBUG=false

# UI Settings
THEME_PRIMARY_COLOR=#2E86AB
ENABLE_DARK_MODE=true
ENABLE_WORKFLOW_HISTORY=true
```

## Verification

### Health Check

Verify all services are running:

```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "active_workflows": 0,
  "completed_workflows": 0
}
```

### Test Analysis

Run a simple test analysis:

1. Open http://localhost:8501
2. Enter repository URL: `https://github.com/octocat/Hello-World`
3. Click "Start Analysis"
4. Verify progress updates
5. Download documentation

### API Testing

Test API endpoints:

```bash
# Test repository validation
curl -X POST "http://localhost:8000/api/analyze" \\
     -H "Content-Type: application/json" \\
     -d '{"repository_url":"https://github.com/octocat/Hello-World"}'
```

## Troubleshooting

### Common Issues

**Issue: "API Server not responding"**
```bash
# Check if port is in use
netstat -tulpn | grep 8000

# Kill existing processes
pkill -f "uvicorn"
pkill -f "streamlit"

# Restart services
python api-frontend/start.py start
```

**Issue: "Repository clone failed"**
```bash
# Check git configuration
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Test git clone manually
git clone https://github.com/octocat/Hello-World test-clone
```

**Issue: "Out of memory during analysis"**
```bash
# Reduce concurrent workflows
export MAX_CONCURRENT_WORKFLOWS=1

# Limit file processing
export MAX_FILES_PER_REPOSITORY=1000
```

**Issue: "Frontend not loading"**
```bash
# Check Streamlit logs
streamlit run frontend/streamlit_app.py --server.port 8501 --logger.level=debug

# Clear browser cache
# Try incognito/private mode
```

### Debug Mode

Enable debug logging:

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
python api-frontend/start.py start
```

### Log Files

Check log files for detailed error information:

```bash
# API logs
tail -f logs/codebase_genius.log

# System logs
journalctl -u codebase-genius -f
```

### Performance Issues

**Slow Analysis:**
- Reduce `MAX_FILES_PER_REPOSITORY`
- Increase `GIT_CLONE_DEPTH` to 1
- Use `basic` analysis depth for large repos

**High Memory Usage:**
- Decrease `MAX_CONCURRENT_WORKFLOWS`
- Enable automatic cleanup
- Monitor with `htop` or `ps`

## Advanced Deployment

### Production Deployment

**Using Gunicorn:**
```bash
pip install gunicorn
gunicorn api.main_api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Reverse Proxy with Nginx:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Scaling

**Horizontal Scaling:**
```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  codebase-genius:
    build: .
    ports:
      - "8000-8003:8000"
    environment:
      - WORKER_ID=${WORKER_ID:-1}
```

**Load Balancer Configuration:**
```bash
# Using HAProxy
frontend http_front
    bind *:80
    default_backend api_servers

backend api_servers
    balance roundrobin
    server api1 127.0.0.1:8000 check
    server api2 127.0.0.1:8001 check
    server api3 127.0.0.1:8002 check
```

### Monitoring

**Health Check Endpoint:**
```bash
# Automated health monitoring
while true; do
    status=$(curl -s http://localhost:8000/health | jq -r '.status')
    if [ "$status" != "healthy" ]; then
        echo "Service unhealthy, restarting..."
        python api-frontend/start.py restart
    fi
    sleep 30
done
```

**Metrics Collection:**
```bash
# Install monitoring tools
pip install prometheus-client psutil

# Add to main_api.py
from prometheus_client import Counter, Histogram, Gauge
```

### Backup and Recovery

**Workflow Data Backup:**
```bash
# Backup workflow data
tar -czf backup-$(date +%Y%m%d).tar.gz /app/temp /app/logs

# Restore from backup
tar -xzf backup-20231201.tar.gz -C /
```

**Configuration Backup:**
```bash
# Backup environment configuration
cp .env .env.backup.$(date +%Y%m%d)
```

---

## Next Steps

After successful installation:

1. **Read the [User Guide](guides/user-guide.md)** for detailed usage instructions
2. **Explore the [API Documentation](guides/api-documentation.md)** for programmatic access
3. **Check [Sample Outputs](samples/)** to see expected documentation formats
4. **Review [Architecture Guide](guides/architecture.md)** for system design details

## Support

For additional support:
- Check the [Troubleshooting Guide](#troubleshooting)
- Review log files for error details
- Verify system requirements are met
- Test with simple repositories first

---

**Installation Complete! 🎉**

You can now analyze repositories and generate comprehensive documentation with Codebase Genius!
