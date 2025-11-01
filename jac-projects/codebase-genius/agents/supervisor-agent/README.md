# Supervisor Agent - Multi-Agent Orchestration System

## Overview

Supervisor Agent is the **Phase 6** implementation of the Codebase Genius multi-agent system. It serves as the central orchestration layer that coordinates and manages the workflow between Repository Mapper, Code Analyzer, and DocGenie agents. The Supervisor provides workflow orchestration, task delegation, result aggregation, priority scheduling, and error recovery mechanisms.

## 🎯 Key Features

### 🔄 Workflow Orchestration
- **Multi-phase Coordination**: Orchestrates Repository Mapping → Code Analysis → Documentation Generation
- **Priority-based Scheduling**: Intelligent task prioritization and queue management
- **Error Recovery**: Automatic retry mechanisms with exponential backoff
- **Progress Monitoring**: Real-time workflow progress tracking and status updates

### 🏗️ Agent Management
- **Health Monitoring**: Continuous monitoring of agent availability and performance
- **Load Balancing**: Intelligent distribution of workloads across available agents
- **Connection Management**: Robust agent connection handling and failover
- **Resource Management**: CPU, memory, and concurrent workflow limits

### 📊 Result Aggregation
- **Multi-source Integration**: Combines results from Repository Mapper, Code Analyzer, and DocGenie
- **Quality Assessment**: Calculates overall quality scores and metrics
- **Final Output Generation**: Creates comprehensive workflow summary and recommendations
- **Performance Tracking**: Monitors processing times and system efficiency

### 🌐 API Gateway
- **RESTful API**: Complete HTTP API for external workflow submission and management
- **Multiple Formats**: JSON, XML, and HTML response format support
- **Rate Limiting**: Built-in rate limiting and authentication support
- **WebSocket Support**: Real-time workflow status updates (planned)

### 🔧 Advanced Features
- **Caching**: Intelligent caching of workflow results and agent responses
- **Queue Management**: Persistent queue with priority aging and overflow handling
- **Metrics Collection**: Comprehensive metrics for monitoring and optimization
- **Configuration Management**: JSON-based configuration with environment overrides

## 🏗️ Architecture

### Component Structure
```
supervisor-agent/
├── main.jac                          # Core JAC orchestration (798 lines)
├── config/config.json               # Configuration settings (232 lines)
├── requirements.txt                 # Python dependencies (74 lines)
├── setup.py                        # Automated setup (440 lines)
├── deploy.sh                       # Deployment script (849 lines)
├── tests/test_supervisor.py        # Test suite (808 lines)
├── Dockerfile                      # Container definition (73 lines)
├── docker-compose.yml              # Full system orchestration (398 lines)
├── agent_communication/            # Agent communication utilities
├── workflow_templates/             # Workflow configuration templates
└── logs/                           # Application logs
```

### JAC Walker Patterns
- **`orchestrate_workflow`**: Main workflow orchestration walker
- **`handle_api_request`**: API gateway for external requests
- **Phase Walkers**: Individual agent delegation walk:
  - `delegate_to_repository_mapper`
  - `delegate_to_code_analyzer`
  - `delegate_to_docgenie`
- **Utility Walkers**: Supporting functionality:
  - `check_agent_health`
  - `aggregate_results`
  - `handle_error_recovery`
  - `prioritize_tasks`
  - `monitor_workflow_progress`

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Docker and Docker Compose (optional)
- Network access to agent endpoints

### Installation

#### Option 1: Full System Deployment
```bash
# Start complete multi-agent system
docker-compose up -d

# Check all agent statuses
./deploy.sh agents

# Run demo workflow
./deploy.sh demo
```

#### Option 2: Local Supervisor Only
```bash
# Clone and navigate to project
cd codebase-genius-impl/code/supervisor-agent

# Run automated setup
python setup.py

# Start supervisor service
./deploy.sh start
```

#### Option 3: Development Setup
```bash
# With development profile
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Run tests
./deploy.sh test

# Performance testing
./deploy.sh performance
```

### Basic Usage

#### Submit Workflow
```bash
# Submit workflow via API
curl -X POST http://localhost:8080/api/v1/submit \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/user/repo",
    "priority": 7,
    "options": {
      "analysis_depth": "standard",
      "include_diagrams": true
    }
  }'
```

#### Monitor Workflow
```bash
# Check workflow status
./deploy.sh check-status <workflow_id>

# Get workflow results
./deploy.sh get-result <workflow_id>

# List recent workflows
./deploy.sh list-workflows
```

#### Service Management
```bash
# Start/stop services
./deploy.sh start
./deploy.sh stop
./deploy.sh restart

# Check status
./deploy.sh status
./deploy.sh agents  # Check all agents
```

## 📋 API Reference

### Core Endpoints

