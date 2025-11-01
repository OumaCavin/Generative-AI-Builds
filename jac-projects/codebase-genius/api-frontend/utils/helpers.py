"""
Utility functions for Codebase Genius API and Frontend
"""

import os;
import re;
import json;
import hashlib;
import shutil;
import tempfile;
import zipfile;
import subprocess;
import mimetypes;
from typing import Dict, List, Optional, Any, Tuple;
from datetime import datetime, timedelta;
import logging;

# Configure logging
logging.basicConfig(level=logging.INFO);
logger = logging.getLogger(__name__);

## Repository Utilities

def validate_repository_url(url: str) -> Tuple[bool, str]:
    """
    Validate repository URL and return (is_valid, error_message)
    
    Args:
        url: Repository URL to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url or not isinstance(url, str):
        return False, "URL is required";
        
    # Remove trailing slashes
    url = url.strip().rstrip('/');
    
    # Pattern for common repository platforms
    patterns = {
        'github': r'^https?://github\.com/[^/]+/[^/]+/?$',
        'gitlab': r'^https?://gitlab\.com/[^/]+/[^/]+/?$',
        'bitbucket': r'^https?://bitbucket\.org/[^/]+/[^/]+/?$',
        'gitee': r'^https?://gitee\.com/[^/]+/[^/]+/?$'
    };
    
    for platform, pattern in patterns.items():
        if re.match(pattern, url):
            return True, "";
            
    # Check if it looks like a valid git repository URL
    git_pattern = r'^https?://[^/]+/[^/]+/[^/]+/?$|^git@[^:]+:[^/]+/[^/]+/?$';
    if re.match(git_pattern, url):
        return True, "";
        
    return False, "Invalid repository URL format. Supported: GitHub, GitLab, Bitbucket, Gitee";

def get_repository_platform(url: str) -> Optional[str]:
    """Extract platform name from repository URL"""
    url = url.lower();
    
    if 'github.com' in url:
        return 'github';
    elif 'gitlab.com' in url:
        return 'gitlab';
    elif 'bitbucket.org' in url:
        return 'bitbucket';
    elif 'gitee.com' in url:
        return 'gitee';
    else:
        return 'unknown';

def extract_repository_info(url: str) -> Dict[str, str]:
    """
    Extract repository information from URL
    
    Args:
        url: Repository URL
        
    Returns:
        Dictionary with repository information
    """
    info = {
        'url': url,
        'platform': get_repository_platform(url),
        'owner': '',
        'name': '',
        'branch': 'main'
    };
    
    # Extract owner and name from GitHub/GitLab URL
    patterns = {
        'github': r'https?://github\.com/([^/]+)/([^/]+)/?',
        'gitlab': r'https?://gitlab\.com/([^/]+)/([^/]+)/?',
        'bitbucket': r'https?://bitbucket\.org/([^/]+)/([^/]+)/?',
        'gitee': r'https?://gitee\.com/([^/]+)/([^/]+)/?'
    };
    
    platform = info['platform'];
    if platform in patterns:
        match = re.match(patterns[platform], url);
        if match:
            info['owner'] = match.group(1);
            info['name'] = match.group(2).replace('.git', '');
            
    return info;

def clone_repository(url: str, target_dir: str, branch: str = 'main', depth: int = 1) -> bool:
    """
    Clone repository to target directory
    
    Args:
        url: Repository URL
        target_dir: Target directory path
        branch: Branch to clone
        depth: Clone depth (1 for shallow clone)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure target directory exists
        os.makedirs(target_dir, exist_ok=True);
        
        # Clone repository
        cmd = [
            'git', 'clone',
            '--depth', str(depth),
            '--branch', branch,
            url,
            target_dir
        ];
        
        logger.info(f"Cloning repository: {url} to {target_dir}");
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        );
        
        if result.returncode == 0:
            logger.info(f"Successfully cloned repository: {url}");
            return True;
        else:
            logger.error(f"Failed to clone repository: {result.stderr}");
            return False;
            
    except subprocess.TimeoutExpired:
        logger.error(f"Repository clone timeout: {url}");
        return False;
    except Exception as e:
        logger.error(f"Error cloning repository {url}: {str(e)}");
        return False;

