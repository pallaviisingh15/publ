"""
Single-command launcher for the Newspaper Distribution System.

Usage:
    python start.py

Starts:
  1. Database init  (creates tables + seeds admin user)
  2. Backend API    http://localhost:8000  (FastAPI / uvicorn)
  3. Frontend UI    http://localhost:8501  (Streamlit)
"""
import os
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent
PYTHON = sys.executable
ENV = {**os.environ, "PYTHONPATH": str(BASE_DIR / "src")}


def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, env=ENV, cwd=BASE_DIR, **kwargs)


def _popen(cmd: list[str]) -> subprocess.Popen:
    return subprocess.Popen(cmd, env=ENV, cwd=BASE_DIR)


def main() -> None:
    print("=" * 56)
    print("  Newspaper Distribution System")
    print("=" * 56)

    # 1. Init DB
    print("\n[1/3] Initialising database…")
    result = _run([PYTHON, "scripts/init_db.py"])
    if result.returncode != 0:
        print("Database initialisation failed. Check your DATABASE_URL in .env")
        sys.exit(1)

    # 2. Backend
    print("\n[2/3] Starting backend API on http://localhost:8000 …")
    backend = _popen([
        PYTHON, "-m", "uvicorn", "backend.main:app",
        "--host", "0.0.0.0", "--port", "8000", "--reload",
    ])

    # Give uvicorn time to bind
    time.sleep(3)

    if backend.poll() is not None:
        print("Backend failed to start. Check logs above.")
        sys.exit(1)

    # 3. Frontend
    print("[3/3] Starting frontend UI on http://localhost:8501 …")
    frontend = _popen([
        PYTHON, "-m", "streamlit", "run",
        str(BASE_DIR / "src" / "frontend" / "main.py"),
        "--server.port", "8501",
        "--server.headless", "true",
    ])

    print()
    print("=" * 56)
    print("  Application is running!")
    print("  Frontend : http://localhost:8501")
    print("  API      : http://localhost:8000")
    print("  API Docs : http://localhost:8000/docs")
    print("  Login    : admin / admin123  (change after first login)")
    print("  Press Ctrl+C to stop all services.")
    print("=" * 56)

    try:
        frontend.wait()
    except KeyboardInterrupt:
        print("\nShutting down…")
    finally:
        frontend.terminate()
        backend.terminate()
        print("Stopped.")


if __name__ == "__main__":
    main()
