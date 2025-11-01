#!/usr/bin/env python3
"""
Codebase Genius - Integration Test Suite
Phase 7: Complete end-to-end pipeline validation

This test suite validates the complete multi-agent system:
Repository Mapper → Code Analyzer → DocGenie → Supervisor

Author: Cavin Otieno
Date: 2025-10-31
"""

import asyncio
import json
import time
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import requests
import tempfile
import shutil
from urllib.parse import urlparse

# Test result tracking
@dataclass
class TestResult:
    """Individual test result tracking"""
    test_name: str
    status: str  # PASS, FAIL, SKIP, ERROR
    duration: float
    repository: str
    error_message: Optional[str] = None
    output_files: List[str] = None
    metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []
        if self.metrics is None:
            self.metrics = {}

@dataclass 
class IntegrationTestResults:
    """Complete integration test results"""
    timestamp: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    total_duration: float
    test_results: List[TestResult]
    system_metrics: Dict[str, Any]
    
class IntegrationTestSuite:
    """Comprehensive integration testing framework"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.results_dir = self.base_dir / "results"
        self.samples_dir = self.base_dir / "samples"
        self.benchmarks_dir = self.base_dir / "benchmarks"
        self.utils_dir = self.base_dir / "utils"
        
        # Agent endpoints
        self.agent_ports = {
            "supervisor": 8080,
            "repository_mapper": 8081, 
            "code_analyzer": 8082,
            "docgenie": 8083
        }
        
        # Test repositories configuration
        self.test_repositories = [
            {
                "name": "simple-python",
                "url": "https://github.com/octocat/Hello-World",
                "type": "python",
                "description": "Simple Python repository for basic testing",
                "expected_files": 10,
                "max_duration": 60
            },
            {
                "name": "complex-python", 
                "url": "https://github.com/psf/requests",
                "type": "python",
                "description": "Complex Python project with multiple modules",
                "expected_files": 50,
                "max_duration": 300
            },
            {
                "name": "jac-example",
                "url": "https://github.com/jaseem/jaic-examples", 
                "type": "jac",
                "description": "JAC language examples repository",
                "expected_files": 20,
                "max_duration": 180
            }
        ]
        
        # Ensure results directory exists
        self.results_dir.mkdir(exist_ok=True)
        
    def start_agents(self) -> bool:
        """Start all required agents for testing"""
        print("🚀 Starting all agents for integration testing...")
        
        try:
            # Start supervisor agent
            supervisor_process = subprocess.Popen([
                "jac", "serve", "code/supervisor-agent/main.jac", 
                "--host", "0.0.0.0", "--port", str(self.agent_ports["supervisor"])
            ], cwd=self.base_dir.parent)
            
            # Start repository mapper
            mapper_process = subprocess.Popen([
                "jac", "serve", "code/repository-mapper-agent/main.jac",
                "--host", "0.0.0.0", "--port", str(self.agent_ports["repository_mapper"])
            ], cwd=self.base_dir.parent)
            
            # Start code analyzer  
            analyzer_process = subprocess.Popen([
                "jac", "serve", "code/code-analyzer-agent/main.jac",
                "--host", "0.0.0.0", "--port", str(self.agent_ports["code_analyzer"])
            ], cwd=self.base_dir.parent)
            
            # Start docgenie
            docgenie_process = subprocess.Popen([
                "jac", "serve", "code/docgenie-agent/main.jac",
                "--host", "0.0.0.0", "--port", str(self.agent_ports["docgenie"])
            ], cwd=self.base_dir.parent)
            
            # Wait for agents to initialize
            time.sleep(10)
            
            # Verify all agents are running
            for agent_name, port in self.agent_ports.items():
                if not self._check_agent_health(agent_name, port):
                    print(f"❌ Agent {agent_name} failed to start on port {port}")
                    return False
            
            print("✅ All agents started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start agents: {e}")
            return False
    
    def stop_agents(self):
        """Stop all running agents"""
        print("🛑 Stopping all agents...")
        try:
            # Kill all jac serve processes
            subprocess.run(["pkill", "-f", "jac serve"], check=False)
            time.sleep(2)
            print("✅ All agents stopped")
        except Exception as e:
            print(f"⚠️  Warning stopping agents: {e}")
    
    def _check_agent_health(self, agent_name: str, port: int) -> bool:
        """Check if agent is healthy and responding"""
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    async def test_end_to_end_pipeline(self, repo_config: Dict) -> TestResult:
        """Test complete pipeline: Repository Mapper → Code Analyzer → DocGenie → Supervisor"""
        test_name = f"end_to_end_{repo_config['name']}"
        start_time = time.time()
        
        try:
            # Step 1: Submit workflow to supervisor
            print(f"📋 Testing {test_name}: Submitting workflow...")
            
            workflow_request = {
                "repository_url": repo_config["url"],
                "priority": 5,
                "output_format": "markdown",
                "include_diagrams": True
            }
            
            supervisor_response = requests.post(
                f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows",
                json=workflow_request,
                timeout=30
            )
            
            if supervisor_response.status_code != 201:
                raise Exception(f"Failed to submit workflow: {supervisor_response.text}")
            
            workflow_data = supervisor_response.json()
            workflow_id = workflow_data["workflow_id"]
            print(f"✅ Workflow submitted with ID: {workflow_id}")
            
            # Step 2: Monitor workflow progress
            print(f"⏳ Monitoring workflow progress...")
            max_wait = repo_config["max_duration"]
            poll_interval = 5
            elapsed = 0
            
            while elapsed < max_wait:
                status_response = requests.get(
                    f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows/{workflow_id}/status",
                    timeout=10
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data["status"]
                    
                    print(f"📊 Workflow status: {status}")
                    
                    if status == "completed":
                        # Step 3: Retrieve results
                        print("✅ Workflow completed, retrieving results...")
                        result_response = requests.get(
                            f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows/{workflow_id}/results",
                            timeout=30
                        )
                        
                        if result_response.status_code == 200:
                            results = result_response.json()
                            
                            # Step 4: Validate results
                            output_files = self._validate_pipeline_results(results, repo_config)
                            
                            # Step 5: Calculate quality metrics
                            metrics = self._calculate_quality_metrics(results, repo_config)
                            
                            duration = time.time() - start_time
                            return TestResult(
                                test_name=test_name,
                                status="PASS",
                                duration=duration,
                                repository=repo_config["url"],
                                output_files=output_files,
                                metrics=metrics
                            )
                        else:
                            raise Exception(f"Failed to retrieve results: {result_response.text}")
                    
                    elif status == "failed":
                        raise Exception(f"Workflow failed: {status_data.get('error', 'Unknown error')}")
                    
                    # Wait before next poll
                    await asyncio.sleep(poll_interval)
                    elapsed += poll_interval
                else:
                    raise Exception(f"Failed to get workflow status: {status_response.text}")
            
            raise Exception(f"Workflow timeout after {max_wait} seconds")
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Pipeline test failed: {str(e)}\n{traceback.format_exc()}"
            print(f"❌ {error_msg}")
            
            return TestResult(
                test_name=test_name,
                status="FAIL",
                duration=duration,
                repository=repo_config["url"],
                error_message=error_msg
            )
    
    def _validate_pipeline_results(self, results: Dict, repo_config: Dict) -> List[str]:
        """Validate pipeline output files and structure"""
        output_files = []
        
        # Check for documentation output
        if "documentation" in results:
            doc_data = results["documentation"]
            
            # Validate markdown structure
            if "markdown" in doc_data:
                markdown_content = doc_data["markdown"]
                if len(markdown_content) > 1000:  # Basic length check
                    output_files.append("documentation.md")
                    print(f"✅ Generated documentation: {len(markdown_content)} characters")
                else:
                    raise Exception("Generated documentation too short")
            
            # Validate diagram files
            if "diagrams" in doc_data:
                diagrams = doc_data["diagrams"]
                for diagram_type, diagram_data in diagrams.items():
                    if "file_path" in diagram_data:
                        output_files.append(diagram_data["file_path"])
                        print(f"✅ Generated diagram: {diagram_type}")
        
        # Check for analysis results
        if "analysis" in results:
            analysis = results["analysis"]
            
            # Validate CCG data
            if "ccg" in analysis:
                ccg_data = analysis["ccg"]
                if "entities" in ccg_data and "relationships" in ccg_data:
                    num_entities = len(ccg_data["entities"])
                    num_relationships = len(ccg_data["relationships"])
                    print(f"✅ CCG Analysis: {num_entities} entities, {num_relationships} relationships")
                    
                    # Check against expected file count
                    if num_entities >= repo_config["expected_files"]:
                        print(f"✅ Entity count meets expectations (expected: {repo_config['expected_files']})")
                    else:
                        print(f"⚠️  Entity count below expectations (got: {num_entities}, expected: {repo_config['expected_files']})")
        
        return output_files
    
    def _calculate_quality_metrics(self, results: Dict, repo_config: Dict) -> Dict[str, Any]:
        """Calculate documentation quality metrics"""
        metrics = {}
        
        # Documentation completeness
        if "documentation" in results:
            doc_data = results["documentation"]
            if "markdown" in doc_data:
                markdown_content = doc_data["markdown"]
                
                # Basic quality metrics
                metrics["doc_length"] = len(markdown_content)
                metrics["has_api_section"] = "API" in markdown_content or "Functions" in markdown_content
                metrics["has_installation"] = "Install" in markdown_content.lower()
                metrics["has_usage"] = "Usage" in markdown_content or "Example" in markdown_content
                metrics["has_architecture"] = "Architecture" in markdown_content or "Structure" in markdown_content
                
                # Calculate completeness score
                sections_present = sum([
                    metrics["has_api_section"],
                    metrics["has_installation"], 
                    metrics["has_usage"],
                    metrics["has_architecture"]
                ])
                metrics["completeness_score"] = sections_present / 4.0
        
        # Analysis quality
        if "analysis" in results:
            analysis = results["analysis"]
            if "ccg" in analysis:
                ccg_data = analysis["ccg"]
                metrics["total_entities"] = len(ccg_data.get("entities", []))
                metrics["total_relationships"] = len(ccg_data.get("relationships", []))
                
                # Relationship density
                if metrics["total_entities"] > 0:
                    metrics["relationship_density"] = metrics["total_relationships"] / metrics["total_entities"]
                else:
                    metrics["relationship_density"] = 0
        
        # Repository processing
        if "repository" in results:
            repo_data = results["repository"]
            metrics["files_processed"] = repo_data.get("file_count", 0)
            metrics["repository_size_kb"] = repo_data.get("size_kb", 0)
            metrics["primary_language"] = repo_data.get("language", "unknown")
        
        return metrics
    
    async def test_agent_isolation(self) -> TestResult:
        """Test individual agent functionality in isolation"""
        test_name = "agent_isolation"
        start_time = time.time()
        
        try:
            # Test repository mapper independently
            print("🧪 Testing Repository Mapper isolation...")
            mapper_response = requests.get(
                f"http://localhost:{self.agent_ports['repository_mapper']}/api/v1/health",
                timeout=10
            )
            if mapper_response.status_code != 200:
                raise Exception("Repository mapper health check failed")
            
            # Test code analyzer independently
            print("🧪 Testing Code Analyzer isolation...")
            analyzer_response = requests.get(
                f"http://localhost:{self.agent_ports['code_analyzer']}/api/v1/health",
                timeout=10
            )
            if analyzer_response.status_code != 200:
                raise Exception("Code analyzer health check failed")
            
            # Test docgenie independently
            print("🧪 Testing DocGenie isolation...")
            docgenie_response = requests.get(
                f"http://localhost:{self.agent_ports['docgenie']}/api/v1/health",
                timeout=10
            )
            if docgenie_response.status_code != 200:
                raise Exception("DocGenie health check failed")
            
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status="PASS",
                duration=duration,
                repository="local_health_check",
                metrics={"agents_healthy": 3}
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status="FAIL",
                duration=duration,
                repository="local_health_check", 
                error_message=str(e)
            )
    
    async def test_error_recovery(self) -> TestResult:
        """Test error handling and recovery mechanisms"""
        test_name = "error_recovery"
        start_time = time.time()
        
        try:
            # Test invalid repository URL
            print("🧪 Testing invalid repository handling...")
            invalid_request = {
                "repository_url": "https://github.com/nonexistent/invalid-repo-12345",
                "priority": 5
            }
            
            response = requests.post(
                f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows",
                json=invalid_request,
                timeout=30
            )
            
            # Should handle gracefully (may return 400 or accept and fail later)
            if response.status_code not in [201, 400, 422]:
                raise Exception(f"Unexpected status code for invalid repo: {response.status_code}")
            
            # Test malformed request
            print("🧪 Testing malformed request handling...")
            malformed_response = requests.post(
                f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows",
                json={"invalid": "data"},
                timeout=10
            )
            
            if malformed_response.status_code not in [400, 422]:
                raise Exception(f"Expected 400/422 for malformed request, got: {malformed_response.status_code}")
            
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status="PASS",
                duration=duration,
                repository="error_scenarios",
                metrics={
                    "invalid_repo_handled": response.status_code != 500,
                    "malformed_request_handled": malformed_response.status_code in [400, 422]
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status="FAIL",
                duration=duration,
                repository="error_scenarios",
                error_message=str(e)
            )
    
    async def run_performance_benchmark(self) -> TestResult:
        """Run performance benchmarks"""
        test_name = "performance_benchmark"
        start_time = time.time()
        
        try:
            # Simple repository for benchmark
            simple_repo = self.test_repositories[0]
            
            print(f"🏃 Running performance benchmark with {simple_repo['name']}")
            
            # Start timing
            workflow_request = {
                "repository_url": simple_repo["url"],
                "priority": 1,  # Highest priority for benchmark
                "output_format": "markdown"
            }
            
            bench_start = time.time()
            
            # Submit and wait for completion
            response = requests.post(
                f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows",
                json=workflow_request,
                timeout=30
            )
            
            if response.status_code != 201:
                raise Exception(f"Benchmark submission failed: {response.text}")
            
            workflow_id = response.json()["workflow_id"]
            
            # Monitor with timeout
            timeout = 300  # 5 minutes
            elapsed = 0
            poll_interval = 5
            
            while elapsed < timeout:
                status_response = requests.get(
                    f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows/{workflow_id}/status",
                    timeout=10
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    
                    if status_data["status"] == "completed":
                        bench_duration = time.time() - bench_start
                        
                        # Get results for metrics
                        result_response = requests.get(
                            f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows/{workflow_id}/results",
                            timeout=30
                        )
                        
                        if result_response.status_code == 200:
                            results = result_response.json()
                            metrics = self._calculate_quality_metrics(results, simple_repo)
                            
                            total_duration = time.time() - start_time
                            return TestResult(
                                test_name=test_name,
                                status="PASS",
                                duration=total_duration,
                                repository=simple_repo["url"],
                                metrics={
                                    "benchmark_duration": bench_duration,
                                    "total_duration": total_duration,
                                    "files_per_second": metrics.get("files_processed", 0) / bench_duration if bench_duration > 0 else 0,
                                    "documentation_quality": metrics.get("completeness_score", 0),
                                    "entities_per_second": metrics.get("total_entities", 0) / bench_duration if bench_duration > 0 else 0
                                }
                            )
                    elif status_data["status"] == "failed":
                        raise Exception(f"Benchmark workflow failed: {status_data.get('error')}")
                
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval
            
            raise Exception("Benchmark timed out")
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status="FAIL", 
                duration=duration,
                repository="performance_test",
                error_message=str(e)
            )
    
    async def run_load_test(self, concurrent_workflows: int = 3) -> TestResult:
        """Run load testing with multiple concurrent workflows"""
        test_name = f"load_test_{concurrent_workflows}_concurrent"
        start_time = time.time()
        
        try:
            print(f"🏋️ Running load test with {concurrent_workflows} concurrent workflows...")
            
            # Start multiple workflows concurrently
            workflow_ids = []
            
            for i in range(concurrent_workflows):
                request_data = {
                    "repository_url": self.test_repositories[0]["url"],  # Use simple repo
                    "priority": 10 - i,  # Different priorities
                    "output_format": "markdown"
                }
                
                response = requests.post(
                    f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows",
                    json=request_data,
                    timeout=30
                )
                
                if response.status_code == 201:
                    workflow_ids.append(response.json()["workflow_id"])
                else:
                    print(f"⚠️ Failed to submit workflow {i+1}: {response.status_code}")
            
            if not workflow_ids:
                raise Exception("No workflows submitted successfully")
            
            print(f"✅ Submitted {len(workflow_ids)} workflows")
            
            # Monitor all workflows
            completed = 0
            failed = 0
            max_wait = 600  # 10 minutes
            elapsed = 0
            poll_interval = 10
            
            while elapsed < max_wait and (completed + failed) < len(workflow_ids):
                for workflow_id in workflow_ids:
                    if workflow_id in workflow_ids:  # Still tracking this workflow
                        try:
                            status_response = requests.get(
                                f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows/{workflow_id}/status",
                                timeout=10
                            )
                            
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                status = status_data["status"]
                                
                                if status == "completed":
                                    completed += 1
                                    workflow_ids.remove(workflow_id)  # Remove from tracking
                                    print(f"✅ Workflow {workflow_id} completed")
                                    
                                elif status == "failed":
                                    failed += 1
                                    workflow_ids.remove(workflow_id)  # Remove from tracking
                                    print(f"❌ Workflow {workflow_id} failed")
                        except:
                            pass  # Continue monitoring other workflows
                
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval
            
            duration = time.time() - start_time
            
            # Calculate load test metrics
            total_workflows = completed + failed
            success_rate = completed / total_workflows if total_workflows > 0 else 0
            
            return TestResult(
                test_name=test_name,
                status="PASS" if success_rate >= 0.8 else "FAIL",  # 80% success rate
                duration=duration,
                repository="load_test",
                metrics={
                    "concurrent_workflows": concurrent_workflows,
                    "completed": completed,
                    "failed": failed,
                    "success_rate": success_rate,
                    "workflows_per_minute": (completed / (duration / 60)) if duration > 0 else 0
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status="FAIL",
                duration=duration,
                repository="load_test",
                error_message=str(e)
            )
    
    async def run_comprehensive_test_suite(self) -> IntegrationTestResults:
        """Run the complete integration test suite"""
        print("🧪 Starting comprehensive integration test suite...")
        print("=" * 60)
        
        all_results = []
        suite_start_time = time.time()
        
        try:
            # Test 1: Agent Isolation
            print("\n1️⃣ Testing Agent Isolation...")
            isolation_result = await self.test_agent_isolation()
            all_results.append(isolation_result)
            print(f"   Result: {isolation_result.status} ({isolation_result.duration:.2f}s)")
            
            # Test 2: End-to-End Pipeline Tests
            print("\n2️⃣ Testing End-to-End Pipeline...")
            for repo_config in self.test_repositories:
                print(f"   📦 Testing {repo_config['name']}...")
                pipeline_result = await self.test_end_to_end_pipeline(repo_config)
                all_results.append(pipeline_result)
                print(f"   Result: {pipeline_result.status} ({pipeline_result.duration:.2f}s)")
            
            # Test 3: Error Recovery
            print("\n3️⃣ Testing Error Recovery...")
            error_result = await self.test_error_recovery()
            all_results.append(error_result)
            print(f"   Result: {error_result.status} ({error_result.duration:.2f}s)")
            
            # Test 4: Performance Benchmark
            print("\n4️⃣ Running Performance Benchmark...")
            perf_result = await self.run_performance_benchmark()
            all_results.append(perf_result)
            print(f"   Result: {perf_result.status} ({perf_result.duration:.2f}s)")
            
            # Test 5: Load Testing
            print("\n5️⃣ Running Load Tests...")
            load_result = await self.run_load_test(2)  # 2 concurrent workflows
            all_results.append(load_result)
            print(f"   Result: {load_result.status} ({load_result.duration:.2f}s)")
            
        except KeyboardInterrupt:
            print("\n⚠️ Test suite interrupted by user")
        except Exception as e:
            print(f"\n❌ Test suite error: {e}")
        
        finally:
            total_duration = time.time() - suite_start_time
            
            # Calculate summary statistics
            passed = len([r for r in all_results if r.status == "PASS"])
            failed = len([r for r in all_results if r.status == "FAIL"])
            skipped = len([r for r in all_results if r.status == "SKIP"])
            errors = len([r for r in all_results if r.status == "ERROR"])
            
            # Create results object
            test_results = IntegrationTestResults(
                timestamp=datetime.now().isoformat(),
                total_tests=len(all_results),
                passed=passed,
                failed=failed, 
                skipped=skipped,
                errors=errors,
                total_duration=total_duration,
                test_results=all_results,
                system_metrics=self._collect_system_metrics()
            )
            
            # Save results
            await self._save_test_results(test_results)
            
            # Print summary
            self._print_test_summary(test_results)
            
            return test_results
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics"""
        try:
            import psutil
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": psutil.disk_usage('/').percent
            }
        except ImportError:
            return {"system_metrics": "psutil not available"}
    
    async def _save_test_results(self, results: IntegrationTestResults):
        """Save test results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = self.results_dir / f"integration_test_results_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(asdict(results), f, indent=2)
        
        # Save human-readable report
        report_file = self.results_dir / f"integration_test_report_{timestamp}.md"
        with open(report_file, 'w') as f:
            f.write(self._generate_test_report(results))
        
        print(f"\n💾 Test results saved:")
        print(f"   📊 JSON: {json_file}")
        print(f"   📝 Report: {report_file}")
    
    def _generate_test_report(self, results: IntegrationTestResults) -> str:
        """Generate human-readable test report"""
        report = f"""# Codebase Genius Integration Test Report

