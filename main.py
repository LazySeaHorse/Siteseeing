#!/usr/bin/env python3
"""
Siteseeing - Website Screenshot Capture Tool
Entry point with automatic virtual environment and dependency management.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def get_venv_python():
    """Get the path to the Python executable in the virtual environment."""
    if platform.system() == "Windows":
        return Path("venv") / "Scripts" / "python.exe"
    return Path("venv") / "bin" / "python"


def create_venv():
    """Create a virtual environment if it doesn't exist."""
    if not Path("venv").exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("Virtual environment created.")


def install_dependencies():
    """Install required dependencies in the virtual environment."""
    venv_python = get_venv_python()
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        # Create requirements.txt if it doesn't exist
        requirements = [
            "selenium>=4.0.0",
            "Pillow>=9.0.0",
            "webdriver-manager>=3.8.0",
        ]
        requirements_file.write_text("\n".join(requirements))
    
    print("Installing dependencies...")
    subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    print("Dependencies installed.")


def run_app():
    """Run the main application."""
    venv_python = get_venv_python()
    
    # Run the app using the venv Python
    result = subprocess.run([
        str(venv_python), "-c",
        "from webshot.app import main; main()"
    ])
    
    sys.exit(result.returncode)


def main():
    """Main entry point."""
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Check if we're already in the venv
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # Already in venv, just run the app
        from webshot.app import main as app_main
        app_main()
    else:
        # Not in venv, set it up
        create_venv()
        install_dependencies()
        run_app()


if __name__ == "__main__":
    main()