def get_repository_structure(repo_dir: str) -> Dict[str, Any]:
    """
    Get repository structure and file information
    
    Args:
        repo_dir: Repository directory path
        
    Returns:
        Dictionary containing repository structure
    """
    structure = {
        'root_path': repo_dir,
        'total_files': 0,
        'total_dirs': 0,
        'files': [],
        'directories': [],
        'file_types': {},
        'total_size': 0,
        'readme_content': '',
        'root_files': []
    };
    
    try:
        for root, dirs, files in os.walk(repo_dir):
            # Skip hidden directories and git folders
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__'];
            
            relative_root = os.path.relpath(root, repo_dir);
            
            if relative_root == '.':
                relative_root = '';
                
            # Process files
            for file in files:
                if file.startswith('.'):
                    continue;
                    
                file_path = os.path.join(root, file);
                relative_path = os.path.relpath(file_path, repo_dir);
                
                try:
                    file_size = os.path.getsize(file_path);
                    file_ext = os.path.splitext(file)[1].lower();
                    
                    file_info = {
                        'path': relative_path,
                        'name': file,
                        'extension': file_ext,
                        'size': file_size,
                        'size_human': format_file_size(file_size),
                        'type': 'binary' if is_binary_file(file_path) else 'text',
                        'directory': relative_root
                    };
                    
                    structure['files'].append(file_info);
                    structure['total_files'] += 1;
                    structure['total_size'] += file_size;
                    
                    # Track file types
                    if file_ext:
                        structure['file_types'][file_ext] = structure['file_types'].get(file_ext, 0) + 1;
                        
                    # Check for README
                    if file.lower().startswith('readme') and relative_root == '':
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                structure['readme_content'] = f.read()[:2000];  # First 2000 chars
                        except:
                            pass;
                            
                except OSError as e:
                    logger.warning(f"Error accessing file {file_path}: {e}");
                    continue;
                    
            # Process directories
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name);
                relative_path = os.path.relpath(dir_path, repo_dir);
                
                structure['directories'].append({
                    'path': relative_path,
                    'name': dir_name,
                    'directory': relative_root
                });
                structure['total_dirs'] += 1;
                
    except Exception as e:
        logger.error(f"Error analyzing repository structure: {e}");
        
    return structure;

def is_binary_file(file_path: str) -> bool:
    """Check if file is binary by examining first few bytes"""
    try:
        with open(file_path, 'rb') as f:
            # Read first 1024 bytes
            sample = f.read(1024);
            
            # Check for null bytes (binary indicator)
            if b'\x00' in sample:
                return True;
                
            # Check for high percentage of non-printable characters
            try:
                text_sample = sample.decode('utf-8', errors='ignore');
                if len(text_sample) > 0:
                    non_printable = sum(1 for c in text_sample if c < 32 and c not in '\t\n\r');
                    if non_printable / len(text_sample) > 0.3:
                        return True;
            except:
                return True;
                
    except Exception as e:
        logger.warning(f"Error checking binary file {file_path}: {e}");
        return True;  # Assume binary if we can't read it
        
    return False;

def filter_files_by_size(files: List[Dict], max_size: int = 10485760) -> List[Dict]:
    """Filter files by size (default 10MB)"""
    return [f for f in files if f['size'] <= max_size];

def filter_files_by_extension(files: List[Dict], extensions: List[str]) -> List[Dict]:
    """Filter files by extension"""
    return [f for f in files if f['extension'] in extensions];

## File Processing Utilities

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B";
        
    size_names = ["B", "KB", "MB", "GB", "TB"];
    i = 0;
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024;
        i += 1;
        
    return f"{size_bytes:.1f} {size_names[i]}";

def calculate_directory_hash(directory: str) -> str:
    """Calculate hash of directory contents"""
    hash_md5 = hashlib.md5();
    
    # Sort files for consistent hashing
    file_paths = [];
    for root, dirs, files in os.walk(directory):
        dirs.sort();  # Sort directories for consistency
        files.sort();  # Sort files for consistency
        
        for file in files:
            if not file.startswith('.'):
                file_paths.append(os.path.relpath(os.path.join(root, file), directory));
                
    # Hash each file's path and content
    for file_path in sorted(file_paths):
        full_path = os.path.join(directory, file_path);
        if os.path.isfile(full_path):
            hash_md5.update(file_path.encode());
            
            try:
                with open(full_path, 'rb') as f:
                    # Hash first and last 1KB for large files
                    if os.path.getsize(full_path) > 2048:
                        hash_md5.update(f.read(1024));
                        f.seek(-1024, 2);
                        hash_md5.update(f.read(1024));
                    else:
                        hash_md5.update(f.read());
            except Exception as e:
                logger.warning(f"Error hashing file {full_path}: {e}");
                
    return hash_md5.hexdigest();