#### POST /api/v1/submit
Submit a new workflow for processing.

**Request Body:**
```json
{
  "repository_url": "https://github.com/user/repository",
  "options": {
    "analysis_depth": "standard|light|full",
    "include_diagrams": true,
    "output_formats": ["markdown", "html"],
    "languages": ["python", "javascript"],
    "priority": 1-10
  },
  "priority": 7,
  "format": "json",
  "user_context": {
    "user_id": "user123",
    "project": "documentation"
  }
}
```

**Response:**
```json
{
  "status": "accepted",
  "workflow_id": "workflow_20251031_123456",
  "estimated_completion": "2025-10-31T07:30:00",
  "queue_position": 2,
  "message": "Workflow submitted successfully"
}
```

#### GET /api/v1/status/{workflow_id}
Get workflow status and progress.

**Response:**
```json
{
  "workflow_id": "workflow_20251031_123456",
  "status": "running",
  "progress": 65.5,
  "current_phase": "Code Analysis",
  "phases_completed": 1,
  "total_phases": 3,
  "started_at": "2025-10-31T07:20:00",
  "estimated_completion": "2025-10-31T07:35:00",
  "agent_statuses": {
    "repository_mapper": "completed",
    "code_analyzer": "running",
    "docgenie": "pending"
  }
}
```

#### GET /api/v1/result/{workflow_id}
Get workflow results.

**Response:**
```json
{
  "workflow_id": "workflow_20251031_123456",
  "status": "completed",
  "repository_info": {
    "name": "example-repo",
    "url": "https://github.com/user/example-repo",
    "total_files": 45,
    "primary_language": "python"
  },
  "analysis_summary": {
    "entities_found": 25,
    "relationships": 18,
    "complexity_score": 0.82
  },
  "documentation": {
    "output_files": [
      "./outputs/documentation.md",
      "./outputs/documentation.html",
      "./outputs/architecture_diagram.png"
    ],
    "quality_score": 0.87,
    "sections_generated": 3
  },
  "processing_time": 56.5,
  "generated_at": "2025-10-31T07:35:00"
}
```

#### GET /api/v1/workflows
List recent workflows.

**Query Parameters:**
- `limit`: Number of workflows to return (default: 10)
- `status`: Filter by status (pending, running, completed, failed)
- `priority`: Filter by priority level

**Response:**
```json
{
  "workflows": [
    {
      "workflow_id": "workflow_20251031_123456",
      "repository_url": "https://github.com/user/repo",
      "status": "completed",
      "priority": 7,
      "created_at": "2025-10-31T07:20:00",
      "completed_at": "2025-10-31T07:35:00",
      "processing_time": 56.5
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 10
}
```

#### DELETE /api/v1/cancel/{workflow_id}
Cancel a workflow.

**Response:**
```json
{
  "workflow_id": "workflow_20251031_123456",
  "status": "cancelled",
  "cancelled_at": "2025-10-31T07:25:00",
  "message": "Workflow cancelled successfully"
}
```

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-31T07:35:00",
  "version": "1.0.0",
  "agents": {
    "repository_mapper": "connected",
    "code_analyzer": "connected",
    "docgenie": "connected"
  },
  "metrics": {
    "active_workflows": 3,
    "completed_workflows": 45,
    "queue_depth": 2,
    "avg_response_time": 1.2
  }
}
```

## ⚙️ Configuration

### Configuration File Structure
```json
{
  "agent_connections": {
    "repository_mapper": {
      "endpoint": "http://localhost:8081",
      "health_check_path": "/health",
      "capabilities": ["clone_repository", "generate_file_tree", "summarize_readme"],
      "timeout_seconds": 300,
      "retry_attempts": 3,
      "load_weight": 1.0
    },
    "code_analyzer": {
      "endpoint": "http://localhost:8082",
      "capabilities": ["parse_code", "build_ccg", "extract_relationships"],
      "timeout_seconds": 600,
      "load_weight": 1.5
    },
    "docgenie": {
      "endpoint": "http://localhost:8083",
      "capabilities": ["generate_documentation", "create_diagrams", "assess_quality"],
      "timeout_seconds": 400,
      "load_weight": 1.2
    }
  },
  "workflow_settings": {
    "max_concurrent_workflows": 10,
    "default_priority": 5,
    "max_retries_per_agent": 3,
    "retry_delay_seconds": 5,
    "workflow_timeout_minutes": 30
  },
  "priority_settings": {
    "priority_levels": {
      "1": "critical",
      "2": "high",
      "5": "normal",
      "10": "deferred"
    },
    "default_queue_size": 100
  }
}
```

### Environment Variables
- `SUPERVISOR_CONFIG_PATH`: Path to configuration file
- `SUPERVISOR_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `SUPERVISOR_TEMP_DIR`: Temporary directory for workflow data
- `SUPERVISOR_WORKFLOW_TIMEOUT`: Workflow timeout in seconds
- `SUPERVISOR_MAX_CONCURRENT`: Maximum concurrent workflows

