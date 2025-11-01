# Supervisor Agent - Multi-Agent Orchestration System
# Phase 6 Implementation: Workflow orchestration, task delegation, and result aggregation

import json
import datetime
import pathlib
import re
import typing
import collections
import concurrent.futures
import asyncio
import queue
import threading
from typing import Dict, List, Optional, Any, Union

## Data Classes for Workflow Management
class WorkflowStatus:
    def __init__(self):
        self.task_id: str = ""
        self.status: str = "pending"  # pending, running, completed, failed, retry
        self.progress: float = 0.0
        self.started_at: str = ""
        self.completed_at: str = ""
        self.error_message: str = ""
        self.result_data: dict = {}
        self.agent_type: str = ""  # repository_mapper, code_analyzer, docgenie
        self.priority: int = 5  # 1-10, higher = more priority
        self.retries: int = 0
        self.max_retries: int = 3

class AgentConnection:
    def __init__(self):
        self.agent_type: str = ""
        self.endpoint: str = ""
        self.status: str = "disconnected"  # connected, disconnected, error
        self.last_heartbeat: str = ""
        self.capabilities: List[str] = []
        self.load: float = 0.0  # 0.0-1.0
        self.response_time: float = 0.0

class TaskRequest:
    def __init__(self):
        self.request_id: str = ""
        self.repository_url: str = ""
        self.analysis_options: dict = {}
        self.priority: int = 5
        self.created_at: str = ""
        self.user_context: dict = {}
        self.workflow_status: WorkflowStatus = WorkflowStatus()

class AggregatedResult:
    def __init__(self):
        self.request_id: str = ""
        self.repository_info: dict = {}
        self.ccg_data: dict = {}
        self.documentation_result: dict = {}
        self.quality_metrics: dict = {}
        self.final_output: dict = {}
        self.processing_time: float = 0.0
        self.agent_results: dict = {}

