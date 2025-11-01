#!/bin/bash
# DocGenie Agent Deployment and Management Script
# Phase 5: Documentation Generation Service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="docgenie-agent"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${PROJECT_ROOT}/config/config.json"
LOG_DIR="${PROJECT_ROOT}/logs"
PID_FILE="${PROJECT_ROOT}/docgenie-agent.pid"
DEMO_DATA_DIR="${PROJECT_ROOT}/tests/demo_data"
OUTPUT_DIR="${PROJECT_ROOT}/outputs"

# Functions
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

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is not installed"
        exit 1
    fi
    
    # Check JAC runtime
    if ! python3 -c "import jac_lang" &> /dev/null; then
        log_warning "JAC runtime not found, attempting to install..."
        pip3 install jac-lang>=0.9.0
    fi
    
    # Check Docker (optional)
    if command -v docker &> /dev/null; then
        log_success "Docker is available"
    else
        log_warning "Docker not found (optional for container deployment)"
    fi
    
    log_success "Dependencies check completed"
}

setup_environment() {
    log_info "Setting up environment..."
    
    # Create directories
    mkdir -p "$LOG_DIR" "$OUTPUT_DIR" "$DEMO_DATA_DIR"
    
    # Set permissions
    chmod 755 "$PROJECT_ROOT"
    chmod 644 "$CONFIG_FILE"
    
    # Set environment variables
    export DOCGENIE_CONFIG_PATH="$CONFIG_FILE"
    export DOCGENIE_LOG_LEVEL="INFO"
    export DOCGENIE_OUTPUT_DIR="$OUTPUT_DIR"
    
    log_success "Environment setup completed"
}

install_dependencies() {
    log_info "Installing dependencies..."
    
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        pip3 install -r "$PROJECT_ROOT/requirements.txt"
        log_success "Dependencies installed from requirements.txt"
    else
        log_warning "requirements.txt not found, installing basic dependencies..."
        pip3 install jac-lang jinja2 graphviz requests fastapi uvicorn
    fi
}

run_setup() {
    log_info "Running setup script..."
    
    if [ -f "$PROJECT_ROOT/setup.py" ]; then
        python3 "$PROJECT_ROOT/setup.py"
        log_success "Setup completed"
    else
        log_warning "setup.py not found, running basic setup"
        install_dependencies
        setup_environment
    fi
}

start_service() {
    log_info "Starting DocGenie Agent service..."
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log_warning "Service is already running (PID: $pid)"
            return 1
        else
            rm "$PID_FILE"
        fi
    fi
    
    # Start the service
    cd "$PROJECT_ROOT"
    nohup python3 -m jac_lang run main.jac > "$LOG_DIR/service.log" 2>&1 &
    local pid=$!
    
    echo "$pid" > "$PID_FILE"
    
    # Wait a moment for startup
    sleep 2
    
    if kill -0 "$pid" 2>/dev/null; then
        log_success "Service started successfully (PID: $pid)"
        echo "📋 Service Management:"
        echo "   - View logs: tail -f $LOG_DIR/service.log"
        echo "   - Stop service: ./deploy.sh stop"
        echo "   - Check status: ./deploy.sh status"
        return 0
    else
        log_error "Service failed to start"
        rm -f "$PID_FILE"
        return 1
    fi
}

stop_service() {
    log_info "Stopping DocGenie Agent service..."
    
    if [ ! -f "$PID_FILE" ]; then
        log_warning "Service is not running (no PID file found)"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    
    if kill -0 "$pid" 2>/dev/null; then
        kill "$pid"
        sleep 2
        
        # Force kill if still running
        if kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid"
        fi
        
        rm "$PID_FILE"
        log_success "Service stopped successfully"
    else
        log_warning "Service was not running"
        rm "$PID_FILE"
    fi
}

restart_service() {
    log_info "Restarting DocGenie Agent service..."
    stop_service
    sleep 2
    start_service
}

show_status() {
    log_info "Checking DocGenie Agent status..."
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log_success "Service is running (PID: $pid)"
            
            # Show memory usage
            if command -v ps &> /dev/null; then
                local mem_usage=$(ps -o pid,ppid,pcpu,pmem,cmd -p "$pid" 2>/dev/null || echo "N/A")
                echo "📊 Process Info:"
                echo "$mem_usage"
            fi
            
            # Show log tail
            if [ -f "$LOG_DIR/service.log" ]; then
                echo "📄 Recent logs:"
                tail -5 "$LOG_DIR/service.log"
            fi
        else
            log_error "Service is not running (stale PID file)"
            rm "$PID_FILE"
        fi
    else
        log_info "Service is not running"
    fi
}

show_logs() {
    local lines=${1:-50}
    log_info "Showing last $lines lines of logs..."
    
    if [ -f "$LOG_DIR/service.log" ]; then
        tail -n "$lines" "$LOG_DIR/service.log"
    else
        log_warning "Log file not found: $LOG_DIR/service.log"
    fi
}

run_tests() {
    log_info "Running tests..."
    
    if [ -d "$PROJECT_ROOT/tests" ]; then
        cd "$PROJECT_ROOT"
        python3 -m pytest tests/ -v --tb=short
        log_success "Tests completed"
    else
        log_warning "Tests directory not found"
    fi
}

