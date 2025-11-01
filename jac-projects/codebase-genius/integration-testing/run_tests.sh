#!/bin/bash
# Codebase Genius - Integration Testing Runner
# Phase 7: Complete integration testing automation script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
INTEGRATION_DIR="$WORKSPACE_DIR/integration-testing"
RESULTS_DIR="$INTEGRATION_DIR/results"

# Helper functions
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

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check pip
    if ! command -v pip &> /dev/null; then
        log_error "pip is required but not installed"
        exit 1
    fi
    
    # Check if JAC is installed
    if ! command -v jac &> /dev/null; then
        log_error "JAC language is required but not installed"
        log_info "Please install JAC: https://github.com/jaseem/jaic"
        exit 1
    fi
    
    log_success "All dependencies found"
}

# Install Python dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    cd "$WORKSPACE_DIR"
    
    # Install dependencies for all agents
    if [ -f "code/repository-mapper-agent/requirements.txt" ]; then
        log_info "Installing Repository Mapper dependencies..."
        pip install -r code/repository-mapper-agent/requirements.txt
    fi
    
    if [ -f "code/code-analyzer-agent/requirements.txt" ]; then
        log_info "Installing Code Analyzer dependencies..."
        pip install -r code/code-analyzer-agent/requirements.txt
    fi
    
    if [ -f "code/docgenie-agent/requirements.txt" ]; then
        log_info "Installing DocGenie dependencies..."
        pip install -r code/docgenie-agent/requirements.txt
    fi
    
    if [ -f "code/supervisor-agent/requirements.txt" ]; then
        log_info "Installing Supervisor dependencies..."
        pip install -r code/supervisor-agent/requirements.txt
    fi
    
    # Install integration testing dependencies
    log_info "Installing integration testing dependencies..."
    pip install requests psutil markdown beautifulsoup4 flask flask-cors
    
    log_success "All dependencies installed"
}

# Generate sample repositories
generate_repositories() {
    log_info "Generating sample test repositories..."
    
    cd "$INTEGRATION_DIR"
    python3 samples/repository_generator.py
    
    log_success "Sample repositories generated"
}

# Run quick test suite
run_quick_tests() {
    log_info "Running quick integration test suite..."
    
    cd "$INTEGRATION_DIR"
    python3 run_all_tests.py --quick
    
    log_success "Quick tests completed"
}

# Run complete test suite
run_complete_tests() {
    log_info "Running complete integration test suite..."
    
    cd "$INTEGRATION_DIR"
    python3 run_all_tests.py
    
    log_success "Complete tests completed"
}

# Run specific test type
run_specific_test() {
    local test_type=$1
    
    cd "$INTEGRATION_DIR"
    
    case $test_type in
        "integration")
            log_info "Running integration tests only..."
            python3 run_all_tests.py --integration-only
            ;;
        "performance")
            log_info "Running performance tests only..."
            python3 run_all_tests.py --performance-only
            ;;
        "error")
            log_info "Running error scenario tests only..."
            python3 run_all_tests.py --error-only
            ;;
        "load")
            log_info "Running load tests only..."
            python3 run_all_tests.py --load-only
            ;;
        *)
            log_error "Unknown test type: $test_type"
            exit 1
            ;;
    esac
    
    log_success "$test_type tests completed"
}

# View results
view_results() {
    log_info "Viewing test results..."
    
    if [ ! -d "$RESULTS_DIR" ]; then
        log_warning "No results directory found. Run tests first."
        exit 1
    fi
    
    echo ""
    echo "Available test results:"
    ls -la "$RESULTS_DIR"/*.md 2>/dev/null || echo "No markdown reports found"
    echo ""
    
    # Show latest summary if available
    latest_summary=$(ls -t "$RESULTS_DIR"/test_suite_summary_*.md 2>/dev/null | head -1)
    if [ -n "$latest_summary" ]; then
        echo "Latest summary report:"
        echo "====================="
        head -50 "$latest_summary"
        echo ""
        log_info "Full report available at: $latest_summary"
    else
        log_warning "No summary reports found"
    fi
}

# Cleanup
cleanup() {
    log_info "Cleaning up..."
    
    # Kill any running JAC processes
    pkill -f "jac serve" 2>/dev/null || true
    
    log_success "Cleanup completed"
}

# Help function
show_help() {
    echo "Codebase Genius Integration Test Suite"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  setup              Full setup (dependencies + repositories)"
    echo "  quick              Run quick test suite"
    echo "  complete           Run complete test suite"
    echo "  integration        Run integration tests only"
    echo "  performance        Run performance tests only"
    echo "  error              Run error scenario tests only"
    echo "  load               Run load tests only"
    echo "  results            View test results"
    echo "  cleanup            Stop agents and cleanup"
    echo "  help               Show this help"
    echo ""
    echo "Options:"
    echo "  --skip-deps        Skip dependency installation"
    echo "  --skip-repos       Skip repository generation"
    echo ""
    echo "Examples:"
    echo "  $0 setup          # Full setup"
    echo "  $0 quick          # Quick test"
    echo "  $0 complete       # Full test suite"
    echo "  $0 results        # View results"
}

# Main script logic
main() {
    local command=${1:-help}
    shift || true
    
    local skip_deps=false
    local skip_repos=false
    
    # Parse options
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-deps)
                skip_deps=true
                shift
                ;;
            --skip-repos)
                skip_repos=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Execute command
    case $command in
        "setup")
            check_dependencies
            if [ "$skip_deps" = false ]; then
                install_dependencies
            fi
            if [ "$skip_repos" = false ]; then
                generate_repositories
            fi
            log_success "Setup completed successfully!"
            ;;
        "quick")
            check_dependencies
            run_quick_tests
            ;;
        "complete")
            check_dependencies
            if [ "$skip_deps" = false ]; then
                install_dependencies
            fi
            if [ "$skip_repos" = false ]; then
                generate_repositories
            fi
            run_complete_tests
            ;;
        "integration")
            check_dependencies
            run_specific_test "integration"
            ;;
        "performance")
            check_dependencies
            run_specific_test "performance"
            ;;
        "error")
            check_dependencies
            run_specific_test "error"
            ;;
        "load")
            check_dependencies
            run_specific_test "load"
            ;;
        "results")
            view_results
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Trap cleanup on script exit
trap cleanup EXIT

# Run main function
main "$@"
