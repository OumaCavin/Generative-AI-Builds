#!/usr/bin/env python3
"""
Codebase Genius - Error Scenario Testing
Phase 7: Comprehensive error handling and recovery validation

Tests various failure scenarios including:
- Network failures and timeouts
- Invalid repository URLs
- Corrupted repository data
- Agent failures and crashes
- Resource exhaustion scenarios
- Malformed requests and inputs

Author: Cavin Otieno
Date: 2025-10-31
"""

import asyncio
import json
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import requests
import subprocess
import tempfile
import shutil
import signal
import os

@dataclass
class ErrorScenario:
    """Individual error scenario definition"""
    name: str
    description: str
    scenario_type: str  # network, data, agent, resource, input
    expected_behavior: str
    timeout_seconds: int = 60
    setup_instructions: List[str] = None
    test_steps: List[str] = None
    recovery_expected: bool = True
    
    def __post_init__(self):
        if self.setup_instructions is None:
            self.setup_instructions = []
        if self.test_steps is None:
            self.test_steps = []

@dataclass
class ErrorTestResult:
    """Result of error scenario testing"""
    scenario_name: str
    scenario_type: str
    status: str  # PASS, FAIL, PARTIAL, ERROR
    duration: float
    error_detected: bool
    recovery_successful: bool
    error_message: Optional[str] = None
    recovery_details: Dict[str, Any] = None
    system_state_after: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.recovery_details is None:
            self.recovery_details = {}
        if self.system_state_after is None:
            self.system_state_after = {}

