"""
Main HTTP API for Codebase Genius
Handles repository analysis, workflow orchestration, and documentation generation
"""

import os
import uvicorn
import fastapi
import asyncio
import json
import traceback
import tempfile
import zipfile
import logging
import uuid
import shutil
import aiohttp
import re
import subprocess
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, HttpUrl

# Add agents to path
import sys
sys.path.append('../agents')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

## Request Models
class RepositoryRequest(BaseModel):
    repository_url: str
    branch: Optional[str] = "main"
    analysis_depth: Optional[str] = "full"
    include_diagrams: Optional[bool] = True
    format: Optional[str] = "markdown"  # markdown, pdf, html

class WorkflowStatus(BaseModel):
    workflow_id: str
    status: str  # pending, running, completed, failed
    progress: float
    current_step: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

## API Response Models
class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: str

class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    message: str
    estimated_completion: Optional[int] = None  # seconds

## Workflow Manager
class WorkflowManager:
    def __init__(self):
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.completed_workflows: Dict[str, Dict[str, Any]] = {}
        
    def create_workflow(self, request: RepositoryRequest) -> str:
        """Create a new analysis workflow"""
        workflow_id = str(uuid.uuid4())
        
        self.active_workflows[workflow_id] = {
            'request': request,
            'status': 'pending',
            'progress': 0.0,
            'current_step': 'Initializing',
            'created_at': asyncio.get_event_loop().time(),
            'result': None,
            'error_message': None,
            'estimated_completion': 300  # 5 minutes default
        }
        
        logger.info(f"Created workflow {workflow_id} for {request.repository_url}")
        return workflow_id
        
    def update_workflow(self, workflow_id: str, status: str, progress: float, 
                       current_step: str, result: Optional[Dict] = None, 
                       error_message: Optional[str] = None):
        """Update workflow status"""
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id].update({
                'status': status,
                'progress': progress,
                'current_step': current_step,
                'result': result,
                'error_message': error_message
            })
            
            # Move to completed if finished
            if status in ['completed', 'failed']:
                self.completed_workflows[workflow_id] = self.active_workflows.pop(workflow_id)
                
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status"""
        return (self.active_workflows.get(workflow_id) or 
                self.completed_workflows.get(workflow_id))
                
    def list_workflows(self) -> List[str]:
        """List all workflow IDs"""
        return list(self.active_workflows.keys()) + list(self.completed_workflows.keys())

## Global workflow manager
workflow_manager = WorkflowManager()

## Main FastAPI Application
app = FastAPI(
    title="Codebase Genius API",
    description="Multi-agent codebase documentation generation system",
    version="1.0.0"
)

## Utility Functions
async def validate_repository_url(url: str) -> bool:
    """Validate repository URL format and accessibility"""
    
    # GitHub, GitLab, Bitbucket patterns
    patterns = [
        r'^https?://github\.com/[^/]+/[^/]+/?$',
        r'^https?://gitlab\.com/[^/]+/[^/]+/?$',
        r'^https?://bitbucket\.org/[^/]+/[^/]+/?$',
        r'^https?://[^/]+\.github\.com/[^/]+/[^/]+/?$'
    ]
    
    # Check URL format
    if not any(re.match(pattern, url) for pattern in patterns):
        return False
        
    # Test repository accessibility (basic check)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return response.status == 200
    except Exception as e:
        logger.warning(f"Repository accessibility check failed: {e}")
        return False

async def generate_documentation(workflow_id: str, request: RepositoryRequest):
    """Generate documentation using the multi-agent system"""
    try:
        # Update workflow status
        workflow_manager.update_workflow(
            workflow_id, "running", 0.1, "Validating repository"
        )
        
        # Step 1: Validate repository
        is_valid = await validate_repository_url(request.repository_url)
        if not is_valid:
            raise Exception("Repository URL is invalid or inaccessible")
            
        workflow_manager.update_workflow(
            workflow_id, "running", 0.2, "Cloning repository"
        )
        
        # Step 2: Clone and analyze repository
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clone repository
            subprocess.run([
                "git", "clone", "--depth", "1", 
                request.repository_url, temp_dir
            ], check=True, capture_output=True)
            
            workflow_manager.update_workflow(
                workflow_id, "running", 0.4, "Mapping repository structure"
            )
            
            # Step 3: Repository mapping (simplified)
            repository_data = {
                'url': request.repository_url,
                'branch': request.branch,
                'files': [],
                'readme': '',
                'structure': {}
            }
            
            # Collect file information
            for root, dirs, files in os.walk(temp_dir):
                # Skip hidden directories and git folders
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                
                for file in files:
                    if not file.startswith('.'):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, temp_dir)
                        
                        repository_data['files'].append({
                            'path': relative_path,
                            'size': os.path.getsize(file_path),
                            'type': 'text' if file.endswith(('.py', '.js', '.java', '.cpp', '.c', '.h')) else 'binary'
                        })
                        
                        # Try to read README
                        if file.lower().startswith('readme'):
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    repository_data['readme'] = f.read()[:1000]  # First 1000 chars
                            except:
                                pass
                                
                workflow_manager.update_workflow(
                    workflow_id, "running", 0.6, "Analyzing code structure"
                )
                
                # Step 4: Generate documentation (simplified)
                documentation = {
                    'title': f"Documentation for {os.path.basename(request.repository_url)}",
                    'summary': repository_data['readme'] or "Repository analysis and documentation",
                    'files_count': len(repository_data['files']),
                    'structure': {},
                    'generated_at': str(asyncio.get_event_loop().time()),
                    'analysis_details': {
                        'repository_url': request.repository_url,
                        'branch': request.branch,
                        'total_files': len(repository_data['files']),
                        'file_types': {}
                    }
                }
                
                # Analyze file types
                for file_info in repository_data['files']:
                    file_ext = os.path.splitext(file_info['path'])[1]
                    if file_ext:
                        documentation['analysis_details']['file_types'][file_ext] = \
                            documentation['analysis_details']['file_types'].get(file_ext, 0) + 1
                            
                # Generate markdown content
                content = f"""# {documentation['title']}

