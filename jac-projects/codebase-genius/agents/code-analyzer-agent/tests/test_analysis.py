#!/usr/bin/env python3
"""
Test suite for Code Analyzer Agent
Comprehensive testing of Tree-sitter integration, CCG construction, and API endpoints
"""

import requests
import json
import time
import sys
import os
import subprocess
import tempfile
import shutil
from pathlib import Path

class CodeAnalyzerTester:
    def __init__(self, base_url="http://localhost:8081"):
        self.base_url = base_url
        self.test_results = []
        
    def log_test(self, test_name, success, message="", details=None):
        """Log test results"""
        status = "PASS" if success else "FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        if details:
            result["details"] = details
            
        self.test_results.append(result)
        
        status_symbol = "✅" if success else "❌"
        print(f"{status_symbol} {test_name}: {message}")
        
        if not success and details:
            print(f"   Details: {details}")

class TestRepository:
    """Create test repositories for analysis"""
    
    @staticmethod
    def create_python_repo(path):
        """Create a Python test repository"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Main module
        main_py = path / "main.py"
        main_py.write_text('''
"""
Main application module.
"""

import os
import sys
from typing import List, Dict
from utils import helper_function
from models.user import User
from services.auth import AuthenticationService

class Application:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        self.auth_service = AuthenticationService()
        self.users = []
    
    def run(self):
        """Run the application."""
        print("Starting application...")
        result = self.process_data()
        return result
    
    def process_data(self) -> List[Dict]:
        """Process application data."""
        data = []
        for user in self.users:
            processed = self.transform_user(user)
            data.append(processed)
        return data
    
    def transform_user(self, user: User) -> Dict:
        """Transform user data."""
        return {
            "id": user.id,
            "name": user.name.upper(),
            "email": user.email.lower(),
            "active": user.is_active
        }
    
    async def async_operation(self):
        """Async operation for testing."""
        result = await self.auth_service.validate_token()
        return result

if __name__ == "__main__":
    app = Application()
    app.run()
''')
        
        # Utils module
        utils_py = path / "utils.py"
        utils_py.write_text('''
"""
Utility functions module.
"""

import json
from datetime import datetime
from typing import Any

def helper_function(data: Any) -> str:
    """Helper function to process data."""
    return json.dumps(data, default=str)

def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp for display."""
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

class Logger:
    """Simple logging class."""
    
    def __init__(self, name: str):
        self.name = name
        self.logs = []
    
    def log(self, message: str, level: str = "INFO"):
        """Add log entry."""
        entry = {
            "timestamp": format_timestamp(datetime.now()),
            "level": level,
            "message": message
        }
        self.logs.append(entry)
    
    def get_logs(self) -> List[Dict]:
        """Retrieve all logs."""
        return self.logs.copy()
''')
        
        # Models
        models_dir = path / "models"
        models_dir.mkdir(exist_ok=True)
        
        user_py = models_dir / "user.py"
        user_py.write_text('''
"""
User model definition.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    """User domain model."""
    
    id: int
    name: str
    email: str
    is_active: bool = True
    
    def deactivate(self):
        """Deactivate user."""
        self.is_active = False
    
    def activate(self):
        """Activate user."""
        self.is_active = True
    
    @property
    def display_name(self) -> str:
        """Get display name."""
        return self.name if self.name else "Anonymous"
    
    def __str__(self) -> str:
        return f"User(id={self.id}, name='{self.name}', email='{self.email}')"
''')
        
        # Services
        services_dir = path / "services"
        services_dir.mkdir(exist_ok=True)
        
        auth_py = services_dir / "auth.py"
        auth_py.write_text('''
"""
Authentication service module.
"""

import hashlib
from typing import Optional
from models.user import User

class AuthenticationService:
    """Handles user authentication."""
    
    def __init__(self):
        """Initialize authentication service."""
        self.users = {}
        self.sessions = {}
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials."""
        # Simplified authentication
        user_id = hashlib.md5(username.encode()).hexdigest()[:8]
        user = User(
            id=int(user_id, 16),
            name=username,
            email=f"{username}@example.com"
        )
        return user
    
    async def validate_token(self) -> bool:
        """Validate authentication token (async)."""
        # Simulate async validation
        await asyncio.sleep(0.1)
        return True
    
    def create_session(self, user: User) -> str:
        """Create user session."""
        session_id = hashlib.sha256(f"{user.id}{time.time()}".encode()).hexdigest()
        self.sessions[session_id] = user
        return session_id
