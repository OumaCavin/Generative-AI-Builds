#!/usr/bin/env python3
"""
Codebase Genius - Performance Benchmarking Suite
Phase 7: Performance analysis and optimization tools

Provides comprehensive performance benchmarking including:
- Workflow execution timing
- Memory usage profiling
- Agent response time analysis
- Scalability testing
- Bottleneck identification

Author: Cavin Otieno
Date: 2025-10-31
"""

import asyncio
import json
import time
import psutil
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import requests
import gc
import tracemalloc
import cProfile
import pstats
from io import StringIO

@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

@dataclass
class BenchmarkResult:
    """Complete benchmark result"""
    test_name: str
    start_time: datetime
    end_time: datetime
    duration: float
    metrics: List[PerformanceMetric]
    memory_snapshot: Dict[str, Any]
    system_load: Dict[str, Any]
    repository_info: Dict[str, Any]
    
class PerformanceBenchmarkSuite:
    """Comprehensive performance benchmarking framework"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.results_dir = self.base_dir / "results" / "performance"
        self.benchmarks_dir = self.base_dir / "benchmarks"
        
        # Agent endpoints
        self.agent_ports = {
            "supervisor": 8080,
            "repository_mapper": 8081,
            "code_analyzer": 8082, 
            "docgenie": 8083
        }
        
        # Benchmark repositories of varying complexity
        self.benchmark_repositories = [
            {
                "name": "micro-python",
                "url": "https://github.com/octocat/Hello-World",
                "complexity": "very_low",
                "expected_duration": 30,
                "description": "Minimal Python project"
            },
            {
                "name": "small-python",
                "url": "https://github.com/psf/requests",
                "complexity": "low",
                "expected_duration": 120,
                "description": "Small Python library"
            },
            {
                "name": "medium-python",
                "url": "https://github.com/python/cpython",
                "complexity": "medium",
                "expected_duration": 300,
                "description": "Medium-sized Python project"
            },
            {
                "name": "jac-project",
                "url": "https://github.com/jaseem/jaic-examples",
                "complexity": "medium",
                "expected_duration": 180,
                "description": "JAC language project"
            }
        ]
        
        # Ensure results directory exists
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def start_system_monitoring(self) -> Dict[str, Any]:
        """Start system performance monitoring"""
        # Start memory tracing
        tracemalloc.start()
        
        # Get initial system state
        initial_memory = psutil.virtual_memory()
        initial_cpu = psutil.cpu_percent(interval=1)
        initial_disk = psutil.disk_usage('/')
        
        return {
            "initial_memory_mb": initial_memory.used / 1024 / 1024,
            "initial_memory_percent": initial_memory.percent,
            "initial_cpu_percent": initial_cpu,
            "initial_disk_usage_percent": (initial_disk.used / initial_disk.total) * 100,
            "tracemalloc_started": True
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            disk = psutil.disk_usage('/')
            
            return {
                "memory_used_mb": memory.used / 1024 / 1024,
                "memory_available_mb": memory.available / 1024 / 1024,
                "memory_percent": memory.percent,
                "cpu_percent": cpu_percent,
                "cpu_count": cpu_count,
                "disk_used_gb": disk.used / 1024 / 1024 / 1024,
                "disk_free_gb": disk.free / 1024 / 1024 / 1024,
                "disk_usage_percent": (disk.used / disk.total) * 100,
                "load_average": os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_memory_snapshot(self) -> Dict[str, Any]:
        """Get detailed memory usage snapshot"""
        try:
            current, peak = tracemalloc.get_traced_memory()
            return {
                "current_memory_mb": current / 1024 / 1024,
                "peak_memory_mb": peak / 1024 / 1024,
                "memory_traces": len(tracemalloc.get_traced_memory())
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def benchmark_agent_response_time(self) -> List[PerformanceMetric]:
        """Benchmark individual agent response times"""
        print("⏱️  Benchmarking agent response times...")
        metrics = []
        
        for agent_name, port in self.agent_ports.items():
            print(f"  Testing {agent_name} (port {port})...")
            
            # Test health endpoint
            response_times = []
            for i in range(10):  # 10 requests
                start_time = time.time()
                try:
                    response = requests.get(
                        f"http://localhost:{port}/health",
                        timeout=10
                    )
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        response_times.append((end_time - start_time) * 1000)  # Convert to ms
                except Exception as e:
                    print(f"    ⚠️  Request {i+1} failed: {e}")
                
                await asyncio.sleep(0.1)  # Small delay between requests
            
            if response_times:
                avg_response_time = statistics.mean(response_times)
                min_response_time = min(response_times)
                max_response_time = max(response_times)
                
                metrics.append(PerformanceMetric(
                    name=f"{agent_name}_avg_response_time",
                    value=avg_response_time,
                    unit="ms",
                    timestamp=datetime.now(),
                    context={
                        "min_time": min_response_time,
                        "max_time": max_response_time,
                        "requests_sent": len(response_times),
                        "successful_requests": len(response_times)
                    }
                ))
                
                print(f"    ✅ Avg: {avg_response_time:.2f}ms, Min: {min_response_time:.2f}ms, Max: {max_response_time:.2f}ms")
            else:
                print(f"    ❌ No successful requests")
        
        return metrics
    
    async def benchmark_workflow_execution(self, repo_config: Dict, profile_code: bool = False) -> BenchmarkResult:
        """Benchmark complete workflow execution with profiling"""
        print(f"🏃 Benchmarking workflow execution: {repo_config['name']}")
        
        # Start monitoring
        system_monitor = self.start_system_monitoring()
        start_time = datetime.now()
        
        # Optional code profiling
        profiler = None
        if profile_code:
            profiler = cProfile.Profile()
            profiler.enable()
        
        metrics = []
        memory_snapshots = []
        
        try:
            # Submit workflow
            workflow_request = {
                "repository_url": repo_config["url"],
                "priority": 1,  # Highest priority
                "output_format": "markdown",
                "include_diagrams": True
            }
            
            print(f"  📤 Submitting workflow...")
            submit_start = time.time()
            
            response = requests.post(
                f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows",
                json=workflow_request,
                timeout=30
            )
            
            submit_duration = time.time() - submit_start
            metrics.append(PerformanceMetric(
                name="workflow_submission_time",
                value=submit_duration * 1000,
                unit="ms",
                timestamp=datetime.now(),
                context={"status_code": response.status_code}
            ))
            
            if response.status_code != 201:
                raise Exception(f"Workflow submission failed: {response.text}")
            
            workflow_id = response.json()["workflow_id"]
            print(f"  ✅ Workflow ID: {workflow_id}")
            
            # Monitor workflow execution
            print(f"  ⏳ Monitoring execution...")
            max_wait = repo_config["expected_duration"] * 2  # Double expected time
            poll_interval = 5
            elapsed = 0
            last_memory_check = 0
            
            while elapsed < max_wait:
                # Check workflow status
                status_response = requests.get(
                    f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows/{workflow_id}/status",
                    timeout=10
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data["status"]
                    
                    if status == "completed":
                        print(f"  ✅ Workflow completed")
                        
                        # Get final results
                        result_response = requests.get(
                            f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows/{workflow_id}/results",
                            timeout=30
                        )
                        
                        if result_response.status_code == 200:
                            results = result_response.json()
                            
                            # Collect performance metrics from results
                            exec_duration = elapsed
                            metrics.extend([
                                PerformanceMetric(
                                    name="total_execution_time",
                                    value=exec_duration,
                                    unit="seconds",
                                    timestamp=datetime.now()
                                ),
                                PerformanceMetric(
                                    name="workflow_id",
                                    value=workflow_id,
                                    unit="id",
                                    timestamp=datetime.now()
                                )
                            ])
                            
                            # Extract repository metrics
                            if "repository" in results:
                                repo_data = results["repository"]
                                metrics.extend([
                                    PerformanceMetric(
                                        name="files_processed",
                                        value=repo_data.get("file_count", 0),
                                        unit="count",
                                        timestamp=datetime.now()
                                    ),
                                    PerformanceMetric(
                                        name="repository_size_kb",
                                        value=repo_data.get("size_kb", 0),
                                        unit="kb",
                                        timestamp=datetime.now()
                                    )
                                ])
                            
                            # Extract analysis metrics
                            if "analysis" in results and "ccg" in results["analysis"]:
                                ccg_data = results["analysis"]["ccg"]
                                metrics.extend([
                                    PerformanceMetric(
                                        name="entities_extracted",
                                        value=len(ccg_data.get("entities", [])),
                                        unit="count",
                                        timestamp=datetime.now()
                                    ),
                                    PerformanceMetric(
                                        name="relationships_mapped",
                                        value=len(ccg_data.get("relationships", [])),
                                        unit="count",
                                        timestamp=datetime.now()
                                    )
                                ])
                            
                            # Calculate derived metrics
                            files_processed = next((m.value for m in metrics if m.name == "files_processed"), 0)
                            entities_extracted = next((m.value for m in metrics if m.name == "entities_extracted"), 0)
                            
                            if exec_duration > 0:
                                metrics.extend([
                                    PerformanceMetric(
                                        name="files_per_second",
                                        value=files_processed / exec_duration,
                                        unit="files/sec",
                                        timestamp=datetime.now()
                                    ),
                                    PerformanceMetric(
                                        name="entities_per_second",
                                        value=entities_extracted / exec_duration,
                                        unit="entities/sec",
                                        timestamp=datetime.now()
                                    )
                                ])
                            
                            break
                    
                    elif status == "failed":
                        raise Exception(f"Workflow failed: {status_data.get('error', 'Unknown error')}")
                
                # Collect periodic metrics
                current_time = time.time()
                if current_time - last_memory_check >= 10:  # Every 10 seconds
                    memory_snapshot = self.get_memory_snapshot()
                    memory_snapshots.append(memory_snapshot)
                    
                    system_metrics = self.get_system_metrics()
                    metrics.extend([
                        PerformanceMetric(
                            name="memory_usage_mb",
                            value=memory_snapshot.get("current_memory_mb", 0),
                            unit="mb",
                            timestamp=datetime.now()
                        ),
                        PerformanceMetric(
                            name="cpu_usage_percent",
                            value=system_metrics.get("cpu_percent", 0),
                            unit="percent",
                            timestamp=datetime.now()
                        )
                    ])
                    
                    last_memory_check = current_time
                
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval
            else:
                raise Exception(f"Workflow timeout after {max_wait} seconds")
            
            # Stop profiling if enabled
            if profiler:
                profiler.disable()
            
            # Get final system state
            end_time = datetime.now()
            final_memory = self.get_memory_snapshot()
            final_system = self.get_system_metrics()
            
            return BenchmarkResult(
                test_name=f"workflow_benchmark_{repo_config['name']}",
                start_time=start_time,
                end_time=end_time,
                duration=(end_time - start_time).total_seconds(),
                metrics=metrics,
                memory_snapshot=final_memory,
                system_load=final_system,
                repository_info=repo_config
            )
            
        except Exception as e:
            end_time = datetime.now()
            print(f"  ❌ Benchmark failed: {e}")
            
            return BenchmarkResult(
                test_name=f"workflow_benchmark_{repo_config['name']}_FAILED",
                start_time=start_time,
                end_time=end_time,
                duration=(end_time - start_time).total_seconds(),
                metrics=metrics,
                memory_snapshot=self.get_memory_snapshot(),
                system_load=self.get_system_metrics(),
                repository_info={**repo_config, "error": str(e)}
            )
    
    async def benchmark_concurrent_workflows(self, concurrent_count: int = 3) -> BenchmarkResult:
        """Benchmark concurrent workflow execution"""
        print(f"🏋️ Benchmarking {concurrent_count} concurrent workflows...")
        
        system_monitor = self.start_system_monitoring()
        start_time = datetime.now()
        metrics = []
        
        try:
            # Submit multiple workflows simultaneously
            workflow_ids = []
            
            for i in range(concurrent_count):
                request_data = {
                    "repository_url": self.benchmark_repositories[0]["url"],  # Use simple repo
                    "priority": 10 - i,  # Different priorities
                    "output_format": "markdown"
                }
                
                response = requests.post(
                    f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows",
                    json=request_data,
                    timeout=30
                )
                
                if response.status_code == 201:
                    workflow_id = response.json()["workflow_id"]
                    workflow_ids.append(workflow_id)
                    print(f"  ✅ Submitted workflow {i+1}: {workflow_id}")
                else:
                    print(f"  ❌ Failed to submit workflow {i+1}")
            
            if not workflow_ids:
                raise Exception("No workflows submitted")
            
            # Monitor concurrent execution
            print(f"  ⏳ Monitoring {len(workflow_ids)} concurrent workflows...")
            completed = 0
            failed = 0
            start_monitoring = time.time()
            
            while completed + failed < len(workflow_ids):
                for workflow_id in list(workflow_ids):  # Copy list to modify during iteration
                    try:
                        status_response = requests.get(
                            f"http://localhost:{self.agent_ports['supervisor']}/api/v1/workflows/{workflow_id}/status",
                            timeout=10
                        )
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            
                            if status_data["status"] == "completed":
                                completed += 1
                                workflow_ids.remove(workflow_id)
                                print(f"  ✅ Completed: {workflow_id}")
                                
                            elif status_data["status"] == "failed":
                                failed += 1
                                workflow_ids.remove(workflow_id)
                                print(f"  ❌ Failed: {workflow_id}")
                    except:
                        pass  # Continue monitoring other workflows
                
                await asyncio.sleep(5)
            
            monitoring_duration = time.time() - start_monitoring
            
            # Calculate concurrent performance metrics
            total_workflows = completed + failed
            metrics.extend([
                PerformanceMetric(
                    name="concurrent_workflows",
                    value=concurrent_count,
                    unit="count",
                    timestamp=datetime.now()
                ),
                PerformanceMetric(
                    name="completed_workflows",
                    value=completed,
                    unit="count",
                    timestamp=datetime.now()
                ),
                PerformanceMetric(
                    name="failed_workflows",
                    value=failed,
                    unit="count",
                    timestamp=datetime.now()
                ),
                PerformanceMetric(
                    name="success_rate",
                    value=completed / total_workflows if total_workflows > 0 else 0,
                    unit="ratio",
                    timestamp=datetime.now()
                ),
                PerformanceMetric(
                    name="workflows_per_minute",
                    value=completed / (monitoring_duration / 60) if monitoring_duration > 0 else 0,
                    unit="workflows/min",
                    timestamp=datetime.now()
                )
            ])
            
            end_time = datetime.now()
            
            return BenchmarkResult(
                test_name=f"concurrent_workflows_{concurrent_count}",
                start_time=start_time,
                end_time=end_time,
                duration=(end_time - start_time).total_seconds(),
                metrics=metrics,
                memory_snapshot=self.get_memory_snapshot(),
                system_load=self.get_system_metrics(),
                repository_info={"concurrent_count": concurrent_count}
            )
            
        except Exception as e:
            end_time = datetime.now()
            print(f"  ❌ Concurrent benchmark failed: {e}")
            
            return BenchmarkResult(
                test_name=f"concurrent_workflows_{concurrent_count}_FAILED",
                start_time=start_time,
                end_time=end_time,
                duration=(end_time - start_time).total_seconds(),
                metrics=metrics,
                memory_snapshot=self.get_memory_snapshot(),
                system_load=self.get_system_metrics(),
                repository_info={"error": str(e)}
            )
    
    def identify_performance_bottlenecks(self, benchmark_results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Analyze benchmark results to identify performance bottlenecks"""
        print("🔍 Analyzing performance bottlenecks...")
        
        analysis = {
            "slowest_workflows": [],
            "high_memory_usage": [],
            "high_cpu_usage": [],
            "recommendations": []
        }
        
        for result in benchmark_results:
            duration = result.duration
            memory_mb = result.memory_snapshot.get("current_memory_mb", 0)
            cpu_percent = result.system_load.get("cpu_percent", 0)
            
            # Identify slow workflows (>300s)
            if duration > 300:
                analysis["slowest_workflows"].append({
                    "test": result.test_name,
                    "duration": duration,
                    "repository": result.repository_info.get("name", "unknown")
                })
            
            # Identify high memory usage (>500MB)
            if memory_mb > 500:
                analysis["high_memory_usage"].append({
                    "test": result.test_name,
                    "memory_mb": memory_mb,
                    "repository": result.repository_info.get("name", "unknown")
                })
            
            # Identify high CPU usage (>80%)
            if cpu_percent > 80:
                analysis["high_cpu_usage"].append({
                    "test": result.test_name,
                    "cpu_percent": cpu_percent,
                    "repository": result.repository_info.get("name", "unknown")
                })
        
        # Generate recommendations
        if analysis["slowest_workflows"]:
            analysis["recommendations"].append(
                "Consider optimizing large repository processing or implementing parallel processing"
            )
        
        if analysis["high_memory_usage"]:
            analysis["recommendations"].append(
                "Implement memory optimization techniques such as streaming processing or garbage collection tuning"
            )
        
        if analysis["high_cpu_usage"]:
            analysis["recommendations"].append(
                "Consider load balancing or resource allocation optimization"
            )
        
        if not analysis["slowest_workflows"] and not analysis["high_memory_usage"] and not analysis["high_cpu_usage"]:
            analysis["recommendations"].append("Performance metrics are within acceptable ranges")
        
        return analysis
    
    async def run_comprehensive_benchmark_suite(self) -> Dict[str, Any]:
        """Run complete performance benchmarking suite"""
        print("🚀 Starting comprehensive performance benchmark suite...")
        print("=" * 60)
        
        all_results = []
        
        # Benchmark 1: Individual agent response times
        print("\n1️⃣ Benchmarking agent response times...")
        agent_metrics = await self.benchmark_agent_response_time()
        all_results.append(BenchmarkResult(
            test_name="agent_response_times",
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration=0,
            metrics=agent_metrics,
            memory_snapshot=self.get_memory_snapshot(),
            system_load=self.get_system_metrics(),
            repository_info={"type": "agent_health"}
        ))
        
        # Benchmark 2: Workflow execution on different repositories
        print("\n2️⃣ Benchmarking workflow execution...")
        for repo_config in self.benchmark_repositories:
            workflow_result = await self.benchmark_workflow_execution(repo_config)
            all_results.append(workflow_result)
            print(f"  Result: {workflow_result.test_name} ({workflow_result.duration:.2f}s)")
        
        # Benchmark 3: Concurrent workflows
        print("\n3️⃣ Benchmarking concurrent workflows...")
        concurrent_result = await self.benchmark_concurrent_workflows(2)
        all_results.append(concurrent_result)
        print(f"  Result: {concurrent_result.test_name} ({concurrent_result.duration:.2f}s)")
        
        # Analyze results
        print("\n4️⃣ Analyzing performance bottlenecks...")
        bottleneck_analysis = self.identify_performance_bottlenecks(all_results)
        
        # Save results
        await self._save_benchmark_results(all_results, bottleneck_analysis)
        
        # Print summary
        self._print_benchmark_summary(all_results, bottleneck_analysis)
        
        return {
            "benchmark_results": all_results,
            "bottleneck_analysis": bottleneck_analysis
        }
    
    async def _save_benchmark_results(self, results: List[BenchmarkResult], analysis: Dict[str, Any]):
        """Save benchmark results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = self.results_dir / f"performance_benchmarks_{timestamp}.json"
        json_data = {
            "timestamp": timestamp,
            "results": [asdict(result) for result in results],
            "bottleneck_analysis": analysis
        }
        
        with open(json_file, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        # Save human-readable report
        report_file = self.results_dir / f"performance_report_{timestamp}.md"
        with open(report_file, 'w') as f:
            f.write(self._generate_benchmark_report(results, analysis))
        
        print(f"\n💾 Benchmark results saved:")
        print(f"   📊 JSON: {json_file}")
        print(f"   📝 Report: {report_file}")
    
    def _generate_benchmark_report(self, results: List[BenchmarkResult], analysis: Dict[str, Any]) -> str:
        """Generate human-readable benchmark report"""
        report = f"""# Codebase Genius Performance Benchmark Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Executive Summary

