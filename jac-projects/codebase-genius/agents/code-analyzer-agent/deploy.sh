#!/bin/bash

# Codebase Genius Code Analyzer - Deployment and Testing Script
# Handles Tree-sitter setup, analysis, and performance testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${PURPLE}[DEBUG]${NC} $1"
}

# Check system prerequisites
check_system_prerequisites() {
    log_info "Checking system prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed."
        exit 1
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        log_error "Git is required but not installed."
        exit 1
    fi
    
    # Check pip
    if ! command -v pip &> /dev/null; then
        log_error "pip is required but not installed."
        exit 1
    fi
    
    # Check tree-sitter CLI (optional)
    if command -v tree-sitter &> /dev/null; then
        log_success "Tree-sitter CLI found"
        TREE_SITTER_AVAILABLE=true
    else
        log_warning "Tree-sitter CLI not found (optional)"
        TREE_SITTER_AVAILABLE=false
    fi
    
    log_success "System prerequisites satisfied"
}

# Setup Python environment
setup_python_environment() {
    log_info "Setting up Python environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_success "Created virtual environment"
    else
        log_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt
    
    log_success "Python environment ready"
}

# Install JAC runtime
install_jac_runtime() {
    log_info "Installing JAC runtime..."
    
    source venv/bin/activate
    pip install jaclang jac-cloud
    
    log_success "JAC runtime installed"
}

# Install Tree-sitter grammars
install_tree_sitter_grammars() {
    log_info "Installing Tree-sitter grammars..."
    
    # Create parsers directory
    mkdir -p parsers
    
    # List of grammars to install
    grammars=(
        "https://github.com/tree-sitter/tree-sitter-python.git:python"
        "https://github.com/tree-sitter/tree-sitter-javascript.git:javascript"
        "https://github.com/tree-sitter/tree-sitter-typescript.git:typescript"
        "https://github.com/tree-sitter/tree-sitter-java.git:java"
        "https://github.com/tree-sitter/tree-sitter-cpp.git:cpp"
        "https://github.com/tree-sitter/tree-sitter-c.git:c"
        "https://github.com/tree-sitter/tree-sitter-go.git:go"
        "https://github.com/tree-sitter/tree-sitter-rust.git:rust"
        "https://github.com/tree-sitter/tree-sitter-php.git:php"
        "https://github.com/tree-sitter/tree-sitter-ruby.git:ruby"
    )
    
    installed_count=0
    for grammar_spec in "${grammars[@]}"; do
        IFS=':' read -r repo_url lang_name <<< "$grammar_spec"
        
        if [ -d "parsers/$lang_name" ]; then
            log_info "Grammar $lang_name already installed"
            installed_count=$((installed_count + 1))
            continue
        fi
        
        log_info "Installing grammar: $lang_name"
        if git clone "$repo_url" "parsers/$lang_name"; then
            installed_count=$((installed_count + 1))
            log_success "Installed $lang_name grammar"
        else
            log_warning "Failed to install $lang_name grammar"
        fi
    done
    
    log_success "Installed $installed_count Tree-sitter grammars"
}

