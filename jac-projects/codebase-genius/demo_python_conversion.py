#!/usr/bin/env python3
"""
Codebase Genius - Python Starter Script
Demonstrates the converted system running with standard Python
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

def test_repository_mapping():
    """Test the repository mapper agent"""
    print("🗺️ Testing Repository Mapper Agent...")
    
    try:
        from agents.repository-mapper-agent.main import map_repository_api
        
        # Test with a small public repository
        test_repo = "https://github.com/octocat/Hello-World"
        result = map_repository_api(test_repo, max_file_size=1024*1024)  # 1MB limit
        
        if result.get("status") == "success":
            print("✅ Repository mapping successful!")
            stats = result.get("file_tree", {}).get("statistics", {})
            print(f"   📁 Files found: {stats.get('total_files', 0)}")
            print(f"   📂 Directories: {stats.get('total_directories', 0)}")
            print(f"   💾 Total size: {stats.get('total_size_bytes', 0)} bytes")
            
            # Show language distribution
            lang_dist = stats.get('language_distribution', {})
            if lang_dist:
                print("   🔤 Languages detected:")
                for lang, count in lang_dist.items():
                    print(f"      - {lang}: {count} files")
        else:
            print(f"❌ Repository mapping failed: {result.get('error', 'Unknown error')}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_code_analysis():
    """Test the code analyzer agent"""
    print("🔍 Testing Code Analyzer Agent...")
    
    try:
        from agents.code-analyzer-agent.main import analyze_repository_api
        
        # Create a temporary test repository
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files
            test_py = Path(temp_dir) / "test.py"
            test_py.write_text('''
def hello_world():
    """A simple function"""
    print("Hello, World!")
    return "Hello"

class Calculator:
    """A simple calculator class"""
    
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b

# Usage example
calc = Calculator()
result = calc.add(5, 3)
print(f"Result: {result}")
''')
            
            test_js = Path(temp_dir) / "test.js"
            test_js.write_text('''
function greet(name) {
    return `Hello, ${name}!`;
}

class Greeter {
    constructor(name) {
        this.name = name;
    }
    
    greet() {
        return greet(this.name);
    }
}

const greeter = new Greeter("World");
console.log(greeter.greet());
''')
            
            # Analyze the repository
            result = analyze_repository_api(temp_dir, analysis_depth="basic")
            
            if result.get("status") == "success":
                print("✅ Code analysis successful!")
                metrics = result.get("metrics", {})
                print(f"   📊 Total elements: {metrics.get('total_elements', 0)}")
                print(f"   🔗 Total relationships: {metrics.get('total_relationships', 0)}")
                print(f"   ⏱️ Analysis timestamp: {metrics.get('analysis_timestamp', 'N/A')}")
            else:
                print(f"❌ Code analysis failed: {result.get('error', 'Unknown error')}")
                
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_documentation_generation():
    """Test the DocGenie agent"""
    print("📚 Testing DocGenie Agent...")
    
    try:
        from agents.docgenie-agent.main import generate_documentation_api
        
        # Sample CCG data
        sample_ccg_data = {
            "entities": [
                {
                    "id": "entity_1",
                    "name": "Calculator",
                    "type": "class",
                    "file_path": "src/calculator.py",
                    "start_line": 1,
                    "end_line": 25,
                    "complexity": 5.5,
                    "dependencies": [],
                    "documentation": "A calculator class with basic arithmetic operations"
                },
                {
                    "id": "entity_2",
                    "name": "add_numbers",
                    "type": "function",
                    "file_path": "src/utils.py",
                    "start_line": 10,
                    "end_line": 20,
                    "complexity": 2.0,
                    "dependencies": [],
                    "documentation": "Add two numbers together"
                }
            ],
            "relationships": [
                {
                    "from": "entity_1",
                    "to": "entity_2",
                    "type": "calls",
                    "confidence": 0.95,
                    "context": "Calculator uses add_numbers function"
                }
            ],
            "metadata": {
                "repository_name": "sample-calculator",
                "total_files": 5,
                "analysis_date": "2024-01-01T00:00:00",
                "languages_detected": ["python"],
                "complexity_stats": {
                    "avg_complexity": 3.75,
                    "max_complexity": 5.5,
                    "complexity_distribution": {"low": 2, "medium": 0, "high": 0}
                }
            }
        }
        
        sample_repo_info = {
            "url": "https://github.com/example/calculator",
            "name": "sample-calculator",
            "description": "A simple calculator library"
        }
        
        # Generate documentation
        result = generate_documentation_api(sample_ccg_data, sample_repo_info)
        
        if result.get("status") == "success":
            print("✅ Documentation generation successful!")
            output_files = result.get("output_files", [])
            print(f"   📄 Generated files: {len(output_files)}")
            for file_path in output_files:
                print(f"      - {file_path}")
            
            quality_metrics = result.get("quality_metrics", {})
            print(f"   ⭐ Quality score: {quality_metrics.get('quality_score', 0):.2f}")
            print(f"   📖 Sections generated: {quality_metrics.get('total_sections', 0)}")
            print(f"   📚 Citations added: {quality_metrics.get('total_citations', 0)}")
        else:
            print(f"❌ Documentation generation failed: {result.get('error', 'Unknown error')}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_supervisor_workflow():
    """Test the supervisor agent with a complete workflow"""
    print("🎯 Testing Supervisor Agent (Complete Workflow)...")
    
    try:
        from agents.supervisor-agent.main import process_api_request
        
        # Test request data
        request_data = {
            "repository_url": "https://github.com/octocat/Hello-World",
            "options": {
                "depth": "basic",
                "include_diagrams": False
            },
            "priority": 5
        }
        
        print("   🚀 Starting complete workflow...")
        result = process_api_request(request_data)
        
        if result.get("status") == "completed":
            print("✅ Complete workflow successful!")
            print(f"   🆔 Workflow ID: {result.get('workflow_id', 'N/A')}")
            print(f"   ⏱️ Total time: {result.get('total_time', 0):.2f} seconds")
            
            quality_metrics = result.get('quality_metrics', {})
            print(f"   ⭐ Overall quality score: {quality_metrics.get('overall_score', 0):.2f}")
            
            final_output = result.get('final_output', {})
            if final_output:
                print(f"   📋 Summary: {final_output.get('summary', 'N/A')}")
        else:
            print(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main test function"""
    print("🚀 Codebase Genius - Python Conversion Demo")
    print("=" * 50)
    print("Testing all converted components...")
    print()
    
    # Check if we're in the right directory
    if not Path("api-frontend").exists():
        print("❌ Please run this script from the codebase-genius-impl directory")
        return
    
    # Run tests
    test_repository_mapping()
    print()
    
    test_code_analysis()
    print()
    
    test_documentation_generation()
    print()
    
    test_supervisor_workflow()
    print()
    
    print("🎉 Demo completed!")
    print()
    print("Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Start the API server: python api-frontend/start.py")
    print("3. Open browser to: http://localhost:8501")
    print("4. Or use API directly: http://localhost:8000")

if __name__ == "__main__":
    main()
