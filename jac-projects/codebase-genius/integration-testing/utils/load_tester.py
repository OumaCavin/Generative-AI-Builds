#!/usr/bin/env python3
"""
Codebase Genius - Load Testing Framework
Phase 7: System capacity and scalability testing

Provides comprehensive load testing including:
- Concurrent workflow execution
- Sustained load testing
- Resource utilization monitoring
- Performance degradation detection
- Scalability bottleneck identification

Author: Cavin Otieno
Date: 2025-10-31
"""

import asyncio
import json
import time
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import psutil
import threading
from collections import defaultdict, deque

@dataclass
class LoadTestConfig:
    """Load test configuration"""
    name: str
    description: str
    concurrent_workflows: int
    test_duration_seconds: int
    workflow_interval_seconds: float
    repository_url: str
    priority_levels: List[int] = None
    expected_throughput: float = None  # workflows per minute
    
    def __post_init__(self):
        if self.priority_levels is None:
            self.priority_levels = [5, 6, 7, 8, 9]  # Range of priorities
        if self.expected_throughput is None:
            self.expected_throughput = self.concurrent_workflows / (self.test_duration_seconds / 60)

@dataclass
class LoadTestResult:
    """Individual load test result"""
    test_name: str
    start_time: datetime
    end_time: datetime
    duration: float
    config: LoadTestConfig
    metrics: Dict[str, Any]
    workflow_results: List[Dict[str, Any]]
    resource_metrics: List[Dict[str, Any]]
    errors_encountered: List[str]

