# Codebase Genius - Repository Mapper Agent
# Complete Python implementation for repository mapping and analysis

import json
import datetime
import pathlib
import re
import typing
import os
import stat
import shutil
from typing import Dict, List, Optional, Any, Union

try:
    import github
    import git
    GITHUB_AND_GIT_AVAILABLE = True
except ImportError:
    GITHUB_AND_GIT_AVAILABLE = False
    print("Warning: GitHub/Git libraries not available. Using basic file system operations.")

## Data Classes for Repository Mapping
class Repository:
    def __init__(self):
        self.url: str = ""
        self.clone_path: str = ""
        self.file_tree: Dict[str, Any] = {}
        self.readme_summary: str = ""
        self.validation_status: str = ""
        self.error_message: str = ""
        self.processing_timestamp: datetime.datetime = datetime.datetime.now()
        self.repository_stats: Dict[str, Any] = {}

class FileNode:
    def __init__(self):
        self.path: str = ""
        self.name: str = ""
        self.type: str = ""  # 'file', 'directory'
        self.size: int = 0
        self.extension: str = ""
        self.language_detected: str = ""
        self.is_ignored: bool = False
        self.content_preview: str = ""

class RepoFile:
    def __init__(self):
        self.relationship_type: str = ""  # 'contains', 'implements', 'depends_on'
        self.importance_score: float = 0.0

