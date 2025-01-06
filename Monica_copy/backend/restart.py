#!/usr/bin/env python3
import subprocess
import time
import sys
import os

def kill_process_on_port(port):
    try:
        # Find process using the port
        result = subprocess.run(['lsof', '-i', f':{port}', '-t'], capture_output=True, text=True)
        pids = result.stdout.strip().split('\n')
        
        # Kill each process
        for pid in pids:
            if pid:
                print(f"Killing process {pid} on port {port}")
                subprocess.run(['kill', '-9', pid])
                time.sleep(0.5)  # Give some time for the process to die
        
        return True
    except Exception as e:
        print(f"Error killing processes: {e}")
        return False

def start_server():
    try:
        # Get the virtual environment python path
        venv_python = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'venv', 'bin', 'uvicorn')
        
        # Start the server with uvicorn
        cmd = [
            venv_python,
            "main:app",
            "--host", "127.0.0.1",
            "--port", "8080",
            "--reload",
            "--log-level", "debug"
        ]
        
        print("Starting server...")
        process = subprocess.Popen(
            cmd,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # Wait a bit to see if the server starts successfully
        time.sleep(2)
        
        # Check if the process is still running
        if process.poll() is None:
            print("Server started successfully!")
            return True
        else:
            print("Server failed to start!")
            return False
            
    except Exception as e:
        print(f"Error starting server: {e}")
        return False

def main():
    port = 8080
    
    print(f"Killing any processes on port {port}...")
    if kill_process_on_port(port):
        print("Successfully killed old processes")
    else:
        print("Failed to kill all processes")
        sys.exit(1)
    
    # Give a moment for ports to be freed
    time.sleep(1)
    
    if start_server():
        print("Server restart completed successfully!")
    else:
        print("Failed to restart server")
        sys.exit(1)

if __name__ == "__main__":
    main()