''')
        
        # Requirements file
        req_py = path / "requirements.txt"
        req_py.write_text('''
requests>=2.31.0
asyncio>=3.4.3
dataclasses>=0.6
typing-extensions>=4.7.0
''')
        
        # Configuration
        config_py = path / "config.py"
        config_py.write_text('''
"""
Configuration settings.
"""

import os
from typing import Dict, Any

class Config:
    """Application configuration."""
    
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
    
    # API settings
    API_VERSION = "v1"
    API_PREFIX = f"/api/{API_VERSION}"
    
    # Security settings
    PASSWORD_MIN_LENGTH = 8
    SESSION_TIMEOUT = 3600  # 1 hour
    
    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """Get database configuration."""
        return {
            "url": cls.DATABASE_URL,
            "debug": cls.DEBUG
        }
''')
        
        print(f"✅ Created Python test repository: {path}")

class CodeAnalyzerTests:
    """Test suite for Code Analyzer"""
    
    def __init__(self):
        self.tester = CodeAnalyzerTester()
        self.test_repo_path = None
        
    def setup(self):
        """Set up test environment"""
        print("🔧 Setting up test environment...")
        
        # Create temporary test repository
        self.test_repo_path = tempfile.mkdtemp(prefix="code_analyzer_test_")
        TestRepository.create_python_repo(self.test_repo_path)
        
        # Ensure service is running
        if not self.wait_for_service():
            print("❌ Service not available")
            return False
            
        return True
        
    def teardown(self):
        """Clean up test environment"""
        if self.test_repo_path and os.path.exists(self.test_repo_path):
            shutil.rmtree(self.test_repo_path)
            print(f"✅ Cleaned up test repository: {self.test_repo_path}")
    
    def wait_for_service(self, timeout=30):
        """Wait for service to be available"""
        print("⏳ Waiting for service to be available...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.tester.base_url}/api/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Service is available")
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(2)
        
        print("❌ Service not available within timeout")
        return False
    
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{self.tester.base_url}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("service") == "Code Analyzer Agent":
                    self.tester.log_test(
                        "Health Check", True, 
                        "Service is healthy",
                        {"service": data.get("service"), "version": data.get("version")}
                    )
                    return True
            
            self.tester.log_test(
                "Health Check", False,
                f"Unexpected response: {response.status_code}",
                {"response": response.text}
            )
            return False
            
        except Exception as e:
            self.tester.log_test("Health Check", False, f"Request failed: {str(e)}")
            return False
    
    def test_repository_analysis(self):
        """Test repository analysis endpoint"""
        try:
            payload = {
                "repository_path": self.test_repo_path,
                "analysis_depth": "full",
                "max_file_size": 1048576
            }
            
            response = requests.post(
                f"{self.tester.base_url}/api/analyze-repository",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    metrics = result.get("metrics", {})
                    self.tester.log_test(
                        "Repository Analysis", True,
                        "Analysis completed successfully",
                        {
                            "files_analyzed": metrics.get("total_files", 0),
                            "elements_found": metrics.get("total_elements", 0),
                            "relationships": metrics.get("total_relationships", 0)
                        }
                    )
                    return True
                else:
                    self.tester.log_test(
                        "Repository Analysis", False,
                        f"Analysis failed: {result.get('error', 'Unknown error')}"
                    )
                    return False
            else:
                self.tester.log_test(
                    "Repository Analysis", False,
                    f"HTTP error: {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            self.tester.log_test("Repository Analysis", False, f"Request failed: {str(e)}")
            return False
    
    def test_relationship_query(self):
        """Test relationship query endpoint"""
        try:
            payload = {
                "repository_path": self.test_repo_path,
                "query_type": "dependencies",
                "element_name": "Application",
                "max_results": 10
            }
            
            response = requests.post(
                f"{self.tester.base_url}/api/query-relationships",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    query_result = result.get("query_result", {})
                    self.tester.log_test(
                        "Relationship Query", True,
                        "Query executed successfully",
                        {
                            "query_type": query_result.get("query_type"),
                            "element": query_result.get("element_name")
                        }
                    )
                    return True
                else:
                    self.tester.log_test(
                        "Relationship Query", False,
                        f"Query failed: {result.get('error', 'Unknown error')}"
                    )
                    return False
            else:
                self.tester.log_test(
                    "Relationship Query", False,
                    f"HTTP error: {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            self.tester.log_test("Relationship Query", False, f"Request failed: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test error handling with invalid inputs"""
        try:
            # Test with non-existent repository
            payload = {
                "repository_path": "/nonexistent/path",
                "analysis_depth": "basic"
            }
            
            response = requests.post(
                f"{self.tester.base_url}/api/analyze-repository",
                json=payload,
                timeout=30
            )
            
            # Should return an error response
            if response.status_code in [400, 404, 500]:
                self.tester.log_test(
                    "Error Handling", True,
                    "Properly handled invalid repository path",
                    {"status_code": response.status_code}
                )
                return True
            else:
                self.tester.log_test(
                    "Error Handling", False,
                    f"Unexpected status code: {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            self.tester.log_test("Error Handling", False, f"Request failed: {str(e)}")
            return False
    
    def test_performance_analysis(self):
        """Test performance with larger repository"""
        try:
            # Create a larger test repository
            large_repo = tempfile.mkdtemp(prefix="code_analyzer_perf_")
            TestRepository.create_python_repo(large_repo)
            
            # Add more complex files
            complex_py = Path(large_repo) / "complex.py"
            complex_py.write_text('''
