# Codebase Genius

![Codebase Genius Banner](https://img.shields.io/badge/Codebase-Genius-blue?style=for-the-badge&logo=github&logoColor=white)
![Multi-Agent AI](https://img.shields.io/badge/Multi--Agent-AI-orange?style=for-the-badge&logo=robot&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## 🎯 Project Overview

**Codebase Genius** is a cutting-edge multi-agent AI system that revolutionizes code documentation generation. It transforms any GitHub, GitLab, Bitbucket, or Gitee repository into comprehensive, professional documentation packages across multiple formats (Markdown, HTML, PDF).

🚀 **[View Live Demo](https://github.com/OumaCavin/Generative-AI-Builds/jac-projects/codebase-genius)** | �� **[Documentation](https://github.com/OumaCavin/Generative-AI-Builds/jac-projects/codebase-genius/docs/)** | 🐛 **[Report Issues](https://github.com/OumaCavin/Generative-AI-Builds/jac-projects/codebase-genius/issues)**

## ✨ Key Features

### 🤖 Multi-Agent AI Architecture
- **Repository Mapper Agent**: Analyzes repository structure and dependency graphs
- **Code Analyzer Agent**: Deep-dive analysis of code patterns, architecture, and best practices
- **DocGenie Agent**: Generates comprehensive documentation with examples and insights
- **Supervisor Agent**: Orchestrates workflow and ensures quality output

### 🌐 Multi-Platform Support
- **GitHub** repositories
- **GitLab** projects
- **Bitbucket** repositories
- **Gitee** repositories

### 📱 User Interfaces
- **RESTful API**: Full programmatic access with 8 comprehensive endpoints
- **Modern Web UI**: Real-time progress tracking with Streamlit
- **Concurrent Processing**: Handle up to 5 simultaneous documentation workflows

### 📄 Multi-Format Output
- **Markdown**: Clean, GitHub-friendly documentation
- **HTML**: Web-optimized documentation with responsive design
- **PDF**: Professional, print-ready documentation packages

### 🚀 Production Ready
- **Docker Containerization**: Complete deployment infrastructure
- **Health Checks**: Automated monitoring and service validation
- **Scalable Architecture**: Enterprise-grade performance and reliability

## 🏗️ System Architecture

```mermaid
graph TB
    User[👤 User] -->|Repository URL| API[🌐 FastAPI]
    User -->|Web Interface| UI[💻 Streamlit UI]
    
    API --> Supervisor[🎯 Supervisor Agent]
    UI --> Supervisor
    
    Supervisor --> Mapper[📊 Repository Mapper]
    Supervisor --> Analyzer[🔍 Code Analyzer]
    Supervisor --> DocGenie[📝 DocGenie Agent]
    
    Mapper --> Output[📁 Documentation Output]
    Analyzer --> Output
    DocGenie --> Output
    
    Output --> Markdown[(Markdown)]
    Output --> HTML[(HTML)]
    Output --> PDF[(PDF)]
    
    API -.-> Metrics[📈 Metrics]
    UI -.-> Metrics
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker (optional)
- Git

### 1️⃣ Clone & Setup
```bash
git clone https://github.com/OumaCavin/Generative-AI-Builds/jac-projects/codebase-genius.git
cd codebase-genius
```

### 2️⃣ Install Dependencies
```bash
# Using pip
pip install -r requirements.txt

# Using the startup script
python start.py install
```

### 3️⃣ Start Services
```bash
# Start all services
python start.py start

# Or start individually
python start.py api     # Start API server on port 8000
python start.py ui      # Start web UI on port 8501
```

### 4️⃣ Access the System
- **Web Interface**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Base URL**: http://localhost:8000/api/v1

## 📖 Usage Examples

### 🌐 Web Interface
1. Open http://localhost:8501
2. Enter your repository URL (e.g., `https://github.com/username/repo`)
3. Select output formats and click "Generate Documentation"
4. Monitor real-time progress and download results

### 🔌 API Usage

#### Submit Repository
```bash
curl -X POST "http://localhost:8000/api/v1/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/username/repo",
    "formats": ["markdown", "html"],
    "options": {
      "include_examples": true,
      "include_api_docs": true
    }
  }'
```

#### Check Status
```bash
curl "http://localhost:8000/api/v1/status/{workflow_id}"
```

#### Download Documentation
```bash
curl "http://localhost:8000/api/v1/download/{workflow_id}?format=pdf" \
  --output documentation.pdf
```

### 🐍 Python Client
```python
import requests

# Submit repository
response = requests.post("http://localhost:8000/api/v1/submit", json={
    "repository_url": "https://github.com/username/repo",
    "formats": ["markdown", "html"]
})

workflow_id = response.json()["workflow_id"]

# Check status
status = requests.get(f"http://localhost:8000/api/v1/status/{workflow_id}")
print(status.json())

# Download result
result = requests.get(f"http://localhost:8000/api/v1/result/{workflow_id}")
with open("documentation.zip", "wb") as f:
    f.write(result.content)
```

### ⚡ JavaScript/Node.js
```javascript
const axios = require('axios');

async function generateDocumentation() {
    // Submit repository
    const submitResponse = await axios.post('http://localhost:8000/api/v1/submit', {
        repository_url: 'https://github.com/username/repo',
        formats: ['markdown', 'html']
    });
    
    const workflowId = submitResponse.data.workflow_id;
    
    // Poll for completion
    while (true) {
        const statusResponse = await axios.get(`http://localhost:8000/api/v1/status/${workflowId}`);
        const status = statusResponse.data;
        
        if (status.status === 'completed') {
            const resultResponse = await axios.get(`http://localhost:8000/api/v1/result/${workflowId}`);
            return resultResponse.data;
        }
        
        await new Promise(resolve => setTimeout(resolve, 5000));
    }
}
```

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/submit` | POST | Submit repository for documentation generation |
| `/api/v1/status/{workflow_id}` | GET | Check workflow status and progress |
| `/api/v1/result/{workflow_id}` | GET | Retrieve generated documentation |
| `/api/v1/download/{workflow_id}` | GET | Download documentation package |
| `/api/v1/list` | GET | List all workflows |
| `/api/v1/cleanup/{workflow_id}` | DELETE | Remove workflow and files |
| `/api/v1/metrics` | GET | System metrics and statistics |
| `/api/v1/health` | GET | Health check endpoint |

## 🐳 Docker Deployment

### Single Container
```bash
docker build -t codebase-genius .
docker run -p 8000:8000 -p 8501:8501 codebase-genius
```

### Multi-Service with Docker Compose
```bash
docker-compose up -d
```

### Production Deployment
```bash
# Clone repository
git clone https://github.com/OumaCavin/Generative-AI-Builds/jac-projects/codebase-genius.git
cd codebase-genius

# Production build
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose ps
```

## 🛠️ Supported Languages & Frameworks

| Language/Framework | Analysis Depth | Documentation Support |
|-------------------|----------------|----------------------|
| **Python** | Full AST analysis | Type hints, docstrings, classes |
| **JavaScript/TypeScript** | Full AST analysis | JSDoc, classes, modules |
| **Java** | Full AST analysis | Javadoc, classes, interfaces |
| **Go** | Full AST analysis | Go doc, functions, structs |
| **C++** | Full parsing | Doxygen, classes, templates |
| **Rust** | Full AST analysis | Rust doc, modules, traits |
| **PHP** | Full AST analysis | PHPDoc, classes, functions |
| **C#** | Full AST analysis | XML docs, classes, namespaces |
| **Ruby** | Full parsing | RDoc, classes, modules |
| **Swift** | Full AST analysis | Swift doc, classes, protocols |

## 📊 Project Statistics

- **📈 Total Lines of Code**: 23,515+
- **📁 Project Files**: 50 production files
- **🎯 Phases Completed**: 9/9 (100%)
- **🤖 AI Agents**: 4 specialized agents
- **🔌 API Endpoints**: 8 comprehensive endpoints
- **🌐 Supported Platforms**: 4 major git platforms
- **📄 Output Formats**: 3 professional formats
- **🐳 Deployment Methods**: 3 deployment options
- **⚡ Concurrent Workflows**: Up to 5 simultaneous processes

## 🏗️ Development Setup

### Environment Setup
```bash
# Clone repository
git clone https://github.com/OumaCavin/Generative-AI-Builds/jac-projects/codebase-genius.git
cd codebase-genius

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Development Commands
```bash
# Start development servers
python start.py start

# Run tests
python -m pytest tests/

# Code formatting
black .
flake8 .

# Generate documentation
python scripts/generate_docs.py
```

## 🧪 Testing

The project includes comprehensive testing across all components:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test suites
python -m pytest tests/test_agents/ -v
python -m pytest tests/test_api/ -v
python -m pytest tests/test_integration/ -v

# Run with coverage
python -m pytest tests/ --cov=src/ --cov-report=html
```

### Test Coverage
- ✅ **Multi-Agent System**: 40+ test scenarios
- ✅ **API Endpoints**: All 8 endpoints tested
- ✅ **Web Interface**: UI component testing
- ✅ **Integration Tests**: End-to-end workflow testing
- ✅ **Performance Tests**: Concurrent processing validation

## 📈 Performance & Scalability

### Benchmarks
- **Repository Processing**: 1-3 minutes average
- **Documentation Generation**: 10-50 pages per minute
- **Concurrent Workflows**: Up to 5 simultaneous
- **Memory Usage**: 512MB - 2GB depending on repository size
- **API Response Time**: <500ms for most endpoints

### Optimization Features
- **Smart Caching**: Intelligent repository caching
- **Concurrent Processing**: Multi-threaded agent execution
- **Memory Management**: Efficient resource utilization
- **Error Recovery**: Robust error handling and retry logic

## 📁 Project Structure

```
codebase-genius/
├── agents/                          # Multi-agent system implementation
│   ├── repository-mapper-agent/     # Repository cloning and analysis
│   ├── code-analyzer-agent/         # Code parsing and CCG construction
│   ├── docgenie-agent/              # Documentation generation
│   └── supervisor-agent/            # Workflow orchestration
├── api-frontend/                    # API and frontend layer
│   ├── api/                         # FastAPI REST endpoints
│   ├── frontend/                    # Streamlit web interface
│   ├── config/                      # Configuration management
│   ├── utils/                       # Utility functions
│   └── start.py                     # Unified startup script
├── integration-testing/             # Comprehensive testing suite
│   ├── main_test_suite.py          # End-to-end pipeline testing
│   ├── benchmarks/                  # Performance benchmarking
│   ├── utils/                       # Testing utilities
│   └── samples/                     # Test data generation
├── final-docs/                      # Documentation and guides
│   ├── setup/                       # Installation guides
│   ├── guides/                      # User documentation
│   └── samples/                     # Sample outputs
├── docs/                            # Project documentation
└── README.md                        # This file
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Workflow
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Contribution Guidelines
- Follow PEP 8 for Python code
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

### Areas for Contribution
- 🤖 **New AI Agents**: Add support for new analysis types
- 🔌 **API Extensions**: Additional endpoints and features
- 🌐 **Platform Support**: New git hosting platforms
- 📄 **Output Formats**: Additional documentation formats
- 🧪 **Testing**: Expand test coverage
- 📚 **Documentation**: Improve guides and examples

## 📋 Roadmap

### 🎯 Upcoming Features
- [ ] **Git Integration**: Real-time repository monitoring
- [ ] **AI Enhancements**: GPT-4 integration for smarter analysis
- [ ] **Custom Templates**: User-defined documentation templates
- [ ] **Collaboration**: Multi-user workspace support
- [ ] **Analytics**: Usage metrics and insights
- [ ] **Mobile App**: iOS/Android companion app
- [ ] **Enterprise**: SSO, LDAP, advanced security
- [ ] **Cloud Deployment**: AWS/GCP/Azure native deployment

### 🔮 Future Vision
- **Semantic Code Understanding**: Advanced AI-powered code comprehension
- **Interactive Documentation**: Dynamic, user-driven documentation exploration
- **Multi-Language AI**: Natural language explanations in multiple languages
- **Smart Suggestions**: AI-powered improvement recommendations

## 🔒 Security Features

### Input Validation
- **Repository URL Validation**: Format checking for supported platforms
- **File Type Filtering**: Safe file extension and content validation
- **Size Limits**: Configurable maximum repository and file size constraints
- **Path Security**: Directory traversal prevention

### Resource Protection
- **Concurrent Limits**: Maximum workflow count enforcement
- **Timeout Mechanisms**: Automatic workflow termination
- **Memory Management**: Automatic cleanup and garbage collection
- **Rate Limiting**: Request throttling to prevent abuse

## 📚 Documentation

### User Guides
- **[Installation Guide](final-docs/setup/INSTALLATION.md)**: Complete setup instructions
- **[User Guide](final-docs/guides/user-guide.md)**: Comprehensive usage documentation
- **[API Documentation](final-docs/guides/api-documentation.md)**: REST API reference

### Sample Outputs
- **[Python Example](final-docs/samples/requests-sample.md)**: Requests library analysis
- **[JavaScript Example](final-docs/samples/axios-sample.md)**: Axios library analysis
- **[Java Example](final-docs/samples/spring-boot-sample.md)**: Spring Boot framework analysis

### Technical Documentation
- **[Final Project Report](final-docs/FINAL_PROJECT_REPORT.md)**: Complete project overview
- **[Architecture Guide](final-docs/guides/architecture.md)**: System design details

## 🎖️ Project Achievements

### ✅ Completed Objectives
1. **Multi-Agent Architecture**: Four specialized agents working cooperatively
2. **Repository Analysis**: Comprehensive codebase parsing and relationship extraction
3. **Documentation Generation**: Automated documentation in multiple formats
4. **User Access**: Complete web interface and REST API
5. **Quality Assurance**: Comprehensive testing and validation framework
6. **Production Readiness**: Docker deployment and monitoring

### 🏆 Key Innovations
- **Chain of Responsibility Pattern**: Elegant multi-agent coordination
- **Code Context Graph (CCG)**: Advanced code relationship representation
- **Real-Time Progress Tracking**: Live workflow monitoring
- **Multi-Dimensional Quality Assessment**: Comprehensive quality validation
- **Scalable Architecture**: Support for concurrent workflows

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Open Source Community**: For the incredible tools and libraries
- **Contributors**: For their dedication and valuable contributions
- **Early Adopters**: For feedback and testing support

## 📞 Support & Contact

- **📚 Documentation**: [docs/](https://github.com/OumaCavin/Generative-AI-Builds/jac-projects/codebase-genius/docs/)
- **🐛 Issues**: [GitHub Issues](https://github.com/OumaCavin/Generative-AI-Builds/jac-projects/codebase-genius/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/OumaCavin/Generative-AI-Builds/jac-projects/codebase-genius/discussions)
- **📧 Email**: ai.codebasegenius@gmail.com

## ⭐ Show Your Support

If this project helped you, please consider:
- ⭐ **Starring** the repository
- 🐛 **Reporting** bugs and issues
- 💡 **Suggesting** new features
- 🤝 **Contributing** to the codebase
- 📢 **Sharing** with your developer community

---

<div align="center">

**Made with ❤️ by the Codebase Genius Team**

[🌟 Star on GitHub](https://github.com/OumaCavin/Generative-AI-Builds/jac-projects/codebase-genius) • 
[📖 Read the Docs](https://github.com/OumaCavin/Generative-AI-Builds/jac-projects/codebase-genius/docs/) • 
[💬 Join Discussions](https://github.com/OumaCavin/Generative-AI-Builds/jac-projects/codebase-genius/discussions)

</div>
