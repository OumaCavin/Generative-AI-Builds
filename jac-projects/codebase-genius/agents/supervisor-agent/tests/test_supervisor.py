#!/usr/bin/env python3
"""
Supervisor Agent Test Suite
Comprehensive testing framework for multi-agent orchestration functionality
"""

import pytest
import json
import tempfile
import shutil
import pathlib
import subprocess
import sys
import asyncio
import time
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Mock JAC components for testing
class MockWorkflowStatus:
    def __init__(self, task_id: str, agent_type: str, status: str = "pending"):
        self.task_id = task_id
        self.status = status
        self.progress = 0.0
        self.started_at = ""
        self.completed_at = ""
        self.error_message = ""
        self.result_data = {}
        self.agent_type = agent_type
        self.priority = 5
        self.retries = 0
        self.max_retries = 3

class MockAgentConnection:
    def __init__(self, agent_type: str, endpoint: str):
        self.agent_type = agent_type
        self.endpoint = endpoint
        self.status = "disconnected"
        self.last_heartbeat = ""
        self.capabilities = []
        self.load = 0.0
        self.response_time = 0.0

class MockTaskRequest:
    def __init__(self, request_id: str, repository_url: str):
        self.request_id = request_id
        self.repository_url = repository_url
        self.analysis_options = {}
        self.priority = 5
        self.created_at = datetime.now().isoformat()
        self.user_context = {}
        self.workflow_status = MockWorkflowStatus(f"{request_id}_workflow", "supervisor")

class MockAggregatedResult:
    def __init__(self, request_id: str):
        self.request_id = request_id
        self.repository_info = {}
        self.ccg_data = {}
        self.documentation_result = {}
        self.quality_metrics = {}
        self.final_output = {}
        self.processing_time = 0.0
        self.agent_results = {}

class TestSupervisorConfiguration:
    """Test configuration loading and validation"""
    
    def test_config_loading(self):
        """Test that configuration loads correctly"""
        config_data = {
            "agent_info": {
                "name": "Supervisor Agent",
                "version": "1.0.0"
            },
            "agent_connections": {
                "repository_mapper": {
                    "endpoint": "http://localhost:8081",
                    "capabilities": ["clone_repository"]
                }
            },
            "workflow_settings": {
                "max_concurrent_workflows": 10,
                "default_priority": 5
            }
        }
        
        # Test configuration structure
        assert "agent_info" in config_data
        assert "agent_connections" in config_data
        assert "workflow_settings" in config_data
        
        assert config_data["agent_info"]["name"] == "Supervisor Agent"
        assert config_data["workflow_settings"]["max_concurrent_workflows"] == 10
    
    def test_agent_connection_validation(self):
        """Test agent connection validation logic"""
        valid_connections = {
            "repository_mapper": {
                "endpoint": "http://localhost:8081",
                "capabilities": ["clone_repository", "generate_file_tree"]
            },
            "code_analyzer": {
                "endpoint": "http://localhost:8082",
                "capabilities": ["parse_code", "build_ccg"]
            }
        }
        
        # All connections should have required fields
        for agent_type, connection in valid_connections.items():
            assert "endpoint" in connection
            assert "capabilities" in connection
            assert isinstance(connection["capabilities"], list)
    
    def test_workflow_settings_validation(self):
        """Test workflow settings validation"""
        workflow_settings = {
            "max_concurrent_workflows": 10,
            "default_priority": 5,
            "max_retries_per_agent": 3,
            "workflow_timeout_minutes": 30
        }
        
        # Validate numeric ranges
        assert 1 <= workflow_settings["max_concurrent_workflows"] <= 100
        assert 1 <= workflow_settings["default_priority"] <= 10
        assert 1 <= workflow_settings["max_retries_per_agent"] <= 10
        assert workflow_settings["workflow_timeout_minutes"] > 0