run_benchmark() {
    log_info "Running performance benchmark..."
    
    local test_data="$DEMO_DATA_DIR/sample_ccg.json"
    
    if [ ! -f "$test_data" ]; then
        log_info "Creating sample CCG data for benchmark..."
        mkdir -p "$DEMO_DATA_DIR"
        cat > "$test_data" << 'EOF'
{
  "entities": [
    {
      "id": "entity_1",
      "name": "TestClass",
      "type": "class",
      "file_path": "test.py",
      "start_line": 1,
      "end_line": 50,
      "complexity": 8.5,
      "dependencies": ["entity_2"],
      "dependents": [],
      "documentation": "A test class for documentation generation",
      "source_code": "class TestClass:\n    def __init__(self):\n        pass"
    },
    {
      "id": "entity_2", 
      "name": "test_function",
      "type": "function",
      "file_path": "test.py",
      "start_line": 55,
      "end_line": 70,
      "complexity": 3.2,
      "dependencies": [],
      "dependents": ["entity_1"],
      "documentation": "A test function",
      "source_code": "def test_function():\n    return 'hello'"
    }
  ],
  "relationships": [
    {
      "from": "entity_1",
      "to": "entity_2",
      "type": "calls",
      "confidence": 0.95,
      "context": "TestClass calls test_function in method_x"
    }
  ],
  "metadata": {
    "repository_name": "test-repo",
    "repository_url": "https://github.com/test/repo",
    "total_files": 10,
    "generation_date": "2025-10-31T07:19:41"
  }
}
EOF
    fi
    
    # Run benchmark
    cd "$PROJECT_ROOT"
    time python3 main.jac --benchmark --input "$test_data" --output "$OUTPUT_DIR/benchmark"
    
    log_success "Benchmark completed"
}

generate_demo() {
    log_info "Generating demo documentation..."
    
    local demo_input="$DEMO_DATA_DIR/demo_ccg.json"
    
    # Create comprehensive demo data
    cat > "$demo_input" << 'EOF'
{
  "entities": [
    {
      "id": "calc_1",
      "name": "Calculator",
      "type": "class",
      "file_path": "calculator.py",
      "start_line": 1,
      "end_line": 100,
      "complexity": 12.5,
      "dependencies": [],
      "dependents": [],
      "documentation": "A simple calculator class with basic arithmetic operations",
      "source_code": "class Calculator:\n    def add(self, a, b):\n        return a + b\n    \n    def subtract(self, a, b):\n        return a - b"
    },
    {
      "id": "math_1",
      "name": "math_utils",
      "type": "function", 
      "file_path": "math_utils.py",
      "start_line": 10,
      "end_line": 50,
      "complexity": 5.8,
      "dependencies": [],
      "dependents": ["calc_1"],
      "documentation": "Mathematical utility functions",
      "source_code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)"
    },
    {
      "id": "main_1",
      "name": "main",
      "type": "function",
      "file_path": "main.py", 
      "start_line": 1,
      "end_line": 20,
      "complexity": 2.1,
      "dependencies": ["calc_1", "math_1"],
      "dependents": [],
      "documentation": "Main entry point for the application",
      "source_code": "def main():\n    calc = Calculator()\n    result = calc.add(5, 3)\n    print(result)"
    }
  ],
  "relationships": [
    {
      "from": "main_1",
      "to": "calc_1", 
      "type": "instantiates",
      "confidence": 1.0,
      "context": "main function creates Calculator instance"
    },
    {
      "from": "main_1",
      "to": "math_1",
      "type": "calls",
      "confidence": 0.9,
      "context": "main function calls math_utils functions"
    }
  ],
  "metadata": {
    "repository_name": "demo-calculator",
    "repository_url": "https://github.com/example/demo-calculator",
    "total_files": 3,
    "generation_date": "2025-10-31T07:19:41",
    "description": "Demo project for DocGenie Agent documentation"
  }
}
EOF
    
    # Generate documentation
    cd "$PROJECT_ROOT"
    export DOCGENIE_DEMO_MODE=true
    python3 main.jac --demo --input "$demo_input" --output "$OUTPUT_DIR/demo"
    
    log_success "Demo documentation generated in $OUTPUT_DIR/demo/"
    echo "📁 Generated files:"
    ls -la "$OUTPUT_DIR/demo/" 2>/dev/null || echo "   No files generated"
}

show_config() {
    log_info "Current configuration:"
    
    if [ -f "$CONFIG_FILE" ]; then
        cat "$CONFIG_FILE"
    else
        log_warning "Configuration file not found: $CONFIG_FILE"
    fi
}

show_help() {
    echo "DocGenie Agent Deployment Script"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  start         Start the DocGenie Agent service"
    echo "  stop          Stop the DocGenie Agent service"  
    echo "  restart       Restart the DocGenie Agent service"
    echo "  status        Show service status and logs"
    echo "  logs [lines]  Show service logs (default: 50 lines)"
    echo "  test          Run tests"
    echo "  benchmark     Run performance benchmark"
    echo "  demo          Generate demo documentation"
    echo "  setup         Run full setup and installation"
    echo "  config        Show current configuration"
    echo "  help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start the service"
    echo "  $0 logs 100                 # Show last 100 log lines"
    echo "  $0 demo                     # Generate demo documentation"
    echo "  $0 setup                    # Run full setup"
}

# Main command handling
case "${1:-help}" in
    "start")
        check_dependencies
        setup_environment
        start_service
        ;;
    "stop")
        stop_service
        ;;
    "restart")
        check_dependencies
        setup_environment
        restart_service
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs "${2:-50}"
        ;;
    "test")
        run_tests
        ;;
    "benchmark")
        check_dependencies
        run_benchmark
        ;;
    "demo")
        check_dependencies
        setup_environment
        generate_demo
        ;;
    "setup")
        check_dependencies
        run_setup
        ;;
    "config")
        show_config
        ;;
    "help"|*)
        show_help
        ;;
esac
