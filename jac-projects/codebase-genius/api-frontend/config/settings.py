"""
Configuration settings for Codebase Genius API and Frontend
"""

import os;
from typing import Dict, List, Optional;

# API Configuration
class APIConfig:
    """API server configuration"""
    HOST = os.getenv("API_HOST", "0.0.0.0");
    PORT = int(os.getenv("API_PORT", "8000"));
    DEBUG = os.getenv("DEBUG", "False").lower() == "true";
    WORKERS = int(os.getenv("WORKERS", "1"));
    
    # CORS settings
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8501",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8501",
        "*"  # Allow all for development
    ];
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"));
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"));  # seconds
    
    # Workflow settings
    MAX_WORKFLOW_DURATION = int(os.getenv("MAX_WORKFLOW_DURATION", "1800"));  # 30 minutes
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "104857600"));  # 100MB
    MAX_CONCURRENT_WORKFLOWS = int(os.getenv("MAX_CONCURRENT_WORKFLOWS", "5"));

# Repository Configuration
class RepositoryConfig:
    """Repository processing configuration"""
    
    # Supported platforms
    SUPPORTED_PLATFORMS = [
        "github.com",
        "gitlab.com", 
        "bitbucket.org",
        "source.developers.google.com"
    ];
    
    # Supported repository types
    SUPPORTED_REPOSITORIES = [
        "github",
        "gitlab", 
        "bitbucket"
    ];
    
    # Clone settings
    CLONE_DEPTH = int(os.getenv("GIT_CLONE_DEPTH", "1"));
    CLONE_TIMEOUT = int(os.getenv("GIT_CLONE_TIMEOUT", "300"));  # 5 minutes
    
    # File processing limits
    MAX_FILES_PER_REPOSITORY = int(os.getenv("MAX_FILES_PER_REPOSITORY", "10000"));
    MAX_FILE_SIZE_BYTES = int(os.getenv("MAX_FILE_SIZE_BYTES", "10485760"));  # 10MB
    SUPPORTED_FILE_EXTENSIONS = [
        ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".h", 
        ".go", ".rs", ".php", ".rb", ".scala", ".kt", ".swift", ".cs",
        ".html", ".css", ".scss", ".sass", ".less", ".vue", ".svelte",
        ".md", ".rst", ".txt", ".json", ".yaml", ".yml", ".xml", ".toml",
        ".sql", ".sh", ".bash", ".zsh", ".fish", ".bat", ".ps1"
    ];
    
    # Binary file extensions to skip
    BINARY_EXTENSIONS = [
        ".exe", ".dll", ".so", ".dylib", ".bin", ".img", ".iso",
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".ico",
        ".mp3", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm"
    ];

# Analysis Configuration  
class AnalysisConfig:
    """Code analysis configuration"""
    
    # Analysis depth levels
    ANALYSIS_LEVELS = {
        "basic": {
            "description": "Basic repository structure and key files",
            "max_files": 100,
            "include_relationships": False,
            "generate_diagrams": False
        },
        "full": {
            "description": "Complete codebase analysis with relationships",
            "max_files": 1000,
            "include_relationships": True,
            "generate_diagrams": True
        },
        "comprehensive": {
            "description": "Deep analysis including edge cases and metrics",
            "max_files": 5000,
            "include_relationships": True,
            "generate_diagrams": True,
            "calculate_metrics": True,
            "analyze_dependencies": True
        }
    };
    
    # Code parsing settings
    TREE_SITTER_LANGUAGES = [
        "python", "javascript", "typescript", "java", "cpp", "c",
        "go", "rust", "php", "ruby", "scala", "kotlin", "swift",
        "csharp", "bash", "json", "yaml"
    ];
    
    # Quality assessment weights
    QUALITY_WEIGHTS = {
        "structure": 0.25,
        "completeness": 0.30,
        "citations": 0.20,
        "readability": 0.15,
        "accuracy": 0.10
    };