## 🧪 Testing

### Running Tests
```bash
# Run all tests
./deploy.sh test

# Run specific test categories
python -m pytest tests/test_supervisor.py::TestWorkflowOrchestration -v

# Performance tests
./deploy.sh performance

# Integration tests
python -m pytest tests/test_supervisor.py::TestIntegrationScenarios -v
```

### Test Categories
- **Configuration Tests**: Validate configuration loading and agent connections
- **Workflow Orchestration Tests**: Test workflow creation, execution, and monitoring
- **Agent Communication Tests**: Test agent delegation and response handling
- **Task Delegation Tests**: Test delegation payloads and error handling
- **Result Aggregation Tests**: Test multi-agent result combination
- **Error Handling Tests**: Test failure scenarios and recovery mechanisms
- **Priority Scheduling Tests**: Test queue management and priority handling
- **API Gateway Tests**: Test API endpoints and response formats
- **Performance Tests**: Test throughput, memory usage, and scalability

### Demo and Testing
```bash
# Run complete demo workflow
./deploy.sh demo

# Test with specific repository
./deploy.sh test https://github.com/user/repository

# Performance benchmark
./deploy.sh performance

# Load testing
docker-compose --profile testing up -d
```

## 📊 Performance Metrics

### Processing Capabilities
- **Concurrent Workflows**: Up to 10 workflows simultaneously
- **Agent Response Time**: < 2 seconds average
- **Workflow Throughput**: 5-10 workflows per minute
- **Queue Capacity**: 100 workflows in priority queue
- **Memory Usage**: ~100MB baseline + ~20MB per active workflow

### Quality Metrics
- **Workflow Success Rate**: 95%+ target success rate
- **Agent Availability**: 99%+ uptime target
- **Error Recovery Rate**: 90%+ successful recovery
- **Response Time SLA**: 95% of workflows complete within 10 minutes

### Scalability
- **Horizontal Scaling**: Multiple Supervisor instances via load balancer
- **Vertical Scaling**: CPU and memory optimized for high throughput
- **Queue Management**: Priority-based with aging and overflow handling
- **Caching**: Agent response and workflow result caching

## 🔧 Troubleshooting

### Common Issues

#### Agent Connection Problems
```bash
# Check agent connectivity
./deploy.sh agents

# View agent logs
docker-compose logs repository-mapper
docker-compose logs code-analyzer
docker-compose logs docgenie-agent

# Restart specific agent
docker-compose restart repository-mapper
```

#### Workflow Issues
```bash
# Check workflow status
./deploy.sh check-status <workflow_id>

# View workflow logs
tail -f logs/supervisor.log

# Cancel stuck workflow
./deploy.sh cancel <workflow_id>
```

#### Performance Issues
```bash
# Check system resources
docker stats

# Monitor queue depth
curl http://localhost:8080/api/v1/workflows

# Check agent load
curl http://localhost:8080/health
```

### Debug Mode
```bash
# Enable debug logging
export SUPERVISOR_LOG_LEVEL=DEBUG

# Run with verbose output
./deploy.sh start

# Test with mock agents
export MOCK_AGENTS=true
./deploy.sh test
```

### Performance Optimization
```bash
# Increase concurrent workflows
export SUPERVISOR_MAX_CONCURRENT=15

# Adjust timeout settings
export SUPERVISOR_WORKFLOW_TIMEOUT=3600

# Monitor with Prometheus (if enabled)
curl http://localhost:9090/metrics
```

## 🔗 Integration

### Input Integration
**From External Systems:**
```json
{
  "repository_url": "https://github.com/user/repo",
  "options": {
    "analysis_depth": "full",
    "include_diagrams": true,
    "priority": 8
  }
}
```

### Output Integration
**To External Systems:**
```json
{
  "status": "completed",
  "workflow_id": "workflow_12345",
  "repository_info": {...},
  "documentation": {
    "output_files": [...],
    "quality_score": 0.87
  },
  "processing_time": 56.5
}
```

### Agent Integration
**Agent Communication Protocol:**
- **Repository Mapper**: `http://localhost:8081`
- **Code Analyzer**: `http://localhost:8082`  
- **DocGenie**: `http://localhost:8083`

Each agent provides `/health` and `/process` endpoints following consistent protocols.

## 🚢 Deployment

