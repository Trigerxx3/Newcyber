#!/usr/bin/env python3
"""
Robust Flask server startup script with auto-restart functionality
"""
import os
import sys
import time
import subprocess
import signal
from pathlib import Path

def signal_handler(sig, frame):
    print('\n🛑 Server shutdown requested...')
    sys.exit(0)

def start_flask_server():
    """Start the Flask server with proper error handling"""
    try:
        print("🚀 Starting Cyber Intelligence Platform API server...")
        print(f"📂 Working directory: {os.getcwd()}")
        print(f"🐍 Python executable: {sys.executable}")
        
        # Change to the correct directory
        script_dir = Path(__file__).parent
        os.chdir(script_dir)
        
        # Import and run the Flask app
        from app import create_app
        
        app = create_app()
        
        # Configure server settings
        host = '0.0.0.0'
        port = 5000
        debug = True
        
        print(f"🌐 Server starting on http://{host}:{port}")
        print(f"📋 Health check: http://127.0.0.1:{port}/health")
        print(f"🔧 Debug mode: {debug}")
        print("=" * 50)
        
        # Start the server
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=False,  # Disable reloader to prevent issues
            threaded=True
        )
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

def main():
    """Main function with restart logic"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🔄 Flask Server Manager Starting...")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            if start_flask_server():
                print("✅ Server started successfully!")
                break
            else:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"⚠️ Server failed to start. Retrying in 5 seconds... ({retry_count}/{max_retries})")
                    time.sleep(5)
                else:
                    print("❌ Max retries reached. Server failed to start.")
                    sys.exit(1)
                    
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"⚠️ Retrying in 5 seconds... ({retry_count}/{max_retries})")
                time.sleep(5)
            else:
                print("❌ Max retries reached. Exiting.")
                sys.exit(1)

if __name__ == "__main__":
    main()