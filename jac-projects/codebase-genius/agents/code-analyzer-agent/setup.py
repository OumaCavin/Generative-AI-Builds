#!/usr/bin/env python3
"""
Code Analyzer Setup Script
Initializes Tree-sitter parsers and dependencies for Codebase Genius Code Analyzer
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

def create_directories():
    """Create necessary directories for the project"""
    directories = [
        "logs",
        "cache",
        "output",
        "config",
        "tests",
        "parsers",
        "data"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_tree_sitter():
    """Set up Tree-sitter language parsers"""
    print("🌳 Setting up Tree-sitter parsers...")
    
    try:
        # Check if Tree-sitter is available
        import tree_sitter
        print("✅ Tree-sitter library found")
        
        # Test each parser
        parsers_to_test = [
            ("python", "tree_sitter.Language('tree-sitter-python', 'python')"),
            ("javascript", "tree_sitter.Language('tree-sitter-javascript', 'javascript')"),
            ("typescript", "tree_sitter.Language('tree-sitter-typescript', 'typescript')"),
            ("java", "tree_sitter.Language('tree-sitter-java', 'java')"),
            ("cpp", "tree_sitter.Language('tree-sitter-cpp', 'cpp')"),
            ("c", "tree_sitter.Language('tree-sitter-c', 'c')")
        ]
        
        available_parsers = []
        for lang_name, parser_expr in parsers_to_test:
            try:
                # Test parser compilation
                eval_result = eval(parser_expr)
                available_parsers.append(lang_name)
                print(f"✅ {lang_name} parser available")
            except Exception as e:
                print(f"⚠️  {lang_name} parser not available: {str(e)}")
        
        return {
            "status": "success",
            "available_parsers": available_parsers,
            "total_parsers": len(available_parsers)
        }
        
    except ImportError as e:
        print(f"❌ Tree-sitter not available: {e}")
        return {
            "status": "error",
            "error": str(e),
            "available_parsers": []
        }
    except Exception as e:
        print(f"❌ Tree-sitter setup failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "available_parsers": []
        }

def install_tree_sitter_grammars():
    """Install Tree-sitter language grammars"""
    print("📦 Installing Tree-sitter grammars...")
    
    grammars = [
        "git clone https://github.com/tree-sitter/tree-sitter-python.git parsers/python",
        "git clone https://github.com/tree-sitter/tree-sitter-javascript.git parsers/javascript",
        "git clone https://github.com/tree-sitter/tree-sitter-typescript.git parsers/typescript",
        "git clone https://github.com/tree-sitter/tree-sitter-java.git parsers/java",
        "git clone https://github.com/tree-sitter/tree-sitter-cpp.git parsers/cpp",
        "git clone https://github.com/tree-sitter/tree-sitter-c.git parsers/c",
        "git clone https://github.com/tree-sitter/tree-sitter-go.git parsers/go",
        "git clone https://github.com/tree-sitter/tree-sitter-rust.git parsers/rust",
        "git clone https://github.com/tree-sitter/tree-sitter-php.git parsers/php",
        "git clone https://github.com/tree-sitter/tree-sitter-ruby.git parsers/ruby"
    ]
    
    installed_grammars = []
    for grammar_cmd in grammars:
        try:
            # Extract language name from command
            lang_name = grammar_cmd.split('/')[-1].split('.')[0].split('-')[-1]
            
            # Check if already installed
            if os.path.exists(f"parsers/{lang_name}"):
                print(f"✅ {lang_name} grammar already installed")
                installed_grammars.append(lang_name)
                continue
            
            # Clone the repository
            subprocess.run(grammar_cmd.split(), check=True, capture_output=True)
            print(f"✅ Installed {lang_name} grammar")
            installed_grammars.append(lang_name)
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Failed to install grammar for {lang_name}: {e}")
        except Exception as e:
            print(f"⚠️  Error installing grammar: {e}")
    
    return installed_grammars

def build_parser_binaries():
    """Build Tree-sitter parser binaries"""
    print("🔨 Building parser binaries...")
    
    built_parsers = []
    parser_dirs = Path("parsers")
    
    if not parser_dirs.exists():
        print("⚠️  No parsers directory found")
        return built_parsers
    
    for lang_dir in parser_dirs.iterdir():
        if lang_dir.is_dir():
            lang_name = lang_dir.name
            try:
                # Build the parser
                build_cmd = ["tree-sitter", "build", str(lang_dir)]
                result = subprocess.run(build_cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    built_parsers.append(lang_name)
                    print(f"✅ Built {lang_name} parser")
                else:
                    print(f"⚠️  Failed to build {lang_name} parser: {result.stderr}")
                    
            except FileNotFoundError:
                print(f"⚠️  tree-sitter CLI not found for {lang_name}")
            except Exception as e:
                print(f"⚠️  Error building {lang_name} parser: {e}")
    
    return built_parsers

def create_test_repository():
    """Create a test repository for validation"""
    print("🧪 Creating test repository...")
    
    test_repo_path = Path("tests/test_repository")
    test_repo_path.mkdir(parents=True, exist_ok=True)
    
    # Create test Python file
    python_test = test_repo_path / "calculator.py"
    python_content = '''
"""
Calculator module for testing code analysis.
"""

class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        """Initialize the calculator."""
        self.history = []
    
    def add(self, a, b):
        """Add two numbers."""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a, b):
        """Subtract b from a."""
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a, b):
        """Multiply two numbers."""
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a, b):
        """Divide a by b."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result
    
    def get_history(self):
        """Get calculation history."""
        return self.history
    
    def clear_history(self):
        """Clear calculation history."""
        self.history.clear()


