#!/usr/bin/env python3
"""
Simple Flask Server Manager - Windows Compatible
"""
import os
import sys
import time
import signal
import subprocess
from pathlib import Path

class SimpleFlaskManager:
    def __init__(self):
        self.server_process = None
        self.should_run = True
        self.restart_count = 0
        self.max_restarts = 10
        
    def signal_handler(self, sig, frame):
        print('Server shutdown requested...')
        self.should_run = False
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=10)
            except:
                if self.server_process.poll() is None:
                    self.server_process.kill()
        sys.exit(0)
    
    def start_server(self):
        """Start the Flask server"""
        try:
            script_dir = Path(__file__).parent
            os.chdir(script_dir)
            
            print("Starting Flask server...")
            
            # Start server with minimal output
            self.server_process = subprocess.Popen(
                [sys.executable, 'run_simple.py'],
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            print(f"Server started with PID: {self.server_process.pid}")
            return True
            
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False
    
    def is_server_healthy(self):
        """Check if server is responding"""
        try:
            import requests
            response = requests.get('http://127.0.0.1:5000/health', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def run(self):
        """Main management loop"""
        signal.signal(signal.SIGINT, self.signal_handler)
        
        print("=" * 50)
        print("Flask Server Manager Starting...")
        print("Press Ctrl+C to stop")
        print("=" * 50)
        
        while self.should_run and self.restart_count < self.max_restarts:
            try:
                # Start server if not running
                if not self.server_process or self.server_process.poll() is not None:
                    if not self.start_server():
                        print(f"Start failed. Attempt {self.restart_count + 1}/{self.max_restarts}")
                        self.restart_count += 1
                        time.sleep(5)
                        continue
                    
                    self.restart_count = 0
                
                # Wait before checking
                time.sleep(10)
                
                # Check if process died
                if self.server_process.poll() is not None:
                    print("Server process stopped. Restarting...")
                    self.restart_count += 1
                    time.sleep(5)
                    continue
                
                # Check health
                if not self.is_server_healthy():
                    print("Health check failed. Restarting...")
                    if self.server_process:
                        self.server_process.terminate()
                        time.sleep(3)
                        if self.server_process.poll() is None:
                            self.server_process.kill()
                    self.restart_count += 1
                    time.sleep(5)
                    continue
                
                print(f"Server healthy (PID: {self.server_process.pid})")
                time.sleep(30)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)
        
        if self.restart_count >= self.max_restarts:
            print(f"Max restarts ({self.max_restarts}) reached.")
        
        print("Server manager stopped")

if __name__ == "__main__":
    manager = SimpleFlaskManager()
    manager.run()