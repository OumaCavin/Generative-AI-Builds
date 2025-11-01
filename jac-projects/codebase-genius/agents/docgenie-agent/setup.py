#!/usr/bin/env python3
"""
DocGenie Agent Setup Script
Automated installation and configuration for the documentation generation agent
"""

import os
import sys
import subprocess
import json
import shutil
import pathlib
from typing import Dict, List, Any

class DocGenieSetup:
    def __init__(self):
        self.project_root = pathlib.Path(__file__).parent.absolute()
        self.config_file = self.project_root / "config" / "config.json"
        self.requirements_file = self.project_root / "requirements.txt"
        
    def check_prerequisites(self) -> bool:
        """Check if prerequisites are installed"""
        print("🔍 Checking prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher is required")
            return False
        
        print(f"✅ Python version: {sys.version}")
        
        # Check pip
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         check=True, capture_output=True)
            print("✅ pip is available")
        except subprocess.CalledProcessError:
            print("❌ pip is not available")
            return False
        
        # Check Node.js (for potential future JS processing)
        try:
            subprocess.run(["node", "--version"], 
                         check=True, capture_output=True)
            print("✅ Node.js is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Node.js not found (optional for this agent)")
        
        return True
    
    def install_dependencies(self) -> bool:
        """Install required Python packages"""
        print("📦 Installing dependencies...")
        
        try:
            # Upgrade pip first
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ], check=True, capture_output=True)
            
            # Install requirements
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", 
                str(self.requirements_file)
            ], check=True, capture_output=True)
            
            print("✅ Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def setup_directories(self) -> bool:
        """Create required directories"""
        print("📁 Setting up directories...")
        
        directories = [
            "templates",
            "outputs", 
            "diagrams",
            "cache",
            "logs"
        ]
        
        try:
            for directory in directories:
                dir_path = self.project_root / directory
                dir_path.mkdir(exist_ok=True)
                print(f"✅ Created directory: {directory}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create directories: {e}")
            return False
    
    def create_template_files(self) -> bool:
        """Create default documentation templates"""
        print("📝 Creating template files...")
        
        templates = {
            "overview_template.md": """# {{ repository_name }} - Codebase Analysis

## Overview
{{ overview_description }}

**Repository**: {{ repository_url }}
**Generated**: {{ generation_date }}
**Analyzer**: {{ analyzer_version }}

## Quick Statistics
- **Total Files**: {{ total_files }}
- **Total Entities**: {{ total_entities }}
- **Total Relationships**: {{ total_relationships }}
- **Average Complexity**: {{ avg_complexity }}

## Architecture Overview
{{ architecture_summary }}

## High-Level Structure
{{ structure_summary }}

## Next Steps
- Review the [API Reference](./api_reference.md) for detailed entity documentation
- Check the [Architecture Analysis](./architecture.md) for system design insights
- Examine the [Call Graph](./call_graph.png) for execution flow
""",
            
            "api_template.md": """# API Reference

## Classes
{% for class in classes %}
### {{ class.name }}
**File**: `{{ class.file_path }}` (lines {{ class.start_line }}-{{ class.end_line }})
**Complexity**: {{ class.complexity }}

{{ class.documentation if class.documentation else "*No documentation available.*" }}

#### Methods
{% for method in class.methods %}
- **{{ method.name }}** ({{ method.type }}) - Complexity: {{ method.complexity }}
  - Line: {{ method.start_line }}-{{ method.end_line }}
{% endfor %}

#### Dependencies
{% if class.dependencies %}
{% for dep in class.dependencies %}
- {{ dep }}
{% endfor %}
{% else %}
- No external dependencies detected
{% endif %}

#### Usage Example
```python
# Example usage of {{ class.name }}
{{ class.example_code if class.example_code else "# Example code not available" }}
```

---
{% endfor %}

## Functions
{% for func in functions %}
### {{ func.name }}
**File**: `{{ func.file_path }}` (lines {{ func.start_line }}-{{ func.end_line }})
**Complexity**: {{ func.complexity }}

{{ func.documentation if func.documentation else "*No documentation available.*" }}

#### Parameters
{% if func.parameters %}
{% for param in func.parameters %}
- **{{ param.name }}** ({{ param.type }}) - {{ param.description }}
{% endfor %}
{% else %}
- No parameters documented
{% endif %}

#### Dependencies
{% if func.dependencies %}
{% for dep in func.dependencies %}
- {{ dep }}
{% endfor %}
{% else %}
- No external dependencies detected
{% endif %}

#### Usage Example
```{{ func.language or 'python' }}
{{ func.example_code if func.example_code else "# Example code not available" }}
```

---
{% endfor %}

## Modules
{% for module in modules %}
### {{ module.name }}
**File**: `{{ module.file_path }}`

{{ module.documentation if module.documentation else "*No documentation available.*" }}

#### Exported Entities
{% for entity in module.exports %}
- **{{ entity.name }}** ({{ entity.type }}) - Line {{ entity.line }}
{% endfor %}

---
{% endfor %}
""",
            
            "architecture_template.md": """# Architecture Analysis

## System Components
{{ components_summary }}

## Dependency Analysis
### Dependency Graph Statistics
- **Total Import Relationships**: {{ total_imports }}
- **Total Call Relationships**: {{ total_calls }}
- **Average Dependency Depth**: {{ avg_depth }}
- **Most Imported Module**: {{ top_imported_module }}

### High-Impact Components
These components have the highest number of dependencies:

{% for component in high_impact_components %}
- **{{ component.name }}** ({{ component.type }})
  - Dependencies: {{ component.dep_count }}
  - Dependents: {{ component.dep_of_count }}
  - File: `{{ component.file_path }}`
{% endfor %}

## Complexity Analysis
{{ complexity_summary }}

### Complexity Hotspots
These entities exceed the complexity threshold:

{% for hotspot in complexity_hotspots %}
- **{{ hotspot.name }}** ({{ hotspot.type }})
  - Complexity: {{ hotspot.complexity }}
  - File: `{{ hotspot.file_path }}` (line {{ hotspot.line }})
  - **Recommendation**: {{ hotspot.recommendation }}
{% endfor %}

## Design Patterns Detected
{{ patterns_summary }}

## Code Quality Metrics
- **Maintainability Index**: {{ maintainability_index }}
- **Technical Debt Ratio**: {{ debt_ratio }}
- **Code Coverage**: {{ code_coverage }}

## Recommendations
{% for recommendation in recommendations %}
- {{ recommendation }}
{% endfor %}
"""
        }
        
        try:
            template_dir = self.project_root / "templates"
            for template_name, template_content in templates.items():
                template_path = template_dir / template_name
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(template_content)
                print(f"✅ Created template: {template_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create templates: {e}")
            return False
    
    def validate_installation(self) -> bool:
        """Validate the installation"""
        print("🔍 Validating installation...")
        
        try:
            # Test JAC language import
            import jac_lang
            print("✅ JAC language runtime available")
            
            # Test template engine
            import jinja2
            print("✅ Jinja2 template engine available")
            
            # Test diagram generation
            import graphviz
            print("✅ Graphviz diagram generation available")
            
            # Test configuration
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                assert 'agent_info' in config
                assert 'documentation_settings' in config
                print("✅ Configuration file valid")
            
            return True
            
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return False
    
    def run_tests(self) -> bool:
        """Run basic tests"""
        print("🧪 Running tests...")
        
        try:
            # Run pytest if available
            result = subprocess.run([
                sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ All tests passed")
                return True
            else:
                print(f"⚠️  Some tests failed: {result.stdout}")
                return False
                
        except Exception as e:
            print(f"⚠️  Could not run tests: {e}")
            return False
    
    def print_next_steps(self):
        """Print next steps for the user"""
        print("\n" + "="*60)
        print("🎉 DocGenie Agent setup completed successfully!")
        print("="*60)
        print("\n📚 Quick Start:")
        print("1. Run the agent: python main.jac")
        print("2. Test with sample data: python tests/test_documentation.py")
        print("3. Generate sample docs: ./deploy.sh demo")
        print("4. Check configuration: cat config/config.json")
        print("\n🔗 Integration:")
        print("- Input: CCG data from Code Analyzer Agent")
        print("- Output: Markdown and HTML documentation")
        print("- API: POST /generate for documentation generation")
        print("\n📁 Key Files:")
        print(f"- Main implementation: {self.project_root}/main.jac")
        print(f"- Configuration: {self.config_file}")
        print(f"- Templates: {self.project_root}/templates/")
        print(f"- Outputs: {self.project_root}/outputs/")
        print("\n🚀 Ready to generate documentation!")
    
    def setup(self) -> bool:
        """Main setup process"""
        print("🚀 DocGenie Agent Setup Starting...")
        print(f"Project root: {self.project_root}")
        
        steps = [
            ("Checking prerequisites", self.check_prerequisites),
            ("Installing dependencies", self.install_dependencies),
            ("Setting up directories", self.setup_directories),
            ("Creating templates", self.create_template_files),
            ("Validating installation", self.validate_installation),
            ("Running tests", self.run_tests)
        ]
        
        for step_name, step_func in steps:
            print(f"\n--- {step_name} ---")
            if not step_func():
                print(f"❌ Setup failed at: {step_name}")
                return False
        
        self.print_next_steps()
        return True

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--validate-only":
        # Only run validation
        setup = DocGenieSetup()
        return setup.validate_installation()
    
    # Run full setup
    setup = DocGenieSetup()
    success = setup.setup()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