This report presents performance benchmarks for the Codebase Genius multi-agent system, including agent response times, workflow execution performance, and concurrent processing capabilities.

## Benchmark Results

"""
        
        for result in results:
            report += f"""### {result.test_name}

- **Duration:** {result.duration:.2f} seconds
- **Repository:** {result.repository_info.get('name', result.repository_info.get('type', 'unknown'))}

**Metrics:**
"""
            
            for metric in result.metrics:
                report += f"- {metric.name}: {metric.value:.2f} {metric.unit}\n"
            
            report += f"""
**System Load:**
- Memory: {result.system_load.get('memory_percent', 0):.1f}%
- CPU: {result.system_load.get('cpu_percent', 0):.1f}%

"""
        
        # Performance Analysis
        report += "## Performance Analysis\n\n"
        
        if analysis["slowest_workflows"]:
            report += "### Slowest Workflows (>300s)\n\n"
            for item in analysis["slowest_workflows"]:
                report += f"- **{item['test']}**: {item['duration']:.2f}s ({item['repository']})\n"
            report += "\n"
        
        if analysis["high_memory_usage"]:
            report += "### High Memory Usage (>500MB)\n\n"
            for item in analysis["high_memory_usage"]:
                report += f"- **{item['test']}**: {item['memory_mb']:.1f}MB ({item['repository']})\n"
            report += "\n"
        
        if analysis["high_cpu_usage"]:
            report += "### High CPU Usage (>80%)\n\n"
            for item in analysis["high_cpu_usage"]:
                report += f"- **{item['test']}**: {item['cpu_percent']:.1f}% ({item['repository']})\n"
            report += "\n"
        
        # Recommendations
        report += "## Recommendations\n\n"
        for i, recommendation in enumerate(analysis["recommendations"], 1):
            report += f"{i}. {recommendation}\n"
        
        report += f"""

