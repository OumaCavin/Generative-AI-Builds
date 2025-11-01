#!/usr/bin/env python3
"""
Codebase Genius Startup Script
"""

import subprocess
import sys
import os
import time
import signal

class ServiceManager:
    def __init__(self):
        self.processes = []
    
    def start_api(self):
        """Start FastAPI server"""
        print("🌐 Starting API server on port 8000...")
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "api-frontend.api.main_api:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
        self.processes.append(("API", process))
        time.sleep(2)
        print("✅ API server started")
    
    def start_ui(self):
        """Start Streamlit UI"""
        print("💻 Starting Web UI on port 8501...")
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run",
            "api-frontend/frontend/streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ])
        self.processes.append(("UI", process))
        time.sleep(3)
        print("✅ Web UI started")
    
    def start_all(self):
        """Start all services"""
        print("🚀 Starting all services...")
        self.start_api()
        self.start_ui()
        
        print("\n🎉 All services started!")
        print("📱 Web Interface: http://localhost:8501")
        print("📚 API Docs: http://localhost:8000/docs")
        print("❤️  Health Check: http://localhost:8000/health")
        print("\nPress Ctrl+C to stop all services")
        
        try:
            for name, process in self.processes:
                process.wait()
        except KeyboardInterrupt:
            self.stop_all()
    
    def stop_all(self):
        """Stop all services"""
        print("\n🛑 Stopping all services...")
        for name, process in self.processes:
            process.terminate()
        print("✅ All services stopped")

if __name__ == "__main__":
    manager = ServiceManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "start":
            manager.start_all()
        elif command == "api":
            manager.start_api()
        elif command == "ui":
            manager.start_ui()
        elif command == "stop":
            manager.stop_all()
        else:
            print("Usage: python start.py [start|api|ui|stop]")
    else:
        print("Usage: python start.py [start|api|ui|stop]")