## Supervisor Agent Class
class SupervisorAgent:
    def __init__(self):
        self.task_request: TaskRequest = TaskRequest()
        self.workflow_id: str = ""
        self.agent_connections: Dict[str, AgentConnection] = {}
        self.workflow_history: List[WorkflowStatus] = []
        self.error_recovery_active: bool = False
        self.priority_queue: List[dict] = []
    
    def initialize_agents(self) -> Dict[str, AgentConnection]:
        """Initialize agent connections"""
        print("[Supervisor] Initializing agent connections...")
        
        # Initialize agent connections based on configuration
        agent_configs = {
            "repository_mapper": {
                "endpoint": "http://localhost:8081",
                "capabilities": ["clone_repository", "generate_file_tree", "summarize_readme"]
            },
            "code_analyzer": {
                "endpoint": "http://localhost:8082", 
                "capabilities": ["parse_code", "build_ccg", "extract_relationships"]
            },
            "docgenie": {
                "endpoint": "http://localhost:8083",
                "capabilities": ["generate_documentation", "create_diagrams", "assess_quality"]
            }
        }
        
        # Load configuration override if available
        config_path = "./config/config.json"
        if pathlib.Path(config_path).exists():
            with open(config_path) as f:
                config = json.load(f)
                agent_configs = config.get("agent_connections", agent_configs)
        
        # Create agent connection objects
        for agent_type, config in agent_configs.items():
            connection = AgentConnection()
            connection.agent_type = agent_type
            connection.endpoint = config["endpoint"]
            connection.capabilities = config["capabilities"]
            connection.status = "disconnected"
            self.agent_connections[agent_type] = connection
        
        print(f"[Supervisor] Initialized {len(self.agent_connections)} agent connections")
        return self.agent_connections
    
    def validate_repository(self):
        """Validate repository URL"""
        print("[Supervisor] Validating repository URL...")
        
        repository_url = self.task_request.repository_url
        
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(repository_url):
            raise ValueError(f"Invalid repository URL: {repository_url}")
        
        # Check if it's a GitHub repository (most common case)
        github_pattern = re.compile(r'github\.com/[\w.-]+/[\w.-]+(?:\.git)?/?$')
        if github_pattern.search(repository_url):
            print(f"[Supervisor] Validated GitHub repository: {repository_url}")
        else:
            print(f"[Supervisor] Validated repository URL: {repository_url}")
        
        print("[Supervisor] Repository validation completed")
    
    def check_agent_health(self) -> Dict[str, AgentConnection]:
        """Check agent health"""
        print("[Supervisor] Checking agent health...")
        
        healthy_agents = {}
        
        for agent_type, connection in self.agent_connections.items():
            try:
                # Simulate health check (in real implementation, this would be an HTTP request)
                print(f"[Supervisor] Checking {agent_type} agent health...")
                
                # Mock health check response
                health_status = "connected" if agent_type != "docgenie" else "error"
                
                connection.status = health_status
                connection.last_heartbeat = datetime.datetime.now().isoformat()
                
                if health_status == "connected":
                    healthy_agents[agent_type] = connection
                    print(f"[Supervisor] {agent_type} agent is healthy")
                else:
                    print(f"[Supervisor] {agent_type} agent is unhealthy")
                
            except Exception as e:
                print(f"[Supervisor] Health check failed for {agent_type}: {e}")
                connection.status = "error"
        
        if len(healthy_agents) < 3:
            print(f"[Supervisor] WARNING: Only {len(healthy_agents)}/3 agents are healthy")
            # In production, this might trigger fallback mechanisms
        
        return healthy_agents
    
    def delegate_to_repository_mapper(self) -> dict:
        """Delegate task to Repository Mapper Agent"""
        print("[Supervisor] Delegating task to Repository Mapper Agent...")
        
        self.task_request.workflow_status = WorkflowStatus()
        self.task_request.workflow_status.task_id = f"{self.workflow_id}_repo_mapper"
        self.task_request.workflow_status.status = "running"
        self.task_request.workflow_status.started_at = datetime.datetime.now().isoformat()
        self.task_request.workflow_status.agent_type = "repository_mapper"
        self.task_request.workflow_status.priority = self.task_request.priority
        
        repository_url = self.task_request.repository_url
        
        # Prepare task payload
        task_payload = {
            "action": "map_repository",
            "repository_url": repository_url,
            "output_dir": f"./temp/repo_{self.workflow_id}",
            "options": {
                "include_file_tree": True,
                "include_readme": True,
                "include_metadata": True
            }
        }
        
        try:
            # Simulate agent communication (in real implementation, this would be HTTP request)
            print(f"[Supervisor] Sending task to Repository Mapper: {task_payload['action']}")
            
            # Mock response for demonstration
            repository_result = {
                "status": "completed",
                "repository_info": {
                    "url": repository_url,
                    "name": "sample-repository",
                    "description": "A sample repository for testing",
                    "total_files": 45,
                    "primary_language": "python",
                    "clone_path": f"./temp/repo_{self.workflow_id}"
                },
                "file_tree": {
                    "total_files": 45,
                    "file_types": {".py": 25, ".md": 8, ".txt": 5, ".json": 7},
                    "root_structure": [
                        {"name": "src", "type": "directory", "files": 15},
                        {"name": "tests", "type": "directory", "files": 12},
                        {"name": "README.md", "type": "file", "lines": 150}
                    ]
                },
                "readme_summary": {
                    "description": "Sample repository documentation",
                    "sections": ["Overview", "Installation", "Usage", "Contributing"],
                    "quality_score": 0.85
                },
                "processing_time": 12.5,
                "error": None
            }
            
            # Update workflow status
            self.task_request.workflow_status.status = "completed"
            self.task_request.workflow_status.completed_at = datetime.datetime.now().isoformat()
            self.task_request.workflow_status.progress = 100.0
            self.task_request.workflow_status.result_data = repository_result
            
            print("[Supervisor] Repository Mapper task completed successfully")
            return repository_result
            
        except Exception as e:
            print(f"[Supervisor] Repository Mapper task failed: {e}")
            self.task_request.workflow_status.status = "failed"
            self.task_request.workflow_status.error_message = str(e)
            raise
    
    def delegate_to_code_analyzer(self, repository_result: dict) -> dict:
        """Delegate task to Code Analyzer Agent"""
        print("[Supervisor] Delegating task to Code Analyzer Agent...")
        
        repository_path = repository_result["repository_info"]["clone_path"]
        
        # Update workflow status for Code Analyzer
        code_analyzer_status = WorkflowStatus()
        code_analyzer_status.task_id = f"{self.workflow_id}_code_analyzer"
        code_analyzer_status.status = "running"
        code_analyzer_status.started_at = datetime.datetime.now().isoformat()
        code_analyzer_status.agent_type = "code_analyzer"
        code_analyzer_status.priority = self.task_request.priority
        
        # Prepare task payload
        task_payload = {
            "action": "analyze_repository",
            "repository_path": repository_path,
            "analysis_options": {
                "depth": "full",
                "languages": ["python", "javascript", "java"],
                "include_relationships": True,
                "include_metrics": True
            }
        }
        
        try:
            print(f"[Supervisor] Sending task to Code Analyzer: {task_payload['action']}")
            
            # Mock response for demonstration
            ccg_result = {
                "status": "completed",
                "ccg_data": {
                    "entities": [
                        {
                            "id": "entity_1",
                            "name": "Calculator",
                            "type": "class",
                            "file_path": "src/calculator.py",
                            "start_line": 1,
                            "end_line": 50,
                            "complexity": 8.5,
                            "dependencies": [],
                            "dependents": [],
                            "documentation": "A calculator class with basic operations",
                            "source_code": "class Calculator:\\n    def add(self, a, b):\\n        return a + b"
                        },
                        {
                            "id": "entity_2",
                            "name": "add_numbers",
                            "type": "function",
                            "file_path": "src/utils.py",
                            "start_line": 10,
                            "end_line": 25,
                            "complexity": 3.2,
                            "dependencies": [],
                            "dependents": ["entity_1"],
                            "documentation": "Add two numbers together",
                            "source_code": "def add_numbers(a, b):\\n    return a + b"
                        }
                    ],
                    "relationships": [
                        {
                            "from": "entity_1",
                            "to": "entity_2",
                            "type": "calls",
                            "confidence": 0.95,
                            "context": "Calculator.add method calls add_numbers"
                        }
                    ],
                    "metadata": {
                        "repository_name": "sample-repository",
                        "total_files": 45,
                        "analysis_date": datetime.datetime.now().isoformat(),
                        "languages_detected": ["python"],
                        "complexity_stats": {
                            "avg_complexity": 5.85,
                            "max_complexity": 8.5,
                            "complexity_distribution": {"low": 15, "medium": 8, "high": 3}
                        }
                    }
                },
                "processing_time": 25.3,
                "error": None
            }
            
            # Update workflow status
            code_analyzer_status.status = "completed"
            code_analyzer_status.completed_at = datetime.datetime.now().isoformat()
            code_analyzer_status.progress = 100.0
            code_analyzer_status.result_data = ccg_result
            
            print("[Supervisor] Code Analyzer task completed successfully")
            return ccg_result
            
        except Exception as e:
            print(f"[Supervisor] Code Analyzer task failed: {e}")
            code_analyzer_status.status = "failed"
            code_analyzer_status.error_message = str(e)
            raise
    
    def delegate_to_docgenie(self, ccg_result: dict, repository_result: dict) -> dict:
        """Delegate task to DocGenie Agent"""
        print("[Supervisor] Delegating task to DocGenie Agent...")
        
        # Update workflow status for DocGenie
        docgenie_status = WorkflowStatus()
        docgenie_status.task_id = f"{self.workflow_id}_docgenie"
        docgenie_status.status = "running"
        docgenie_status.started_at = datetime.datetime.now().isoformat()
        docgenie_status.agent_type = "docgenie"
        docgenie_status.priority = self.task_request.priority
        
        # Prepare task payload
        task_payload = {
            "action": "generate_documentation",
            "ccg_data": ccg_result["ccg_data"],
            "repository_info": repository_result["repository_info"],
            "output_options": {
                "formats": ["markdown", "html"],
                "include_diagrams": True,
                "include_citations": True
            }
        }
        
        try:
            print(f"[Supervisor] Sending task to DocGenie: {task_payload['action']}")
            
            # Mock response for demonstration
            documentation_result = {
                "status": "completed",
                "output_files": [
                    "./outputs/documentation.md",
                    "./outputs/documentation.html",
                    "./outputs/architecture_diagram.png",
                    "./outputs/call_graph.png"
                ],
                "quality_metrics": {
                    "quality_score": 0.85,
                    "total_sections": 3,
                    "total_citations": 15,
                    "has_overview": True,
                    "has_api_reference": True,
                    "has_architecture": True,
                    "diagram_count": 2
                },
                "sections_generated": [
                    {"id": "overview", "title": "Repository Overview", "lines": 25},
                    {"id": "api_reference", "title": "API Reference", "lines": 45},
                    {"id": "architecture", "title": "Architecture Analysis", "lines": 30}
                ],
                "processing_time": 18.7,
                "error": None
            }
            
            # Update workflow status
            docgenie_status.status = "completed"
            docgenie_status.completed_at = datetime.datetime.now().isoformat()
            docgenie_status.progress = 100.0
            docgenie_status.result_data = documentation_result
            
            print("[Supervisor] DocGenie task completed successfully")
            return documentation_result
            
        except Exception as e:
            print(f"[Supervisor] DocGenie task failed: {e}")
            docgenie_status.status = "failed"
            docgenie_status.error_message = str(e)
            raise
    
    def aggregate_results(self, repository_result: dict, ccg_result: dict, documentation_result: dict) -> AggregatedResult:
        """Aggregate results from all agents"""
        print("[Supervisor] Aggregating results from all agents...")
        
        # Create aggregated result
        aggregated_result = AggregatedResult()
        aggregated_result.request_id = self.workflow_id
        aggregated_result.repository_info = repository_result["repository_info"]
        aggregated_result.ccg_data = ccg_result["ccg_data"]
        aggregated_result.documentation_result = documentation_result
        aggregated_result.processing_time = (
            repository_result["processing_time"] + 
            ccg_result["processing_time"] + 
            documentation_result["processing_time"]
        )
        aggregated_result.agent_results = {
            "repository_mapper": repository_result,
            "code_analyzer": ccg_result,
            "docgenie": documentation_result
        }
        
        # Calculate overall quality metrics
        doc_quality = documentation_result["quality_metrics"]["quality_score"]
        repo_quality = repository_result["readme_summary"]["quality_score"]
        analysis_quality = min(ccg_result["ccg_data"]["metadata"]["complexity_stats"]["avg_complexity"] / 10.0, 1.0)
        
        aggregated_result.quality_metrics = {
            "overall_score": (doc_quality + repo_quality + analysis_quality) / 3.0,
            "documentation_quality": doc_quality,
            "repository_quality": repo_quality,
            "analysis_quality": analysis_quality,
            "processing_efficiency": min(1.0, 60.0 / aggregated_result.processing_time)  # Target: under 60 seconds
        }
        
        # Generate final output summary
        aggregated_result.final_output = {
            "status": "completed",
            "summary": f"Successfully processed repository '{aggregated_result.repository_info['name']}' with {len(aggregated_result.ccg_data['entities'])} entities and {len(aggregated_result.ccg_data['relationships'])} relationships",
            "generated_files": documentation_result["output_files"],
            "quality_score": aggregated_result.quality_metrics["overall_score"],
            "processing_time": aggregated_result.processing_time,
            "recommendations": [
                "Review high-complexity entities for potential refactoring",
                "Add more detailed documentation for complex functions",
                "Consider improving test coverage for core modules"
            ]
        }
        
        print(f"[Supervisor] Results aggregated successfully - Quality Score: {aggregated_result.quality_metrics['overall_score']:.2f}")
        return aggregated_result
    
    def handle_error_recovery(self):
        """Handle error recovery"""
        print("[Supervisor] Initiating error recovery process...")
        
        self.error_recovery_active = True
        failed_agents = []
        
        # Identify failed agents from workflow history
        for status in self.workflow_history:
            if status.status == "failed":
                failed_agents.append(status.agent_type)
        
        if not failed_agents:
            print("[Supervisor] No failed agents to recover")
            self.error_recovery_active = False
            return
        
        print(f"[Supervisor] Attempting recovery for agents: {failed_agents}")
        
        # Retry failed agents with exponential backoff
        for agent_type in failed_agents:
            try:
                print(f"[Supervisor] Retrying {agent_type} agent...")
                
                # Find the failed status and increment retry count
                for status in self.workflow_history:
                    if status.agent_type == agent_type and status.status == "failed":
                        status.retries += 1
                        if status.retries < status.max_retries:
                            status.status = "retry"
                            print(f"[Supervisor] Retry {status.retries}/{status.max_retries} for {agent_type}")
                            
                            # Re-delegate based on agent type
                            if agent_type == "repository_mapper":
                                self.delegate_to_repository_mapper()
                            elif agent_type == "code_analyzer":
                                # This would need the repository result from previous step
                                pass
                            elif agent_type == "docgenie":
                                # This would need previous results
                                pass
                        else:
                            print(f"[Supervisor] {agent_type} agent exceeded maximum retries")
                            status.status = "failed_permanent"
                        break
                
            except Exception as e:
                print(f"[Supervisor] Recovery failed for {agent_type}: {e}")
        
        self.error_recovery_active = False
        print("[Supervisor] Error recovery process completed")
    
    def prioritize_tasks(self):
        """Manage task priority queue"""
        print("[Supervisor] Managing task priority queue...")
        
        # Add current task to priority queue
        self.priority_queue.append({
            "task_id": self.workflow_id,
            "priority": self.task_request.priority,
            "created_at": self.task_request.created_at,
            "repository_url": self.task_request.repository_url,
            "status": "pending"
        })
        
        # Sort by priority (higher priority first) then by creation time
        self.priority_queue.sort(key=lambda x: (-x["priority"], x["created_at"]))
        
        # Show queue status
        print(f"[Supervisor] Priority queue contains {len(self.priority_queue)} tasks")
        for i, task in enumerate(self.priority_queue[:5]):  # Show top 5
            print(f"  {i+1}. Priority {task['priority']}: {task['repository_url']} ({task['status']})")
        
        if len(self.priority_queue) > 5:
            print(f"  ... and {len(self.priority_queue) - 5} more tasks")
    
    def monitor_workflow_progress(self) -> dict:
        """Monitor workflow progress"""
        print("[Supervisor] Monitoring workflow progress...")
        
        total_agents = 3
        completed_agents = 0
        
        for status in self.workflow_history:
            if status.status == "completed":
                completed_agents += 1
        
        progress_percentage = (completed_agents / total_agents) * 100.0
        
        progress_summary = {
            "total_agents": total_agents,
            "completed_agents": completed_agents,
            "progress_percentage": progress_percentage,
            "current_phase": "Documentation Generation" if completed_agents >= 2 else "Analysis Phase",
            "estimated_completion": "2-3 minutes" if progress_percentage < 100 else "Complete"
        }
        
        print(f"[Supervisor] Workflow Progress: {progress_percentage:.1f}% ({completed_agents}/{total_agents} agents completed)")
        print(f"[Supervisor] Current Phase: {progress_summary['current_phase']}")
        
        return progress_summary
    
    def execute_complete_workflow(self, task_request: TaskRequest) -> dict:
        """Execute complete workflow orchestration"""
        print("🚀 Supervisor Agent: Starting complete workflow orchestration...")
        
        start_time = datetime.datetime.now()
        self.workflow_id = f"workflow_{start_time.strftime('%Y%m%d_%H%M%S')}"
        self.task_request = task_request
        
        print(f"[Supervisor] Workflow ID: {self.workflow_id}")
        
        try:
            # Step 1: Initialize agents and connections
            self.initialize_agents()
            
            # Step 2: Validate repository URL
            self.validate_repository()
            
            # Step 3: Check agent health
            healthy_agents = self.check_agent_health()
            
            if len(healthy_agents) < 3:
                print("[Supervisor] WARNING: Not all agents are healthy, proceeding with available agents")
            
            # Step 4: Manage task priority
            self.prioritize_tasks()
            
            # Step 5: Execute workflow phases
            print("\\n[Supervisor] === WORKFLOW EXECUTION PHASES ===")
            
            # Phase 1: Repository Mapping
            print("\\n--- Phase 1: Repository Mapping ---")
            repository_result = self.delegate_to_repository_mapper()
            self.workflow_history.append(self.task_request.workflow_status)
            
            # Phase 2: Code Analysis  
            print("\\n--- Phase 2: Code Analysis ---")
            ccg_result = self.delegate_to_code_analyzer(repository_result)
            
            # Phase 3: Documentation Generation
            print("\\n--- Phase 3: Documentation Generation ---")
            documentation_result = self.delegate_to_docgenie(ccg_result, repository_result)
            
            # Step 6: Monitor progress
            progress_summary = self.monitor_workflow_progress()
            
            # Step 7: Aggregate results
            print("\\n--- Result Aggregation ---")
            aggregated_result = self.aggregate_results(repository_result, ccg_result, documentation_result)
            
            # Step 8: Handle any errors or recovery
            if any(status.status == "failed" for status in self.workflow_history):
                self.handle_error_recovery()
            
            end_time = datetime.datetime.now()
            total_time = (end_time - start_time).total_seconds()
            
            print(f"\\n✅ Supervisor Agent: Workflow completed successfully in {total_time:.2f} seconds")
            
            return {
                "status": "completed",
                "workflow_id": self.workflow_id,
                "total_time": total_time,
                "aggregated_result": aggregated_result.__dict__,
                "progress_summary": progress_summary,
                "agent_statuses": {status.agent_type: status.status for status in self.workflow_history},
                "quality_metrics": aggregated_result.quality_metrics,
                "final_output": aggregated_result.final_output
            }
            
        except Exception as e:
            print(f"❌ Supervisor Agent: Workflow failed with error: {e}")
            
            # Attempt error recovery
            try:
                self.handle_error_recovery()
            except Exception as recovery_error:
                print(f"❌ Error recovery also failed: {recovery_error}")
            
            return {
                "status": "failed",
                "workflow_id": self.workflow_id,
                "error": str(e),
                "workflow_history": [status.__dict__ for status in self.workflow_history],
                "partial_results": {}
            }