def create_archive(source_dir: str, output_path: str, archive_type: str = 'zip') -> bool:
    """Create archive from directory"""
    try:
        if archive_type.lower() == 'zip':
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file);
                        arc_name = os.path.relpath(file_path, source_dir);
                        zipf.write(file_path, arc_name);
                        
        elif archive_type.lower() == 'tar.gz':
            import tarfile;
            with tarfile.open(output_path, 'w:gz') as tar:
                tar.add(source_dir, arcname=os.path.basename(source_dir));
                
        else:
            raise ValueError(f"Unsupported archive type: {archive_type}");
            
        return True;
        
    except Exception as e:
        logger.error(f"Error creating archive {output_path}: {e}");
        return False;

## Documentation Utilities

def generate_markdown_content(structure: Dict[str, Any], title: str = None) -> str:
    """Generate markdown documentation from repository structure"""
    
    repo_info = structure.get('repository_info', {});
    title = title or f"Documentation for {repo_info.get('name', 'Repository')}";
    
    content = f"""# {title}

## Repository Overview

- **URL**: {repo_info.get('url', 'Unknown')}
- **Platform**: {repo_info.get('platform', 'Unknown')}
- **Owner**: {repo_info.get('owner', 'Unknown')}
- **Name**: {repo_info.get('name', 'Unknown')}
- **Branch**: {repo_info.get('branch', 'main')}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

{structure.get('readme_content', 'No README content available.')}

## Repository Statistics

- **Total Files**: {structure.get('total_files', 0)}
- **Total Directories**: {structure.get('total_dirs', 0)}
- **Total Size**: {format_file_size(structure.get('total_size', 0))}

## File Type Distribution

""";
    
    # Add file type breakdown
    file_types = structure.get('file_types', {});
    for ext, count in sorted(file_types.items()):
        if ext:  # Skip empty extensions
            content += f"- `{ext}`: {count} files\n";
            
    content += f"""

## Directory Structure

```
{generate_directory_tree(structure.get('root_path', ''))}
```

## Key Files

""";
    
    # Add top files by size
    files = structure.get('files', []);
    files_by_size = sorted(files, key=lambda x: x['size'], reverse=True)[:20];
    
    for file_info in files_by_size:
        if file_info['type'] == 'text':
            content += f"- `{file_info['path']}` ({file_info['size_human']})\n";
            
    content += f"""

## Generated by Codebase Genius

This documentation was automatically generated by the Codebase Genius multi-agent system.

The system analyzed the repository structure, identified file types, and generated comprehensive documentation for better understanding and maintenance.

---
*Generated by Codebase Genius - AI-Powered Code Documentation*
*Timestamp: {datetime.now().isoformat()}*
""";
    
    return content;

def generate_directory_tree(root_path: str, max_depth: int = 3) -> str:
    """Generate directory tree representation"""
    tree_lines = [];
    
    def add_tree(current_path: str, prefix: str = "", depth: int = 0):
        if depth >= max_depth:
            return;
            
        try:
            items = os.listdir(current_path);
            # Filter hidden items and sort
            items = [item for item in items if not item.startswith('.') and item != '__pycache__'];
            items.sort();
            
            for i, item in enumerate(items):
                item_path = os.path.join(current_path, item);
                is_last = i == len(items) - 1;
                
                current_prefix = "└── " if is_last else "├── ";
                tree_lines.append(f"{prefix}{current_prefix}{item}");
                
                if os.path.isdir(item_path):
                    next_prefix = prefix + ("    " if is_last else "│   ");
                    add_tree(item_path, next_prefix, depth + 1);
                    
        except PermissionError:
            pass;  # Skip directories we can't read
            
    try:
        add_tree(root_path);
    except Exception as e:
        logger.warning(f"Error generating directory tree: {e}");
        
    return "\n".join(tree_lines);

