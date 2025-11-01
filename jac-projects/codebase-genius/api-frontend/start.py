#!/usr/bin/env python3
"""
Codebase Genius Startup Script
Main entry point for starting both API server and Streamlit frontend
"""

import os;
import sys;
import subprocess;
import signal;
import time;
import threading;
from pathlib import Path;

# Add project root to Python path
project_root = Path(__file__).parent.parent;
sys.path.insert(0, str(project_root));

# Import configuration
try:
    from config.settings import APIConfig, FrontendConfig, DeploymentConfig;
except ImportError as e:
    print(f"❌ Configuration import error: {e}");
    print("Please ensure all dependencies are installed: pip install -r requirements.txt");
    sys.exit(1);

class CodebaseGeniusLauncher:
    """Launcher for Codebase Genius components"""
    
    def __init__(self):
        self.api_process = None;
        self.frontend_process = None;
        self.running = False;
        
    def start_api_server(self):
        """Start the FastAPI server"""
        print("🚀 Starting API Server...");
        
        # Set environment variables
        os.environ["API_HOST"] = APIConfig.HOST;
        os.environ["API_PORT"] = str(APIConfig.PORT);
        os.environ["DEBUG"] = str(APIConfig.DEBUG);
        
        try:
            # Run uvicorn directly
            import uvicorn;
            
            print(f"✅ API Server starting on {APIConfig.HOST}:{APIConfig.PORT}");
            
            # Change to the api directory to ensure correct imports
            api_dir = project_root / "api-frontend" / "api";
            original_cwd = os.getcwd();
            os.chdir(str(api_dir));
            
            try:
                uvicorn.run(
                    "main_api:app",
                    host=APIConfig.HOST,
                    port=APIConfig.PORT,
                    reload=True,
                    log_level="info",
                    reload_dirs=[str(project_root / "api-frontend")]
                );
            finally:
                os.chdir(original_cwd);
            
        except Exception as e:
            print(f"❌ Failed to start API Server: {e}");
            import traceback;
            print(traceback.format_exc());
            return False;
            
    def start_frontend(self):
        """Start the Streamlit frontend"""
        print("🌐 Starting Frontend...");
        
        # Set environment variables
        os.environ["STREAMLIT_SERVER_PORT"] = str(FrontendConfig.STREAMLIT_SERVER_PORT);
        os.environ["STREAMLIT_SERVER_HOST"] = FrontendConfig.STREAMLIT_SERVER_HOST;
        
        try:
            # Start Streamlit
            cmd = [
                sys.executable, "-m", "streamlit", "run",
                "frontend/streamlit_app.py",
                "--server.port", str(FrontendConfig.STREAMLIT_SERVER_PORT),
                "--server.address", FrontendConfig.STREAMLIT_SERVER_HOST
            ];
            
            if FrontendConfig.STREAMLIT_DEBUG:
                cmd.append("--logger.level=debug");
                
            print(f"✅ Frontend starting on {FrontendConfig.STREAMLIT_SERVER_HOST}:{FrontendConfig.STREAMLIT_SERVER_PORT}");
            
            self.frontend_process = subprocess.Popen(
                cmd,
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            );
            
            # Wait for frontend to be ready
            time.sleep(3);
            
            if self.frontend_process.poll() is None:
                print("✅ Frontend started successfully");
                return True;
            else:
                stdout, stderr = self.frontend_process.communicate();
                print(f"❌ Frontend failed to start: {stderr.decode()}");
                return False;
                
        except Exception as e:
            print(f"❌ Failed to start Frontend: {e}");
            return False;
            
    def start_components(self, components="all"):
        """Start specified components"""
        print("🧠 Codebase Genius Launcher");
        print("=" * 50);
        
        components = components.lower();
        
        success = True;
        
        if components in ["all", "api"]:
            success &= self.start_api_server();
            
        if components in ["all", "frontend"]:
            success &= self.start_frontend();
            
        if success:
            print("\n🎉 Codebase Genius is running!");
            print(f"📊 API Server: http://{APIConfig.HOST}:{APIConfig.PORT}");
            print(f"�� Frontend: http://{FrontendConfig.STREAMLIT_SERVER_HOST}:{FrontendConfig.STREAMLIT_SERVER_PORT}");
            print("\nPress Ctrl+C to stop all services");
            
            try:
                self.running = True;
                
                # Keep the script running
                while self.running:
                    time.sleep(1);
                    
                    # Check if processes are still running
                    if self.frontend_process and self.frontend_process.poll() is not None:
                        print("❌ Frontend process terminated unexpectedly");
                        self.running = False;
                        
            except KeyboardInterrupt:
                print("\n🛑 Shutting down Codebase Genius...");
                self.shutdown();
                
        return success;
        
    def shutdown(self):
        """Shutdown all components"""
        self.running = False;
        
        if self.frontend_process:
            print("🛑 Stopping Frontend...");
            self.frontend_process.terminate();
            
            try:
                self.frontend_process.wait(timeout=5);
            except subprocess.TimeoutExpired:
                print("⚠️  Force killing Frontend process...");
                self.frontend_process.kill();
                
        print("✅ Codebase Genius stopped");
        
    def health_check(self):
        """Perform health check on all components"""
        import requests;
        
        print("🔍 Health Check");
        print("-" * 30);
        
        # Check API
        try:
            response = requests.get(f"http://{APIConfig.HOST}:{APIConfig.PORT}/health", timeout=5);
            if response.status_code == 200:
                print("✅ API Server: Healthy");
            else:
                print("❌ API Server: Unhealthy");
        except Exception as e:
            print(f"❌ API Server: Error - {e}");
            
        # Check Frontend
        try:
            response = requests.get(f"http://{FrontendConfig.STREAMLIT_SERVER_HOST}:{FrontendConfig.STREAMLIT_SERVER_PORT}", timeout=5);
            if response.status_code == 200:
                print("✅ Frontend: Healthy");
            else:
                print("❌ Frontend: Unhealthy");
        except Exception as e:
            print(f"❌ Frontend: Error - {e}");
            
    def install_dependencies(self):
        """Install required dependencies"""
        print("📦 Installing dependencies...");
        
        requirements_file = project_root / "api-frontend" / "requirements.txt";
        
        if not requirements_file.exists():
            print(f"❌ Requirements file not found: {requirements_file}");
            return False;
            
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ]);
            print("✅ Dependencies installed successfully");
            return True;
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}");
            return False;