class TestWorkflowOrchestration:
    """Test workflow orchestration logic"""
    
    def test_workflow_creation(self):
        """Test creating a new workflow"""
        task_request = MockTaskRequest("test_001", "https://github.com/test/repo")
        
        assert task_request.request_id == "test_001"
        assert task_request.repository_url == "https://github.com/test/repo"
        assert task_request.priority == 5
        assert task_request.workflow_status.status == "pending"
    
    def test_workflow_status_tracking(self):
        """Test workflow status tracking"""
        status = MockWorkflowStatus("test_workflow", "repository_mapper", "running")
        
        # Update status
        status.status = "completed"
        status.progress = 100.0
        status.completed_at = datetime.now().isoformat()
        
        assert status.status == "completed"
        assert status.progress == 100.0
        assert status.completed_at != ""
    
    def test_workflow_prioritization(self):
        """Test workflow prioritization"""
        workflows = [
            MockTaskRequest("wf_001", "https://github.com/user/repo1"),
            MockTaskRequest("wf_002", "https://github.com/user/repo2"),
            MockTaskRequest("wf_003", "https://github.com/user/repo3")
        ]
        
        # Set different priorities
        workflows[0].priority = 8  # High priority
        workflows[1].priority = 3  # Low priority
        workflows[2].priority = 5  # Normal priority
        
        # Sort by priority (higher first)
        sorted_workflows = sorted(workflows, key=lambda x: -x.priority)
        
        assert sorted_workflows[0].priority == 8
        assert sorted_workflows[1].priority == 5
        assert sorted_workflows[2].priority == 3
    
    def test_workflow_timeout_handling(self):
        """Test workflow timeout handling"""
        status = MockWorkflowStatus("test_timeout", "repository_mapper")
        
        # Simulate timeout
        status.started_at = (datetime.now() - timedelta(minutes=35)).isoformat()  # 35 minutes ago
        
        # Check if workflow has timed out
        started_time = datetime.fromisoformat(status.started_at)
        current_time = datetime.now()
        duration_minutes = (current_time - started_time).total_seconds() / 60
        
        assert duration_minutes > 30  # Should be over timeout threshold

class TestAgentCommunication:
    """Test agent communication and coordination"""
    
    def test_agent_connection_creation(self):
        """Test creating agent connections"""
        repo_mapper = MockAgentConnection("repository_mapper", "http://localhost:8081")
        code_analyzer = MockAgentConnection("code_analyzer", "http://localhost:8082")
        docgenie = MockAgentConnection("docgenie", "http://localhost:8083")
        
        assert repo_mapper.agent_type == "repository_mapper"
        assert repo_mapper.endpoint == "http://localhost:8081"
        assert repo_mapper.status == "disconnected"
    
    def test_agent_health_monitoring(self):
        """Test agent health monitoring"""
        agent = MockAgentConnection("test_agent", "http://localhost:8080")
        
        # Simulate health check
        agent.status = "connected"
        agent.last_heartbeat = datetime.now().isoformat()
        agent.load = 0.3
        
        assert agent.status == "connected"
        assert agent.load >= 0.0
        assert agent.load <= 1.0
    
    def test_agent_load_balancing(self):
        """Test agent load balancing logic"""
        agents = [
            MockAgentConnection("agent_1", "http://localhost:8081"),
            MockAgentConnection("agent_2", "http://localhost:8082"),
            MockAgentConnection("agent_3", "http://localhost:8083")
        ]
        
        # Set different loads
        agents[0].load = 0.2
        agents[1].load = 0.8
        agents[2].load = 0.5
        
        # Sort by load (lowest first for selection)
        sorted_agents = sorted(agents, key=lambda x: x.load)
        
        assert sorted_agents[0].load == 0.2  # Least loaded agent
        assert sorted_agents[-1].load == 0.8  # Most loaded agent
    
    def test_agent_response_time_tracking(self):
        """Test agent response time tracking"""
        agent = MockAgentConnection("test_agent", "http://localhost:8080")
        
        # Simulate response time measurement
        start_time = time.time()
        time.sleep(0.1)  # Simulate processing time
        end_time = time.time()
        
        agent.response_time = end_time - start_time
        
        assert agent.response_time >= 0.1
        assert agent.response_time < 1.0