def convert_markdown_to_html(markdown_content: str) -> str:
    """Convert markdown content to HTML"""
    try:
        import markdown;
        
        html = markdown.markdown(
            markdown_content,
            extensions=[
                'markdown.extensions.tables',
                'markdown.extensions.fenced_code',
                'markdown.extensions.toc',
                'markdown.extensions.codehilite'
            ]
        );
        
        # Add basic styling
        styled_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Documentation</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 24px;
            margin-bottom: 16px;
        }}
        
        h1 {{
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        
        code {{
            background-color: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        
        pre {{
            background-color: #f8f9fa;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
        }}
        
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 0;
            padding-left: 16px;
            color: #666;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        
        th {{
            background-color: #f2f2f2;
        }}
    </style>
</head>
<body>
{html}
</body>
</html>
""";
        
        return styled_html;
        
    except ImportError:
        logger.warning("Markdown library not available, returning plain HTML");
        # Basic HTML conversion without markdown processing
        html_content = markdown_content.replace('\n', '<br>\n');
        return f"<html><body><pre>{html_content}</pre></body></html>";
    except Exception as e:
        logger.error(f"Error converting markdown to HTML: {e}");
        return f"<html><body><pre>{markdown_content}</pre></body></html>";

## Workflow Utilities

def create_workflow_id() -> str:
    """Create unique workflow ID"""
    import uuid;
    return str(uuid.uuid4());

def generate_workflow_status(workflow_id: str, status: str, progress: float, 
                           current_step: str, result: Optional[Dict] = None,
                           error_message: Optional[str] = None) -> Dict[str, Any]:
    """Generate workflow status response"""
    return {
        'workflow_id': workflow_id,
        'status': status,
        'progress': progress,
        'current_step': current_step,
        'result': result,
        'error_message': error_message,
        'timestamp': datetime.now().isoformat()
    };

def cleanup_old_workflows(workflow_dir: str, max_age_hours: int = 24) -> int:
    """Cleanup old workflow directories"""
    cleaned_count = 0;
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours);
    
    try:
        if os.path.exists(workflow_dir):
            for item in os.listdir(workflow_dir):
                item_path = os.path.join(workflow_dir, item);
                
                if os.path.isdir(item_path):
                    # Check modification time
                    mtime = datetime.fromtimestamp(os.path.getmtime(item_path));
                    if mtime < cutoff_time:
                        shutil.rmtree(item_path);
                        cleaned_count += 1;
                        logger.info(f"Cleaned up old workflow directory: {item_path}");
                        
    except Exception as e:
        logger.error(f"Error cleaning up workflows: {e}");
        
    return cleaned_count;

## Validation Utilities

def validate_output_format(format_str: str) -> bool:
    """Validate output format"""
    return format_str.lower() in ['markdown', 'html', 'pdf'];

def validate_analysis_depth(depth: str) -> bool:
    """Validate analysis depth"""
    return depth.lower() in ['basic', 'full', 'comprehensive'];

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove or replace unsafe characters
    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename);
    
    # Limit length
    if len(safe_filename) > 255:
        name, ext = os.path.splitext(safe_filename);
        safe_filename = name[:255-len(ext)] + ext;
        
    return safe_filename;

def is_safe_path(path: str, base_dir: str) -> bool:
    """Check if path is safe (within base directory)"""
    try:
        # Resolve to absolute paths
        abs_path = os.path.realpath(path);
        abs_base = os.path.realpath(base_dir);
        
        # Check if path is within base directory
        return abs_path.startswith(abs_base);
        
    except Exception:
        return False;

## Performance Utilities

def get_directory_size(directory: str) -> int:
    """Get total size of directory in bytes"""
    total_size = 0;
    
    try:
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename);
                try:
                    total_size += os.path.getsize(filepath);
                except OSError:
                    pass;  # Skip files we can't access
                    
    except Exception as e:
        logger.error(f"Error calculating directory size: {e}");
        
    return total_size;

def get_system_info() -> Dict[str, Any]:
    """Get system information for monitoring"""
    import psutil;
    
    return {
        'cpu_count': psutil.cpu_count(),
        'memory_total': psutil.virtual_memory().total,
        'memory_available': psutil.virtual_memory().available,
        'disk_usage': psutil.disk_usage('/').percent,
        'timestamp': datetime.now().isoformat()
    };

def measure_execution_time(func):
    """Decorator to measure function execution time"""
    import time;
    
    def wrapper(*args, **kwargs):
        start_time = time.time();
        result = func(*args, **kwargs);
        end_time = time.time();
        
        logger.info(f"{func.__name__} executed in {end_time - start_time:.2f} seconds");
        return result;
        
    return wrapper;