@dataclass
class SystemLoadMetrics:
    """System load metrics snapshot"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_io_read: float
    disk_io_write: float
    network_connections: int
    active_workflows: int
    queued_workflows: int
    completed_workflows: int
    failed_workflows: int

class LoadTestFramework:
    """Comprehensive load testing framework"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.results_dir = self.base_dir / "results" / "load_testing"
        
        # Agent endpoints
        self.agent_ports = {
            "supervisor": 8080,
            "repository_mapper": 8081,
            "code_analyzer": 8082,
            "docgenie": 8083
        }
        
        # Load test configurations
        self.load_test_configs = [
            LoadTestConfig(
                name="light_load",
                description="Light concurrent load - 2 workflows",
                concurrent_workflows=2,
                test_duration_seconds=120,
                workflow_interval_seconds=5.0,
                repository_url="https://github.com/octocat/Hello-World",
                expected_throughput=2.0
            ),
            LoadTestConfig(
                name="medium_load",
                description="Medium concurrent load - 5 workflows",
                concurrent_workflows=5,
                test_duration_seconds=300,
                workflow_interval_seconds=3.0,
                repository_url="https://github.com/psf/requests",
                expected_throughput=10.0
            ),
            LoadTestConfig(
                name="heavy_load",
                description="Heavy concurrent load - 10 workflows",
                concurrent_workflows=10,
                test_duration_seconds=600,
                workflow_interval_seconds=2.0,
                repository_url="https://github.com/octocat/Hello-World",
                expected_throughput=30.0
            ),
            LoadTestConfig(
                name="stress_test",
                description="Stress test - 15 concurrent workflows",
                concurrent_workflows=15,
                test_duration_seconds=900,
                workflow_interval_seconds=1.0,
                repository_url="https://github.com/octocat/Hello-World",
                expected_throughput=60.0
            )
        ]
        
        # Resource monitoring
        self.monitoring_active = False
        self.resource_metrics = []
        
        # Ensure results directory exists
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def start_resource_monitoring(self, duration_seconds: int, interval_seconds: int = 5) -> asyncio.Task:
        """Start resource monitoring in background"""
        self.monitoring_active = True
        self.resource_metrics.clear()
        
        async def monitor_resources():
            start_time = time.time()
            while self.monitoring_active and (time.time() - start_time) < duration_seconds:
                try:
                    # Get system metrics
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    memory = psutil.virtual_memory()
                    disk_io = psutil.disk_io_counters()
                    network_connections = len(psutil.net_connections())
                    
                    # Get workflow metrics from supervisor
                    workflow_metrics = await self._get_workflow_metrics()
                    
                    snapshot = SystemLoadMetrics(
                        timestamp=datetime.now(),
                        cpu_percent=cpu_percent,
                        memory_percent=memory.percent,
                        memory_mb=memory.used / 1024 / 1024,
                        disk_io_read=disk_io.read_bytes if disk_io else 0,
                        disk_io_write=disk_io.write_bytes if disk_io else 0,
                        network_connections=network_connections,
                        active_workflows=workflow_metrics.get("active", 0),
                        queued_workflows=workflow_metrics.get("queued", 0),
                        completed_workflows=workflow_metrics.get("completed", 0),
                        failed_workflows=workflow_metrics.get("failed", 0)
                    )
                    
                    self.resource_metrics.append(snapshot)
                    
                except Exception as e:
                    print(f"⚠️  Error collecting metrics: {e}")
                
                await asyncio.sleep(interval_seconds)
        
        return asyncio.create_task(monitor_resources())
    
    async def _get_workflow_metrics(self) -> Dict[str, int]:
        """Get current workflow metrics from supervisor"""
        try:
            response = requests.get(
                f"http://localhost:{self.agent_ports['supervisor']}/api/v1/metrics",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"active": 0, "queued": 0, "completed": 0, "failed": 0}
        except:
            return {"active": 0, "queued": 0, "completed": 0, "failed": 0}
    
    async def submit_workload(self, config: LoadTestConfig, test_start_time: datetime) -> List[Dict[str, Any]]:
        """Submit workload according to configuration"""
        print(f"📤 Submitting workload: {config.name}")
        print(f"   Concurrent workflows: {config.concurrent_workflows}")
        print(f"   Duration: {config.test_duration_seconds}s")
        print(f"   Interval: {config.workflow_interval_seconds}s")
        
        workflow_results = []
        end_time = test_start_time + timedelta(seconds=config.test_duration_seconds)
        
        # Submit workflows at specified intervals
        workflow_count = 0
        while datetime.now() < end_time and workflow_count < config.concurrent_workflows:
            # Select priority
            priority_idx = workflow_count % len(config.priority_levels)
            priority = config.priority_levels[priority_idx]
            
            # Submit workflow
            request_data = {
                "repository_url": config.repository_url,
                "priority": priority,
                "output_format": "markdown"
            }
            
            try:
                response = requests.post(
                    f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows",
                    json=request_data,
                    timeout=30
                )
                
                if response.status_code == 201:
                    workflow_data = response.json()
                    workflow_result = {
                        "workflow_id": workflow_data["workflow_id"],
                        "priority": priority,
                        "submitted_at": datetime.now().isoformat(),
                        "status": "submitted"
                    }
                    workflow_results.append(workflow_result)
                    workflow_count += 1
                    
                    print(f"  ✅ Submitted workflow {workflow_count}: {workflow_data['workflow_id']}")
                else:
                    print(f"  ❌ Failed to submit workflow {workflow_count + 1}: {response.status_code}")
                    
            except Exception as e:
                print(f"  ⚠️  Error submitting workflow {workflow_count + 1}: {e}")
            
            # Wait before next submission (unless we've reached the concurrent limit)
            if workflow_count < config.concurrent_workflows:
                await asyncio.sleep(config.workflow_interval_seconds)
        
        print(f"📊 Submitted {len(workflow_results)} workflows")
        return workflow_results
    
    async def monitor_workflow_progress(self, workflow_results: List[Dict[str, Any]], config: LoadTestConfig) -> List[Dict[str, Any]]:
        """Monitor workflow progress and collect results"""
        print(f"⏳ Monitoring workflow progress...")
        
        # Track workflow statuses
        workflow_statuses = {result["workflow_id"]: result for result in workflow_results}
        completed_workflows = []
        failed_workflows = []
        
        # Monitor until all workflows complete or timeout
        start_monitoring = time.time()
        timeout = config.test_duration_seconds * 2  # Double the test duration for monitoring
        poll_interval = 10
        
        while (time.time() - start_monitoring) < timeout:
            active_count = 0
            completed_count = len(completed_workflows)
            failed_count = len(failed_workflows)
            
            # Check status of each workflow
            for workflow_id in list(workflow_statuses.keys()):
                try:
                    status_response = requests.get(
                        f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows/{workflow_id}/status",
                        timeout=10
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status = status_data["status"]
                        
                        workflow_status = workflow_statuses[workflow_id]
                        workflow_status["status"] = status
                        
                        if status == "completed":
                            # Get final results
                            try:
                                result_response = requests.get(
                                    f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows/{workflow_id}/results",
                                    timeout=30
                                )
                                
                                if result_response.status_code == 200:
                                    workflow_status["results"] = result_response.json()
                                    workflow_status["completed_at"] = datetime.now().isoformat()
                                
                            except Exception as e:
                                workflow_status["results_error"] = str(e)
                            
                            completed_workflows.append(workflow_status)
                            del workflow_statuses[workflow_id]
                            print(f"  ✅ Completed: {workflow_id}")
                            
                        elif status == "failed":
                            workflow_status["error"] = status_data.get("error", "Unknown error")
                            workflow_status["failed_at"] = datetime.now().isoformat()
                            failed_workflows.append(workflow_status)
                            del workflow_statuses[workflow_id]
                            print(f"  ❌ Failed: {workflow_id}")
                            
                        elif status in ["running", "queued"]:
                            active_count += 1
                    
                except Exception as e:
                    print(f"  ⚠️  Error checking workflow {workflow_id}: {e}")
            
            # Print progress update
            total_checked = len(completed_workflows) + len(failed_workflows)
            print(f"  📊 Progress: {len(completed_workflows)} completed, {len(failed_workflows)} failed, {active_count} active")
            
            # Check if all workflows are done
            if not workflow_statuses:
                print("  🎉 All workflows completed!")
                break
            
            # Check for excessive time
            elapsed = time.time() - start_monitoring
            if elapsed > timeout:
                print(f"  ⏰ Monitoring timeout after {timeout}s")
                # Mark remaining workflows as timeout
                for workflow_id, status in workflow_statuses.items():
                    status["status"] = "timeout"
                    status["timeout_at"] = datetime.now().isoformat()
                break
            
            await asyncio.sleep(poll_interval)
        
        # Combine all results
        all_results = completed_workflows + failed_workflows + list(workflow_statuses.values())
        return all_results
    
    def analyze_load_test_results(self, result: LoadTestResult) -> Dict[str, Any]:
        """Analyze load test results for performance metrics"""
        print(f"📈 Analyzing results for {result.test_name}...")
        
        analysis = {
            "test_name": result.test_name,
            "duration": result.duration,
            "workflows_submitted": len(result.workflow_results),
            "workflows_completed": len([w for w in result.workflow_results if w.get("status") == "completed"]),
            "workflows_failed": len([w for w in result.workflow_results if w.get("status") == "failed"]),
            "workflows_timeout": len([w for w in result.workflow_results if w.get("status") == "timeout"]),
        }
        
        # Calculate success rate
        total_workflows = analysis["workflows_submitted"]
        successful_workflows = analysis["workflows_completed"]
        analysis["success_rate"] = successful_workflows / total_workflows if total_workflows > 0 else 0
        
        # Calculate throughput
        if result.duration > 0:
            analysis["throughput_per_minute"] = successful_workflows / (result.duration / 60)
            analysis["throughput_per_second"] = successful_workflows / result.duration
        else:
            analysis["throughput_per_minute"] = 0
            analysis["throughput_per_second"] = 0
        
        # Calculate average workflow duration
        completed_workflows = [w for w in result.workflow_results if w.get("completed_at") and w.get("submitted_at")]
        if completed_workflows:
            durations = []
            for workflow in completed_workflows:
                try:
                    submitted = datetime.fromisoformat(workflow["submitted_at"])
                    completed = datetime.fromisoformat(workflow["completed_at"])
                    durations.append((completed - submitted).total_seconds())
                except:
                    pass
            
            if durations:
                analysis["avg_workflow_duration"] = statistics.mean(durations)
                analysis["min_workflow_duration"] = min(durations)
                analysis["max_workflow_duration"] = max(durations)
                analysis["median_workflow_duration"] = statistics.median(durations)
        
        # Resource utilization analysis
        if result.resource_metrics:
            cpu_samples = [m.cpu_percent for m in result.resource_metrics if m.cpu_percent is not None]
            memory_samples = [m.memory_percent for m in result.resource_metrics if m.memory_percent is not None]
            
            if cpu_samples:
                analysis["avg_cpu_percent"] = statistics.mean(cpu_samples)
                analysis["max_cpu_percent"] = max(cpu_samples)
                analysis["min_cpu_percent"] = min(cpu_samples)
            
            if memory_samples:
                analysis["avg_memory_percent"] = statistics.mean(memory_samples)
                analysis["max_memory_percent"] = max(memory_samples)
                analysis["min_memory_percent"] = min(memory_samples)
        
        # Performance degradation detection
        if "expected_throughput" in result.config.__dict__:
            expected_throughput = result.config.expected_throughput
            actual_throughput = analysis["throughput_per_minute"]
            
            if expected_throughput > 0:
                throughput_ratio = actual_throughput / expected_throughput
                analysis["throughput_ratio"] = throughput_ratio
                
                if throughput_ratio < 0.7:
                    analysis["performance_degraded"] = True
                    analysis["degradation_severity"] = "high" if throughput_ratio < 0.5 else "moderate"
                elif throughput_ratio < 0.9:
                    analysis["performance_degraded"] = True
                    analysis["degradation_severity"] = "low"
                else:
                    analysis["performance_degraded"] = False
        
        # Queue management analysis
        if result.resource_metrics:
            max_queued = max([m.queued_workflows for m in result.resource_metrics])
            max_active = max([m.active_workflows for m in result.resource_metrics])
            
            analysis["max_concurrent_workflows"] = max_active
            analysis["max_queued_workflows"] = max_queued
            analysis["queue_efficiency"] = analysis["max_concurrent_workflows"] / max_queued if max_queued > 0 else 1.0
        
        return analysis
    
    async def run_load_test(self, config: LoadTestConfig) -> LoadTestResult:
        """Run individual load test"""
        print(f"\n🏃 Running load test: {config.name}")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Start resource monitoring
            monitor_task = self.start_resource_monitoring(config.test_duration_seconds + 300)  # Extra time for monitoring
            
            # Submit workload
            workflow_results = await self.submit_workload(config, start_time)
            
            # Monitor progress
            final_results = await self.monitor_workflow_progress(workflow_results, config)
            
            # Stop monitoring
            self.monitoring_active = False
            await monitor_task
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Create result
            result = LoadTestResult(
                test_name=config.name,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                config=config,
                metrics={},
                workflow_results=final_results,
                resource_metrics=self.resource_metrics.copy(),
                errors_encountered=[]
            )
            
            # Analyze results
            analysis = self.analyze_load_test_results(result)
            result.metrics = analysis
            
            # Print summary
            print(f"\n📊 Load Test Results: {config.name}")
            print(f"   Duration: {duration:.1f}s")
            print(f"   Submitted: {analysis['workflows_submitted']}")
            print(f"   Completed: {analysis['workflows_completed']}")
            print(f"   Success Rate: {analysis['success_rate']*100:.1f}%")
            print(f"   Throughput: {analysis['throughput_per_minute']:.1f} workflows/min")
            
            if analysis.get("avg_cpu_percent"):
                print(f"   Avg CPU: {analysis['avg_cpu_percent']:.1f}%")
            if analysis.get("avg_memory_percent"):
                print(f"   Avg Memory: {analysis['avg_memory_percent']:.1f}%")
            
            return result
            
        except Exception as e:
            end_time = datetime.now()
            print(f"❌ Load test failed: {e}")
            
            return LoadTestResult(
                test_name=config.name,
                start_time=start_time,
                end_time=end_time,
                duration=(end_time - start_time).total_seconds(),
                config=config,
                metrics={"error": str(e)},
                workflow_results=[],
                resource_metrics=self.resource_metrics.copy(),
                errors_encountered=[str(e)]
            )
    
    async def run_comprehensive_load_testing(self) -> List[LoadTestResult]:
        """Run comprehensive load testing suite"""
        print("🚀 Starting comprehensive load testing...")
        print("=" * 60)
        
        all_results = []
        
        # Run each load test configuration
        for config in self.load_test_configs:
            try:
                result = await self.run_load_test(config)
                all_results.append(result)
                
                # Small delay between tests
                await asyncio.sleep(30)
                
            except KeyboardInterrupt:
                print(f"\n⚠️  Load test interrupted: {config.name}")
                break
            except Exception as e:
                print(f"❌ Load test failed: {config.name} - {e}")
                continue
        
        # Save results
        await self._save_load_test_results(all_results)
        
        # Print comprehensive summary
        self._print_load_test_summary(all_results)
        
        return all_results
    
    async def _save_load_test_results(self, results: List[LoadTestResult]):
        """Save load test results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = self.results_dir / f"load_testing_{timestamp}.json"
        json_data = {
            "timestamp": timestamp,
            "total_tests": len(results),
            "results": [asdict(result) for result in results]
        }
        
        with open(json_file, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        # Save human-readable report
        report_file = self.results_dir / f"load_testing_report_{timestamp}.md"
        with open(report_file, 'w') as f:
            f.write(self._generate_load_test_report(results))
        
        print(f"\n💾 Load testing results saved:")
        print(f"   📊 JSON: {json_file}")
        print(f"   📝 Report: {report_file}")
    
    def _generate_load_test_report(self, results: List[LoadTestResult]) -> str:
        """Generate human-readable load test report"""
        report = f"""# Codebase Genius Load Testing Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Tests Completed:** {len(results)}

## Executive Summary

This report presents load testing results for the Codebase Genius multi-agent system, evaluating system performance under various concurrent workflow loads.

## Test Results

"""
        
        for result in results:
            analysis = result.metrics
            status = "✅ PASS" if analysis.get("success_rate", 0) >= 0.8 else "❌ FAIL"
            
            report += f"""### {result.test_name} {status}

**Configuration:**
- Concurrent Workflows: {result.config.concurrent_workflows}
- Duration: {result.config.test_duration_seconds}s
- Repository: {result.config.repository_url}

**Performance:**
- Duration: {result.duration:.1f}s
- Workflows Submitted: {analysis.get('workflows_submitted', 0)}
- Workflows Completed: {analysis.get('workflows_completed', 0)}
- Success Rate: {analysis.get('success_rate', 0)*100:.1f}%
- Throughput: {analysis.get('throughput_per_minute', 0):.1f} workflows/min

**Resource Utilization:**
"""
            
            if analysis.get("avg_cpu_percent"):
                report += f"- Average CPU: {analysis['avg_cpu_percent']:.1f}%\n"
            if analysis.get("max_cpu_percent"):
                report += f"- Peak CPU: {analysis['max_cpu_percent']:.1f}%\n"
            if analysis.get("avg_memory_percent"):
                report += f"- Average Memory: {analysis['avg_memory_percent']:.1f}%\n"
            if analysis.get("max_memory_percent"):
                report += f"- Peak Memory: {analysis['max_memory_percent']:.1f}%\n"
            
            report += "\n"
        
        # Performance summary
        report += "## Performance Summary\n\n"
        
        # Calculate aggregate metrics
        total_completed = sum(r.metrics.get("workflows_completed", 0) for r in results)
        total_submitted = sum(r.metrics.get("workflows_submitted", 0) for r in results)
        avg_success_rate = sum(r.metrics.get("success_rate", 0) for r in results) / len(results) if results else 0
        
        report += f"- **Total Workflows Submitted:** {total_submitted}\n"
        report += f"- **Total Workflows Completed:** {total_completed}\n"
        report += f"- **Overall Success Rate:** {avg_success_rate*100:.1f}%\n"
        
        # Scalability assessment
        max_throughput = max([r.metrics.get("throughput_per_minute", 0) for r in results])
        report += f"- **Maximum Throughput:** {max_throughput:.1f} workflows/min\n"
        
        # Recommendations
        report += "\n## Recommendations\n\n"
        
        if avg_success_rate < 0.8:
            report += "- **Critical:** Success rate below 80% indicates system instability\n"
            report += "- Consider reducing concurrent workload or improving error handling\n"
        elif avg_success_rate < 0.9:
            report += "- **Warning:** Success rate could be improved\n"
            report += "- Monitor system resources and optimize bottlenecks\n"
        else:
            report += "- **Good:** System demonstrates stable performance under load\n"
        
        report += "- Monitor resource utilization during peak loads\n"
        report += "- Consider implementing auto-scaling for high-concurrency scenarios\n"
        
        return report
    
    def _print_load_test_summary(self, results: List[LoadTestResult]):
        """Print load test summary to console"""
        print("\n" + "=" * 60)
        print("🏋️ LOAD TESTING SUMMARY")
        print("=" * 60)
        
        total_completed = sum(r.metrics.get("workflows_completed", 0) for r in results)
        total_submitted = sum(r.metrics.get("workflows_submitted", 0) for r in results)
        avg_success_rate = sum(r.metrics.get("success_rate", 0) for r in results) / len(results) if results else 0
        
        print(f"Tests Completed: {len(results)}")
        print(f"Total Workflows: {total_submitted} submitted, {total_completed} completed")
        print(f"Overall Success Rate: {avg_success_rate*100:.1f}%")
        
        # Show best and worst performers
        if results:
            best_performer = max(results, key=lambda r: r.metrics.get("success_rate", 0))
            worst_performer = min(results, key=lambda r: r.metrics.get("success_rate", 1))
            
            print(f"Best Performance: {best_performer.test_name} ({best_performer.metrics.get('success_rate', 0)*100:.1f}%)")
            print(f"Needs Improvement: {worst_performer.test_name} ({worst_performer.metrics.get('success_rate', 0)*100:.1f}%)")
        
        print("=" * 60)

async def main():
    """Main load testing execution"""
    import sys
    
    load_tester = LoadTestFramework()
    
    try:
        # Run comprehensive load testing
        results = await load_tester.run_comprehensive_load_testing()
        
        # Calculate overall success
        total_success_rate = sum(r.metrics.get("success_rate", 0) for r in results) / len(results) if results else 0
        
        print(f"\n✅ Load testing completed! Overall success rate: {total_success_rate*100:.1f}%")
        return 0 if total_success_rate >= 0.8 else 1
        
    except Exception as e:
        print(f"\n❌ Load testing failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