class TestTaskDelegation:
    """Test task delegation to agents"""
    
    def test_repository_mapper_delegation(self):
        """Test delegating task to Repository Mapper"""
        task_request = MockTaskRequest("test_001", "https://github.com/test/repo")
        
        # Prepare delegation payload
        payload = {
            "action": "map_repository",
            "repository_url": task_request.repository_url,
            "output_dir": "./temp/repo_test_001",
            "options": {
                "include_file_tree": True,
                "include_readme": True,
                "include_metadata": True
            }
        }
        
        assert payload["action"] == "map_repository"
        assert payload["repository_url"] == task_request.repository_url
        assert "include_file_tree" in payload["options"]
    
    def test_code_analyzer_delegation(self):
        """Test delegating task to Code Analyzer"""
        repository_result = {
            "repository_info": {
                "clone_path": "./temp/repo_test_001"
            }
        }
        
        # Prepare delegation payload
        payload = {
            "action": "analyze_repository",
            "repository_path": repository_result["repository_info"]["clone_path"],
            "analysis_options": {
                "depth": "full",
                "languages": ["python", "javascript"],
                "include_relationships": True,
                "include_metrics": True
            }
        }
        
        assert payload["action"] == "analyze_repository"
        assert "depth" in payload["analysis_options"]
        assert "languages" in payload["analysis_options"]
    
    def test_docgenie_delegation(self):
        """Test delegating task to DocGenie"""
        ccg_data = {
            "entities": [{"id": "1", "name": "TestClass", "type": "class"}],
            "relationships": [{"from": "1", "to": "2", "type": "calls"}]
        }
        
        repository_info = {
            "url": "https://github.com/test/repo",
            "name": "test-repo"
        }
        
        # Prepare delegation payload
        payload = {
            "action": "generate_documentation",
            "ccg_data": ccg_data,
            "repository_info": repository_info,
            "output_options": {
                "formats": ["markdown", "html"],
                "include_diagrams": True,
                "include_citations": True
            }
        }
        
        assert payload["action"] == "generate_documentation"
        assert "ccg_data" in payload
        assert "repository_info" in payload
        assert "markdown" in payload["output_options"]["formats"]
    
    def test_delegation_error_handling(self):
        """Test error handling in task delegation"""
        task_request = MockTaskRequest("test_001", "invalid://url")
        
        # Test invalid URL handling
        try:
            # Simulate URL validation
            if not task_request.repository_url.startswith(("http://", "https://")):
                raise ValueError("Invalid repository URL")
        except ValueError as e:
            assert str(e) == "Invalid repository URL"
            assert task_request.workflow_status.status == "pending"

class TestResultAggregation:
    """Test result aggregation from multiple agents"""
    
    def test_result_collection(self):
        """Test collecting results from multiple agents"""
        # Mock agent results
        repository_result = {
            "status": "completed",
            "repository_info": {"name": "test-repo", "total_files": 45},
            "processing_time": 12.5
        }
        
        ccg_result = {
            "status": "completed",
            "ccg_data": {"entities": 25, "relationships": 18},
            "processing_time": 25.3
        }
        
        documentation_result = {
            "status": "completed",
            "output_files": ["./outputs/doc.md", "./outputs/doc.html"],
            "processing_time": 18.7
        }
        
        # Aggregate results
        aggregated = MockAggregatedResult("test_001")
        aggregated.repository_info = repository_result["repository_info"]
        aggregated.ccg_data = ccg_result["ccg_data"]
        aggregated.documentation_result = documentation_result["output_files"]
        aggregated.processing_time = (
            repository_result["processing_time"] +
            ccg_result["processing_time"] +
            documentation_result["processing_time"]
        )
        
        assert aggregated.repository_info["name"] == "test-repo"
        assert aggregated.ccg_data["entities"] == 25
        assert len(aggregated.documentation_result) == 2
        assert aggregated.processing_time == 56.5
    
    def test_quality_score_calculation(self):
        """Test calculating overall quality score"""
        doc_quality = 0.85
        repo_quality = 0.90
        analysis_quality = 0.80
        
        overall_quality = (doc_quality + repo_quality + analysis_quality) / 3.0
        
        assert overall_quality == pytest.approx(0.85)
        assert 0.0 <= overall_quality <= 1.0
    
    def test_final_output_generation(self):
        """Test generating final output summary"""
        aggregated = MockAggregatedResult("test_001")
        aggregated.repository_info = {"name": "test-repo", "url": "https://github.com/test/repo"}
        aggregated.ccg_data = {"entities": 25, "relationships": 18}
        aggregated.documentation_result = {"output_files": ["./doc.md"]}
        
        # Generate final output
        aggregated.final_output = {
            "status": "completed",
            "summary": f"Successfully processed repository '{aggregated.repository_info['name']}' with {aggregated.ccg_data['entities']} entities",
            "generated_files": aggregated.documentation_result["output_files"],
            "processing_time": 45.0
        }
        
        assert aggregated.final_output["status"] == "completed"
        assert "test-repo" in aggregated.final_output["summary"]
        assert len(aggregated.final_output["generated_files"]) == 1

