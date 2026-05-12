#!/usr/bin/env python
"""
Run both Django and FastAPI servers simultaneously.

Django runs on port 8000 (default)
FastAPI runs on port 8001

Usage:
    python run_all.py
"""
import os
import sys
import subprocess
import signal
import time
from pathlib import Path

# Get the project directory
PROJECT_DIR = Path(__file__).resolve().parent

def run_servers():
    """Run Django and FastAPI servers."""
    print("=" * 70)
    print("Starting R-E-S-Q Backend with Django + FastAPI")
    print("=" * 70)
    print("\n📍 Django REST API: http://localhost:8000")
    print("📍 FastAPI IoT API: http://localhost:8001")
    print("📍 API Documentation: http://localhost:8001/docs")
    print("\nPress Ctrl+C to stop all servers\n")
    print("=" * 70 + "\n")

    # Start Django server
    django_process = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"],
        cwd=PROJECT_DIR,
    )

    # Give Django a moment to start
    time.sleep(2)

    # Start FastAPI server
    fastapi_process = subprocess.Popen(
        [sys.executable, "iot_fastapi.py"],
        cwd=PROJECT_DIR,
    )

    print("✓ Django server started")
    print("✓ FastAPI server started\n")

    def signal_handler(sig, frame):
        print("\n\n" + "=" * 70)
        print("Shutting down servers...")
        print("=" * 70)
        django_process.terminate()
        fastapi_process.terminate()
        
        # Wait for processes to terminate
        try:
            django_process.wait(timeout=5)
            fastapi_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            django_process.kill()
            fastapi_process.kill()
        
        print("✓ All servers stopped")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Keep processes running
    try:
        while True:
            # Check if processes are still running
            if django_process.poll() is not None:
                print("❌ Django server stopped unexpectedly")
                fastapi_process.terminate()
                sys.exit(1)
            
            if fastapi_process.poll() is not None:
                print("❌ FastAPI server stopped unexpectedly")
                django_process.terminate()
                sys.exit(1)
            
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    try:
        run_servers()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