## Repository Mapper Agent Class
class RepositoryMapperAgent:
    def __init__(self):
        self.repository_url: str = ""
        self.output_format: str = "json"
        self.max_file_size: int = 10485760  # 10MB default
        self.include_ignored: bool = False
    
    def validate_github_url(self, repository_url: str) -> Dict[str, Any]:
        """Validate GitHub repository URL format"""
        # Validate GitHub repository URL format
        github_pattern = r'(?:https?:\/\/)?github\.com\/[\w\-\.]+\/[\w\-\.]+(?:\.git)?/?'
        if not re.match(github_pattern, repository_url, re.IGNORECASE):
            return {"error": "Invalid GitHub repository URL format"}
        
        # Extract username and repo name
        repo_match = re.match(r'(?:https?:\/\/)?github\.com\/([\w\-\.]+)\/([\w\-\.]+)(?:\.git)?/?', repository_url, re.IGNORECASE)
        if not repo_match:
            return {"error": "Could not parse repository information"}
            
        return {"status": "valid", "username": repo_match.group(1), "repository": repo_match.group(2)}
    
    def clone_repository(self, repository_url: str) -> Dict[str, Any]:
        """Clone the repository using GitPython"""
        try:
            if not GITHUB_AND_GIT_AVAILABLE:
                return {"error": "GitPython not available. Please install with: pip install GitPython"}
            
            # Create temporary directory for cloning
            temp_dir = f"/tmp/codebase_genius_{datetime.datetime.now().timestamp()}"
            
            # Clone repository
            repo = git.Repo.clone_from(
                repository_url,
                temp_dir,
                depth=1,  # Shallow clone for performance
                single_branch=True,
                branch="main"
            )
            
            # If main branch doesn't exist, try master
            if not repo.heads.main.exists():
                if repo.heads.master.exists():
                    repo.git.checkout("master")
                    
            return {
                "status": "success",
                "clone_path": temp_dir,
                "repository_info": {
                    "name": repo.working_tree_dir.split('/')[-1],
                    "remote_url": repo.remotes.origin.url,
                    "commit_hash": repo.head.commit.hexsha,
                    "branch": repo.active_branch.name
                }
            }
            
        except git.GitCommandError as e:
            if "Authentication" in str(e):
                return {"error": "Authentication failed - repository may be private"}
            else:
                return {"error": f"Git clone failed: {str(e)}"}
                
        except Exception as e:
            return {"error": f"Repository cloning failed: {str(e)}"}
    
    def generate_file_tree(self, clone_path: str, max_file_size: int = 10485760) -> Dict[str, Any]:
        """Generate comprehensive file tree structure"""
        try:
            # List of directories/files to ignore
            ignore_patterns = [
                ".git", ".svn", ".hg",
                "node_modules", "__pycache__", ".pytest_cache",
                "target", "build", "dist", "out",
                ".DS_Store", "Thumbs.db",
                "*.pyc", "*.pyo", "*.pyd",
                ".env", ".env.local", "secrets.txt"
            ]
            
            file_tree = {}
            
            def should_ignore(path_str):
                name = os.path.basename(path_str)
                for pattern in ignore_patterns:
                    if pattern.startswith("*") and name.endswith(pattern[1:]):
                        return True
                    elif pattern == name:
                        return True
                return False
            
            def process_directory(dir_path, tree_dict):
                if not os.path.isdir(dir_path):
                    return
                    
                for item in os.listdir(dir_path):
                    item_path = os.path.join(dir_path, item)
                    
                    if should_ignore(item_path):
                        continue
                        
                    item_stat = os.stat(item_path)
                    
                    if os.path.isdir(item_path):
                        # Process directory
                        tree_dict[item] = {
                            "type": "directory",
                            "size": item_stat.st_size,
                            "children": {}
                        }
                        process_directory(item_path, tree_dict[item]["children"])
                    else:
                        # Process file
                        extension = os.path.splitext(item)[1].lower()
                        language = self.detect_language_from_extension(extension)
                        
                        # Skip files larger than max_file_size
                        if item_stat.st_size > max_file_size:
                            continue
                            
                        # Read preview content for text files
                        content_preview = ""
                        if extension in [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".md", ".txt", ".yml", ".yaml", ".json", ".xml", ".html", ".css"]:
                            try:
                                with open(item_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content_preview = f.read(1000)  # First 1000 chars
                            except:
                                content_preview = "[Binary or unreadable file]"
                        
                        tree_dict[item] = {
                            "type": "file",
                            "size": item_stat.st_size,
                            "extension": extension,
                            "language": language,
                            "content_preview": content_preview
                        }
            
            def detect_language_from_extension(ext):
                """Detect programming language from file extension"""
                language_map = {
                    ".py": "Python",
                    ".js": "JavaScript",
                    ".ts": "TypeScript",
                    ".java": "Java",
                    ".cpp": "C++",
                    ".c": "C",
                    ".h": "C/C++ Header",
                    ".cc": "C++",
                    ".cs": "C#",
                    ".php": "PHP",
                    ".rb": "Ruby",
                    ".go": "Go",
                    ".rs": "Rust",
                    ".swift": "Swift",
                    ".kt": "Kotlin",
                    ".scala": "Scala",
                    ".sh": "Shell",
                    ".bat": "Batch",
                    ".ps1": "PowerShell",
                    ".html": "HTML",
                    ".css": "CSS",
                    ".scss": "SCSS",
                    ".less": "LESS",
                    ".vue": "Vue.js",
                    ".jsx": "React JSX",
                    ".tsx": "React TSX",
                    ".md": "Markdown",
                    ".txt": "Plain Text",
                    ".yml": "YAML",
                    ".yaml": "YAML",
                    ".json": "JSON",
                    ".xml": "XML",
                    ".toml": "TOML",
                    ".ini": "INI",
                    ".cfg": "Configuration",
                    ".conf": "Configuration"
                }
                return language_map.get(ext.lower(), "Unknown")
            
            # Process the repository directory
            process_directory(clone_path, file_tree)
            
            # Calculate statistics
            file_count = 0
            directory_count = 0
            total_size = 0
            language_distribution = {}
            
            def calculate_stats(tree_dict, current_path=""):
                nonlocal file_count, directory_count, total_size, language_distribution
                
                for name, item in tree_dict.items():
                    current_item_path = os.path.join(current_path, name)
                    
                    if item["type"] == "directory":
                        directory_count += 1
                        calculate_stats(item["children"], current_item_path)
                    else:
                        file_count += 1
                        total_size += item["size"]
                        language = item["language"]
                        if language in language_distribution:
                            language_distribution[language] += 1
                        else:
                            language_distribution[language] = 1
            
            calculate_stats(file_tree)
            
            stats = {
                "total_files": file_count,
                "total_directories": directory_count,
                "total_size_bytes": total_size,
                "language_distribution": language_distribution,
                "generation_timestamp": datetime.datetime.now().isoformat()
            }
            
            return {
                "status": "success",
                "file_tree": file_tree,
                "statistics": stats
            }
            
        except Exception as e:
            return {"error": f"File tree generation failed: {str(e)}"}
    
    def detect_language_from_extension(self, ext: str) -> str:
        """Detect programming language from file extension"""
        language_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".cpp": "C++",
            ".c": "C",
            ".h": "C/C++ Header",
            ".cc": "C++",
            ".cs": "C#",
            ".php": "PHP",
            ".rb": "Ruby",
            ".go": "Go",
            ".rs": "Rust",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".scala": "Scala",
            ".sh": "Shell",
            ".bat": "Batch",
            ".ps1": "PowerShell",
            ".html": "HTML",
            ".css": "CSS",
            ".scss": "SCSS",
            ".less": "LESS",
            ".vue": "Vue.js",
            ".jsx": "React JSX",
            ".tsx": "React TSX",
            ".md": "Markdown",
            ".txt": "Plain Text",
            ".yml": "YAML",
            ".yaml": "YAML",
            ".json": "JSON",
            ".xml": "XML",
            ".toml": "TOML",
            ".ini": "INI",
            ".cfg": "Configuration",
            ".conf": "Configuration"
        }
        return language_map.get(ext.lower(), "Unknown")
    
    def summarize_readme(self, clone_path: str) -> Dict[str, Any]:
        """Extract and summarize README files"""
        try:
            readme_files = [
                "README.md", "README.rst", "README.txt", "README",
                "readme.md", "readme.rst", "readme.txt", "readme"
            ]
            
            readme_content = ""
            readme_file_found = ""
            
            for readme_name in readme_files:
                readme_path = os.path.join(clone_path, readme_name)
                if os.path.exists(readme_path):
                    try:
                        with open(readme_path, 'r', encoding='utf-8') as f:
                            readme_content = f.read()
                        readme_file_found = readme_name
                        break
                    except Exception:
                        continue
            
            if not readme_content:
                return {
                    "status": "not_found",
                    "message": "No README file found or readable"
                }
            else:
                # Basic summarization (in production, this would use LLM)
                summary = self.generate_basic_summary(readme_content)
                
                return {
                    "status": "success",
                    "file_found": readme_file_found,
                    "content_length": len(readme_content),
                    "summary": summary,
                    "full_content": readme_content[:5000]  # First 5000 chars
                }
                
        except Exception as e:
            return {"error": f"README summarization failed: {str(e)}"}
    
    def generate_basic_summary(self, content: str) -> Dict[str, str]:
        """Generate basic summary from README content"""
        lines = content.split('\n')
        title = ""
        description_lines = []
        
        # Extract title (first heading)
        for line in lines:
            if line.startswith('#'):
                title = line.lstrip('#').strip()
                break
        
        # Extract description (first paragraph after title)
        in_description = False
        for line in lines:
            if line.startswith('#'):
                in_description = True
                continue
            
            if in_description and line.strip():
                description_lines.append(line.strip())
                if len(description_lines) >= 3:  # Limit to 3 lines
                    break
        
        description = ' '.join(description_lines)
        
        # Extract installation and usage sections if present
        installation_section = ""
        usage_section = ""
        
        current_section = ""
        for line in lines:
            if line.lower().startswith('## installation'):
                current_section = "installation"
                continue
            elif line.lower().startswith('## usage') or line.lower().startswith('## usage'):
                current_section = "usage"
                continue
            elif line.startswith('##') or line.startswith('#'):
                current_section = ""
                continue
            
            if current_section == "installation" and line.strip():
                installation_section += line.strip() + " "
            elif current_section == "usage" and line.strip():
                usage_section += line.strip() + " "
        
        summary = {
            "title": title or "Repository Documentation",
            "description": description[:500] if description else "No description found",
            "installation_instructions": installation_section[:200] if installation_section else "",
            "usage_instructions": usage_section[:200] if usage_section else ""
        }
        
        return summary
    
    def cleanup_repository(self, clone_path: str) -> Dict[str, Any]:
        """Clean up temporary repository directory"""
        try:
            if os.path.exists(clone_path):
                shutil.rmtree(clone_path)
                return {"status": "success", "message": "Repository cleaned up successfully"}
            else:
                return {"status": "warning", "message": "Repository directory not found for cleanup"}
        except Exception as e:
            return {"status": "error", "message": f"Cleanup failed: {str(e)}"}
    
    def map_repository(self, repository_url: str, output_format: str = "json", max_file_size: int = 10485760, include_ignored: bool = False) -> Dict[str, Any]:
        """Main repository mapping function"""
        print("🗺️ Repository Mapper Agent: Starting repository mapping...")
        
        self.repository_url = repository_url
        self.output_format = output_format
        self.max_file_size = max_file_size
        self.include_ignored = include_ignored
        
        try:
            # Step 1: Validate URL
            validation_result = self.validate_github_url(repository_url)
            if "error" in validation_result:
                return {"error": "URL validation failed", "details": validation_result["error"]}
            
            print("✅ Step 1: Repository URL validated successfully")
            
            # Step 2: Clone repository
            clone_result = self.clone_repository(repository_url)
            if "error" in clone_result:
                return {"error": "Repository cloning failed", "details": clone_result["error"]}
            
            clone_path = clone_result["clone_path"]
            print("✅ Step 2: Repository cloned successfully")
            
            # Step 3: Generate file tree
            file_tree_result = self.generate_file_tree(clone_path, max_file_size)
            if "error" in file_tree_result:
                return {"error": "File tree generation failed", "details": file_tree_result["error"]}
            
            print("✅ Step 3: File tree generated successfully")
            
            # Step 4: Summarize README
            readme_result = self.summarize_readme(clone_path)
            if "error" in readme_result:
                return {"error": "README summarization failed", "details": readme_result["error"]}
            
            print("✅ Step 4: README summarized successfully")
            
            # Step 5: Clean up
            cleanup_result = self.cleanup_repository(clone_path)
            
            # Return comprehensive results
            final_result = {
                "status": "success",
                "repository_url": repository_url,
                "validation": validation_result,
                "cloning": clone_result,
                "file_tree": file_tree_result,
                "readme": readme_result,
                "processing_complete": True,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            print("🎉 Repository Mapper Agent: Repository mapping completed successfully!")
            return final_result
            
        except Exception as e:
            print(f"❌ Repository Mapper Agent: Mapping failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

## API Functions for external use
def map_repository_api(repository_url: str, output_format: str = "json", max_file_size: int = 10485760, include_ignored: bool = False) -> Dict[str, Any]:
    """API function for repository mapping"""
    agent = RepositoryMapperAgent()
    return agent.map_repository(repository_url, output_format, max_file_size, include_ignored)

def repository_mapper_health_check():
    """Health check for Repository Mapper Agent"""
    return {
        "service": "Repository Mapper Agent",
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "1.0.0",
        "github_git_available": GITHUB_AND_GIT_AVAILABLE,
        "supported_formats": ["json"],
        "supported_languages": ["All detected by extension"],
        "endpoints": [
            "/api/map-repository",
            "/api/test-mapping",
            "/api/health"
        ]
    }

if __name__ == "__main__":
    # Example usage
    test_url = "https://github.com/microsoft/vscode"
    result = map_repository_api(test_url, max_file_size=1048576)  # 1MB for testing
    print(json.dumps(result, indent=2))