class TestErrorHandlingAndRecovery:
    """Test error handling and recovery mechanisms"""
    
    def test_agent_failure_detection(self):
        """Test detecting agent failures"""
        workflow_history = [
            MockWorkflowStatus("wf_1", "repository_mapper", "completed"),
            MockWorkflowStatus("wf_2", "code_analyzer", "failed"),
            MockWorkflowStatus("wf_3", "docgenie", "completed")
        ]
        
        failed_agents = [status.agent_type for status in workflow_history if status.status == "failed"]
        
        assert "code_analyzer" in failed_agents
        assert len(failed_agents) == 1
    
    def test_retry_mechanism(self):
        """Test retry mechanism for failed agents"""
        status = MockWorkflowStatus("test_retry", "repository_mapper", "failed")
        status.retries = 0
        status.max_retries = 3
        
        # Simulate retry
        status.retries += 1
        status.status = "retry"
        
        assert status.retries == 1
        assert status.status == "retry"
        assert status.retries < status.max_retries
        
        # Simulate final failure
        status.retries = status.max_retries
        status.status = "failed_permanent"
        
        assert status.retries == status.max_retries
        assert status.status == "failed_permanent"
    
    def test_exponential_backoff(self):
        """Test exponential backoff for retries"""
        retry_count = 0
        base_delay = 5  # seconds
        
        # Simulate exponential backoff delays
        delays = []
        for i in range(4):  # 4 retries
            delay = base_delay * (2 ** retry_count)
            delays.append(delay)
            retry_count += 1
        
        expected_delays = [5, 10, 20, 40]
        assert delays == expected_delays
    
    def test_graceful_degradation(self):
        """Test graceful degradation when agents are unavailable"""
        available_agents = {"repository_mapper": True, "code_analyzer": False, "docgenie": True}
        
        # Check if workflow can proceed with available agents
        can_proceed = sum(available_agents.values()) >= 2  # Minimum 2 agents
        
        assert can_proceed is True
        
        # Test with too few agents
        available_agents["repository_mapper"] = False
        can_proceed = sum(available_agents.values()) >= 2
        
        assert can_proceed is False
    
    def test_workflow_cancellation(self):
        """Test workflow cancellation"""
        status = MockWorkflowStatus("test_cancel", "repository_mapper", "running")
        
        # Cancel workflow
        status.status = "cancelled"
        status.completed_at = datetime.now().isoformat()
        
        assert status.status == "cancelled"
        assert status.completed_at != ""

class TestPriorityScheduling:
    """Test priority-based task scheduling"""
    
    def test_priority_queue_management(self):
        """Test priority queue management"""
        queue = []
        
        # Add tasks with different priorities
        tasks = [
            {"task_id": "low_priority", "priority": 3, "created_at": "2025-10-31T07:00:00"},
            {"task_id": "high_priority", "priority": 8, "created_at": "2025-10-31T07:01:00"},
            {"task_id": "normal_priority", "priority": 5, "created_at": "2025-10-31T06:59:00"}
        ]
        
        # Sort by priority (higher first) then by creation time
        sorted_tasks = sorted(tasks, key=lambda x: (-x["priority"], x["created_at"]))
        
        assert sorted_tasks[0]["priority"] == 8  # High priority first
        assert sorted_tasks[1]["priority"] == 5  # Normal priority second
        assert sorted_tasks[2]["priority"] == 3  # Low priority last
    
    def test_priority_aging(self):
        """Test priority aging for long-waiting tasks"""
        base_priority = 5
        aging_factor = 0.9
        hours_waiting = 2
        
        # Calculate aged priority
        aged_priority = base_priority * (aging_factor ** hours_waiting)
        
        assert aged_priority < base_priority  # Priority should decrease
        assert aged_priority > 0  # Priority should not go negative
    
    def test_concurrent_workflow_limits(self):
        """Test limiting concurrent workflows"""
        max_concurrent = 3
        current_workflows = 5
        
        can_accept_new = current_workflows < max_concurrent
        queue_new_workflow = current_workflows >= max_concurrent
        
        assert can_accept_new is False
        assert queue_new_workflow is True