"""
Complex module for performance testing.
"""

class ComplexProcessor:
    """Complex processing class with deep nesting."""
    
    def __init__(self):
        self.data = {}
        self.processors = []
        
    def process_nested_conditions(self, value):
        """Method with complex conditional logic."""
        if value > 100:
            if value > 200:
                if value > 300:
                    return self.handle_high_value(value)
                else:
                    return self.handle_medium_value(value)
            else:
                return self.handle_low_value(value)
        elif value < 0:
            return self.handle_negative_value(value)
        else:
            return self.handle_zero_value(value)
    
    def handle_high_value(self, value):
        """Handle high values."""
        return value * 2
    
    def handle_medium_value(self, value):
        """Handle medium values."""
        return value * 1.5
    
    def handle_low_value(self, value):
        """Handle low values."""
        return value * 1.2
    
    def handle_negative_value(self, value):
        """Handle negative values."""
        return abs(value)
    
    def handle_zero_value(self, value):
        """Handle zero value."""
        return 0
''')
            
            start_time = time.time()
            
            payload = {
                "repository_path": large_repo,
                "analysis_depth": "full",
                "max_file_size": 1048576
            }
            
            response = requests.post(
                f"{self.tester.base_url}/api/analyze-repository",
                json=payload,
                timeout=60
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    self.tester.log_test(
                        "Performance Analysis", True,
                        f"Performance test completed in {duration:.2f}s",
                        {
                            "duration": duration,
                            "repository_size": len(list(Path(large_repo).rglob("*.py")))
                        }
                    )
                    success = True
                else:
                    self.tester.log_test(
                        "Performance Analysis", False,
                        f"Analysis failed: {result.get('error')}"
                    )
                    success = False
            else:
                self.tester.log_test(
                    "Performance Analysis", False,
                    f"HTTP error: {response.status_code}"
                )
                success = False
            
            # Cleanup
            shutil.rmtree(large_repo)
            return success
            
        except Exception as e:
            self.tester.log_test("Performance Analysis", False, f"Request failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Running Code Analyzer Tests")
        print("=" * 50)
        
        if not self.setup():
            print("❌ Test setup failed")
            return False
        
        try:
            # Run tests
            self.test_health_check()
            self.test_repository_analysis()
            self.test_relationship_query()
            self.test_error_handling()
            self.test_performance_analysis()
            
            # Generate report
            self.generate_report()
            
            return True
            
        finally:
            self.teardown()
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 50)
        print("�� Test Results Summary")
        print("=" * 50)
        
        passed = sum(1 for result in self.tester.test_results if result["status"] == "PASS")
        total = len(self.tester.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {passed/total*100:.1f}%")
        
        if passed == total:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n❌ {total - passed} test(s) failed")
            print("\nFailed Tests:")
            for result in self.tester.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result['message']}")
        
        # Save detailed report
        report_file = f"test_results_{int(time.time())}.json"
        with open(report_file, "w") as f:
            json.dump(self.tester.test_results, f, indent=2)
        print(f"\n📄 Detailed report saved: {report_file}")

def main():
    """Main test execution"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Code Analyzer Test Suite")
        print("Usage: python test_analysis.py")
        print("This will run all tests against the Code Analyzer service.")
        return
    
    # Run tests
    tester = CodeAnalyzerTests()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