# Documentation Configuration
class DocumentationConfig:
    """Documentation generation configuration"""
    
    # Supported output formats
    OUTPUT_FORMATS = ["markdown", "html", "pdf"];
    
    # Template settings
    USE_TEMPLATES = True;
    CUSTOM_TEMPLATES_DIR = os.getenv("CUSTOM_TEMPLATES_DIR", "./templates");
    
    # Diagram settings
    DIAGRAM_FORMATS = ["svg", "png", "pdf"];
    DIAGRAM_ENGINE = "graphviz";  # Options: graphviz, mermaid, plantuml
    
    # Citation settings
    ENABLE_CITATIONS = True;
    CITATION_STYLE = "numbered";  # Options: numbered, apa, mla
    
    # Markdown options
    MARKDOWN_EXTENSIONS = [
        "markdown.extensions.tables",
        "markdown.extensions.fenced_code", 
        "markdown.extensions.toc",
        "markdown.extensions.codehilite",
        "markdown.extensions.attr_list"
    ];

# Frontend Configuration
class FrontendConfig:
    """Frontend configuration"""
    
    # Streamlit settings
    STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_PORT", "8501"));
    STREAMLIT_SERVER_HOST = os.getenv("STREAMLIT_HOST", "0.0.0.0");
    STREAMLIT_DEBUG = os.getenv("STREAMLIT_DEBUG", "False").lower() == "true";
    
    # UI settings
    THEME_PRIMARY_COLOR = "#2E86AB";
    THEME_BACKGROUND_COLOR = "#FFFFFF";
    THEME_SECONDARY_BACKGROUND_COLOR = "#F0F2F6";
    THEME_TEXT_COLOR = "#262730";
    
    # Feature flags
    ENABLE_REAL_TIME_UPDATES = True;
    ENABLE_DARK_MODE = True;
    ENABLE_WORKFLOW_HISTORY = True;
    ENABLE_BULK_OPERATIONS = False;  # For future enhancement
    
    # Pagination
    DEFAULT_PAGE_SIZE = 50;
    MAX_PAGE_SIZE = 500;

# Database Configuration (if using persistent storage)
class DatabaseConfig:
    """Database configuration for persistent storage"""
    
    # SQLite (for development)
    SQLITE_PATH = os.getenv("SQLITE_PATH", "./codebase_genius.db");
    
    # PostgreSQL (for production)
    POSTGRES_URL = os.getenv("DATABASE_URL");
    
    # Redis (for caching and sessions)
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0");
    
    # Workflow retention
    WORKFLOW_RETENTION_DAYS = int(os.getenv("WORKFLOW_RETENTION_DAYS", "7"));
    CLEANUP_INTERVAL_HOURS = int(os.getenv("CLEANUP_INTERVAL_HOURS", "24"));

# Logging Configuration
class LoggingConfig:
    """Logging configuration"""
    
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO");
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s";
    LOG_FILE = os.getenv("LOG_FILE", "./logs/codebase_genius.log");
    LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", "10485760"));  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"));
    
    # Structured logging
    ENABLE_JSON_LOGS = os.getenv("ENABLE_JSON_LOGS", "False").lower() == "true";
    
    # Log rotation
    ENABLE_LOG_ROTATION = True;

# Security Configuration
class SecurityConfig:
    """Security settings"""
    
    # API Key management
    REQUIRE_API_KEY = os.getenv("REQUIRE_API_KEY", "False").lower() == "true";
    API_KEY_HEADER = "X-API-Key";
    
    # Authentication
    ENABLE_AUTH = os.getenv("ENABLE_AUTH", "False").lower() == "true";
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key");
    JWT_ALGORITHM = "HS256";
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"));
    
    # CORS
    CORS_ALLOW_CREDENTIALS = True;
    CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"];
    CORS_ALLOW_HEADERS = ["*"];
    
    # Rate limiting
    ENABLE_RATE_LIMITING = True;
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"));

# Monitoring Configuration
class MonitoringConfig:
    """Monitoring and metrics configuration"""
    
    # Health check endpoints
    ENABLE_HEALTH_CHECKS = True;
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"));
    
    # Metrics collection
    ENABLE_METRICS = True;
    METRICS_PORT = int(os.getenv("METRICS_PORT", "9090"));
    
    # Performance monitoring
    MONITOR_MEMORY_USAGE = True;
    MONITOR_CPU_USAGE = True;
    MONITOR_DISK_USAGE = True;
    MONITOR_NETWORK_USAGE = True;
    
    # Alert thresholds
    MEMORY_THRESHOLD = int(os.getenv("MEMORY_THRESHOLD", "80"));  # percentage
    CPU_THRESHOLD = int(os.getenv("CPU_THRESHOLD", "80"));  # percentage
    DISK_THRESHOLD = int(os.getenv("DISK_THRESHOLD", "85"));  # percentage