# Build Tree-sitter parsers
build_parsers() {
    if [ "$TREE_SITTER_AVAILABLE" = false ]; then
        log_warning "Tree-sitter CLI not available, skipping parser builds"
        return 0
    fi
    
    log_info "Building Tree-sitter parsers..."
    
    built_count=0
    for lang_dir in parsers/*/; do
        if [ -d "$lang_dir" ]; then
            lang_name=$(basename "$lang_dir")
            log_info "Building $lang_name parser..."
            
            if tree-sitter build "$lang_dir"; then
                built_count=$((built_count + 1))
                log_success "Built $lang_name parser"
            else
                log_warning "Failed to build $lang_name parser"
            fi
        fi
    done
    
    log_success "Built $built_count parsers"
}

# Create directory structure
create_directories() {
    log_info "Creating directory structure..."
    
    directories=(
        "logs"
        "cache"
        "output"
        "config"
        "tests"
        "data"
        "temp"
    )
    
    for directory in "${directories[@]}"; do
        mkdir -p "$directory"
    done
    
    log_success "Directory structure created"
}

# Run parser validation tests
validate_parsers() {
    log_info "Running parser validation tests..."
    
    source venv/bin/activate
    
    # Test Python parser
    if python3 -c "
import tree_sitter
try:
    lang = tree_sitter.Language('tree-sitter-python', 'python')
    parser = tree_sitter.Parser(lang)
    print('✅ Python parser: OK')
except Exception as e:
    print(f'❌ Python parser: {e}')
"; then
        log_success "Python parser validation passed"
    else
        log_warning "Python parser validation failed"
    fi
    
    # Test JavaScript parser
    if python3 -c "
import tree_sitter
try:
    lang = tree_sitter.Language('tree-sitter-javascript', 'javascript')
    parser = tree_sitter.Parser(lang)
    print('✅ JavaScript parser: OK')
except Exception as e:
    print(f'❌ JavaScript parser: {e}')
"; then
        log_success "JavaScript parser validation passed"
    else
        log_warning "JavaScript parser validation failed"
    fi
}

# Run code analysis tests
run_analysis_tests() {
    log_info "Running code analysis tests..."
    
    source venv/bin/activate
    
    # Ensure service is running for API tests
    if ! pgrep -f "jac serve" > /dev/null; then
        log_warning "Service not running, starting it for tests..."
        start_service
        sleep 10
    fi
    
    # Test with sample repository
    if python3 -c "
import requests
import json
import time

# Test health check
try:
    response = requests.get('http://localhost:8081/api/health', timeout=10)
    if response.status_code == 200:
        print('✅ API Health check: OK')
    else:
        print(f'❌ API Health check: {response.status_code}')
except Exception as e:
    print(f'❌ API Health check: {e}')
"; then
        log_success "API tests completed"
    else
        log_warning "API tests had issues"
    fi
}

# Start Code Analyzer service
start_service() {
    log_info "Starting Code Analyzer service..."
    
    source venv/bin/activate
    
    # Check if port is available
    if lsof -Pi :8081 -sTCP:LISTEN -t >/dev/null; then
        log_warning "Port 8081 already in use"
        return 1
    fi
    
    # Start service in background
    nohup jac serve main.jac > logs/service.log 2>&1 &
    echo $! > service.pid
    
    log_success "Service started (PID: $(cat service.pid))"
}

# Stop Code Analyzer service
stop_service() {
    log_info "Stopping service..."
    
    if [ -f "service.pid" ]; then
        PID=$(cat service.pid)
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            rm service.pid
            log_success "Service stopped"
        else
            log_warning "Service PID exists but process not running"
            rm service.pid
        fi
    else
        log_warning "No PID file found"
    fi
}

# Performance benchmarking
run_benchmarks() {
    log_info "Running performance benchmarks..."
    
    source venv/bin/activate
    
    # Ensure service is running
    if ! pgrep -f "jac serve" > /dev/null; then
        log_warning "Service not running, starting for benchmarks..."
        start_service
        sleep 10
    fi
    
    # Benchmark with test repository
    python3 -c "
import time
import requests
import json

start_time = time.time()

try:
    # Test repository analysis
    response = requests.post(
        'http://localhost:8081/api/analyze-repository',
        json={
            'repository_path': '/tmp/test_repo',
            'analysis_depth': 'basic',
            'max_file_size': 1048576
        },
        timeout=60
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    if response.status_code == 200:
        print(f'✅ Benchmark completed in {duration:.2f} seconds')
        result = response.json()
        if 'metrics' in result:
            metrics = result['metrics']
            print(f'   - Files analyzed: {metrics.get(\"total_files\", 0)}')
            print(f'   - Elements found: {metrics.get(\"total_elements\", 0)}')
            print(f'   - Relationships: {metrics.get(\"total_relationships\", 0)}')
    else:
        print(f'❌ Benchmark failed: {response.status_code}')
        print(response.text)
        
except Exception as e:
    print(f'❌ Benchmark error: {e}')
"
    
    log_success "Performance benchmarks completed"
}

# Show service status
show_status() {
    log_info "Code Analyzer service status:"
    
    if [ -f "service.pid" ]; then
        PID=$(cat service.pid)
        if kill -0 $PID 2>/dev/null; then
            echo "✅ Service is running (PID: $PID)"
            echo "📡 API available at: http://localhost:8081"
            echo "🏥 Health check: http://localhost:8081/api/health"
            echo "🔍 Analysis endpoint: http://localhost:8081/api/analyze-repository"
            echo "📊 Query endpoint: http://localhost:8081/api/query-relationships"
            echo "📈 Logs: tail -f logs/service.log"
        else
            echo "❌ Service PID exists but process is not running"
            rm service.pid
        fi
    else
        echo "❌ Service is not running"
    fi
}

# Clean up resources
cleanup() {
    log_info "Cleaning up resources..."
    
    # Stop service
    stop_service
    
    # Clean temporary files
    rm -rf temp/* 2>/dev/null || true
    rm -rf cache/* 2>/dev/null || true
    
    # Clean logs but keep recent ones
    find logs/ -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    log_success "Cleanup completed"
}

# Show help
show_help() {
    echo "Codebase Genius Code Analyzer - Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup             - Complete setup with Tree-sitter parsers"
    echo "  setup-basic       - Basic setup without Tree-sitter grammars"
    echo "  install-grammars  - Install Tree-sitter language grammars"
    echo "  build-parsers     - Build Tree-sitter parser binaries"
    echo "  validate          - Validate parser installation"
    echo "  start             - Start the service"
    echo "  stop              - Stop the service"
    echo "  restart           - Restart the service"
    echo "  status            - Show service status"
    echo "  test              - Run analysis tests"
    echo "  benchmark         - Run performance benchmarks"
    echo "  logs              - Show service logs"
    echo "  cleanup           - Clean up and stop service"
    echo "  demo              - Run a demo analysis"
    echo "  help              - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup           # Complete setup"
    echo "  $0 install-grammars # Install Tree-sitter grammars"
    echo "  $0 demo           # Run demo analysis"
    echo ""
    echo "Note: Some commands require tree-sitter CLI to be installed"
}

# Demo analysis
run_demo() {
    log_info "Running Code Analyzer demo..."
    
    source venv/bin/activate
    
    # Ensure service is running
    if ! pgrep -f "jac serve" > /dev/null; then
        log_warning "Service not running, starting it..."
        start_service
        sleep 10
    fi
    
    # Create demo repository
    demo_repo="/tmp/code_analyzer_demo"
    mkdir -p "$demo_repo"
    
    # Create sample Python file
    cat > "$demo_repo/demo.py" << 'EOF'
"""
Demo module for testing code analysis.
"""

import os
import sys
from typing import List, Optional

class DataProcessor:
    """Process data with various transformations."""
    
    def __init__(self, config: dict):
        """Initialize with configuration."""
        self.config = config
        self.processed_count = 0
    
    def load_data(self, file_path: str) -> List[dict]:
        """Load data from file."""
        try:
            with open(file_path, 'r') as f:
                data = eval(f.read())  # Simplified for demo
            return data
        except Exception as e:
            print(f"Error loading data: {e}")
            return []
    
    def transform_data(self, data: List[dict]) -> List[dict]:
        """Transform data according to config."""
        transformed = []
        for item in data:
            if 'name' in item:
                item['name'] = item['name'].upper()
            transformed.append(item)
        return transformed
    
    def save_data(self, data: List[dict], output_path: str) -> bool:
        """Save processed data."""
        try:
            with open(output_path, 'w') as f:
                f.write(str(data))
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False

def process_file(input_path: str, output_path: str):
    """Process a single file."""
    processor = DataProcessor({"transform": True})
    data = processor.load_data(input_path)
    if data:
        transformed = processor.transform_data(data)
        processor.save_data(transformed, output_path)

if __name__ == "__main__":
    process_file("input.txt", "output.txt")
EOF
    
    # Run analysis
    log_info "Analyzing demo repository..."
    
    response=$(curl -s -X POST http://localhost:8081/api/analyze-repository \
        -H "Content-Type: application/json" \
        -d "{\"repository_path\": \"$demo_repo\", \"analysis_depth\": \"full\"}")
    
    if echo "$response" | grep -q '"status": "success"'; then
        log_success "Demo analysis completed successfully!"
        echo "📊 Results:"
        echo "$response" | python3 -m json.tool | head -20
    else
        log_error "Demo analysis failed"
        echo "$response"
    fi
    
    # Clean up
    rm -rf "$demo_repo"
}

# Main script logic
main() {
    case "${1:-help}" in
        "setup")
            log_info "Setting up Code Analyzer with Tree-sitter parsers..."
            check_system_prerequisites
            setup_python_environment
            install_jac_runtime
            create_directories
            install_tree_sitter_grammars
            build_parsers
            validate_parsers
            log_success "Setup completed! Run '$0 start' to start the service"
            ;;
        "setup-basic")
            log_info "Setting up Code Analyzer (basic)..."
            check_system_prerequisites
            setup_python_environment
            install_jac_runtime
            create_directories
            validate_parsers
            log_success "Basic setup completed!"
            ;;
        "install-grammars")
            install_tree_sitter_grammars
            ;;
        "build-parsers")
            build_parsers
            ;;
        "validate")
            validate_parsers
            ;;
        "start")
            start_service
            ;;
        "stop")
            stop_service
            ;;
        "restart")
            stop_service
            sleep 2
            start_service
            ;;
        "status")
            show_status
            ;;
        "test")
            run_analysis_tests
            ;;
        "benchmark")
            run_benchmarks
            ;;
        "logs")
            tail -f logs/service.log
            ;;
        "cleanup")
            cleanup
            ;;
        "demo")
            run_demo
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Handle signals
trap cleanup EXIT

# Run main function
main "$@"