**Generated:** {results.timestamp}
**Duration:** {results.total_duration:.2f} seconds

## Summary

- **Total Tests:** {results.total_tests}
- **Passed:** {results.passed} ✅
- **Failed:** {results.failed} ❌
- **Skipped:** {results.skipped} ⏭️
- **Errors:** {results.errors} 💥

## Test Results

"""
        
        for test_result in results.test_results:
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌", 
                "SKIP": "⏭️",
                "ERROR": "💥"
            }.get(test_result.status, "❓")
            
            report += f"""### {status_icon} {test_result.test_name}

- **Status:** {test_result.status}
- **Duration:** {test_result.duration:.2f}s
- **Repository:** {test_result.repository}
- **Output Files:** {len(test_result.output_files)}

"""
            
            if test_result.metrics:
                report += "**Metrics:**\n"
                for key, value in test_result.metrics.items():
                    report += f"- {key}: {value}\n"
                report += "\n"
            
            if test_result.error_message:
                report += f"**Error:** {test_result.error_message}\n\n"
        
        # System metrics
        if results.system_metrics:
            report += "## System Metrics\n\n"
            for key, value in results.system_metrics.items():
                report += f"- {key}: {value}\n"
        
        return report
    
    def _print_test_summary(self, results: IntegrationTestResults):
        """Print test summary to console"""
        print("\n" + "=" * 60)
        print("🎯 INTEGRATION TEST SUMMARY")
        print("=" * 60)
        print(f"Total Duration: {results.total_duration:.2f} seconds")
        print(f"Total Tests: {results.total_tests}")
        print(f"Passed: {results.passed} ✅")
        print(f"Failed: {results.failed} ❌")
        print(f"Success Rate: {(results.passed / results.total_tests * 100):.1f}%" if results.total_tests > 0 else "N/A")
        print("=" * 60)

async def main():
    """Main test execution"""
    test_suite = IntegrationTestSuite()
    
    try:
        # Start agents
        if not test_suite.start_agents():
            print("❌ Failed to start agents. Exiting.")
            return 1
        
        # Run comprehensive test suite
        results = await test_suite.run_comprehensive_test_suite()
        
        # Return exit code based on results
        if results.failed > 0 or results.errors > 0:
            print(f"\n❌ Integration tests completed with {results.failed} failures and {results.errors} errors")
            return 1
        else:
            print(f"\n✅ All integration tests passed!")
            return 0
            
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted")
        return 1
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return 1
    finally:
        test_suite.stop_agents()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
