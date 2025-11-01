#!/usr/bin/env python3
"""
Test script to verify the Jac to Python conversion works correctly
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported correctly"""
    print("🧪 Testing module imports...")
    
    try:
        # Test API imports
        print("  Testing main_api imports...")
        from api.main_api import app, main
        print("  ✅ main_api imported successfully")
        
        # Test agent imports
        print("  Testing agent imports...")
        from code.supervisor-agent.main import SupervisorAgent
        from code.docgenie-agent.main import DocGenieAgent  
        from code.code-analyzer.main import CodeAnalyzer
        from code.repository-mapper.main import RepositoryMapper
        print("  ✅ All agents imported successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_functionality():
    """Test basic API functionality"""
    print("\n🔧 Testing API functionality...")
    
    try:
        from api.main_api import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        if response.status_code == 200:
            print("  ✅ Health endpoint working")
        else:
            print(f"  ❌ Health endpoint failed: {response.status_code}")
            return False
            
        # Test config endpoint
        response = client.get("/api/config")
        if response.status_code == 200:
            print("  ✅ Config endpoint working")
        else:
            print(f"  ❌ Config endpoint failed: {response.status_code}")
            return False
            
        return True
        
    except Exception as e:
        print(f"  ❌ API functionality test failed: {e}")
        return False

def test_agent_initialization():
    """Test that agents can be initialized"""
    print("\n🤖 Testing agent initialization...")
    
    try:
        # Test Supervisor Agent
        from code.supervisor-agent.main import SupervisorAgent
        supervisor = SupervisorAgent()
        print("  ✅ SupervisorAgent initialized")
        
        # Test DocGenie Agent
        from code.docgenie-agent.main import DocGenieAgent
        docgenie = DocGenieAgent()
        print("  ✅ DocGenieAgent initialized")
        
        # Test Code Analyzer
        from code.code-analyzer.main import CodeAnalyzer
        analyzer = CodeAnalyzer()
        print("  ✅ CodeAnalyzer initialized")
        
        # Test Repository Mapper
        from code.repository-mapper.main import RepositoryMapper
        mapper = RepositoryMapper()
        print("  ✅ RepositoryMapper initialized")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Agent initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """Test that all required dependencies are available"""
    print("\n📦 Testing dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn', 
        'jinja2',
        'tree_sitter',
        'pygithub',
        'gitpython',
        'graphviz',
        'pydantic',
        'asyncio',
        'zipfile',
        'json',
        'pathlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main test function"""
    print("🧠 Codebase Genius - Conversion Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Run tests
    if test_dependencies():
        tests_passed += 1
        
    if test_imports():
        tests_passed += 1
        
    if test_agent_initialization():
        tests_passed += 1
        
    if test_api_functionality():
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Conversion is successful.")
        return True
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
