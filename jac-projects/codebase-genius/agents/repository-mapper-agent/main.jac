# Codebase Genius - Repository Mapper Agent
# Complete JAC implementation following byLLM patterns

import py from github;
import py from git;
import py from pathlib;
import py from typing;
import py from datetime;

# Repository data node representing a GitHub repository
node repository {
    has url: str;
    has clone_path: str;
    has file_tree: dict;
    has readme_summary: str;
    has validation_status: str;
    has error_message: str;
    has processing_timestamp: datetime.datetime;
    has repository_stats: dict;
}

# File system node for individual files and directories
node file_node {
    has path: str;
    has name: str;
    has type: str;  # 'file', 'directory'
    has size: int;
    has extension: str;
    has language_detected: str;
    has is_ignored: bool;
    has content_preview: str;
}

# Connection edge between repository and files
edge repo_file {
    has relationship_type: str;  # 'contains', 'implements', 'depends_on'
    has importance_score: float;
}

# Repository Mapper Walker - Main entry point
walker map_repository {
    has repository_url: str;
    has output_format: str = "json";
    has max_file_size: int = 10485760;  # 10MB default
    has include_ignored: bool = false;
    
    can validate_github_url with entry {
        # Validate GitHub repository URL format
        if repository_url not in /(?:https?:\/\/)?github\.com\/[\w\-\.]+\/[\w\-\.]+(?:\.git)?/i:
            report {"error": "Invalid GitHub repository URL format"};
            disengage;
        }
        
        # Extract username and repo name
        repo_match = repository_url.match(/(?:https?:\/\/)?github\.com\/([\w\-\.]+)\/([\w\-\.]+)(?:\.git)?/i);
        if not repo_match:
            report {"error": "Could not parse repository information"};
            disengage;
            
        report {"status": "valid", "username": repo_match[0], "repository": repo_match[1]};
    }
    
    can clone_repository with entry {
        # Clone the repository using GitPython
        try {
            import py from git;
            
            # Create temporary directory for cloning
            temp_dir = f"/tmp/codebase_genius_{datetime.datetime.now().timestamp()}";
            
            # Clone repository
            repo = git.Repo.clone_from(
                repository_url,
                temp_dir,
                depth=1,  # Shallow clone for performance
                single_branch=True,
                branch="main"
            );
            
            # If main branch doesn't exist, try master
            if not repo.heads.main.exists():
                if repo.heads.master.exists():
                    repo.git.checkout("master");
                    
            report {
                "status": "success",
                "clone_path": temp_dir,
                "repository_info": {
                    "name": repo.working_tree_dir.split('/')[-1],
                    "remote_url": repo.remotes.origin.url,
                    "commit_hash": repo.head.commit.hexsha,
                    "branch": repo.active_branch.name
                }
            };
        }
        
        except git.GitCommandError as e {
            if "Authentication" in str(e):
                report {"error": "Authentication failed - repository may be private"};
            else:
                report {"error": f"Git clone failed: {str(e)}"};
            disengage;
        }
        
        except Exception as e {
            report {"error": f"Repository cloning failed: {str(e)}"};
            disengage;
        }
    }
    
    can generate_file_tree with entry {
        # Generate comprehensive file tree structure
        try {
            import py from pathlib;
            import py from os;
            import py from stat;
            
            # List of directories/files to ignore
            ignore_patterns = [
                ".git", ".svn", ".hg",
                "node_modules", "__pycache__", ".pytest_cache",
                "target", "build", "dist", "out",
                ".DS_Store", "Thumbs.db",
                "*.pyc", "*.pyo", "*.pyd",
                ".env", ".env.local", "secrets.txt"
            ];
            
            file_tree = {};
            
            def should_ignore(path_str):
                name = os.path.basename(path_str);
                for pattern in ignore_patterns:
                    if pattern.startswith("*") and name.endswith(pattern[1:]):
                        return True;
                    elif pattern == name:
                        return True;
                return false;
            
            def process_directory(dir_path, tree_dict):
                if not os.path.isdir(dir_path):
                    return;
                    
                for item in os.listdir(dir_path):
                    item_path = os.path.join(dir_path, item);
                    
                    if should_ignore(item_path):
                        continue;
                        
                    item_stat = os.stat(item_path);
                    
                    if os.path.isdir(item_path):
                        # Process directory
                        tree_dict[item] = {
                            "type": "directory",
                            "size": item_stat.st_size,
                            "children": {}
                        };
                        process_directory(item_path, tree_dict[item]["children"]);
                    else:
                        # Process file
                        extension = os.path.splitext(item)[1].lower();
                        language = detect_language_from_extension(extension);
                        
                        # Skip files larger than max_file_size
                        if item_stat.st_size > max_file_size:
                            continue;
                            
                        # Read preview content for text files
                        content_preview = "";
                        if extension in [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".md", ".txt", ".yml", ".yaml", ".json", ".xml", ".html", ".css"]:
                            try {
                                with open(item_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content_preview = f.read(1000);  # First 1000 chars
                            } catch:
                                content_preview = "[Binary or unreadable file]";
                        
                        tree_dict[item] = {
                            "type": "file",
                            "size": item_stat.st_size,
                            "extension": extension,
                            "language": language,
                            "content_preview": content_preview
                        };
            
            def detect_language_from_extension(ext):
                language_map = {
                    ".py": "Python",
                    ".js": "JavaScript",
                    ".ts": "TypeScript",
                    ".java": "Java",
                    ".cpp": "C++",
                    ".c": "C",
                    ".h": "C/C++ Header",
                    ".cpp": "C++",
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
                };
                return language_map.get(ext.lower(), "Unknown");
            
            # Process the repository directory
            process_directory(clone_path, file_tree);
            
            # Calculate statistics
            file_count = 0;
            directory_count = 0;
            total_size = 0;
            language_distribution = {};
            
            def calculate_stats(tree_dict, current_path=""):
                nonlocal file_count, directory_count, total_size, language_distribution;
                
                for name, item in tree_dict.items():
                    current_item_path = os.path.join(current_path, name);
                    
                    if item["type"] == "directory":
                        directory_count += 1;
                        calculate_stats(item["children"], current_item_path);
                    else:
                        file_count += 1;
                        total_size += item["size"];
                        language = item["language"];
                        if language in language_distribution:
                            language_distribution[language] += 1;
                        else:
                            language_distribution[language] = 1;
            
            calculate_stats(file_tree);
            
            stats = {
                "total_files": file_count,
                "total_directories": directory_count,
                "total_size_bytes": total_size,
                "language_distribution": language_distribution,
                "generation_timestamp": str(datetime.datetime.now())
            };
            
            report {
                "status": "success",
                "file_tree": file_tree,
                "statistics": stats
            };
        }
        
        except Exception as e {
            report {"error": f"File tree generation failed: {str(e)}"};
            disengage;
        }
    }
    
    can summarize_readme with entry {
        # Extract and summarize README files
        try {
            readme_files = [
                "README.md", "README.rst", "README.txt", "README",
                "readme.md", "readme.rst", "readme.txt", "readme"
            ];
            
            readme_content = "";
            readme_file_found = "";
            
            for readme_name in readme_files:
                readme_path = os.path.join(clone_path, readme_name);
                if os.path.exists(readme_path):
                    try {
                        with open(readme_path, 'r', encoding='utf-8') as f:
                            readme_content = f.read();
                        readme_file_found = readme_name;
                        break;
                    } catch Exception:
                        continue;
            
            if not readme_content:
                report {
                    "status": "not_found",
                    "message": "No README file found or readable"
                };
            else:
                # Basic summarization (in production, this would use LLM)
                summary = generate_basic_summary(readme_content);
                
                report {
                    "status": "success",
                    "file_found": readme_file_found,
                    "content_length": len(readme_content),
                    "summary": summary,
                    "full_content": readme_content[:5000]  # First 5000 chars
                };
        }
        
        except Exception as e {
            report {"error": f"README summarization failed: {str(e)}"};
            disengage;
        }
    
    can generate_basic_summary(content: str) -> str {
        lines = content.split('\n');
        title = "";
        description_lines = [];
        
        # Extract title (first heading)
        for line in lines:
            if line.startswith('#'):
                title = line.lstrip('#').strip();
                break;
        
        # Extract description (first paragraph after title)
        in_description = false;
        for line in lines:
            if line.startswith('#'):
                in_description = true;
                continue;
            
            if in_description and line.strip():
                description_lines.append(line.strip());
                if len(description_lines) >= 3:  # Limit to 3 lines
                    break;
        
        description = ' '.join(description_lines);
        
        # Extract installation and usage sections if present
        installation_section = "";
        usage_section = "";
        
        current_section = "";
        for line in lines:
            if line.lower().startswith('## installation'):
                current_section = "installation";
                continue;
            elif line.lower().startswith('## usage') or line.lower().startswith('## usage'):
                current_section = "usage";
                continue;
            elif line.startswith('##') or line.startswith('#'):
                current_section = "";
                continue;
            
            if current_section == "installation" and line.strip():
                installation_section += line.strip() + " ";
            elif current_section == "usage" and line.strip():
                usage_section += line.strip() + " ";
        
        summary = {
            "title": title or "Repository Documentation",
            "description": description[:500] if description else "No description found",
            "installation_instructions": installation_section[:200] if installation_section else "",
            "usage_instructions": usage_section[:200] if usage_section else ""
        };
        
        return str(summary);
    }
    
    can cleanup_repository with entry {
        # Clean up temporary repository directory
        try {
            if os.path.exists(clone_path):
                import shutil;
                shutil.rmtree(clone_path);
                report {"status": "success", "message": "Repository cleaned up successfully"};
            else:
                report {"status": "warning", "message": "Repository directory not found for cleanup"};
        } catch Exception as e {
            report {"status": "error", "message": f"Cleanup failed: {str(e)}"};
        }
    }
    
    # Main execution flow
    with entry {
        report {"step": "starting", "message": "Repository mapping process initiated"};
        
        # Step 1: Validate URL
        validation_result = spawn validate_github_url;
        if validation_result["error"]:
            report {"error": "URL validation failed", "details": validation_result["error"]};
            disengage;
        
        report {"step": "validated", "message": "Repository URL validated successfully"};
        
        # Step 2: Clone repository
        clone_result = spawn clone_repository;
        if clone_result["error"]:
            report {"error": "Repository cloning failed", "details": clone_result["error"]};
            disengage;
        
        clone_path = clone_result["clone_path"];
        report {"step": "cloned", "message": "Repository cloned successfully"};
        
        # Step 3: Generate file tree
        file_tree_result = spawn generate_file_tree;
        if file_tree_result["error"]:
            report {"error": "File tree generation failed", "details": file_tree_result["error"]};
            disengage;
        
        report {"step": "mapped", "message": "File tree generated successfully"};
        
        # Step 4: Summarize README
        readme_result = spawn summarize_readme;
        if readme_result["error"]:
            report {"error": "README summarization failed", "details": readme_result["error"]};
            disengage;
        
        report {"step": "summarized", "message": "README summarized successfully"};
        
        # Step 5: Clean up
        spawn cleanup_repository;
        
        # Return comprehensive results
        final_result = {
            "status": "success",
            "repository_url": repository_url,
            "validation": validation_result,
            "cloning": clone_result,
            "file_tree": file_tree_result,
            "readme": readme_result,
            "processing_complete": true,
            "timestamp": str(datetime.datetime.now())
        };
        
        report final_result;
    }
}

# HTTP API Walker - Repository Mapping Endpoint
walker api_map_repository {
    has repository_url: str;
    has output_format: str = "json";
    has max_file_size: int = 10485760;
    has include_ignored: bool = false;
    
    with entry {
        # Call the main repository mapping walker
        result = spawn map_repository {
            repository_url: repository_url,
            output_format: output_format,
            max_file_size: max_file_size,
            include_ignored: include_ignored
        };
        
        # Return result for HTTP endpoint
        report result;
    }
}

# Test walker for validating the implementation
walker test_repository_mapping {
    has test_url: str = "https://github.com/microsoft/vscode";
    
    with entry {
        report {"message": "Testing repository mapping with sample repository"};
        
        result = spawn api_map_repository {
            repository_url: test_url,
            max_file_size: 1048576  # 1MB for testing
        };
        
        report {
            "test_result": result,
            "status": "completed" if result.get("status") == "success" else "failed"
        };
    }
}

# Health check walker
walker health_check {
    with entry {
        report {
            "service": "Repository Mapper Agent",
            "status": "healthy",
            "timestamp": str(datetime.datetime.now()),
            "version": "1.0.0",
            "endpoints": [
                "/api/map-repository",
                "/api/test-mapping",
                "/api/health"
            ]
        };
    }
}