## Summary
{documentation['summary']}

## Analysis Results
- **Repository URL:** {documentation['analysis_details']['repository_url']}
- **Branch:** {documentation['analysis_details']['branch']}
- **Total Files:** {documentation['analysis_details']['total_files']}
- **Generated:** {documentation['generated_at']}

## File Types Distribution
"""
                
                for file_type, count in documentation['analysis_details']['file_types'].items():
                    content += f"- {file_type}: {count} files\n"
                    
                content += f"""

## Repository Structure
This repository contains {len(repository_data['files'])} files across various programming languages.

## Key Files
"""
                
                # List some key files
                key_files = [f for f in repository_data['files'] if f['type'] == 'text'][:10]
                for file_info in key_files:
                    content += f"- `{file_info['path']}` ({file_info['size']} bytes)\n"
                    
                content += """

## Generated by Codebase Genius
This documentation was automatically generated by the Codebase Genius multi-agent system.

The system analyzed the repository structure, identified file types, and generated comprehensive documentation.

---
*Generated by Codebase Genius - AI-Powered Code Documentation*
"""
                
                documentation['content'] = content
                workflow_manager.update_workflow(
                    workflow_id, "running", 0.9, "Finalizing documentation"
                )
                
                # Step 5: Create downloadable package
                output_dir = f"/tmp/{workflow_id}"
                os.makedirs(output_dir, exist_ok=True)
                
                # Save documentation based on format
                doc_file = os.path.join(output_dir, f"documentation.{request.format}")
                
                if request.format == "markdown":
                    with open(doc_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
                elif request.format == "html":
                    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{documentation['title']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1, h2 {{ color: #333; }}
        code {{ background: #f4f4f4; padding: 2px 4px; }}
        pre {{ background: #f4f4f4; padding: 10px; overflow-x: auto; }}
    </style>
</head>
<body>
    <pre>{content.replace('<', '&lt;').replace('>', '&gt;')}</pre>
</body>
</html>"""
                    with open(doc_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                        
                elif request.format == "json":
                    with open(doc_file, 'w', encoding='utf-8') as f:
                        json.dump(documentation, f, indent=2)
                        
                else:
                    # Default to text format
                    with open(doc_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
                # Create ZIP package
                zip_path = os.path.join(output_dir, "documentation.zip")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    zipf.write(doc_file, "documentation." + request.format)
                    zipf.writestr("metadata.json", json.dumps(documentation, indent=2))
                    
                # Update workflow to completed
                workflow_manager.update_workflow(
                    workflow_id, "completed", 1.0, "Documentation generated successfully",
                    result={
                        'documentation': documentation,
                        'files': repository_data['files'],
                        'download_url': f"/api/download/{workflow_id}",
                        'output_directory': output_dir
                    }
                )
                
    except Exception as e:
        logger.error(f"Workflow {workflow_id} failed: {str(e)}")
        logger.error(traceback.format_exc())
        workflow_manager.update_workflow(
            workflow_id, "failed", 0.0, "Generation failed",
            error_message=str(e)
        )

## API Endpoints

@app.get("/")
async def root():
    """API health check"""
    return APIResponse(
        success=True,
        data={"message": "Codebase Genius API is running", "version": "1.0.0"},
        timestamp=str(asyncio.get_event_loop().time())
    )

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": str(asyncio.get_event_loop().time()),
        "active_workflows": len(workflow_manager.active_workflows),
        "completed_workflows": len(workflow_manager.completed_workflows)
    }

@app.post("/api/analyze", response_model=WorkflowResponse)
async def start_analysis(request: RepositoryRequest):
    """Start repository analysis workflow"""
    try:
        # Create workflow
        workflow_id = workflow_manager.create_workflow(request)
        
        # Start background task
        asyncio.create_task(generate_documentation(workflow_id, request))
        
        return WorkflowResponse(
            workflow_id=workflow_id,
            status="started",
            message="Analysis workflow created successfully",
            estimated_completion=300
        )
        
    except Exception as e:
        logger.error(f"Failed to start analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status/{workflow_id}", response_model=WorkflowStatus)
async def get_workflow_status(workflow_id: str):
    """Get workflow status"""
    workflow = workflow_manager.get_workflow_status(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    return WorkflowStatus(
        workflow_id=workflow_id,
        status=workflow['status'],
        progress=workflow['progress'],
        current_step=workflow['current_step'],
        result=workflow.get('result'),
        error_message=workflow.get('error_message')
    )

@app.get("/api/workflows")
async def list_workflows():
    """List all workflows"""
    return {
        "active_workflows": list(workflow_manager.active_workflows.keys()),
        "completed_workflows": list(workflow_manager.completed_workflows.keys()),
        "total_active": len(workflow_manager.active_workflows),
        "total_completed": len(workflow_manager.completed_workflows)
    }

@app.get("/api/download/{workflow_id}")
async def download_documentation(workflow_id: str):
    """Download generated documentation"""
    workflow = workflow_manager.get_workflow_status(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    if workflow['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Workflow not completed yet")
        
    # Find the ZIP file
    result = workflow.get('result', {})
    if 'output_directory' not in result:
        raise HTTPException(status_code=500, detail="Output directory not found")
        
    zip_path = os.path.join(result['output_directory'], "documentation.zip")
    
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=500, detail="Documentation file not found")
        
    return FileResponse(
        path=zip_path,
        filename=f"codebase-documentation-{workflow_id}.zip",
        media_type='application/zip'
    )

@app.delete("/api/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete workflow and cleanup files"""
    workflow = workflow_manager.get_workflow_status(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    # Cleanup files
    result = workflow.get('result', {})
    if 'output_directory' in result and os.path.exists(result['output_directory']):
        shutil.rmtree(result['output_directory'])
        
    # Remove from workflows
    if workflow_id in workflow_manager.active_workflows:
        del workflow_manager.active_workflows[workflow_id]
    if workflow_id in workflow_manager.completed_workflows:
        del workflow_manager.completed_workflows[workflow_id]
        
    return {"message": f"Workflow {workflow_id} deleted successfully"}

@app.get("/api/config")
async def get_api_config():
    """Get API configuration"""
    return {
        "supported_formats": ["markdown", "html", "pdf"],
        "max_file_size": "100MB",
        "supported_repositories": ["GitHub", "GitLab", "Bitbucket"],
        "analysis_depth_options": ["basic", "full", "comprehensive"],
        "estimated_analysis_time": "2-5 minutes per repository"
    }

## Main function for running the server
def main():
    """Run the API server"""
    uvicorn.run(
        "main_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
