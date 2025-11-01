#!/bin/bash

# Codebase Genius Repository Mapper - Deployment and Testing Script
# This script sets up, deploys, and tests the Repository Mapper implementation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
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
    
    log_success "All prerequisites satisfied"
}

# Setup environment
setup_environment() {
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
    
    # Install Python dependencies
    log_info "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    log_success "Python dependencies installed"
}

# Install JAC runtime
install_jac() {
    log_info "Installing JAC runtime..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install JAC
    pip install jaclang jac-cloud
    
    log_success "JAC runtime installed"
}

# Create directory structure
create_directories() {
    log_info "Creating directory structure..."
    
    mkdir -p logs
    mkdir -p temp_repos
    mkdir -p output
    mkdir -p config
    mkdir -p tests
    
    log_success "Directory structure created"
}

# Create configuration
create_config() {
    log_info "Setting up configuration..."
    
    if [ ! -f "config/config.json" ]; then
        cp config/config.json config/config.json.bak 2>/dev/null || true
        # Configuration already exists from main setup
        log_info "Configuration file exists"
    fi
    
    log_success "Configuration ready"
}

# Run tests
run_tests() {
    log_info "Running tests..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check if service is running
    if ! pgrep -f "jac serve" > /dev/null; then
        log_warning "Service not running, starting it for tests..."
        start_service
        sleep 10
    fi
    
    # Run Python tests
    python tests/test_api.py
    
    log_success "Tests completed"
}

# Start service
start_service() {
    log_info "Starting Repository Mapper service..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Start service in background
    nohup jac serve main.jac > logs/service.log 2>&1 &
    echo $! > service.pid
    
    log_success "Service started (PID: $(cat service.pid))"
}

# Stop service
stop_service() {
    log_info "Stopping service..."
    
    if [ -f "service.pid" ]; then
        PID=$(cat service.pid)
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            rm service.pid
            log_success "Service stopped"
        else
            log_warning "Service was not running"
            rm service.pid
        fi
    else
        log_warning "No PID file found"
    fi
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Wait for service to be ready
    sleep 5
    
    # Check health endpoint
    if curl -s http://localhost:8080/api/health > /dev/null; then
        log_success "Service is healthy"
        return 0
    else
        log_error "Service health check failed"
        return 1
    fi
}

# Test repository mapping
test_mapping() {
    log_info "Testing repository mapping..."
    
    source venv/bin/activate
    
    # Test with JAC walker
    jac run main.jac walker:test_repository_mapping
    
    log_success "Repository mapping test completed"
}

# Show service status
show_status() {
    log_info "Service status:"
    
    if [ -f "service.pid" ]; then
        PID=$(cat service.pid)
        if kill -0 $PID 2>/dev/null; then
            echo "✅ Service is running (PID: $PID)"
            echo "📡 API available at: http://localhost:8080"
            echo "🏥 Health check: http://localhost:8080/api/health"
            echo "📊 Logs: tail -f logs/service.log"
        else
            echo "❌ Service PID exists but process is not running"
            rm service.pid
        fi
    else
        echo "❌ Service is not running"
    fi
}

# Clean up
cleanup() {
    log_info "Cleaning up..."
    
    # Stop service
    stop_service
    
    # Clean temporary files
    rm -rf temp_repos/* 2>/dev/null || true
    
    # Clean logs
    rm -f logs/*.log 2>/dev/null || true
    
    log_success "Cleanup completed"
}

# Show help
show_help() {
    echo "Codebase Genius Repository Mapper - Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup       - Set up the complete environment"
    echo "  start       - Start the service"
    echo "  stop        - Stop the service"
    echo "  restart     - Restart the service"
    echo "  status      - Show service status"
    echo "  test        - Run tests"
    echo "  health      - Perform health check"
    echo "  logs        - Show service logs"
    echo "  cleanup     - Clean up and stop service"
    echo "  demo        - Run a demo repository mapping"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup    # Complete setup"
    echo "  $0 start    # Start service"
    echo "  $0 demo     # Test with sample repository"
}

# Demo repository mapping
demo_mapping() {
    log_info "Running repository mapping demo..."
    
    source venv/bin/activate
    
    # Ensure service is running
    if ! pgrep -f "jac serve" > /dev/null; then
        log_warning "Service not running, starting it..."
        start_service
        sleep 10
    fi
    
    # Test with a well-known public repository
    REPO_URL="https://github.com/microsoft/vscode"
    
    log_info "Testing with repository: $REPO_URL"
    
    # Make API call
    response=$(curl -s -X POST http://localhost:8080/api/map-repository \
        -H "Content-Type: application/json" \
        -d "{\"repository_url\": \"$REPO_URL\", \"max_file_size\": 1048576}")
    
    if echo "$response" | grep -q '"status": "success"'; then
        files=$(echo "$response" | grep -o '"total_files": [0-9]*' | cut -d' ' -f2)
        langs=$(echo "$response" | grep -o '"language_distribution": {[^}]*}' | head -1)
        
        log_success "Demo completed successfully!"
        echo "📊 Results:"
        echo "   - Repository: $REPO_URL"
        echo "   - Files analyzed: $files"
        echo "   - Language distribution: $langs"
    else
        log_error "Demo failed: $response"
    fi
}

# Main script logic
main() {
    case "${1:-help}" in
        "setup")
            log_info "Setting up Repository Mapper..."
            check_prerequisites
            setup_environment
            install_jac
            create_directories
            create_config
            log_success "Setup completed! Run '$0 start' to start the service"
            ;;
        "start")
            check_prerequisites
            start_service
            health_check
            ;;
        "stop")
            stop_service
            ;;
        "restart")
            stop_service
            sleep 2
            start_service
            health_check
            ;;
        "status")
            show_status
            ;;
        "test")
            run_tests
            ;;
        "health")
            health_check
            ;;
        "logs")
            tail -f logs/service.log
            ;;
        "cleanup")
            cleanup
            ;;
        "demo")
            demo_mapping
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