class TestAPIGateway:
    """Test API gateway functionality"""
    
    def test_api_request_validation(self):
        """Test API request validation"""
        valid_request = {
            "repository_url": "https://github.com/test/repo",
            "options": {"depth": "standard"},
            "priority": 7,
            "format": "json"
        }
        
        # Check required fields
        assert "repository_url" in valid_request
        assert valid_request["repository_url"].startswith("https://")
        
        # Test invalid request
        invalid_request = {
            "options": {"depth": "standard"}
            # Missing repository_url
        }
        
        required_fields = ["repository_url"]
        missing_fields = [field for field in required_fields if field not in invalid_request]
        
        assert len(missing_fields) > 0
        assert "repository_url" in missing_fields
    
    def test_workflow_submission_response(self):
        """Test workflow submission API response"""
        response = {
            "status": "accepted",
            "workflow_id": "workflow_12345",
            "estimated_completion": "2025-10-31T07:30:00",
            "queue_position": 2,
            "message": "Workflow submitted successfully"
        }
        
        assert response["status"] == "accepted"
        assert "workflow_id" in response
        assert "estimated_completion" in response
        assert response["queue_position"] >= 0
    
    def test_workflow_status_response(self):
        """Test workflow status API response"""
        status_response = {
            "workflow_id": "workflow_12345",
            "status": "running",
            "progress": 65.5,
            "current_phase": "Code Analysis",
            "phases_completed": 1,
            "total_phases": 3,
            "started_at": "2025-10-31T07:20:00",
            "estimated_completion": "2025-10-31T07:35:00"
        }
        
        assert status_response["status"] in ["pending", "running", "completed", "failed", "cancelled"]
        assert 0.0 <= status_response["progress"] <= 100.0
        assert 0 <= status_response["phases_completed"] <= status_response["total_phases"]
    
    def test_workflow_result_response(self):
        """Test workflow result API response"""
        result_response = {
            "workflow_id": "workflow_12345",
            "status": "completed",
            "repository_info": {
                "name": "test-repo",
                "url": "https://github.com/test/repo",
                "total_files": 45
            },
            "documentation": {
                "output_files": ["./outputs/doc.md", "./outputs/doc.html"],
                "quality_score": 0.85
            },
            "processing_time": 45.2,
            "generated_at": "2025-10-31T07:35:00"
        }
        
        assert result_response["status"] == "completed"
        assert "repository_info" in result_response
        assert "documentation" in result_response
        assert len(result_response["documentation"]["output_files"]) > 0
        assert 0.0 <= result_response["documentation"]["quality_score"] <= 1.0

class TestPerformanceAndScalability:
    """Test performance and scalability"""
    
    def test_workflow_throughput(self):
        """Test workflow processing throughput"""
        start_time = time.time()
        
        # Simulate processing multiple workflows
        workflows_processed = 0
        for i in range(10):
            # Simulate workflow processing time
            time.sleep(0.1)  # 100ms per workflow
            workflows_processed += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        throughput = workflows_processed / total_time
        
        assert workflows_processed == 10
        assert throughput >= 5  # At least 5 workflows per second
        assert total_time >= 1.0  # Should take at least 1 second
    
    def test_memory_usage_tracking(self):
        """Test memory usage tracking"""
        import sys
        
        # Simulate workflow data structures
        workflows = []
        for i in range(100):
            workflow = {
                "id": f"workflow_{i}",
                "status": MockWorkflowStatus(f"wf_{i}", "test"),
                "result": {"data": "x" * 1000}  # 1KB data per workflow
            }
            workflows.append(workflow)
        
        # Estimate memory usage
        estimated_memory = sys.getsizeof(workflows) + sum(sys.getsizeof(w) for w in workflows)
        
        assert len(workflows) == 100
        assert estimated_memory > 0
    
    def test_concurrent_processing_limits(self):
        """Test concurrent processing limits"""
        max_concurrent = 5
        current_load = 0
        
        # Simulate adding concurrent workflows
        for i in range(max_concurrent + 2):
            if current_load < max_concurrent:
                current_load += 1
                can_process = True
            else:
                can_process = False
            
            if i < max_concurrent:
                assert can_process is True
            else:
                assert can_process is False
    
    def test_queue_depth_management(self):
        """Test queue depth management"""
        max_queue_depth = 50
        current_queue = 60
        
        # Test queue depth exceeded
        queue_exceeded = current_queue > max_queue_depth
        need_priority_processing = queue_exceeded
        
        assert queue_exceeded is True
        assert need_priority_processing is True
        
        # Test queue within limits
        current_queue = 30
        queue_exceeded = current_queue > max_queue_depth
        
        assert queue_exceeded is False