## System Configuration

- **CPU Cores:** {results[0].system_load.get('cpu_count', 'unknown') if results else 'unknown'}
- **Memory:** {results[0].system_load.get('memory_used_mb', 0) / 1024:.1f}GB used / {results[0].system_load.get('memory_available_mb', 0) / 1024:.1f}GB available (if available)

## Conclusion

Performance testing completed successfully. See detailed metrics above for specific performance characteristics.
"""
        
        return report
    
    def _print_benchmark_summary(self, results: List[BenchmarkResult], analysis: Dict[str, Any]):
        """Print benchmark summary to console"""
        print("\n" + "=" * 60)
        print("⚡ PERFORMANCE BENCHMARK SUMMARY")
        print("=" * 60)
        
        for result in results:
            print(f"\n📊 {result.test_name}")
            print(f"   Duration: {result.duration:.2f}s")
            
            # Show key metrics
            key_metrics = [m for m in result.metrics if m.name in [
                "total_execution_time", "files_per_second", "entities_per_second",
                "workflows_per_minute", "success_rate"
            ]]
            
            for metric in key_metrics:
                print(f"   {metric.name}: {metric.value:.2f} {metric.unit}")
        
        print(f"\n🔍 Bottleneck Analysis:")
        if analysis["slowest_workflows"]:
            print(f"   ⚠️  {len(analysis['slowest_workflows'])} slow workflows identified")
        if analysis["high_memory_usage"]:
            print(f"   ⚠️  {len(analysis['high_memory_usage'])} high memory usage cases")
        if analysis["high_cpu_usage"]:
            print(f"   ⚠️  {len(analysis['high_cpu_usage'])} high CPU usage cases")
        
        if not analysis["slowest_workflows"] and not analysis["high_memory_usage"] and not analysis["high_cpu_usage"]:
            print("   ✅ No significant bottlenecks detected")
        
        print("=" * 60)

async def main():
    """Main benchmark execution"""
    benchmark_suite = PerformanceBenchmarkSuite()
    
    try:
        # Run comprehensive benchmark
        results = await benchmark_suite.run_comprehensive_benchmark_suite()
        
        print("\n✅ Performance benchmarking completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Benchmarking failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import os
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