def simple_calculation():
    """Perform a simple calculation."""
    calc = Calculator()
    return calc.add(5, 3)


if __name__ == "__main__":
    calc = Calculator()
    print(f"5 + 3 = {calc.add(5, 3)}")
    print(f"10 - 4 = {calc.subtract(10, 4)}")
'''
    
    # Create test JavaScript file
    js_test = test_repo_path / "utils.js"
    js_content = '''
/**
 * Utility functions for testing
 */

class StringUtils {
    /**
     * Capitalize first letter of string
     * @param {string} str - Input string
     * @returns {string} Capitalized string
     */
    static capitalize(str) {
        if (!str || typeof str !== 'string') {
            throw new Error('Invalid input');
        }
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
    
    /**
     * Reverse string
     * @param {string} str - Input string
     * @returns {string} Reversed string
     */
    static reverse(str) {
        return str.split('').reverse().join('');
    }
}

/**
 * Math utilities
 */
class MathUtils {
    static fibonacci(n) {
        if (n <= 1) return n;
        return this.fibonacci(n - 1) + this.fibonacci(n - 2);
    }
    
    static factorial(n) {
        if (n <= 1) return 1;
        return n * this.factorial(n - 1);
    }
}

module.exports = { StringUtils, MathUtils };
'''
    
    try:
        python_test.write_text(python_content)
        js_test.write_text(js_content)
        print("✅ Test repository created")
        return True
    except Exception as e:
        print(f"❌ Failed to create test repository: {e}")
        return False

def validate_installation():
    """Validate the installation by running tests"""
    print("🔍 Validating installation...")
    
    try:
        # Test Tree-sitter import
        import tree_sitter
        print("✅ Tree-sitter import successful")
        
        # Test if we can create parsers
        try:
            python_parser = tree_sitter.Language('tree-sitter-python', 'python')
            js_parser = tree_sitter.Language('tree-sitter-javascript', 'javascript')
            print("✅ Parser creation successful")
        except Exception as e:
            print(f"⚠️  Parser creation failed: {e}")
            return False
        
        # Test file parsing
        test_file = Path("tests/test_repository/calculator.py")
        if test_file.exists():
            source_code = test_file.read_text()
            tree = python_parser.parse(source_code.encode())
            if tree and tree.root_node:
                print("✅ File parsing successful")
            else:
                print("⚠️  File parsing returned empty tree")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import validation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

def create_environment_config():
    """Create environment-specific configuration"""
    env_config = {
        "environment": "development",
        "debug_mode": True,
        "log_level": "DEBUG",
        "cache_enabled": True,
        "parallel_processing": True,
        "performance_monitoring": True
    }
    
    with open("config/environment.json", "w") as f:
        json.dump(env_config, f, indent=2)
    
    print("✅ Created environment configuration")

def setup_monitoring():
    """Set up monitoring and performance tracking"""
    print("📊 Setting up monitoring...")
    
    monitoring_config = {
        "metrics": {
            "enable_collection": True,
            "collection_interval": 60,
            "retention_days": 7
        },
        "alerts": {
            "enable_alerts": True,
            "memory_threshold_mb": 1024,
            "cpu_threshold_percent": 80,
            "error_rate_threshold": 0.05
        },
        "profiling": {
            "enable_profiling": False,
            "profile_threshold_ms": 100,
            "sample_rate": 0.1
        }
    }
    
    with open("config/monitoring.json", "w") as f:
        json.dump(monitoring_config, f, indent=2)
    
    print("✅ Created monitoring configuration")

def main():
    """Main setup function"""
    print("🚀 Setting up Codebase Genius Code Analyzer")
    print("=" * 60)
    
    # Create directory structure
    create_directories()
    
    # Set up environment
    print("\n📦 Setting up Python environment...")
    try:
        # Check if virtual environment exists
        if not os.path.exists("venv"):
            print("Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        
        # Activate virtual environment
        if os.name == 'nt':  # Windows
            python_executable = "venv\\Scripts\\python.exe"
            pip_executable = "venv\\Scripts\\pip.exe"
        else:  # Unix/Linux/macOS
            python_executable = "venv/bin/python"
            pip_executable = "venv/bin/pip"
        
        # Install dependencies
        print("Installing dependencies...")
        subprocess.run([
            pip_executable, "install", "-r", "requirements.txt"
        ], check=True)
        
        print("✅ Python environment setup completed")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to set up Python environment: {e}")
        return False
    
    # Install JAC runtime
    print("\n�� Setting up JAC runtime...")
    try:
        subprocess.run([
            python_executable, "-m", "pip", "install", "jaclang", "jac-cloud"
        ], check=True)
        print("✅ JAC runtime installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install JAC runtime: {e}")
        return False
    
    # Set up Tree-sitter
    print("\n🌳 Setting up Tree-sitter...")
    tree_sitter_result = setup_tree_sitter()
    
    if tree_sitter_result["status"] == "error":
        print("⚠️  Tree-sitter setup had issues, continuing anyway...")
    
    # Install Tree-sitter grammars (optional, for advanced users)
    if "--install-grammars" in sys.argv:
        print("\n📚 Installing Tree-sitter grammars...")
        installed_grammars = install_tree_sitter_grammars()
        built_parsers = build_parser_binaries()
        print(f"✅ Installed {len(installed_grammars)} grammars, built {len(built_parsers)} parsers")
    
    # Create test repository
    print("\n🧪 Creating test repository...")
    create_test_repository()
    
    # Create additional configuration
    print("\n⚙️  Creating configuration files...")
    create_environment_config()
    setup_monitoring()
    
    # Validate installation
    print("\n🔍 Validating installation...")
    if validate_installation():
        print("✅ Installation validation successful")
    else:
        print("⚠️  Installation validation had warnings")
    
    print("\n" + "=" * 60)
    print("🎉 Code Analyzer setup completed!")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("\n2. Start the service:")
    print("   jac serve main.jac")
    print("\n3. Run tests:")
    print("   python tests/test_analysis.py")
    print("\n4. Test with sample repository:")
    print("   jac run main.jac walker:test_code_analysis")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