# Deployment Configuration
class DeploymentConfig:
    """Deployment-related settings"""
    
    # Docker settings
    DOCKER_IMAGE_NAME = "codebase-genius";
    DOCKER_IMAGE_TAG = "latest";
    DOCKER_CONTAINER_NAME = "codebase-genius-app";
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development");  # development, staging, production
    
    # Scaling
    MIN_WORKERS = int(os.getenv("MIN_WORKERS", "1"));
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "10"));
    WORKER_TIMEOUT = int(os.getenv("WORKER_TIMEOUT", "300"));
    
    # Resource limits
    MEMORY_LIMIT = os.getenv("MEMORY_LIMIT", "2Gi");
    CPU_LIMIT = os.getenv("CPU_LIMIT", "1000m");

# Export all configurations
__all__ = [
    "APIConfig",
    "RepositoryConfig", 
    "AnalysisConfig",
    "DocumentationConfig",
    "FrontendConfig",
    "DatabaseConfig",
    "LoggingConfig",
    "SecurityConfig",
    "MonitoringConfig",
    "DeploymentConfig"
];

# Helper function to get all configurations as dictionary
def get_all_configs() -> Dict[str, Dict]:
    """Get all configuration classes as a dictionary"""
    configs = {};
    
    for config_name in __all__:
        config_class = globals()[config_name];
        config_dict = {};
        
        # Get all uppercase attributes (configuration constants)
        for attr_name in dir(config_class):
            if attr_name.isupper() and not attr_name.startswith('_'):
                config_dict[attr_name] = getattr(config_class, attr_name);
                
        configs[config_name] = config_dict;
        
    return configs;

# Validation function
def validate_config() -> List[str]:
    """Validate configuration settings"""
    errors = [];
    
    # Check required environment variables for production
    if os.getenv("ENVIRONMENT") == "production":
        if not os.getenv("DATABASE_URL"):
            errors.append("DATABASE_URL is required in production");
        if not os.getenv("JWT_SECRET_KEY"):
            errors.append("JWT_SECRET_KEY is required in production");
            
    # Check port ranges
    if not (1 <= APIConfig.PORT <= 65535):
        errors.append(f"Invalid API port: {APIConfig.PORT}");
        
    if not (1 <= FrontendConfig.STREAMLIT_SERVER_PORT <= 65535):
        errors.append(f"Invalid Streamlit port: {FrontendConfig.STREAMLIT_SERVER_PORT}");
        
    # Check file limits
    if RepositoryConfig.MAX_FILES_PER_REPOSITORY <= 0:
        errors.append("MAX_FILES_PER_REPOSITORY must be positive");
        
    if RepositoryConfig.MAX_FILE_SIZE_BYTES <= 0:
        errors.append("MAX_FILE_SIZE_BYTES must be positive");
        
    return errors;

# Development helper
def print_config_summary():
    """Print configuration summary for debugging"""
    print("🔧 Codebase Genius Configuration Summary");
    print("=" * 50);
    
    configs = get_all_configs();
    
    for config_name, config_values in configs.items():
        print(f"\n📋 {config_name}:");
        for key, value in config_values.items():
            if isinstance(value, (str, int, float, bool)):
                print(f"  {key}: {value}");
            elif isinstance(value, list) and len(value) <= 5:
                print(f"  {key}: {value}");
            elif isinstance(value, dict) and len(value) <= 5:
                print(f"  {key}: {len(value)} items");
            else:
                print(f"  {key}: <{type(value).__name__} with {len(value) if hasattr(value, '__len__') else 'N/A'} items>");

if __name__ == "__main__":
    print_config_summary();
    
    # Validate configuration
    errors = validate_config();
    if errors:
        print("\n❌ Configuration Errors:");
        for error in errors:
            print(f"  - {error}");
    else:
        print("\n✅ Configuration is valid");