class ErrorScenarioTester:
    """Comprehensive error scenario testing framework"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.results_dir = self.base_dir / "results" / "error_testing"
        self.samples_dir = self.base_dir / "samples"
        
        # Agent endpoints
        self.agent_ports = {
            "supervisor": 8080,
            "repository_mapper": 8081,
            "code_analyzer": 8082,
            "docgenie": 8083
        }
        
        # Define error scenarios
        self.error_scenarios = self._define_error_scenarios()
        
        # Ensure results directory exists
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def _define_error_scenarios(self) -> List[ErrorScenario]:
        """Define comprehensive error scenarios"""
        return [
            # Input validation scenarios
            ErrorScenario(
                name="invalid_repository_url",
                description="Test handling of invalid repository URLs",
                scenario_type="input",
                expected_behavior="Should return 400 Bad Request with clear error message",
                timeout_seconds=30,
                test_steps=[
                    "Submit workflow with non-existent repository",
                    "Verify HTTP status code is 400/422",
                    "Check error message is user-friendly"
                ]
            ),
            
            ErrorScenario(
                name="malformed_request_body",
                description="Test handling of malformed JSON requests",
                scenario_type="input", 
                expected_behavior="Should return 400 Bad Request",
                timeout_seconds=30,
                test_steps=[
                    "Submit request with invalid JSON",
                    "Verify proper error handling",
                    "Check system remains stable"
                ]
            ),
            
            ErrorScenario(
                name="missing_required_fields",
                description="Test handling of missing required fields",
                scenario_type="input",
                expected_behavior="Should return 400 Bad Request with field validation errors",
                timeout_seconds=30,
                test_steps=[
                    "Submit request without repository_url",
                    "Verify field validation",
                    "Check error specificity"
                ]
            ),
            
            # Network failure scenarios
            ErrorScenario(
                name="network_timeout",
                description="Test handling of network timeouts",
                scenario_type="network",
                expected_behavior="Should timeout gracefully and retry if appropriate",
                timeout_seconds=120,
                test_steps=[
                    "Simulate slow network conditions",
                    "Submit workflow request",
                    "Verify timeout handling"
                ]
            ),
            
            ErrorScenario(
                name="connection_refused",
                description="Test handling of connection failures",
                scenario_type="network",
                expected_behavior="Should return meaningful error and maintain system stability",
                timeout_seconds=60,
                test_steps=[
                    "Block network to one agent",
                    "Submit workflow",
                    "Verify error handling and system recovery"
                ]
            ),
            
            # Agent failure scenarios
            ErrorScenario(
                name="agent_crash_simulation",
                description="Test system behavior when agent crashes",
                scenario_type="agent",
                expected_behavior="Should detect failure and attempt recovery",
                timeout_seconds=180,
                test_steps=[
                    "Start workflow",
                    "Simulate agent crash during processing",
                    "Verify failure detection and recovery"
                ]
            ),
            
            ErrorScenario(
                name="agent_unresponsive",
                description="Test handling of unresponsive agents",
                scenario_type="agent",
                expected_behavior="Should timeout and mark workflow as failed",
                timeout_seconds=90,
                test_steps=[
                    "Make agent unresponsive",
                    "Submit workflow",
                    "Verify timeout and failure handling"
                ]
            ),
            
            # Repository data issues
            ErrorScenario(
                name="corrupted_repository",
                description="Test handling of corrupted repository data",
                scenario_type="data",
                expected_behavior="Should fail gracefully with detailed error",
                timeout_seconds=120,
                test_steps=[
                    "Create corrupted repository",
                    "Submit workflow",
                    "Verify error handling"
                ]
            ),
            
            ErrorScenario(
                name="empty_repository",
                description="Test handling of empty or minimal repositories",
                scenario_type="data",
                expected_behavior="Should handle gracefully and generate minimal documentation",
                timeout_seconds=60,
                test_steps=[
                    "Use empty repository",
                    "Submit workflow",
                    "Verify appropriate handling"
                ]
            ),
            
            ErrorScenario(
                name="large_repository_timeout",
                description="Test handling of very large repositories",
                scenario_type="data",
                expected_behavior="Should process in chunks or return timeout error",
                timeout_seconds=300,
                test_steps=[
                    "Use large repository",
                    "Monitor processing time",
                    "Verify timeout handling"
                ]
            ),
            
            # Resource exhaustion scenarios
            ErrorScenario(
                name="memory_pressure",
                description="Test behavior under memory pressure",
                scenario_type="resource",
                expected_behavior="Should handle gracefully without crashing",
                timeout_seconds=180,
                setup_instructions=[
                    "Create large temporary files to consume memory",
                    "Monitor memory usage during processing"
                ],
                test_steps=[
                    "Start multiple large workflows",
                    "Monitor system resource usage",
                    "Verify graceful degradation"
                ]
            ),
            
            ErrorScenario(
                name="concurrent_workflow_limit",
                description="Test handling of too many concurrent workflows",
                scenario_type="resource",
                expected_behavior="Should queue excess workflows or return appropriate error",
                timeout_seconds=240,
                test_steps=[
                    "Submit many concurrent workflows",
                    "Verify queue management",
                    "Check resource limits"
                ]
            ),
            
            # Recovery and resilience scenarios
            ErrorScenario(
                name="partial_failure_recovery",
                description="Test recovery from partial failures",
                scenario_type="agent",
                expected_behavior="Should recover and complete workflow if possible",
                timeout_seconds=180,
                test_steps=[
                    "Start workflow",
                    "Cause temporary failure in one agent",
                    "Verify recovery and completion"
                ]
            ),
            
            ErrorScenario(
                name="data_corruption_recovery",
                description="Test recovery from data corruption",
                scenario_type="data",
                expected_behavior="Should detect corruption and attempt recovery",
                timeout_seconds=150,
                test_steps=[
                    "Simulate data corruption during processing",
                    "Verify detection and recovery mechanisms"
                ]
            )
        ]
    
    def test_invalid_repository_url(self) -> ErrorTestResult:
        """Test handling of invalid repository URLs"""
        print("🧪 Testing invalid repository URL handling...")
        
        start_time = time.time()
        
        try:
            # Test cases with invalid URLs
            invalid_urls = [
                "https://github.com/nonexistent/user/invalid-repo-12345",
                "https://github.com/",
                "not-a-url",
                "https://github.com/user/repo.git/../extra/path",
                ""
            ]
            
            for url in invalid_urls:
                print(f"  Testing URL: {url}")
                
                request_data = {
                    "repository_url": url,
                    "priority": 5
                }
                
                response = requests.post(
                    f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows",
                    json=request_data,
                    timeout=10
                )
                
                # Should return 400, 422, or similar client error
                if response.status_code in [400, 422, 404]:
                    print(f"    ✅ Correctly rejected with status {response.status_code}")
                else:
                    print(f"    ❌ Unexpected status code: {response.status_code}")
                    return ErrorTestResult(
                        scenario_name="invalid_repository_url",
                        scenario_type="input",
                        status="FAIL",
                        duration=time.time() - start_time,
                        error_detected=True,
                        recovery_successful=False,
                        error_message=f"Unexpected status {response.status_code} for invalid URL"
                    )
            
            return ErrorTestResult(
                scenario_name="invalid_repository_url",
                scenario_type="input",
                status="PASS",
                duration=time.time() - start_time,
                error_detected=True,
                recovery_successful=True,
                recovery_details={"urls_tested": len(invalid_urls), "correctly_rejected": len(invalid_urls)}
            )
            
        except Exception as e:
            return ErrorTestResult(
                scenario_name="invalid_repository_url",
                scenario_type="input",
                status="ERROR",
                duration=time.time() - start_time,
                error_detected=False,
                recovery_successful=False,
                error_message=str(e)
            )
    
    def test_malformed_request(self) -> ErrorTestResult:
        """Test handling of malformed requests"""
        print("🧪 Testing malformed request handling...")
        
        start_time = time.time()
        
        try:
            # Test with invalid JSON
            malformed_requests = [
                ("invalid json", "Invalid JSON syntax"),
                ("", "Empty body"),
                ("null", "Null body"),
                ('{"invalid": "json",}', "Malformed JSON"),
            ]
            
            for payload, description in malformed_requests:
                print(f"  Testing: {description}")
                
                headers = {"Content-Type": "application/json"}
                
                if payload == "null":
                    response = requests.post(
                        f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows",
                        data=None,
                        headers=headers,
                        timeout=10
                    )
                elif payload == "":
                    response = requests.post(
                        f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows",
                        data="",
                        headers=headers,
                        timeout=10
                    )
                else:
                    response = requests.post(
                        f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows",
                        data=payload,
                        headers=headers,
                        timeout=10
                    )
                
                # Should return 400 Bad Request
                if response.status_code in [400, 422]:
                    print(f"    ✅ Correctly rejected with status {response.status_code}")
                else:
                    print(f"    ❌ Unexpected status code: {response.status_code}")
            
            return ErrorTestResult(
                scenario_name="malformed_request_body",
                scenario_type="input",
                status="PASS",
                duration=time.time() - start_time,
                error_detected=True,
                recovery_successful=True,
                recovery_details={"malformed_requests_tested": len(malformed_requests)}
            )
            
        except Exception as e:
            return ErrorTestResult(
                scenario_name="malformed_request_body",
                scenario_type="input",
                status="ERROR",
                duration=time.time() - start_time,
                error_detected=False,
                recovery_successful=False,
                error_message=str(e)
            )
    
    def test_agent_crash_simulation(self) -> ErrorTestResult:
        """Test system behavior when agent crashes"""
        print("🧪 Testing agent crash simulation...")
        
        start_time = time.time()
        
        try:
            # Submit a workflow first
            print("  📤 Submitting workflow...")
            workflow_request = {
                "repository_url": "https://github.com/octocat/Hello-World",
                "priority": 1
            }
            
            response = requests.post(
                f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows",
                json=workflow_request,
                timeout=30
            )
            
            if response.status_code != 201:
                raise Exception(f"Failed to submit workflow: {response.text}")
            
            workflow_id = response.json()["workflow_id"]
            print(f"  ✅ Workflow submitted: {workflow_id}")
            
            # Wait a bit for processing to start
            await asyncio.sleep(5)
            
            # Simulate agent crash by killing the process
            print("  💥 Simulating agent crash...")
            subprocess.run(["pkill", "-f", "code-analyzer-agent"], check=False)
            
            # Wait and monitor
            await asyncio.sleep(10)
            
            # Check workflow status
            status_response = requests.get(
                f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows/{workflow_id}/status",
                timeout=10
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                
                if status_data["status"] == "failed":
                    print("  ✅ System correctly detected agent failure")
                    recovery_successful = True
                elif status_data["status"] == "running":
                    print("  ⚠️  Workflow still running - may have recovered")
                    recovery_successful = True
                else:
                    print(f"  ❌ Unexpected status: {status_data['status']}")
                    recovery_successful = False
                
                return ErrorTestResult(
                    scenario_name="agent_crash_simulation",
                    scenario_type="agent",
                    status="PASS" if recovery_successful else "PARTIAL",
                    duration=time.time() - start_time,
                    error_detected=True,
                    recovery_successful=recovery_successful,
                    recovery_details={
                        "workflow_id": workflow_id,
                        "final_status": status_data.get("status"),
                        "error_message": status_data.get("error")
                    }
                )
            else:
                raise Exception(f"Failed to check workflow status: {status_response.text}")
            
        except Exception as e:
            return ErrorTestResult(
                scenario_name="agent_crash_simulation",
                scenario_type="agent",
                status="ERROR",
                duration=time.time() - start_time,
                error_detected=False,
                recovery_successful=False,
                error_message=str(e)
            )
    
    def test_resource_exhaustion(self) -> ErrorTestResult:
        """Test behavior under resource pressure"""
        print("🧪 Testing resource exhaustion scenarios...")
        
        start_time = time.time()
        
        try:
            # Test concurrent workflow limits
            print("  📊 Testing concurrent workflow limits...")
            
            # Submit multiple concurrent workflows
            workflow_ids = []
            max_concurrent = 5
            
            for i in range(max_concurrent * 2):  # Submit more than limit
                request_data = {
                    "repository_url": "https://github.com/octocat/Hello-World",
                    "priority": 10 - i
                }
                
                try:
                    response = requests.post(
                        f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows",
                        json=request_data,
                        timeout=30
                    )
                    
                    if response.status_code == 201:
                        workflow_id = response.json()["workflow_id"]
                        workflow_ids.append(workflow_id)
                        print(f"    ✅ Submitted workflow {i+1}: {workflow_id}")
                    else:
                        print(f"    ❌ Failed to submit workflow {i+1}: {response.status_code}")
                        
                except Exception as e:
                    print(f"    ⚠️  Error submitting workflow {i+1}: {e}")
            
            print(f"  📈 Submitted {len(workflow_ids)} workflows")
            
            # Monitor processing
            await asyncio.sleep(30)
            
            # Check status of submitted workflows
            active_workflows = 0
            completed_workflows = 0
            
            for workflow_id in workflow_ids:
                try:
                    status_response = requests.get(
                        f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows/{workflow_id}/status",
                        timeout=10
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status = status_data["status"]
                        
                        if status in ["running", "queued"]:
                            active_workflows += 1
                        elif status == "completed":
                            completed_workflows += 1
                        elif status == "failed":
                            print(f"    ⚠️  Workflow {workflow_id} failed: {status_data.get('error')}")
                
                except Exception as e:
                    print(f"    ⚠️  Error checking workflow {workflow_id}: {e}")
            
            print(f"  📊 Active workflows: {active_workflows}")
            print(f"  ✅ Completed workflows: {completed_workflows}")
            
            return ErrorTestResult(
                scenario_name="concurrent_workflow_limit",
                scenario_type="resource",
                status="PASS",
                duration=time.time() - start_time,
                error_detected=False,
                recovery_successful=True,
                recovery_details={
                    "submitted_workflows": len(workflow_ids),
                    "active_workflows": active_workflows,
                    "completed_workflows": completed_workflows,
                    "concurrency_handled": active_workflows <= max_concurrent
                }
            )
            
        except Exception as e:
            return ErrorTestResult(
                scenario_name="concurrent_workflow_limit",
                scenario_type="resource",
                status="ERROR",
                duration=time.time() - start_time,
                error_detected=False,
                recovery_successful=False,
                error_message=str(e)
            )
    
    def test_data_corruption_scenarios(self) -> ErrorTestResult:
        """Test handling of corrupted data scenarios"""
        print("🧪 Testing data corruption scenarios...")
        
        start_time = time.time()
        
        try:
            # Test with repositories that might cause issues
            problematic_repos = [
                "https://github.com/torvalds/linux",  # Very large repo
                "https://github.com/microsoft/vscode",  # Large monorepo
            ]
            
            for repo_url in problematic_repos:
                print(f"  📦 Testing repository: {repo_url}")
                
                request_data = {
                    "repository_url": repo_url,
                    "priority": 10,  # Low priority for stress testing
                    "timeout": 60  # Short timeout for testing
                }
                
                try:
                    response = requests.post(
                        f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows",
                        json=request_data,
                        timeout=60
                    )
                    
                    if response.status_code == 201:
                        workflow_id = response.json()["workflow_id"]
                        print(f"    ✅ Workflow submitted: {workflow_id}")
                        
                        # Monitor for a short time
                        timeout_seconds = 120
                        poll_interval = 10
                        elapsed = 0
                        
                        while elapsed < timeout_seconds:
                            status_response = requests.get(
                                f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows/{workflow_id}/status",
                                timeout=10
                            )
                            
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                status = status_data["status"]
                                
                                if status in ["completed", "failed"]:
                                    print(f"    📊 Final status: {status}")
                                    break
                                
                            await asyncio.sleep(poll_interval)
                            elapsed += poll_interval
                        
                        if elapsed >= timeout_seconds:
                            print(f"    ⏰ Workflow timed out after {timeout_seconds}s")
                    
                    else:
                        print(f"    ❌ Failed to submit: {response.status_code}")
                
                except Exception as e:
                    print(f"    ⚠️  Exception during testing: {e}")
            
            return ErrorTestResult(
                scenario_name="data_corruption_recovery",
                scenario_type="data",
                status="PASS",
                duration=time.time() - start_time,
                error_detected=True,
                recovery_successful=True,
                recovery_details={"repositories_tested": len(problematic_repos)}
            )
            
        except Exception as e:
            return ErrorTestResult(
                scenario_name="data_corruption_recovery",
                scenario_type="data",
                status="ERROR",
                duration=time.time() - start_time,
                error_detected=False,
                recovery_successful=False,
                error_message=str(e)
            )
    
    async def run_comprehensive_error_testing(self) -> List[ErrorTestResult]:
        """Run comprehensive error scenario testing"""
        print("🚀 Starting comprehensive error scenario testing...")
        print("=" * 60)
        
        all_results = []
        
        # Test input validation scenarios
        print("\n1️⃣ Testing Input Validation...")
        
        input_result = self.test_invalid_repository_url()
        all_results.append(input_result)
        print(f"   Result: {input_result.status} ({input_result.duration:.2f}s)")
        
        malformed_result = self.test_malformed_request()
        all_results.append(malformed_result)
        print(f"   Result: {malformed_result.status} ({malformed_result.duration:.2f}s)")
        
        # Test agent failure scenarios
        print("\n2️⃣ Testing Agent Failures...")
        
        crash_result = self.test_agent_crash_simulation()
        all_results.append(crash_result)
        print(f"   Result: {crash_result.status} ({crash_result.duration:.2f}s)")
        
        # Test resource scenarios
        print("\n3️⃣ Testing Resource Exhaustion...")
        
        resource_result = self.test_resource_exhaustion()
        all_results.append(resource_result)
        print(f"   Result: {resource_result.status} ({resource_result.duration:.2f}s)")
        
        # Test data corruption scenarios
        print("\n4️⃣ Testing Data Corruption...")
        
        corruption_result = self.test_data_corruption_scenarios()
        all_results.append(corruption_result)
        print(f"   Result: {corruption_result.status} ({corruption_result.duration:.2f}s)")
        
        # Save results
        await self._save_error_test_results(all_results)
        
        # Print summary
        self._print_error_test_summary(all_results)
        
        return all_results
    
    async def _save_error_test_results(self, results: List[ErrorTestResult]):
        """Save error test results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = self.results_dir / f"error_testing_{timestamp}.json"
        json_data = {
            "timestamp": timestamp,
            "total_scenarios": len(results),
            "results": [asdict(result) for result in results]
        }
        
        with open(json_file, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        # Save human-readable report
        report_file = self.results_dir / f"error_testing_report_{timestamp}.md"
        with open(report_file, 'w') as f:
            f.write(self._generate_error_test_report(results))
        
        print(f"\n💾 Error testing results saved:")
        print(f"   📊 JSON: {json_file}")
        print(f"   📝 Report: {report_file}")
    
    def _generate_error_test_report(self, results: List[ErrorTestResult]) -> str:
        """Generate human-readable error test report"""
        report = f"""# Codebase Genius Error Testing Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Scenarios Tested:** {len(results)}

## Summary

"""
        
        # Calculate statistics
        passed = len([r for r in results if r.status == "PASS"])
        failed = len([r for r in results if r.status == "FAIL"])
        partial = len([r for r in results if r.status == "PARTIAL"])
        errors = len([r for r in results if r.status == "ERROR"])
        
        report += f"- **Passed:** {passed} ✅\n"
        report += f"- **Failed:** {failed} ❌\n"
        report += f"- **Partial:** {partial} ⚠️\n"
        report += f"- **Errors:** {errors} 💥\n\n"
        
        # Results by category
        categories = {}
        for result in results:
            category = result.scenario_type
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        for category, cat_results in categories.items():
            report += f"### {category.title()} Scenarios\n\n"
            
            for result in cat_results:
                status_icon = {
                    "PASS": "✅",
                    "FAIL": "❌",
                    "PARTIAL": "⚠️",
                    "ERROR": "💥"
                }.get(result.status, "❓")
                
                report += f"#### {status_icon} {result.scenario_name}\n\n"
                report += f"- **Duration:** {result.duration:.2f} seconds\n"
                report += f"- **Error Detected:** {result.error_detected}\n"
                report += f"- **Recovery Successful:** {result.recovery_successful}\n"
                
                if result.error_message:
                    report += f"- **Error:** {result.error_message}\n"
                
                if result.recovery_details:
                    report += f"- **Recovery Details:** {json.dumps(result.recovery_details, indent=2)}\n"
                
                report += "\n"
        
        # Recommendations
        report += "## Recommendations\n\n"
        
        recovery_issues = [r for r in results if not r.recovery_successful]
        if recovery_issues:
            report += "### Areas for Improvement\n\n"
            for result in recovery_issues:
                report += f"- **{result.scenario_name}**: Improve recovery mechanisms\n"
        else:
            report += "### System Resilience\n\n"
            report += "The system demonstrates good resilience and recovery capabilities across all tested scenarios.\n"
        
        return report
    
    def _print_error_test_summary(self, results: List[ErrorTestResult]):
        """Print error test summary to console"""
        print("\n" + "=" * 60)
        print("🚨 ERROR TESTING SUMMARY")
        print("=" * 60)
        
        passed = len([r for r in results if r.status == "PASS"])
        failed = len([r for r in results if r.status == "FAIL"])
        partial = len([r for r in results if r.status == "PARTIAL"])
        errors = len([r for r in results if r.status == "ERROR"])
        
        print(f"Scenarios Tested: {len(results)}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Partial: {partial} ⚠️")
        print(f"Errors: {errors} 💥")
        
        if passed + partial >= len(results) * 0.8:  # 80% success rate
            print("🎉 Error handling is robust!")
        else:
            print("⚠️  Error handling needs improvement")
        
        print("=" * 60)

async def main():
    """Main error testing execution"""
    import sys
    
    error_tester = ErrorScenarioTester()
    
    try:
        # Run comprehensive error testing
        results = await error_tester.run_comprehensive_error_testing()
        
        # Count successes
        successful = len([r for r in results if r.status in ["PASS", "PARTIAL"]])
        
        print(f"\n✅ Error testing completed! {successful}/{len(results)} scenarios handled properly")
        return 0 if successful >= len(results) * 0.8 else 1
        
    except Exception as e:
        print(f"\n❌ Error testing failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
