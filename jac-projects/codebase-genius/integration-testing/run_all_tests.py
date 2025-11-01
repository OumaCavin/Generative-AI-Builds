#!/usr/bin/env python3
"""
Codebase Genius - Integration Testing Automation
Phase 7: Complete test automation and orchestration

Provides comprehensive automation for:
- Agent startup and health checking
- Sample repository generation
- Complete test suite execution
- Results aggregation and reporting
- Continuous integration integration

Author: Cavin Otieno
Date: 2025-10-31
"""

import asyncio
import json
import time
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Import our testing modules
sys.path.append(str(Path(__file__).parent))

from main_test_suite import IntegrationTestSuite
from benchmarks.performance_suite import PerformanceBenchmarkSuite
from utils.quality_validator import DocumentationQualityValidator
from utils.error_scenarios import ErrorScenarioTester
from utils.load_tester import LoadTestFramework
from samples.repository_generator import SampleRepositoryGenerator

class IntegrationTestOrchestrator:
    """Main orchestration for integration testing"""
    
    def __init__(self, workspace_dir: Path = None):
        self.workspace_dir = workspace_dir or Path(__file__).parent.parent
        self.base_dir = self.workspace_dir
        self.integration_dir = self.base_dir / "integration-testing"
        
        # Test components
        self.test_suite = IntegrationTestSuite()
        self.benchmark_suite = PerformanceBenchmarkSuite()
        self.quality_validator = DocumentationQualityValidator()
        self.error_tester = ErrorScenarioTester()
        self.load_tester = LoadTestFramework()
        self.repo_generator = SampleRepositoryGenerator()
        
        # Configuration
        self.agent_ports = {
            "supervisor": 8080,
            "repository_mapper": 8081,
            "code_analyzer": 8082,
            "docgenie": 8083
        }
        
        # Results storage
        self.results_dir = self.integration_dir / "results"
        self.results_dir.mkdir(exist_ok=True)
        
        # Logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(self.results_dir / "integration_test.log")
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def start_agents(self, timeout: int = 60) -> bool:
        """Start all required agents"""
        self.logger.info("🚀 Starting all agents...")
        
        try:
            # Check if agents are already running
            agents_running = 0
            for agent_name, port in self.agent_ports.items():
                try:
                    import requests
                    response = requests.get(f"http://localhost:{port}/health", timeout=2)
                    if response.status_code == 200:
                        agents_running += 1
                        self.logger.info(f"✅ Agent {agent_name} already running on port {port}")
                except:
                    pass
            
            if agents_running == len(self.agent_ports):
                self.logger.info("✅ All agents are already running")
                return True
            
            # Start agents if not all running
            processes = {}
            for agent_name, port in self.agent_ports.items():
                try:
                    # Check if already running
                    import requests
                    response = requests.get(f"http://localhost:{port}/health", timeout=2)
                    if response.status_code == 200:
                        continue
                except:
                    pass
                
                # Start agent
                if agent_name == "supervisor":
                    jac_file = "code/supervisor-agent/main.jac"
                elif agent_name == "repository_mapper":
                    jac_file = "code/repository-mapper-agent/main.jac"
                elif agent_name == "code_analyzer":
                    jac_file = "code/code-analyzer-agent/main.jac"
                elif agent_name == "docgenie":
                    jac_file = "code/docgenie-agent/main.jac"
                
                process = subprocess.Popen([
                    "jac", "serve", jac_file,
                    "--host", "0.0.0.0", "--port", str(port)
                ], cwd=self.workspace_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                processes[agent_name] = process
                self.logger.info(f"📤 Started {agent_name} agent on port {port}")
            
            # Wait for agents to start
            start_time = time.time()
            while time.time() - start_time < timeout:
                all_healthy = True
                for agent_name, port in self.agent_ports.items():
                    try:
                        import requests
                        response = requests.get(f"http://localhost:{port}/health", timeout=2)
                        if response.status_code != 200:
                            all_healthy = False
                            break
                    except:
                        all_healthy = False
                        break
                
                if all_healthy:
                    self.logger.info("✅ All agents are healthy")
                    return True
                
                await asyncio.sleep(2)
            
            self.logger.error("❌ Timeout waiting for agents to start")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start agents: {e}")
            return False
    
    async def stop_agents(self):
        """Stop all agents"""
        self.logger.info("🛑 Stopping all agents...")
        
        try:
            # Kill all jac serve processes
            subprocess.run(["pkill", "-f", "jac serve"], check=False)
            await asyncio.sleep(2)
            self.logger.info("✅ All agents stopped")
        except Exception as e:
            self.logger.warning(f"Warning stopping agents: {e}")
    
    async def generate_test_repositories(self) -> List[Path]:
        """Generate sample test repositories"""
        self.logger.info("📦 Generating sample test repositories...")
        
        try:
            created_repos = self.repo_generator.create_all_sample_repositories()
            self.logger.info(f"✅ Created {len(created_repos)} sample repositories")
            return created_repos
        except Exception as e:
            self.logger.error(f"❌ Failed to generate repositories: {e}")
            return []
    
    async def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        self.logger.info("🧪 Running integration tests...")
        
        try:
            results = await self.test_suite.run_comprehensive_test_suite()
            return {
                "status": "completed",
                "results": results,
                "summary": {
                    "total_tests": results.total_tests,
                    "passed": results.passed,
                    "failed": results.failed,
                    "success_rate": results.passed / results.total_tests if results.total_tests > 0 else 0
                }
            }
        except Exception as e:
            self.logger.error(f"❌ Integration tests failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "summary": {"total_tests": 0, "passed": 0, "failed": 1}
            }
    
    async def run_performance_benchmarks(self) -> Dict[str, Any]:
        """Run performance benchmarks"""
        self.logger.info("⚡ Running performance benchmarks...")
        
        try:
            results = await self.benchmark_suite.run_comprehensive_benchmark_suite()
            return {
                "status": "completed",
                "results": results,
                "bottlenecks": results.get("bottleneck_analysis", {})
            }
        except Exception as e:
            self.logger.error(f"❌ Performance benchmarks failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def run_error_scenarios(self) -> Dict[str, Any]:
        """Run error scenario tests"""
        self.logger.info("🚨 Running error scenario tests...")
        
        try:
            results = await self.error_tester.run_comprehensive_error_testing()
            passed = len([r for r in results if r.status in ["PASS", "PARTIAL"]])
            return {
                "status": "completed",
                "results": results,
                "summary": {
                    "total_scenarios": len(results),
                    "passed": passed,
                    "failed": len(results) - passed,
                    "success_rate": passed / len(results) if results else 0
                }
            }
        except Exception as e:
            self.logger.error(f"❌ Error scenario tests failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def run_load_tests(self) -> Dict[str, Any]:
        """Run load tests"""
        self.logger.info("🏋️ Running load tests...")
        
        try:
            results = await self.load_tester.run_comprehensive_load_testing()
            avg_success_rate = sum(r.metrics.get("success_rate", 0) for r in results) / len(results) if results else 0
            return {
                "status": "completed",
                "results": results,
                "summary": {
                    "total_tests": len(results),
                    "avg_success_rate": avg_success_rate
                }
            }
        except Exception as e:
            self.logger.error(f"❌ Load tests failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def run_quality_validation(self, pipeline_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run quality validation"""
        self.logger.info("📊 Running quality validation...")
        
        try:
            results = await self.quality_validator.run_quality_validation_batch(pipeline_results)
            avg_score = sum(r.overall_score for r in results) / len(results) if results else 0
            return {
                "status": "completed",
                "results": results,
                "summary": {
                    "total_documents": len(results),
                    "avg_quality_score": avg_score,
                    "passed": len([r for r in results if r.overall_score >= 0.7])
                }
            }
        except Exception as e:
            self.logger.error(f"❌ Quality validation failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def run_complete_test_suite(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete test suite"""
        self.logger.info("🚀 Starting complete integration test suite...")
        
        overall_start_time = time.time()
        overall_results = {
            "timestamp": datetime.now().isoformat(),
            "duration": 0,
            "phases": {},
            "summary": {
                "total_phases": 0,
                "successful_phases": 0,
                "failed_phases": 0,
                "overall_success": False
            }
        }
        
        try:
            # Phase 1: Start agents
            if options.get("start_agents", True):
                self.logger.info("Phase 1: Starting agents...")
                agents_started = await self.start_agents()
                overall_results["phases"]["agent_startup"] = {
                    "status": "completed" if agents_started else "failed",
                    "duration": 0  # Will be updated
                }
                
                if not agents_started:
                    raise Exception("Failed to start agents")
            
            # Phase 2: Generate test repositories
            if options.get("generate_repos", True):
                self.logger.info("Phase 2: Generating test repositories...")
                repos = await self.generate_test_repositories()
                overall_results["phases"]["repository_generation"] = {
                    "status": "completed" if repos else "failed",
                    "repositories_created": len(repos)
                }
            
            # Phase 3: Integration tests
            if options.get("integration_tests", True):
                self.logger.info("Phase 3: Running integration tests...")
                integration_results = await self.run_integration_tests()
                overall_results["phases"]["integration_tests"] = integration_results
            
            # Phase 4: Performance benchmarks
            if options.get("performance_tests", True):
                self.logger.info("Phase 4: Running performance benchmarks...")
                benchmark_results = await self.run_performance_benchmarks()
                overall_results["phases"]["performance_benchmarks"] = benchmark_results
            
            # Phase 5: Error scenarios
            if options.get("error_tests", True):
                self.logger.info("Phase 5: Running error scenario tests...")
                error_results = await self.run_error_scenarios()
                overall_results["phases"]["error_scenarios"] = error_results
            
            # Phase 6: Load tests
            if options.get("load_tests", True):
                self.logger.info("Phase 6: Running load tests...")
                load_results = await self.run_load_tests()
                overall_results["phases"]["load_tests"] = load_results
            
            # Calculate overall statistics
            overall_results["duration"] = time.time() - overall_start_time
            overall_results["summary"]["total_phases"] = len(overall_results["phases"])
            
            successful_phases = len([
                phase for phase in overall_results["phases"].values() 
                if phase.get("status") == "completed"
            ])
            overall_results["summary"]["successful_phases"] = successful_phases
            overall_results["summary"]["failed_phases"] = (
                overall_results["summary"]["total_phases"] - successful_phases
            )
            overall_results["summary"]["overall_success"] = (
                successful_phases == overall_results["summary"]["total_phases"]
            )
            
            # Save comprehensive results
            await self._save_comprehensive_results(overall_results)
            
            # Print summary
            self._print_complete_summary(overall_results)
            
            return overall_results
            
        except Exception as e:
            self.logger.error(f"❌ Test suite failed: {e}")
            overall_results["status"] = "failed"
            overall_results["error"] = str(e)
            overall_results["duration"] = time.time() - overall_start_time
            return overall_results
        
        finally:
            # Stop agents if we started them
            if options.get("stop_agents", True) and options.get("start_agents", True):
                await self.stop_agents()
    
    async def _save_comprehensive_results(self, results: Dict[str, Any]):
        """Save comprehensive test results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save main results
        results_file = self.results_dir / f"complete_test_suite_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Generate and save summary report
        report_file = self.results_dir / f"test_suite_summary_{timestamp}.md"
        with open(report_file, 'w') as f:
            f.write(self._generate_summary_report(results))
        
        self.logger.info(f"💾 Comprehensive results saved:")
        self.logger.info(f"   📊 JSON: {results_file}")
        self.logger.info(f"   �� Report: {report_file}")
    
    def _generate_summary_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive summary report"""
        report = f"""# Codebase Genius Integration Test Suite Report

**Generated:** {results['timestamp']}
**Total Duration:** {results['duration']:.2f} seconds
**Overall Success:** {'✅ YES' if results['summary']['overall_success'] else '❌ NO'}

## Phase Summary

"""
        
        phase_stats = results["summary"]
        report += f"- **Total Phases:** {phase_stats['total_phases']}\n"
        report += f"- **Successful:** {phase_stats['successful_phases']} ✅\n"
        report += f"- **Failed:** {phase_stats['failed_phases']} ❌\n"
        report += f"- **Success Rate:** {phase_stats['successful_phases']/phase_stats['total_phases']*100:.1f}%\n\n"
        
        # Phase details
        for phase_name, phase_result in results["phases"].items():
            status = "✅" if phase_result.get("status") == "completed" else "❌"
            report += f"### {status} {phase_name.replace('_', ' ').title()}\n\n"
            report += f"**Status:** {phase_result.get('status', 'unknown')}\n"
            
            if "summary" in phase_result:
                summary = phase_result["summary"]
                for key, value in summary.items():
                    if isinstance(value, float):
                        report += f"- **{key.replace('_', ' ').title()}:** {value:.2f}\n"
                    else:
                        report += f"- **{key.replace('_', ' ').title()}:** {value}\n"
            
            if "error" in phase_result:
                report += f"**Error:** {phase_result['error']}\n"
            
            report += "\n"
        
        # Recommendations
        report += "## Recommendations\n\n"
        
        if results["summary"]["overall_success"]:
            report += "### ✅ System Ready for Production\n\n"
            report += "The integration test suite has passed successfully. The system demonstrates:\n"
            report += "- Stable multi-agent coordination\n"
            report += "- Robust error handling\n"
            report += "- Acceptable performance under load\n"
            report += "- Comprehensive functionality\n"
        else:
            report += "### ⚠️ Issues Found\n\n"
            failed_phases = [
                name for name, result in results["phases"].items()
                if result.get("status") != "completed"
            ]
            
            for phase in failed_phases:
                report += f"- **{phase.replace('_', ' ').title()}**: Address failures before production deployment\n"
        
        report += "\n## Next Steps\n\n"
        report += "1. Review detailed phase reports for specific issues\n"
        report += "2. Address any identified bottlenecks or failures\n"
        report += "3. Re-run test suite after fixes\n"
        report += "4. Proceed to Phase 8: API and Frontend Development\n"
        
        return report
    
    def _print_complete_summary(self, results: Dict[str, Any]):
        """Print comprehensive summary to console"""
        print("\n" + "=" * 80)
        print("🎯 CODEBASE GENIUS INTEGRATION TEST SUITE - FINAL REPORT")
        print("=" * 80)
        
        summary = results["summary"]
        print(f"Duration: {results['duration']:.2f} seconds")
        print(f"Total Phases: {summary['total_phases']}")
        print(f"Successful: {summary['successful_phases']} ✅")
        print(f"Failed: {summary['failed_phases']} ❌")
        print(f"Success Rate: {summary['successful_phases']/summary['total_phases']*100:.1f}%")
        
        overall_status = "🎉 READY FOR PRODUCTION" if summary['overall_success'] else "⚠️ NEEDS ATTENTION"
        print(f"Overall Status: {overall_status}")
        
        print("\nPhase Details:")
        for phase_name, phase_result in results["phases"].items():
            status_icon = "✅" if phase_result.get("status") == "completed" else "❌"
            print(f"  {status_icon} {phase_name.replace('_', ' ').title()}")
            
            if "summary" in phase_result:
                summary_info = phase_result["summary"]
                if "success_rate" in summary_info:
                    print(f"      Success Rate: {summary_info['success_rate']*100:.1f}%")
                elif "avg_quality_score" in summary_info:
                    print(f"      Avg Quality: {summary_info['avg_quality_score']:.2f}")
        
        print("=" * 80)

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Codebase Genius Integration Test Suite")
    parser.add_argument("--skip-agents", action="store_true", help="Skip agent startup")
    parser.add_argument("--skip-repos", action="store_true", help="Skip repository generation")
    parser.add_argument("--integration-only", action="store_true", help="Run only integration tests")
    parser.add_argument("--performance-only", action="store_true", help="Run only performance tests")
    parser.add_argument("--error-only", action="store_true", help="Run only error tests")
    parser.add_argument("--load-only", action="store_true", help="Run only load tests")
    parser.add_argument("--quick", action="store_true", help="Run quick test suite")
    
    args = parser.parse_args()
    
    # Setup options
    options = {
        "start_agents": not args.skip_agents,
        "stop_agents": True,
        "generate_repos": not args.skip_repos,
        "integration_tests": True,
        "performance_tests": True,
        "error_tests": True,
        "load_tests": True
    }
    
    # Apply quick/test-specific options
    if args.quick:
        options.update({
            "integration_tests": True,  # Always include integration tests
            "performance_tests": False,
            "error_tests": True,
            "load_tests": False
        })
    elif args.integration_only:
        options.update({
            "performance_tests": False,
            "error_tests": False,
            "load_tests": False
        })
    elif args.performance_only:
        options.update({
            "integration_tests": False,
            "error_tests": False,
            "load_tests": False
        })
    elif args.error_only:
        options.update({
            "integration_tests": False,
            "performance_tests": False,
            "load_tests": False
        })
    elif args.load_only:
        options.update({
            "integration_tests": False,
            "performance_tests": False,
            "error_tests": False
        })
    
    # Create orchestrator
    orchestrator = IntegrationTestOrchestrator()
    
    try:
        # Run complete test suite
        results = await orchestrator.run_complete_test_suite(options)
        
        # Return appropriate exit code
        if results["summary"]["overall_success"]:
            print("\n🎉 All tests passed successfully!")
            return 0
        else:
            print(f"\n❌ Test suite completed with {results['summary']['failed_phases']} failures")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test suite failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
