#!/usr/bin/env python3
"""
Test suite for Repository Mapper implementation
"""

import requests
import json
import time
import sys

def test_api_health():
    """Test the health check endpoint"""
    try:
        response = requests.get("http://localhost:8080/api/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_repository_mapping():
    """Test repository mapping with a sample repository"""
    test_repo = "https://github.com/microsoft/vscode"
    
    try:
        # Test the main mapping endpoint
        data = {
            "repository_url": test_repo,
            "max_file_size": 1048576,  # 1MB for testing
            "include_ignored": False
        }
        
        response = requests.post(
            "http://localhost:8080/api/map-repository",
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print("✅ Repository mapping test passed")
                print(f"   - Found {result['file_tree']['statistics']['total_files']} files")
                print(f"   - Repository URL: {result['repository_url']}")
                return True
            else:
                print(f"❌ Repository mapping failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Repository mapping request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Repository mapping test error: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Repository Mapper Implementation")
    print("=" * 50)
    
    # Wait for service to be ready
    print("Waiting for service to be ready...")
    time.sleep(5)
    
    tests_passed = 0
    total_tests = 2
    
    # Run tests
    if test_api_health():
        tests_passed += 1
    
    if test_repository_mapping():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("💥 Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