## API Gateway Functions for external requests
def process_api_request(request_data: dict, response_format: str = "json") -> dict:
    """Process external API request"""
    print("[Supervisor API] Processing external API request...")
    
    # Validate request format
    required_fields = ["repository_url"]
    for field in required_fields:
        if field not in request_data:
            raise ValueError(f"Missing required field: {field}")
    
    # Create task request
    task_request = TaskRequest()
    task_request.request_id = f"api_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    task_request.repository_url = request_data["repository_url"]
    task_request.analysis_options = request_data.get("options", {})
    task_request.priority = request_data.get("priority", 5)
    task_request.created_at = datetime.datetime.now().isoformat()
    task_request.user_context = request_data.get("user_context", {})
    
    # Execute workflow
    supervisor = SupervisorAgent()
    result = supervisor.execute_complete_workflow(task_request)
    
    # Format response based on requested format
    if response_format == "json":
        return result
    elif response_format == "html":
        return format_html_response(result)
    else:
        return result

def format_html_response(result_data: dict) -> str:
    """Format response as HTML"""
    
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Codebase Genius - Documentation Generated</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .status {{ padding: 10px; margin: 10px 0; border-radius: 3px; }}
        .success {{ background: #d4edda; color: #155724; }}
        .error {{ background: #f8d7da; color: #721c24; }}
        .metrics {{ display: flex; gap: 20px; }}
        .metric {{ background: #e9ecef; padding: 15px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Codebase Genius Documentation</h1>
        <p>Generated by Supervisor Agent on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="status {'success' if result_data['status'] == 'completed' else 'error'}">
        <h2>Status: {result_data['status'].upper()}</h2>
        <p>Workflow ID: {result_data.get('workflow_id', 'N/A')}</p>
        <p>Processing Time: {result_data.get('total_time', 0):.2f} seconds</p>
    </div>
    
    {f'''
    <div class="metrics">
        <div class="metric">
            <h3>Quality Score</h3>
            <p>{result_data.get('quality_metrics', {}).get('overall_score', 0):.2f}</p>
        </div>
        <div class="metric">
            <h3>Entities Found</h3>
            <p>{len(result_data.get('aggregated_result', {}).get('ccg_data', {}).get('entities', []))}</p>
        </div>
        <div class="metric">
            <h3>Relationships</h3>
            <p>{len(result_data.get('aggregated_result', {}).get('ccg_data', {}).get('relationships', []))}</p>
        </div>
    </div>
    ''' if result_data['status'] == 'completed' else ''}
    
    {f'''
    <h2>Generated Files</h2>
    <ul>
    {''.join([f'<li><a href="{file}">{file}</a></li>' for file in result_data.get('final_output', {}).get('generated_files', [])])}
    </ul>
    ''' if result_data.get('final_output', {}).get('generated_files') else ''}
</body>
</html>
    """
    
    return html_template

# Health check function
def supervisor_health_check():
    """Health check for Supervisor Agent"""
    return {
        "service": "Supervisor Agent",
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "1.0.0",
        "capabilities": [
            "workflow_orchestration",
            "agent_management", 
            "result_aggregation",
            "error_recovery"
        ],
        "endpoints": [
            "/api/orchestrate-workflow",
            "/api/process-request",
            "/api/health"
        ]
    }

if __name__ == "__main__":
    # Example usage
    sample_request = {
        "repository_url": "https://github.com/microsoft/vscode",
        "options": {"depth": "full"},
        "priority": 5
    }
    
    result = process_api_request(sample_request)
    print(json.dumps(result, indent=2))
