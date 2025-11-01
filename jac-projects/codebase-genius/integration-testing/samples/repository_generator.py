#!/usr/bin/env python3
"""
Codebase Genius - Sample Test Repositories
Phase 7: Test data generation and management

Creates various test repositories for different testing scenarios:
- Simple Python repositories
- Complex multi-module projects
- JAC language examples
- Edge case repositories
- Performance test datasets

Author: Cavin Otieno
Date: 2025-10-31
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any
import subprocess

class SampleRepositoryGenerator:
    """Generator for sample test repositories"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent / "samples"
        self.base_dir.mkdir(exist_ok=True)
        
        # Repository configurations
        self.sample_repos = {
            "simple_python": {
                "name": "simple-python",
                "description": "Simple Python module with basic functions",
                "language": "python",
                "files": {
                    "README.md": """# Simple Python Module

A basic Python module for testing documentation generation.

## Installation

```bash
pip install simple-python
```

## Usage

```python
import simple_python
result = simple_python.greet("World")
print(result)  # "Hello, World!"
```

## Functions

- `greet(name)`: Returns a greeting message
- `add(a, b)`: Adds two numbers
- `multiply(a, b)`: Multiplies two numbers
""",
                    "simple_python.py": '''"""Simple Python module for testing."""

def greet(name):
    """Return a greeting message for the given name.
    
    Args:
        name (str): The name to greet
        
    Returns:
        str: Greeting message
        
    Example:
        >>> greet("Alice")
        "Hello, Alice!"
    """
    return f"Hello, {name}!"


def add(a, b):
    """Add two numbers together.
    
    Args:
        a (int or float): First number
        b (int or float): Second number
        
    Returns:
        int or float: Sum of a and b
        
    Example:
        >>> add(2, 3)
        5
    """
    return a + b


def multiply(a, b):
    """Multiply two numbers.
    
    Args:
        a (int or float): First number
        b (int or float): Second number
        
    Returns:
        int or float: Product of a and b
        
    Example:
        >>> multiply(4, 5)
        20
    """
    return a * b


class Calculator:
    """Simple calculator class for basic arithmetic operations."""
    
    def __init__(self):
        """Initialize the calculator."""
        self.history = []
    
    def calculate(self, operation, a, b):
        """Perform a calculation and store result.
        
        Args:
            operation (str): Type of operation ('add', 'multiply')
            a (int or float): First number
            b (int or float): Second number
            
        Returns:
            int or float: Result of calculation
        """
        if operation == "add":
            result = add(a, b)
        elif operation == "multiply":
            result = multiply(a, b)
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        self.history.append(f"{a} {operation} {b} = {result}")
        return result
    
    def get_history(self):
        """Get calculation history.
        
        Returns:
            list: List of calculation strings
        """
        return self.history.copy()


if __name__ == "__main__":
    # Example usage
    calc = Calculator()
    print(calc.calculate("add", 10, 20))
    print(calc.calculate("multiply", 5, 6))
    print("History:", calc.get_history())
''',
                    "setup.py": '''from setuptools import setup, find_packages

setup(
    name="simple-python",
    version="1.0.0",
    description="Simple Python module for testing",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.6",
    author="Test Author",
    author_email="test@example.com",
    url="https://github.com/example/simple-python",
)
''',
                    "requirements.txt": '''# No dependencies required for this simple module
''',
                    "tests/__init__.py": "",
                    "tests/test_simple_python.py": '''"""Tests for simple_python module."""

import unittest
from simple_python import greet, add, multiply, Calculator


class TestSimplePython(unittest.TestCase):
    """Test cases for simple_python module."""
    
    def test_greet(self):
        """Test the greet function."""
        self.assertEqual(greet("World"), "Hello, World!")
        self.assertEqual(greet("Alice"), "Hello, Alice!")
    
    def test_add(self):
        """Test the add function."""
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(-1, 1), 0)
        self.assertEqual(add(0, 0), 0)
    
    def test_multiply(self):
        """Test the multiply function."""
        self.assertEqual(multiply(2, 3), 6)
        self.assertEqual(multiply(-2, 3), -6)
        self.assertEqual(multiply(0, 100), 0)
    
    def test_calculator(self):
        """Test the Calculator class."""
        calc = Calculator()
        
        result1 = calc.calculate("add", 10, 20)
        self.assertEqual(result1, 30)
        
        result2 = calc.calculate("multiply", 3, 4)
        self.assertEqual(result2, 12)
        
        history = calc.get_history()
        self.assertEqual(len(history), 2)
        self.assertIn("10 add 20 = 30", history)


if __name__ == "__main__":
    unittest.main()
'''
                }
            },
            
            "complex_python": {
                "name": "complex-python",
                "description": "Multi-module Python project with complex structure",
                "language": "python",
                "files": {
                    "README.md": """# Complex Python Project

A complex multi-module Python project for testing advanced documentation features.

## Features

- Data processing modules
- Web API framework
- Database integration
- Configuration management
- Logging and monitoring
- Testing framework

## Architecture

This project uses a modular architecture with the following components:

- `core/`: Core functionality and base classes
- `api/`: REST API endpoints
- `data/`: Data processing and models
- `utils/`: Utility functions and helpers
- `tests/`: Comprehensive test suite
""",
                    "setup.py": '''from setuptools import setup, find_packages

setup(
    name="complex-python",
    version="2.0.0",
    description="Complex Python project for testing",
    packages=find_packages(),
    install_requires=[
        "flask>=2.0.0",
        "sqlalchemy>=1.4.0",
        "pydantic>=1.8.0",
        "python-dotenv>=0.19.0",
    ],
    python_requires=">=3.7",
    author="Test Author",
    author_email="test@example.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
''',
                    "__init__.py": '''"""Complex Python Project."""

__version__ = "2.0.0"
''',
                    "core/__init__.py": '''"""Core functionality module."""''',
                    "core/base.py": '''"""Base classes and core functionality."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging


class BaseService(ABC):
    """Abstract base class for all services."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the service.
        
        Args:
            config: Service configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the service."""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the service."""
        pass


class DataProcessor(BaseService):
    """Base class for data processing services."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the data processor.
        
        Args:
            config: Processor configuration
        """
        super().__init__(config)
        self.processed_count = 0
        self.error_count = 0
    
    def process(self, data: Any) -> Any:
        """Process input data.
        
        Args:
            data: Input data to process
            
        Returns:
            Processed data
            
        Raises:
            ProcessingError: If processing fails
        """
        try:
            result = self._process_data(data)
            self.processed_count += 1
            self.logger.info(f"Processed item {self.processed_count}")
            return result
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Processing failed: {e}")
            raise ProcessingError(f"Data processing failed: {e}") from e
    
    @abstractmethod
    def _process_data(self, data: Any) -> Any:
        """Internal data processing method.
        
        Args:
            data: Input data
            
        Returns:
            Processed data
        """
        pass
    
    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics.
        
        Returns:
            Dictionary with processing statistics
        """
        return {
            "processed": self.processed_count,
            "errors": self.error_count
        }


class ProcessingError(Exception):
    """Exception raised when data processing fails."""
    pass
''',
                    "core/config.py": '''"""Configuration management."""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
import json


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_enabled: bool = False
    
    @property
    def connection_string(self) -> str:
        """Get database connection string."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class APIConfig:
    """API configuration."""
    host: str = "localhost"
    port: int = 8080
    debug: bool = False
    cors_enabled: bool = True
    rate_limit: int = 100
    
    @property
    def base_url(self) -> str:
        """Get API base URL."""
        protocol = "https" if self.port == 443 else "http"
        return f"{protocol}://{self.host}:{self.port}"


class Config:
    """Application configuration manager."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            config_file: Path to configuration file
        """
        self._config: Dict[str, Any] = {}
        self._load_config(config_file)
    
    def _load_config(self, config_file: Optional[str]) -> None:
        """Load configuration from file or environment.
        
        Args:
            config_file: Configuration file path
        """
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self._config = json.load(f)
        else:
            self._config = self._load_from_environment()
    
    def _load_from_environment(self) -> Dict[str, Any]:
        """Load configuration from environment variables.
        
        Returns:
            Configuration dictionary
        """
        return {
            "database": DatabaseConfig(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "5432")),
                database=os.getenv("DB_NAME", "testdb"),
                username=os.getenv("DB_USER", "user"),
                password=os.getenv("DB_PASSWORD", "password"),
                ssl_enabled=os.getenv("DB_SSL", "false").lower() == "true"
            ),
            "api": APIConfig(
                host=os.getenv("API_HOST", "0.0.0.0"),
                port=int(os.getenv("API_PORT", "8080")),
                debug=os.getenv("API_DEBUG", "false").lower() == "true",
                cors_enabled=os.getenv("API_CORS", "true").lower() == "true",
                rate_limit=int(os.getenv("API_RATE_LIMIT", "100"))
            ),
            "logging": {
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "format": os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration.
        
        Returns:
            DatabaseConfig instance
        """
        return self.get("database")
    
    def get_api_config(self) -> APIConfig:
        """Get API configuration.
        
        Returns:
            APIConfig instance
        """
        return self.get("api")
''',
                    "api/__init__.py": '''"""API module."""''',
                    "api/app.py": '''"""Flask application for REST API."""

from flask import Flask, jsonify, request
from flask_cors import CORS
from typing import Dict, Any
import logging

from core.base import BaseService, DataProcessor
from core.config import Config


class APIApplication(BaseService):
    """Main API application service."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the API application.
        
        Args:
            config: Application configuration
        """
        super().__init__(config)
        self.app = None
        self.config_manager = Config()
    
    def initialize(self) -> None:
        """Initialize the Flask application."""
        self.app = Flask(__name__)
        
        # Load configuration
        api_config = self.config_manager.get_api_config()
        
        # Configure Flask app
        self.app.config["DEBUG"] = api_config.debug
        
        # Setup CORS if enabled
        if api_config.cors_enabled:
            CORS(self.app, origins=["*"])
        
        # Setup routes
        self._setup_routes()
        
        # Setup error handlers
        self._setup_error_handlers()
        
        self.logger.info("API application initialized")
    
    def _setup_routes(self) -> None:
        """Setup API routes."""
        
        @self.app.route("/health", methods=["GET"])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "version": "2.0.0"
            })
        
        @self.app.route("/api/v1/process", methods=["POST"])
        def process_data():
            """Process data endpoint."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No data provided"}), 400
                
                # Process data (placeholder)
                result = {
                    "processed": True,
                    "input": data,
                    "result": "Data processed successfully"
                }
                
                return jsonify(result)
                
            except Exception as e:
                self.logger.error(f"Processing failed: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/api/v1/status", methods=["GET"])
        def get_status():
            """Get API status."""
            return jsonify({
                "service": "complex-python-api",
                "version": "2.0.0",
                "status": "running"
            })
    
    def _setup_error_handlers(self) -> None:
        """Setup global error handlers."""
        
        @self.app.errorhandler(404)
        def not_found(error):
            """Handle 404 errors."""
            return jsonify({"error": "Endpoint not found"}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            """Handle 500 errors."""
            return jsonify({"error": "Internal server error"}), 500
    
    def shutdown(self) -> None:
        """Shutdown the application."""
        self.logger.info("Shutting down API application")
    
    def run(self, host: str = None, port: int = None, debug: bool = None) -> None:
        """Run the Flask application.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            debug: Enable debug mode
        """
        if not self.app:
            self.initialize()
        
        api_config = self.config_manager.get_api_config()
        
        self.app.run(
            host=host or api_config.host,
            port=port or api_config.port,
            debug=debug if debug is not None else api_config.debug
        )


# Global API application instance
api_app = APIApplication()


def create_app() -> Flask:
    """Create and configure Flask application.
    
    Returns:
        Configured Flask application
    """
    api_app.initialize()
    return api_app.app


if __name__ == "__main__":
    create_app().run()
''',
                    "data/__init__.py": '''"""Data processing module."""''',
                    "data/models.py": '''"""Data models and structures."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class User:
    """User data model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    preferences: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate user data after initialization."""
        if not self.name:
            raise ValueError("User name is required")
        if "@" not in self.email:
            raise ValueError("Valid email is required")


@dataclass
class Document:
    """Document data model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    author_id: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the document.
        
        Args:
            tag: Tag to add
        """
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the document.
        
        Args:
            tag: Tag to remove
        """
        if tag in self.tags:
            self.tags.remove(tag)
    
    def update_content(self, content: str) -> None:
        """Update document content.
        
        Args:
            content: New content
        """
        self.content = content
        self.updated_at = datetime.now()


@dataclass
class DataRecord:
    """Generic data record model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    data_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    checksum: str = ""
    
    def calculate_checksum(self) -> str:
        """Calculate checksum for the record.
        
        Returns:
            MD5 checksum of the payload
        """
        import hashlib
        content = json.dumps(self.payload, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def validate(self) -> bool:
        """Validate the data record.
        
        Returns:
            True if record is valid
        """
        if not self.id or not self.data_type:
            return False
        
        calculated_checksum = self.calculate_checksum()
        return self.checksum == calculated_checksum


class DataRepository:
    """In-memory data repository for testing."""
    
    def __init__(self):
        """Initialize the repository."""
        self._users: Dict[str, User] = {}
        self._documents: Dict[str, Document] = {}
        self._records: Dict[str, DataRecord] = {}
    
    def add_user(self, user: User) -> User:
        """Add a user to the repository.
        
        Args:
            user: User to add
            
        Returns:
            Added user
        """
        self._users[user.id] = user
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User if found, None otherwise
        """
        return self._users.get(user_id)
    
    def list_users(self) -> List[User]:
        """List all users.
        
        Returns:
            List of users
        """
        return list(self._users.values())
    
    def add_document(self, document: Document) -> Document:
        """Add a document to the repository.
        
        Args:
            document: Document to add
            
        Returns:
            Added document
        """
        self._documents[document.id] = document
        return document
    
    def get_document(self, document_id: str) -> Optional[Document]:
        """Get document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document if found, None otherwise
        """
        return self._documents.get(document_id)
    
    def search_documents(self, query: str) -> List[Document]:
        """Search documents by query.
        
        Args:
            query: Search query
            
        Returns:
            List of matching documents
        """
        results = []
        for doc in self._documents.values():
            if query.lower() in doc.title.lower() or query.lower() in doc.content.lower():
                results.append(doc)
        return results
    
    def add_record(self, record: DataRecord) -> DataRecord:
        """Add a data record to the repository.
        
        Args:
            record: Record to add
            
        Returns:
            Added record
        """
        record.checksum = record.calculate_checksum()
        self._records[record.id] = record
        return record
    
    def get_valid_records(self) -> List[DataRecord]:
        """Get all valid records.
        
        Returns:
            List of valid records
        """
        return [record for record in self._records.values() if record.validate()]
''',
                    "utils/__init__.py": '''"""Utility functions module."""''',
                    "utils/helpers.py": '''"""Utility helper functions."""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import hashlib


def format_datetime(dt: datetime, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime object as string.
    
    Args:
        dt: datetime object
        format_string: Format string
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_string)


def parse_datetime(date_string: str, format_string: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse datetime string to datetime object.
    
    Args:
        date_string: Datetime string
        format_string: Format string
        
    Returns:
        datetime object
        
    Raises:
        ValueError: If parsing fails
    """
    return datetime.strptime(date_string, format_string)


def calculate_hash(data: Any) -> str:
    """Calculate hash of data.
    
    Args:
        data: Data to hash
        
    Returns:
        MD5 hash of the data
    """
    content = json.dumps(data, sort_keys=True) if isinstance(data, (dict, list)) else str(data)
    return hashlib.md5(content.encode()).hexdigest()


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get value from dictionary.
    
    Args:
        dictionary: Dictionary to get value from
        key: Key to get
        default: Default value if key not found
        
    Returns:
        Value or default
    """
    try:
        return dictionary.get(key, default)
    except (AttributeError, TypeError):
        return default


def flatten_dict(dictionary: Dict[str, Any], separator: str = ".") -> Dict[str, str]:
    """Flatten nested dictionary.
    
    Args:
        dictionary: Dictionary to flatten
        separator: Separator for flattened keys
        
    Returns:
        Flattened dictionary
    """
    flattened = {}
    
    def _flatten(obj: Any, parent_key: str = ""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_key = f"{parent_key}{separator}{key}" if parent_key else key
                _flatten(value, new_key)
        else:
            flattened[parent_key] = obj
    
    _flatten(dictionary)
    return flattened


class LoggerMixin:
    """Mixin class that provides logging capabilities."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return logging.getLogger(self.__class__.__name__)


class ValidationError(Exception):
    """Exception raised when validation fails."""
    pass


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate that all required fields are present.
    
    Args:
        data: Data to validate
        required_fields: List of required field names
        
    Raises:
        ValidationError: If any required field is missing
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")


def validate_email(email: str) -> bool:
    """Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
''',
                    "utils/validators.py": """Data validation utilities."""

import re
from typing import Any, List, Dict, Optional
from datetime import datetime


class Validator:
    """Base validation class."""
    
    def __init__(self):
        """Initialize validator."""
        self.errors = []
    
    def validate(self, data: Any) -> bool:
        """Validate data.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        self.errors.clear()
        return self._do_validate(data)
    
    def _do_validate(self, data: Any) -> bool:
        """Perform actual validation (override in subclasses).
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        return True
    
    def get_errors(self) -> List[str]:
        """Get validation errors.
        
        Returns:
            List of error messages
        """
        return self.errors.copy()


class StringValidator(Validator):
    """String validation."""
    
    def __init__(self, min_length: Optional[int] = None, max_length: Optional[int] = None):
        """Initialize string validator.
        
        Args:
            min_length: Minimum string length
            max_length: Maximum string length
        """
        super().__init__()
        self.min_length = min_length
        self.max_length = max_length
    
    def _do_validate(self, data: Any) -> bool:
        """Validate string data.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, str):
            self.errors.append("Value must be a string")
            return False
        
        if self.min_length is not None and len(data) < self.min_length:
            self.errors.append(f"String must be at least {self.min_length} characters")
            return False
        
        if self.max_length is not None and len(data) > self.max_length:
            self.errors.append(f"String must be at most {self.max_length} characters")
            return False
        
        return True


class EmailValidator(StringValidator):
    """Email address validation."""
    
    def __init__(self):
        """Initialize email validator."""
        super().__init__(min_length=5, max_length=255)
        self.email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
    
    def _do_validate(self, data: Any) -> bool:
        """Validate email address.
        
        Args:
            data: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not super()._do_validate(data):
            return False
        
        if not self.email_pattern.match(data):
            self.errors.append("Invalid email format")
            return False
        
        return True


class NumberValidator(Validator):
    """Numeric validation."""
    
    def __init__(self, min_value: Optional[float] = None, max_value: Optional[float] = None):
        """Initialize number validator.
        
        Args:
            min_value: Minimum numeric value
            max_value: Maximum numeric value
        """
        super().__init__()
        self.min_value = min_value
        self.max_value = max_value
    
    def _do_validate(self, data: Any) -> bool:
        """Validate numeric data.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            number = float(data)
        except (ValueError, TypeError):
            self.errors.append("Value must be a number")
            return False
        
        if self.min_value is not None and number < self.min_value:
            self.errors.append(f"Number must be at least {self.min_value}")
            return False
        
        if self.max_value is not None and number > self.max_value:
            self.errors.append(f"Number must be at most {self.max_value}")
            return False
        
        return True


class DateValidator(Validator):
    """Date validation."""
    
    def __init__(self, min_date: Optional[datetime] = None, max_date: Optional[datetime] = None):
        """Initialize date validator.
        
        Args:
            min_date: Minimum date
            max_date: Maximum date
        """
        super().__init__()
        self.min_date = min_date
        self.max_date = max_date
    
    def _do_validate(self, data: Any) -> bool:
        """Validate date data.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if isinstance(data, datetime):
            date_obj = data
        elif isinstance(data, str):
            try:
                date_obj = datetime.fromisoformat(data)
            except ValueError:
                self.errors.append("Invalid date format")
                return False
        else:
            self.errors.append("Value must be a datetime or ISO date string")
            return False
        
        if self.min_date is not None and date_obj < self.min_date:
            self.errors.append(f"Date must be after {self.min_date}")
            return False
        
        if self.max_date is not None and date_obj > self.max_date:
            self.errors.append(f"Date must be before {self.max_date}")
            return False
        
        return True
""",
                    "tests/__init__.py": "",
                    "tests/test_core.py": """Tests for core module.""",
                    "tests/test_api.py": """Tests for API module.""",
                    "tests/test_data.py": """Tests for data module.""",
                    "tests/test_utils.py": """Tests for utils module."""
                }
            },
            
            "jac_example": {
                "name": "jac-example",
                "description": "JAC language example project",
                "language": "jac",
                "files": {
                    "README.md": """# JAC Example Project

This is a sample JAC (Jac Language) project demonstrating various features.

## Features

- Node and edge definitions
- Walker implementations
- Graph traversal algorithms
- Data processing pipelines

## Usage

```bash
jac run main.jac
```
""",
                    "main.jac": '''// Main JAC file
node person: {
    has name: str;
    has age: int;
    has email: str;
}

node project: {
    has title: str;
    has description: str;
    has start_date: str;
}

edge works_on: {
    has role: str;
    has hours_per_week: int;
}

walker init {
    root {
        print("JAC Example Project Initialized");
        take;
    }
    
    person {
        print(f"Person: {here.name}, Age: {here.age}");
        take;
    }
    
    project {
        print(f"Project: {here.title}");
        take;
    }
}

walker process_team {
    has team_size: int = 5;
    
    root {
        print("Processing team...");
        take;
    }
    
    person {
        if (here.age > 25) {
            print(f"Senior: {here.name}");
        } else {
            print(f"Junior: {here.name}");
        }
        take;
    }
}
''',
                    "utils.jac": '''// Utility functions in JAC
node utility {
    has function_name: str;
    has description: str;
}

walker validate_input {
    has input_data: dict;
    has validation_rules: dict;
    
    root {
        print("Validating input data...");
        take;
    }
    
    utility {
        rule_name = here.function_name;
        if (rule_name in validation_rules) {
            result = validation_rules[rule_name](input_data);
            print(f"Validation {rule_name}: {result}");
        }
        take;
    }
}
''',
                    "processors.jac": '''// Data processors in JAC
node processor {
    has processor_type: str;
    has config: dict;
}

walker process_data {
    has data_source: str;
    has output_format: str = "json";
    
    root {
        print("Starting data processing...");
        take;
    }
    
    processor {
        if (here.processor_type == "transform") {
            print("Transforming data...");
            // Data transformation logic
        } else if (here.processor_type == "aggregate") {
            print("Aggregating data...");
            // Data aggregation logic
        }
        take;
    }
}
'''
                }
            },
            
            "edge_cases": {
                "name": "edge-cases",
                "description": "Repository with various edge cases for testing",
                "language": "mixed",
                "files": {
                    "README.md": """# Edge Cases Repository

This repository contains various edge cases for testing documentation generation.

## Edge Cases Included

- Empty files
- Very long files
- Files with special characters
- Binary-like content
- Non-ASCII filenames
- Circular dependencies
- Missing imports
- Syntax errors
""",
                    "empty_file.py": "",
                    "special_chars.md": """# File with Special Characters

This file contains various special characters: àáâãäåæçèéêëìíîï
And symbols: ∑∏∫√∞≈≠≤≥±×÷

Emojis: 🚀🔥��📊🎯✅❌
""",
                    "very_long_file.py": '''"""This is a very long Python file to test documentation generation
with large files. It contains many functions, classes, and complex logic
to test the system's ability to handle substantial codebases.

This file tests:
1. Long function definitions
2. Complex class hierarchies
3. Deeply nested structures
4. Multiple import patterns
5. Extensive documentation strings
6. Various coding patterns
7. Error handling
8. Performance considerations
9. Code organization
10. Maintainability aspects
''' + "\\n".join([f'# Line {i}' for i in range(1000)]),
                    "binary_content.py": '''# This file has binary-like content
import os
data = b"\\x00\\x01\\x02\\x03\\x04\\x05"
'''
                }
            }
        }
    
    def create_sample_repository(self, repo_key: str, output_dir: Path) -> Path:
        """Create a sample repository.
        
        Args:
            repo_key: Key of repository to create
            output_dir: Output directory path
            
        Returns:
            Path to created repository
        """
        if repo_key not in self.sample_repos:
            raise ValueError(f"Unknown repository key: {repo_key}")
        
        repo_config = self.sample_repos[repo_key]
        repo_dir = output_dir / repo_config["name"]
        
        # Create directory structure
        repo_dir.mkdir(parents=True, exist_ok=True)
        
        # Create files
        for file_path, content in repo_config["files"].items():
            full_path = repo_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Initialize git repository if git is available
        try:
            subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_dir, check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"⚠️  Could not initialize git repository for {repo_config['name']}")
        
        return repo_dir
    
    def create_all_sample_repositories(self) -> List[Path]:
        """Create all sample repositories.
        
        Returns:
            List of paths to created repositories
        """
        print("📦 Creating sample test repositories...")
        
        created_repos = []
        for repo_key in self.sample_repos.keys():
            try:
                repo_path = self.create_sample_repository(repo_key, self.base_dir)
                created_repos.append(repo_path)
                print(f"  ✅ Created: {repo_key} -> {repo_path}")
            except Exception as e:
                print(f"  ❌ Failed to create {repo_key}: {e}")
        
        return created_repos
    
    def get_repository_info(self, repo_key: str) -> Dict[str, Any]:
        """Get information about a sample repository.
        
        Args:
            repo_key: Repository key
            
        Returns:
            Repository information
        """
        if repo_key not in self.sample_repos:
            raise ValueError(f"Unknown repository key: {repo_key}")
        
        return self.sample_repos[repo_key].copy()
    
    def list_available_repositories(self) -> List[Dict[str, Any]]:
        """List all available sample repositories.
        
        Returns:
            List of repository information
        """
        return [
            {"key": key, **config}
            for key, config in self.sample_repos.items()
        ]

def main():
    """Main function to create sample repositories."""
    generator = SampleRepositoryGenerator()
    
    # Create all repositories
    created_repos = generator.create_all_sample_repositories()
    
    print(f"\n🎉 Successfully created {len(created_repos)} sample repositories:")
    for repo_path in created_repos:
        print(f"  📁 {repo_path}")
    
    # List available repositories
    print(f"\n📋 Available repositories:")
    for repo_info in generator.list_available_repositories():
        print(f"  - {repo_info['key']}: {repo_info['description']}")

if __name__ == "__main__":
    main()