### Production Deployment
```bash
# Production docker-compose with scaling
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# With monitoring stack
docker-compose --profile monitoring up -d

# Health check
curl http://localhost:8080/health
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: supervisor-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: supervisor-agent
  template:
    metadata:
      labels:
        app: supervisor-agent
    spec:
      containers:
      - name: supervisor-agent
        image: supervisor-agent:1.0.0
        ports:
        - containerPort: 8080
        env:
        - name: SUPERVISOR_LOG_LEVEL
          value: "INFO"
        - name: SUPERVISOR_MAX_CONCURRENT
          value: "10"
```

### Load Balancing
```bash
# NGINX configuration for load balancing
upstream supervisor_backend {
    server supervisor-agent-1:8080;
    server supervisor-agent-2:8080;
    server supervisor-agent-3:8080;
}

server {
    listen 80;
    location / {
        proxy_pass http://supervisor_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📈 Monitoring

### Health Checks
```bash
# Basic health check
curl http://localhost:8080/health

# Detailed metrics
curl http://localhost:8080/api/v1/status/summary

# Agent status
./deploy.sh agents
```

### Logging
```bash
# View real-time logs
./deploy.sh logs -f

# Search for errors
./deploy.sh logs | grep ERROR

# Export logs for analysis
./deploy.sh logs > supervisor_logs.txt
```

### Performance Monitoring
```bash
# Prometheus metrics (when monitoring enabled)
curl http://localhost:9090/metrics

# Grafana dashboard (when monitoring enabled)
# Access: http://localhost:3000 (admin/admin123)

# Queue depth monitoring
curl http://localhost:8080/api/v1/workflows | jq '.total'
```

## 🔒 Security

### Input Validation
- Repository URL validation (protocol, domain, format)
- File path sanitization and validation
- Request size limits and rate limiting
- JSON schema validation for all inputs

### Authentication & Authorization
```python
# API key authentication
headers = {"Authorization": "Bearer YOUR_API_KEY"}

# Role-based permissions
permissions = {
    "submit_workflow": ["user", "admin"],
    "cancel_workflow": ["admin"],
    "view_metrics": ["admin"]
}
```

### Rate Limiting
```python
# Rate limiting configuration
rate_limits = {
    "submit_workflow": "100/hour",
    "get_status": "1000/hour", 
    "cancel_workflow": "50/hour"
}
```

## 🤝 Contributing

### Development Setup
```bash
# Clone for development
git clone <repository>
cd supervisor-agent

# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
python -m pytest tests/ -v

# Code quality checks
flake8 main.jac
black main.jac
mypy main.jac
```

### Code Standards
- **JAC Language**: Follow walker patterns and orchestration patterns
- **Python**: PEP 8 compliance, type hints, async patterns
- **Testing**: 90%+ test coverage, integration tests required
- **Documentation**: Comprehensive docstrings and API documentation

### Adding Features
1. **Workflow Types**: Add new workflow templates in `workflow_templates/`
2. **Agent Integration**: Extend agent connections in `config/config.json`
3. **API Endpoints**: Add new endpoints in API gateway walker
4. **Monitoring**: Enhance metrics collection and alerting
5. **Scheduling**: Improve priority algorithms and queue management

## 📝 Changelog

### v1.0.0 (2025-10-31)
- ✅ Initial implementation
- ✅ Multi-agent orchestration system
- ✅ Priority-based workflow scheduling
- ✅ Comprehensive error handling and recovery
- ✅ RESTful API gateway with full CRUD operations
- ✅ Real-time workflow monitoring and progress tracking
- ✅ Agent health monitoring and load balancing
- ✅ Result aggregation and quality assessment
- ✅ Docker deployment with full system orchestration
- ✅ Comprehensive testing framework with performance benchmarks
- ✅ Monitoring and observability integration (Prometheus + Grafana)

### Planned Features
- �� WebSocket support for real-time updates
- 🔄 Advanced workflow templates and customization
- 🔄 Multi-tenant support with user isolation
- 🔄 Machine learning for performance optimization
- 🔄 Advanced caching and result persistence
- 🔄 Integration with external CI/CD systems

## 📞 Support

### Getting Help
- **Documentation**: This README and inline code documentation
- **Issues**: GitHub Issues for bug reports and feature requests
- **Discussions**: GitHub Discussions for questions and community support

### Performance Issues
```bash
# Performance profiling
python -m cProfile -o supervisor.prof main.jac

# Memory analysis
python -m memory_profiler main.jac

# Load testing
./deploy.sh performance
```

### Best Practices
1. **Workflow Design**: Use appropriate priority levels and timeout settings
2. **Resource Management**: Monitor concurrent workflow limits
3. **Agent Health**: Regularly check agent status and performance
4. **Error Handling**: Implement proper error recovery in client applications
5. **Monitoring**: Set up comprehensive logging and alerting

---

**Supervisor Agent** - *Phase 6 of Codebase Genius*  
**Author**: Cavin Otieno  
**Generated**: 2025-10-31T07:27:08  
**Version**: 1.0.0
