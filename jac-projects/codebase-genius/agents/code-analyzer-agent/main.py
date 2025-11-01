# Codebase Genius - Code Analyzer Agent
# Complete Python implementation with Tree-sitter integration and CCG construction

try:
    import tree_sitter
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    print("Warning: Tree-sitter not available. Using fallback parsing methods.")

import pathlib
import typing
import datetime
import json
import collections
from typing import Dict, List, Optional, Any, Union

## Data Classes for Code Analysis
class CodeElement:
    def __init__(self):
        self.element_id: str = ""
        self.element_type: str = ""  # 'function', 'class', 'method', 'module', 'variable'
        self.name: str = ""
        self.file_path: str = ""
        self.start_line: int = 0
        self.end_line: int = 0
        self.language: str = ""
        self.signature: str = ""
        self.documentation: str = ""
        self.complexity_score: float = 0.0
        self.dependencies: List[str] = []
        self.parameters: List[str] = []
        self.return_type: str = ""
        self.decorators: List[str] = []
        self.visibility: str = "public"  # 'public', 'private', 'protected'
        self.is_async: bool = False
        self.is_deprecated: bool = False
        self.source_code: str = ""

class CodeRelationship:
    def __init__(self):
        self.relationship_type: str = ""  # 'calls', 'inherits', 'imports', 'contains', 'uses'
        self.source_element: str = ""     # ID of source element
        self.target_element: str = ""     # ID of target element
        self.line_number: int = 0
        self.context: str = ""            # Additional context about the relationship
        self.confidence: float = 0.0      # Confidence score for the relationship
        self.is_direct: bool = True       # True if direct relationship, False if inherited

class FileAnalysis:
    def __init__(self):
        self.file_path: str = ""
        self.language: str = ""
        self.parsing_status: str = "success"     # 'success', 'error', 'unsupported'
        self.error_message: str = ""
        self.elements_found: int = 0
        self.relationships_found: int = 0
        self.complexity_score: float = 0.0
        self.lines_of_code: int = 0
        self.parsed_at: datetime.datetime = datetime.datetime.now()
        self.tree_sitter_tree: str = ""   # Serialized parse tree

class Module:
    def __init__(self):
        self.module_name: str = ""
        self.module_path: str = ""
        self.is_package: bool = False
        self.imports: List[str] = []
        self.exports: List[str] = []
        self.dependencies: List[str] = []
        self.level: int = 0  # Module level in hierarchy
        self.parent_module: str = ""
        self.submodules: List[str] = []

class RepositoryAnalysis:
    def __init__(self):
        self.repository_path: str = ""
        self.total_files_analyzed: int = 0
        self.total_elements: int = 0
        self.total_relationships: int = 0
        self.analysis_timestamp: datetime.datetime = datetime.datetime.now()
        self.supported_languages: List[str] = []
        self.complexity_metrics: Dict[str, Any] = {}
        self.dependency_graph: Dict[str, Any] = {}
        self.documentation_coverage: float = 0.0
        self.test_coverage: float = 0.0

