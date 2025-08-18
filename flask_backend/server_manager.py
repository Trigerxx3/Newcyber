#!/usr/bin/env python3
"""
Permanent Flask Server Manager - Keeps the server running reliably
"""
import os
import sys
import time
import signal
import logging
import threading
import subprocess
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FlaskServerManager:
    def __init__(self):
        self.server_process = None
        self.should_run = True
        self.restart_count = 0
        self.max_restarts = 10
        self.restart_delay = 5
        
    def signal_handler(self, sig, frame):
        logger.info('🛑 Shutdown signal received')
        self.should_run = False
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=10)
            except:
                if self.server_process.poll() is None:
                    self.server_process.kill()
        sys.exit(0)
    
    def start_flask_server(self):
        """Start the Flask server process"""
        try:
            # Change to script directory
            script_dir = Path(__file__).parent
            os.chdir(script_dir)
            
            logger.info("🚀 Starting Flask server...")
            
            # Start the server process
            self.server_process = subprocess.Popen(
                [sys.executable, 'run.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            logger.info(f"✅ Flask server started with PID: {self.server_process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start Flask server: {e}")
            return False
    
    def is_server_healthy(self):
        """Check if the server is responding"""
        try:
            import requests
            response = requests.get('http://127.0.0.1:5000/health', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def monitor_server_output(self):
        """Monitor server output in a separate thread"""
        if not self.server_process:
            return
            
        try:
            for line in iter(self.server_process.stdout.readline, ''):
                if line.strip():
                    # Log important server messages
                    if any(keyword in line.lower() for keyword in ['error', 'exception', 'traceback']):
                        logger.error(f"Server Error: {line.strip()}")
                    elif 'running on' in line.lower():
                        logger.info(f"Server Ready: {line.strip()}")
                        
        except Exception as e:
            logger.error(f"Error monitoring server output: {e}")
    
    def run(self):
        """Main server management loop"""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.info("🔄 Flask Server Manager Starting...")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)
        
        while self.should_run and self.restart_count < self.max_restarts:
            try:
                # Start server if not running
                if not self.server_process or self.server_process.poll() is not None:
                    if not self.start_flask_server():
                        logger.error(f"Failed to start server. Attempt {self.restart_count + 1}/{self.max_restarts}")
                        self.restart_count += 1
                        time.sleep(self.restart_delay)
                        continue
                    
                    # Start monitoring in background thread
                    monitor_thread = threading.Thread(target=self.monitor_server_output, daemon=True)
                    monitor_thread.start()
                    
                    # Reset restart count on successful start
                    self.restart_count = 0
                
                # Wait a bit before health check
                time.sleep(10)
                
                # Check if process is still alive
                if self.server_process.poll() is not None:
                    logger.warning("⚠️ Server process has stopped. Restarting...")
                    self.restart_count += 1
                    time.sleep(self.restart_delay)
                    continue
                
                # Check if server is responding
                if not self.is_server_healthy():
                    logger.warning("⚠️ Server health check failed. Restarting...")
                    if self.server_process:
                        self.server_process.terminate()
                        time.sleep(3)
                        if self.server_process.poll() is None:
                            self.server_process.kill()
                    self.restart_count += 1
                    time.sleep(self.restart_delay)
                    continue
                
                # Server is healthy
                logger.info(f"✅ Server is healthy (PID: {self.server_process.pid})")
                
                # Wait before next check
                time.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("🛑 Received keyboard interrupt")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                time.sleep(5)
        
        if self.restart_count >= self.max_restarts:
            logger.error(f"❌ Max restart attempts ({self.max_restarts}) reached. Giving up.")
        
        logger.info("🛑 Server manager stopped")

def main():
    """Main entry point"""
    manager = FlaskServerManager()
    manager.run()

if __name__ == "__main__":
    main()