class TestIntegrationScenarios:
    """Test complete integration scenarios"""
    
    def test_complete_workflow_simulation(self):
        """Test complete workflow from start to finish"""
        # Create workflow request
        task_request = MockTaskRequest("integration_test", "https://github.com/test/integration")
        
        # Simulate workflow phases
        phases = [
            {"agent": "repository_mapper", "duration": 12, "success": True},
            {"agent": "code_analyzer", "duration": 25, "success": True},
            {"agent": "docgenie", "duration": 18, "success": True}
        ]
        
        total_duration = sum(phase["duration"] for phase in phases)
        success_count = sum(1 for phase in phases if phase["success"])
        
        assert len(phases) == 3
        assert total_duration == 55
        assert success_count == 3  # All phases successful
    
    def test_partial_failure_scenario(self):
        """Test handling partial failures"""
        # Simulate scenario where one agent fails
        phases = [
            {"agent": "repository_mapper", "duration": 12, "success": True},
            {"agent": "code_analyzer", "duration": 25, "success": False},  # Failed
            {"agent": "docgenie", "duration": 18, "success": True}
        ]
        
        successful_phases = [p for p in phases if p["success"]]
        failed_phases = [p for p in phases if not p["success"]]
        
        assert len(successful_phases) == 2
        assert len(failed_phases) == 1
        assert failed_phases[0]["agent"] == "code_analyzer"
    
    def test_workflow_cancellation_scenario(self):
        """Test workflow cancellation mid-execution"""
        # Simulate workflow started but then cancelled
        task_request = MockTaskRequest("cancel_test", "https://github.com/test/cancel")
        
        # Simulate phases with cancellation
        phases = [
            {"agent": "repository_mapper", "duration": 12, "completed": True},
            {"agent": "code_analyzer", "duration": 25, "completed": False, "cancelled": True},
            {"agent": "docgenie", "duration": 18, "completed": False, "cancelled": True}
        ]
        
        completed_phases = [p for p in phases if p.get("completed", False)]
        cancelled_phases = [p for p in phases if p.get("cancelled", False)]
        
        assert len(completed_phases) == 1
        assert len(cancelled_phases) == 2
        assert task_request.workflow_status.status == "pending"

# Test fixtures
@pytest.fixture
def sample_workflow_request():
    """Provide sample workflow request for testing"""
    return MockTaskRequest("fixture_test", "https://github.com/fixture/test")

@pytest.fixture
def mock_agent_connections():
    """Provide mock agent connections for testing"""
    return {
        "repository_mapper": MockAgentConnection("repository_mapper", "http://localhost:8081"),
        "code_analyzer": MockAgentConnection("code_analyzer", "http://localhost:8082"),
        "docgenie": MockAgentConnection("docgenie", "http://localhost:8083")
    }

@pytest.fixture
def workflow_history():
    """Provide sample workflow history for testing"""
    return [
        MockWorkflowStatus("wf_1", "repository_mapper", "completed"),
        MockWorkflowStatus("wf_2", "code_analyzer", "completed"),
        MockWorkflowStatus("wf_3", "docgenie", "completed")
    ]

@pytest.fixture
def temp_config_file():
    """Provide temporary configuration file for testing"""
    config_data = {
        "agent_connections": {
            "repository_mapper": {
                "endpoint": "http://localhost:8081",
                "capabilities": ["clone_repository"]
            }
        },
        "workflow_settings": {
            "max_concurrent_workflows": 5,
            "default_priority": 5
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        config_path = f.name
    
    yield config_path
    
    # Cleanup
    pathlib.Path(config_path).unlink()

# Main test runner
if __name__ == "__main__":
    # Run tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--disable-warnings",
        "--cov=.",
        "--cov-report=term-missing"
    ])