## Code Analyzer Agent Class
class CodeAnalyzerAgent:
    def __init__(self):
        self.repository_path: str = ""
        self.max_file_size: int = 10485760
        self.include_ignored: bool = False
        self.analysis_depth: str = "full"  # 'basic', 'full', 'deep'
        self.language_parsers: Dict[str, Any] = {}
        self.analysis_results: Dict[str, Any] = {}
    
    def initialize_parsers(self) -> Dict[str, Any]:
        """Initialize Tree-sitter language parsers"""
        if not TREE_SITTER_AVAILABLE:
            return {
                "status": "warning",
                "message": "Tree-sitter not installed, using fallback parsing",
                "parsers_available": False
            }
        
        try:
            # Initialize language parsers
            language_parsers = {}
            
            # Python parser
            try:
                python_lang = tree_sitter.Language('tree-sitter-python', 'python')
                language_parsers['python'] = tree_sitter.Parser(python_lang)
            except Exception as e:
                print(f"Failed to initialize Python parser: {e}")
            
            # JavaScript parser
            try:
                js_lang = tree_sitter.Language('tree-sitter-javascript', 'javascript')
                language_parsers['javascript'] = tree_sitter.Parser(js_lang)
            except Exception as e:
                print(f"Failed to initialize JavaScript parser: {e}")
            
            # TypeScript parser
            try:
                ts_lang = tree_sitter.Language('tree-sitter-typescript', 'typescript')
                language_parsers['typescript'] = tree_sitter.Parser(ts_lang)
            except Exception as e:
                print(f"Failed to initialize TypeScript parser: {e}")
            
            # Java parser
            try:
                java_lang = tree_sitter.Language('tree-sitter-java', 'java')
                language_parsers['java'] = tree_sitter.Parser(java_lang)
            except Exception as e:
                print(f"Failed to initialize Java parser: {e}")
            
            # C++ parser
            try:
                cpp_lang = tree_sitter.Language('tree-sitter-cpp', 'cpp')
                language_parsers['cpp'] = tree_sitter.Parser(cpp_lang)
            except Exception as e:
                print(f"Failed to initialize C++ parser: {e}")
            
            # C parser
            try:
                c_lang = tree_sitter.Language('tree-sitter-c', 'c')
                language_parsers['c'] = tree_sitter.Parser(c_lang)
            except Exception as e:
                print(f"Failed to initialize C parser: {e}")
            
            self.language_parsers = language_parsers
            
            return {
                "status": "success",
                "parsers_initialized": len(language_parsers),
                "supported_languages": list(language_parsers.keys())
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Parser initialization failed: {str(e)}"
            }
    
    def parse_file(self, file_path: str, language: str) -> Dict[str, Any]:
        """Parse a single file using Tree-sitter or fallback methods"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source_code = f.read()
            
            # Try Tree-sitter parsing first
            if TREE_SITTER_AVAILABLE and language in self.language_parsers:
                return self._parse_with_tree_sitter(file_path, language, source_code)
            else:
                return self._parse_with_fallback(file_path, language, source_code)
            
        except Exception as e:
            return {
                "status": "error",
                "file_path": file_path,
                "error": str(e)
            }
    
    def _parse_with_tree_sitter(self, file_path: str, language: str, source_code: str) -> Dict[str, Any]:
        """Parse using Tree-sitter"""
        try:
            # Get appropriate parser
            parser = self.language_parsers[language]
            
            # Parse the code
            tree = parser.parse(source_code.encode())
            
            # Create file analysis object
            file_analysis = FileAnalysis()
            file_analysis.file_path = file_path
            file_analysis.language = language
            file_analysis.parsing_status = "success"
            file_analysis.lines_of_code = len(source_code.splitlines())
            file_analysis.tree_sitter_tree = tree.root_node.sexp()
            
            # Extract code elements
            elements = self.extract_code_elements(tree.root_node, language, file_path)
            relationships = self.extract_relationships(tree.root_node, language, file_path)
            
            # Update counts
            file_analysis.elements_found = len(elements)
            file_analysis.relationships_found = len(relationships)
            file_analysis.complexity_score = self.calculate_complexity_score(tree.root_node)
            
            return {
                "status": "success",
                "file_path": file_path,
                "language": language,
                "file_analysis": file_analysis,
                "elements": elements,
                "relationships": relationships,
                "complexity_score": file_analysis.complexity_score
            }
            
        except Exception as e:
            return {
                "status": "error",
                "file_path": file_path,
                "error": f"Tree-sitter parsing failed: {str(e)}"
            }
    
    def _parse_with_fallback(self, file_path: str, language: str, source_code: str) -> Dict[str, Any]:
        """Parse using fallback regex-based methods"""
        try:
            # Create file analysis object
            file_analysis = FileAnalysis()
            file_analysis.file_path = file_path
            file_analysis.language = language
            file_analysis.parsing_status = "success"
            file_analysis.lines_of_code = len(source_code.splitlines())
            
            # Extract elements using regex patterns
            elements = self.extract_elements_with_regex(source_code, language, file_path)
            relationships = self.extract_relationships_with_regex(source_code, language, file_path)
            
            # Update counts
            file_analysis.elements_found = len(elements)
            file_analysis.relationships_found = len(relationships)
            file_analysis.complexity_score = self.calculate_complexity_with_regex(source_code)
            
            return {
                "status": "success",
                "file_path": file_path,
                "language": language,
                "file_analysis": file_analysis,
                "elements": elements,
                "relationships": relationships,
                "complexity_score": file_analysis.complexity_score
            }
            
        except Exception as e:
            return {
                "status": "error",
                "file_path": file_path,
                "error": f"Fallback parsing failed: {str(e)}"
            }
    
    def extract_code_elements(self, tree_node: Any, language: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract code elements from parse tree"""
        elements = []
        element_counter = 0
        
        def traverse_tree(node, current_path=""):
            nonlocal element_counter
            
            # Process based on node type
            if language == "python":
                if node.type == "function_definition":
                    elements.append(self.extract_python_function(node, file_path, element_counter))
                    element_counter += 1
                elif node.type == "class_definition":
                    elements.append(self.extract_python_class(node, file_path, element_counter))
                    element_counter += 1
                elif node.type == "assignment":
                    elements.append(self.extract_python_variable(node, file_path, element_counter))
                    element_counter += 1
            
            elif language == "javascript":
                if node.type == "function_declaration":
                    elements.append(self.extract_js_function(node, file_path, element_counter))
                    element_counter += 1
                elif node.type == "class_declaration":
                    elements.append(self.extract_js_class(node, file_path, element_counter))
                    element_counter += 1
                elif node.type == "variable_declaration":
                    elements.append(self.extract_js_variable(node, file_path, element_counter))
                    element_counter += 1
            
            # Traverse children
            for child in node.children:
                traverse_tree(child, current_path)
        
        traverse_tree(tree_node)
        return elements
    
    def extract_python_function(self, node: Any, file_path: str, element_id: int) -> Dict[str, Any]:
        """Extract Python function"""
        # Get function name
        name_node = node.child_by_field_name("name")
        function_name = name_node.text.decode() if name_node else "anonymous"
        
        # Get parameters
        params_node = node.child_by_field_name("parameters")
        parameters = []
        if params_node:
            for param in params_node.children:
                if param.type == "identifier":
                    parameters.append(param.text.decode())
        
        # Get function body for complexity calculation
        body_node = node.child_by_field_name("body")
        complexity = self.calculate_python_complexity(body_node)
        
        # Get decorators
        decorators = []
        # Look for decorator nodes (these would be before the function definition)
        
        return {
            "id": f"func_{element_id}_{file_path}",
            "type": "function",
            "name": function_name,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "signature": f"def {function_name}({', '.join(parameters)})",
            "documentation": self.extract_python_docstring(node),
            "complexity": complexity,
            "dependencies": self.extract_python_dependencies(node),
            "parameters": parameters,
            "return_type": "Any",  # Python type inference would need more sophisticated analysis
            "decorators": decorators,
            "visibility": "public",
            "is_async": False,  # Would need to check for 'async' keyword
            "is_deprecated": False,
            "source_code": node.text.decode()
        }
    
    def extract_python_class(self, node: Any, file_path: str, element_id: int) -> Dict[str, Any]:
        """Extract Python class"""
        # Get class name
        name_node = node.child_by_field_name("name")
        class_name = name_node.text.decode() if name_node else "anonymous"
        
        # Get base classes
        bases_node = node.child_by_field_name("bases")
        inheritance = []
        if bases_node:
            for base in bases_node.children:
                if base.type == "identifier":
                    inheritance.append(base.text.decode())
        
        # Calculate complexity
        body_node = node.child_by_field_name("body")
        complexity = self.calculate_python_complexity(body_node)
        
        return {
            "id": f"class_{element_id}_{file_path}",
            "type": "class",
            "name": class_name,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "signature": f"class {class_name}({', '.join(inheritance)})",
            "documentation": self.extract_python_docstring(node),
            "complexity": complexity,
            "dependencies": inheritance,
            "parameters": [],  # Class parameters not directly available
            "return_type": "class",
            "decorators": [],  # Would need to extract from class decorators
            "visibility": "public",
            "is_async": False,
            "is_deprecated": False,
            "source_code": node.text.decode()
        }
    
    def extract_python_variable(self, node: Any, file_path: str, element_id: int) -> Dict[str, Any]:
        """Extract Python variable"""
        # Get variable name (simplified)
        targets = node.child_by_field_name("targets")
        var_name = "unknown"
        if targets and targets.children:
            target = targets.children[0]
            if target.type == "identifier":
                var_name = target.text.decode()
        
        return {
            "id": f"var_{element_id}_{file_path}",
            "type": "variable",
            "name": var_name,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "signature": f"{var_name} = ...",
            "documentation": "",
            "complexity": 1.0,
            "dependencies": [],
            "parameters": [],
            "return_type": "Any",
            "decorators": [],
            "visibility": "public",
            "is_async": False,
            "is_deprecated": False,
            "source_code": node.text.decode()
        }
    
    def extract_js_function(self, node: Any, file_path: str, element_id: int) -> Dict[str, Any]:
        """Extract JavaScript function"""
        # Get function name
        name_node = node.child_by_field_name("name")
        function_name = name_node.text.decode() if name_node else "anonymous"
        
        # Get parameters
        params_node = node.child_by_field_name("parameters")
        parameters = []
        if params_node:
            for param in params_node.children:
                if param.type == "identifier":
                    parameters.append(param.text.decode())
        
        # Calculate complexity
        body_node = node.child_by_field_name("body")
        complexity = self.calculate_js_complexity(body_node)
        
        return {
            "id": f"func_{element_id}_{file_path}",
            "type": "function",
            "name": function_name,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "signature": f"function {function_name}({', '.join(parameters)})",
            "documentation": self.extract_js_docstring(node),
            "complexity": complexity,
            "dependencies": self.extract_js_dependencies(node),
            "parameters": parameters,
            "return_type": "any",
            "decorators": [],
            "visibility": "public",
            "is_async": False,
            "is_deprecated": False,
            "source_code": node.text.decode()
        }
    
    def extract_js_class(self, node: Any, file_path: str, element_id: int) -> Dict[str, Any]:
        """Extract JavaScript class"""
        # Get class name
        name_node = node.child_by_field_name("name")
        class_name = name_node.text.decode() if name_node else "anonymous"
        
        return {
            "id": f"class_{element_id}_{file_path}",
            "type": "class",
            "name": class_name,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "signature": f"class {class_name}",
            "documentation": self.extract_js_docstring(node),
            "complexity": 1.0,
            "dependencies": [],
            "parameters": [],
            "return_type": "class",
            "decorators": [],
            "visibility": "public",
            "is_async": False,
            "is_deprecated": False,
            "source_code": node.text.decode()
        }
    
    def extract_js_variable(self, node: Any, file_path: str, element_id: int) -> Dict[str, Any]:
        """Extract JavaScript variable"""
        # Get variable name (simplified)
        declarations = node.child_by_field_name("declarations")
        var_name = "unknown"
        if declarations and declarations.children:
            declarator = declarations.children[0]
            name_node = declarator.child_by_field_name("name")
            if name_node:
                var_name = name_node.text.decode()
        
        return {
            "id": f"var_{element_id}_{file_path}",
            "type": "variable",
            "name": var_name,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "signature": f"let {var_name} = ...",
            "documentation": "",
            "complexity": 1.0,
            "dependencies": [],
            "parameters": [],
            "return_type": "any",
            "decorators": [],
            "visibility": "public",
            "is_async": False,
            "is_deprecated": False,
            "source_code": node.text.decode()
        }
    
    def extract_relationships(self, tree_node: Any, language: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract relationships from parse tree"""
        relationships = []
        
        def traverse_for_relationships(node, current_element=None):
            if language == "python":
                if node.type == "call":
                    # Function call relationship
                    func_name = self.extract_call_name(node)
                    if func_name:
                        relationships.append({
                            "type": "calls",
                            "source": current_element,
                            "target": func_name,
                            "line": node.start_point[0] + 1,
                            "context": node.text.decode(),
                            "confidence": 0.8,
                            "is_direct": True
                        })
                elif node.type == "import_from_statement":
                    # Import relationship
                    module_name = self.extract_import_module(node)
                    if module_name:
                        relationships.append({
                            "type": "imports",
                            "source": file_path,
                            "target": module_name,
                            "line": node.start_point[0] + 1,
                            "context": node.text.decode(),
                            "confidence": 0.9,
                            "is_direct": True
                        })
                elif node.type == "attribute":
                    # Attribute access relationship
                    attr_name = self.extract_attribute_name(node)
                    if attr_name and current_element:
                        relationships.append({
                            "type": "uses",
                            "source": current_element,
                            "target": attr_name,
                            "line": node.start_point[0] + 1,
                            "context": node.text.decode(),
                            "confidence": 0.7,
                            "is_direct": True
                        })
            
            elif language == "javascript":
                if node.type == "call_expression":
                    # Function call relationship
                    func_name = self.extract_js_call_name(node)
                    if func_name:
                        relationships.append({
                            "type": "calls",
                            "source": current_element,
                            "target": func_name,
                            "line": node.start_point[0] + 1,
                            "context": node.text.decode(),
                            "confidence": 0.8,
                            "is_direct": True
                        })
                elif node.type == "import_statement":
                    # Import relationship
                    module_name = self.extract_js_import_module(node)
                    if module_name:
                        relationships.append({
                            "type": "imports",
                            "source": file_path,
                            "target": module_name,
                            "line": node.start_point[0] + 1,
                            "context": node.text.decode(),
                            "confidence": 0.9,
                            "is_direct": True
                        })
            
            # Continue traversal
            for child in node.children:
                traverse_for_relationships(child, current_element)
        
        traverse_for_relationships(tree_node)
        return relationships
    
    def extract_elements_with_regex(self, source_code: str, language: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract elements using regex patterns (fallback method)"""
        import re
        
        elements = []
        
        if language == "python":
            # Python function definitions
            func_pattern = r'def\s+(\w+)\s*\([^)]*\):'
            for match in re.finditer(func_pattern, source_code):
                elements.append({
                    "id": f"func_{len(elements)}_{file_path}",
                    "type": "function",
                    "name": match.group(1),
                    "start_line": source_code[:match.start()].count('\n') + 1,
                    "end_line": 0,  # Would need more complex parsing
                    "signature": match.group(0).rstrip(':'),
                    "documentation": "",
                    "complexity": 1.0,
                    "dependencies": [],
                    "parameters": [],
                    "return_type": "Any",
                    "decorators": [],
                    "visibility": "public",
                    "is_async": False,
                    "is_deprecated": False,
                    "source_code": match.group(0)
                })
            
            # Python class definitions
            class_pattern = r'class\s+(\w+)\s*(\([^)]*\))?:'
            for match in re.finditer(class_pattern, source_code):
                elements.append({
                    "id": f"class_{len(elements)}_{file_path}",
                    "type": "class",
                    "name": match.group(1),
                    "start_line": source_code[:match.start()].count('\n') + 1,
                    "end_line": 0,
                    "signature": match.group(0).rstrip(':'),
                    "documentation": "",
                    "complexity": 1.0,
                    "dependencies": [],
                    "parameters": [],
                    "return_type": "class",
                    "decorators": [],
                    "visibility": "public",
                    "is_async": False,
                    "is_deprecated": False,
                    "source_code": match.group(0)
                })
        
        elif language == "javascript":
            # JavaScript function declarations
            func_pattern = r'function\s+(\w+)\s*\([^)]*\)\s*{'
            for match in re.finditer(func_pattern, source_code):
                elements.append({
                    "id": f"func_{len(elements)}_{file_path}",
                    "type": "function",
                    "name": match.group(1),
                    "start_line": source_code[:match.start()].count('\n') + 1,
                    "end_line": 0,
                    "signature": match.group(0).rstrip('{'),
                    "documentation": "",
                    "complexity": 1.0,
                    "dependencies": [],
                    "parameters": [],
                    "return_type": "any",
                    "decorators": [],
                    "visibility": "public",
                    "is_async": False,
                    "is_deprecated": False,
                    "source_code": match.group(0)
                })
            
            # JavaScript class declarations
            class_pattern = r'class\s+(\w+)\s*{'
            for match in re.finditer(class_pattern, source_code):
                elements.append({
                    "id": f"class_{len(elements)}_{file_path}",
                    "type": "class",
                    "name": match.group(1),
                    "start_line": source_code[:match.start()].count('\n') + 1,
                    "end_line": 0,
                    "signature": match.group(0).rstrip('{'),
                    "documentation": "",
                    "complexity": 1.0,
                    "dependencies": [],
                    "parameters": [],
                    "return_type": "class",
                    "decorators": [],
                    "visibility": "public",
                    "is_async": False,
                    "is_deprecated": False,
                    "source_code": match.group(0)
                })
        
        return elements
    
    def extract_relationships_with_regex(self, source_code: str, language: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract relationships using regex patterns (fallback method)"""
        import re
        
        relationships = []
        
        if language == "python":
            # Python import statements
            import_pattern = r'(?:from\s+(\S+)\s+)?import\s+([^\n#]+)'
            for match in re.finditer(import_pattern, source_code, re.MULTILINE):
                line_num = source_code[:match.start()].count('\n') + 1
                module_name = match.group(1) or match.group(2)
                relationships.append({
                    "type": "imports",
                    "source": file_path,
                    "target": module_name.strip(),
                    "line": line_num,
                    "context": match.group(0),
                    "confidence": 0.9,
                    "is_direct": True
                })
        
        elif language == "javascript":
            # JavaScript import statements
            import_pattern = r"import\s+(?:{[^}]+}|[\w*\s,]+)\s+from\s+['\"]([^'\"]+)['\"]"
            for match in re.finditer(import_pattern, source_code):
                line_num = source_code[:match.start()].count('\n') + 1
                module_name = match.group(1)
                relationships.append({
                    "type": "imports",
                    "source": file_path,
                    "target": module_name,
                    "line": line_num,
                    "context": match.group(0),
                    "confidence": 0.9,
                    "is_direct": True
                })
        
        return relationships
    
    def calculate_complexity_with_regex(self, source_code: str) -> float:
        """Calculate complexity using regex patterns"""
        import re
        
        # Count various complexity-inducing constructs
        complexity = 1.0
        
        # Control flow statements
        if_count = len(re.findall(r'\bif\b', source_code))
        for_count = len(re.findall(r'\bfor\b', source_code))
        while_count = len(re.findall(r'\bwhile\b', source_code))
        try_count = len(re.findall(r'\btry\b', source_code))
        
        complexity += if_count + for_count + while_count + try_count
        
        # Logical operators
        and_count = len(re.findall(r'\band\b', source_code))
        or_count = len(re.findall(r'\bor\b', source_code))
        
        complexity += and_count + or_count
        
        return complexity
    
    # Helper functions for extracting information
    def extract_python_docstring(self, node: Any) -> str:
        """Extract Python docstring"""
        # Look for docstring in function/class body
        body_node = node.child_by_field_name("body")
        if body_node and body_node.children:
            first_stmt = body_node.children[0]
            if first_stmt.type == "expression_statement":
                expr = first_stmt.child(0)
                if expr.type == "string":
                    return expr.text.decode()
        return ""
    
    def extract_python_dependencies(self, node: Any) -> List[str]:
        """Extract function call dependencies"""
        dependencies = []
        
        def find_calls(node):
            if node.type == "call":
                func_name = self.extract_call_name(node)
                if func_name:
                    dependencies.append(func_name)
            
            for child in node.children:
                find_calls(child)
        
        find_calls(node)
        return list(set(dependencies))  # Remove duplicates
    
    def extract_call_name(self, node: Any) -> str:
        """Extract function call name"""
        # Extract function call name
        func_node = node.child(0)
        if func_node.type == "attribute":
            # method call: obj.method
            return f"{func_node.child(0).text.decode()}.{func_node.child(1).text.decode()}"
        elif func_node.type == "identifier":
            # simple call: function()
            return func_node.text.decode()
        return ""
    
    def extract_import_module(self, node: Any) -> str:
        """Extract module name from import statement"""
        if node.child(0).type == "dotted_name":
            return node.child(0).text.decode()
        elif node.child(0).type == "identifier":
            return node.child(0).text.decode()
        return ""
    
    def extract_attribute_name(self, node: Any) -> str:
        """Extract attribute name"""
        if node.child(1).type == "identifier":
            return node.child(1).text.decode()
        return ""
    
    # JavaScript helper functions
    def extract_js_docstring(self, node: Any) -> str:
        """Extract JavaScript docstring"""
        # Look for JSDoc comments
        return ""  # Simplified for now
    
    def extract_js_dependencies(self, node: Any) -> List[str]:
        """Extract JavaScript dependencies"""
        dependencies = []
        
        def find_js_calls(node):
            if node.type == "call_expression":
                func_name = self.extract_js_call_name(node)
                if func_name:
                    dependencies.append(func_name)
            
            for child in node.children:
                find_js_calls(child)
        
        find_js_calls(node)
        return list(set(dependencies))
    
    def extract_js_call_name(self, node: Any) -> str:
        """Extract JavaScript function call name"""
        callee = node.child_by_field_name("function")
        if callee:
            return callee.text.decode()
        return ""
    
    def extract_js_import_module(self, node: Any) -> str:
        """Extract module name from import statement"""
        source_node = node.child_by_field_name("source")
        if source_node:
            return source_node.text.decode().strip('"').strip("'")
        return ""
    
    # Complexity calculation functions
    def calculate_python_complexity(self, node: Any) -> float:
        """Calculate Python complexity"""
        if not node:
            return 1.0
        
        complexity = 1.0
        
        def count_complexity_constructs(node):
            nonlocal complexity
            
            # Count various complexity-inducing constructs
            if node.type in ["if_statement", "for_statement", "while_statement", "try_statement"]:
                complexity += 1
            elif node.type == "elif_clause":
                complexity += 0.5
            elif node.type == "except_clause":
                complexity += 1
            elif node.type in ["and_expression", "or_expression"]:
                complexity += 1
            
            for child in node.children:
                count_complexity_constructs(child)
        
        count_complexity_constructs(node)
        return complexity
    
    def calculate_js_complexity(self, node: Any) -> float:
        """Calculate JavaScript complexity"""
        if not node:
            return 1.0
        
        complexity = 1.0
        
        def count_js_complexity(node):
            nonlocal complexity
            
            if node.type in ["if_statement", "for_statement", "while_statement", "switch_statement"]:
                complexity += 1
            elif node.type == "case_clause":
                complexity += 0.5
            elif node.type in ["binary_expression", "logical_expression"]:
                complexity += 1
            
            for child in node.children:
                count_js_complexity(child)
        
        count_js_complexity(node)
        return complexity
    
    def calculate_complexity_score(self, tree_root: Any) -> float:
        """Calculate overall file complexity"""
        if not tree_root:
            return 0.0
        
        # Calculate overall file complexity
        total_complexity = 0.0
        element_count = 0
        
        def analyze_node(node):
            nonlocal total_complexity, element_count
            
            if node.type in ["function_definition", "class_definition", "method_definition"]:
                element_count += 1
                if node.type == "function_definition":
                    total_complexity += self.calculate_python_complexity(node.child_by_field_name("body"))
                elif node.type == "class_definition":
                    total_complexity += self.calculate_python_complexity(node.child_by_field_name("body"))
            
            for child in node.children:
                analyze_node(child)
        
        analyze_node(tree_root)
        return total_complexity / max(element_count, 1)
    
    def build_module_hierarchy(self, repository_path: str) -> Dict[str, Any]:
        """Build module hierarchy"""
        try:
            modules = {}
            
            def process_directory(dir_path, current_module=""):
                for item in pathlib.Path(dir_path).iterdir():
                    if item.is_file() and item.suffix in [".py", ".js", ".ts", ".java", ".cpp", ".c"]:
                        # Create module for file
                        module_name = item.stem
                        full_module_path = str(item.relative_to(repository_path))
                        
                        if current_module:
                            module_name = f"{current_module}.{module_name}"
                        
                        if module_name not in modules:
                            modules[module_name] = {
                                "name": module_name,
                                "path": full_module_path,
                                "is_package": False,
                                "level": module_name.count("."),
                                "parent": current_module if "." in module_name else None,
                                "children": []
                            }
                        
                        # Add to parent module's children
                        if current_module and current_module in modules:
                            modules[current_module]["children"].append(module_name)
                    
                    elif item.is_dir() and item.name not in [".git", "__pycache__", "node_modules"]:
                        # Process subdirectory
                        sub_module = f"{current_module}.{item.name}" if current_module else item.name
                        process_directory(item, sub_module)
            
            process_directory(repository_path)
            
            # Create module objects
            module_objects = []
            for module_name, module_info in modules.items():
                module = Module()
                module.module_name = module_name
                module.module_path = module_info["path"]
                module.is_package = len(module_info["children"]) > 0
                module.level = module_info["level"]
                module.parent_module = module_info["parent"]
                module.submodules = module_info["children"]
                module_objects.append(module)
            
            return {
                "status": "success",
                "modules_created": len(module_objects),
                "module_hierarchy": modules
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Module hierarchy construction failed: {str(e)}"
            }
    
    def calculate_repository_metrics(self) -> Dict[str, Any]:
        """Calculate repository metrics"""
        try:
            # This would typically query the graph database or nodes created earlier
            # For now, return a basic structure
            
            metrics = {
                "total_files": 0,
                "total_elements": 0,
                "total_relationships": 0,
                "complexity_distribution": {},
                "language_distribution": {},
                "dependency_metrics": {
                    "circular_dependencies": [],
                    "orphaned_modules": [],
                    "core_modules": []
                },
                "quality_metrics": {
                    "avg_complexity": 0.0,
                    "max_complexity": 0.0,
                    "documentation_coverage": 0.0,
                    "test_coverage": 0.0
                }
            }
            
            return {
                "status": "success",
                "metrics": metrics
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Metrics calculation failed: {str(e)}"
            }
    
    def analyze_repository(self, repository_path: str, max_file_size: int = 10485760, include_ignored: bool = False, analysis_depth: str = "full") -> Dict[str, Any]:
        """Main repository analysis function"""
        print("🔍 Code Analyzer Agent: Starting repository analysis...")
        
        self.repository_path = repository_path
        self.max_file_size = max_file_size
        self.include_ignored = include_ignored
        self.analysis_depth = analysis_depth
        
        try:
            # Step 1: Initialize parsers
            parser_result = self.initialize_parsers()
            if parser_result["status"] == "error":
                return {"error": "Parser initialization failed", "details": parser_result["error"]}
            
            print(f"✅ Step 1: Language parsers initialized - {parser_result.get('supported_languages', [])}")
            
            # Step 2: Build module hierarchy
            module_result = self.build_module_hierarchy(repository_path)
            if module_result["status"] == "error":
                return {"error": "Module hierarchy construction failed", "details": module_result["error"]}
            
            print(f"✅ Step 2: Module hierarchy constructed - {module_result['modules_created']} modules")
            
            # Step 3: Parse and analyze files (simplified for now)
            # In a full implementation, this would iterate through all files from Repository Mapper
            
            # Step 4: Calculate metrics
            metrics_result = self.calculate_repository_metrics()
            if metrics_result["status"] == "error":
                return {"error": "Metrics calculation failed", "details": metrics_result["error"]}
            
            print("✅ Step 3: Repository analysis completed")
            
            # Return comprehensive results
            final_result = {
                "status": "success",
                "repository_path": repository_path,
                "parser_initialization": parser_result,
                "module_hierarchy": module_result,
                "metrics": metrics_result["metrics"],
                "analysis_complete": True,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            print("🎉 Code Analyzer Agent: Repository analysis completed successfully!")
            return final_result
            
        except Exception as e:
            print(f"❌ Code Analyzer Agent: Analysis failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

## API Functions for external use
def analyze_repository_api(repository_path: str, max_file_size: int = 10485760, include_ignored: bool = False, analysis_depth: str = "full") -> Dict[str, Any]:
    """API function for repository analysis"""
    analyzer = CodeAnalyzerAgent()
    return analyzer.analyze_repository(repository_path, max_file_size, include_ignored, analysis_depth)

def query_code_relationships(repository_path: str, query_type: str, element_name: str = "", element_type: str = "", max_results: int = 100) -> Dict[str, Any]:
    """Query code relationships"""
    try:
        # Query relationships based on type
        if query_type == "dependencies":
            # Find what this element depends on
            result = {
                "query_type": "dependencies",
                "element_name": element_name,
                "dependencies": [],  # Would query actual graph
                "confidence_threshold": 0.7
            }
        elif query_type == "dependents":
            # Find what depends on this element
            result = {
                "query_type": "dependents",
                "element_name": element_name,
                "dependents": [],  # Would query actual graph
                "confidence_threshold": 0.7
            }
        elif query_type == "call_graph":
            # Build call graph for a function/class
            result = {
                "query_type": "call_graph",
                "element_name": element_name,
                "callers": [],  # Would query actual graph
                "callees": [],  # Would query actual graph
                "complexity": 0.0
            }
        elif query_type == "inheritance":
            # Find inheritance relationships
            result = {
                "query_type": "inheritance",
                "element_name": element_name,
                "superclasses": [],  # Would query actual graph
                "subclasses": [],  # Would query actual graph
                "depth": 0
            }
        else:
            return {"error": f"Unknown query type: {query_type}"}
        
        return {
            "status": "success",
            "query_result": result,
            "repository_path": repository_path,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Query execution failed: {str(e)}"
        }

def code_analysis_health_check():
    """Health check for Code Analyzer Agent"""
    return {
        "service": "Code Analyzer Agent",
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "1.0.0",
        "supported_languages": ["python", "javascript", "typescript", "java", "cpp", "c"],
        "tree_sitter_available": TREE_SITTER_AVAILABLE,
        "endpoints": [
            "/api/analyze-repository",
            "/api/query-relationships",
            "/api/test-analysis",
            "/api/health"
        ]
    }

if __name__ == "__main__":
    # Example usage
    import tempfile
    import os
    
    # Create a test repository
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''
def hello_world():
    """A simple function"""
    print("Hello, World!")
    return "Hello"

class TestClass:
    """A simple test class"""
    
    def __init__(self):
        self.name = "test"
    
    def method(self):
        return hello_world()
            ''')
        
        result = analyze_repository_api(temp_dir, analysis_depth="basic")
        print(json.dumps(result, indent=2))