def print_usage():
    """Print usage information"""
    print("""
🧠 Codebase Genius Launcher

Usage:
    python start.py [command] [options]

Commands:
    start [component]     Start services (api, frontend, or all)
    health               Check service health
    install              Install dependencies
    help                 Show this help message

Components:
    api                  Start only API server
    frontend             Start only Streamlit frontend
    all                  Start both API and frontend (default)

Examples:
    python start.py start                    # Start both services
    python start.py start api               # Start only API
    python start.py start frontend          # Start only frontend
    python start.py health                  # Check service health
    python start.py install                 # Install dependencies
""");

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print_usage();
        return;
        
    command = sys.argv[1].lower();
    launcher = CodebaseGeniusLauncher();
    
    try:
        if command == "start":
            component = sys.argv[2].lower() if len(sys.argv) > 2 else "all";
            launcher.start_components(component);
            
        elif command == "health":
            launcher.health_check();
            
        elif command == "install":
            launcher.install_dependencies();
            
        elif command in ["help", "-h", "--help"]:
            print_usage();
            
        else:
            print(f"❌ Unknown command: {command}");
            print_usage();
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user");
        launcher.shutdown();
    except Exception as e:
        print(f"❌ Unexpected error: {e}");
        launcher.shutdown();

if __name__ == "__main__":
    main();
