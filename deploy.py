#!/usr/bin/env python3
"""
Professional Deployment Script for ProjectOps Assistant
Sets up the environment and launches the enterprise project management system
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import config

def print_banner():
    """Print professional deployment banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║              🚀 ProjectOps Assistant v2.0.0                 ║
    ║                                                              ║
    ║         Enterprise Project Management System                 ║
    ║                                                              ║
    ║         Developed by: Jayshil Singh                          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit', 'pandas', 'plotly', 'streamlit-authenticator',
        'reportlab', 'openpyxl'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages)
    else:
        print("✅ All dependencies are installed")

def setup_environment():
    """Set up the project environment"""
    print("\n🔧 Setting up environment...")
    
    # Create directories
    config.ensure_directories()
    print("✅ Directory structure created")
    
    # Check if database exists
    if not config.DATABASE_PATH.exists():
        print("📊 Initializing database...")
        # Import and initialize database
        from database import ProjectOpsDatabase
        db = ProjectOpsDatabase(str(config.DATABASE_PATH))
        print("✅ Database initialized")
    else:
        print("✅ Database already exists")

def check_file_permissions():
    """Check file permissions and accessibility"""
    print("\n🔐 Checking file permissions...")
    
    try:
        # Test write access to projects directory
        test_file = config.PROJECTS_ROOT / "test_write.tmp"
        test_file.write_text("test")
        test_file.unlink()
        print("✅ Write permissions verified")
    except Exception as e:
        print(f"❌ Permission error: {e}")
        print("Please run as administrator or check folder permissions")
        sys.exit(1)

def validate_configuration():
    """Validate configuration settings"""
    print("\n⚙️ Validating configuration...")
    
    # Check paths
    paths_to_check = [
        config.PROJECTS_ROOT,
        config.CLIENT_PROJECTS_DIR,
        config.BACKUPS_DIR,
        config.TEMPLATES_DIR
    ]
    
    for path in paths_to_check:
        if not path.exists():
            print(f"⚠️ Warning: {path} does not exist (will be created)")
    
    print("✅ Configuration validated")

def start_application():
    """Start the Streamlit application"""
    print("\n🚀 Starting ProjectOps Assistant...")
    print("📱 Application will open in your default browser")
    print("🔗 Local URL: http://localhost:8501")
    print("🔄 Press Ctrl+C to stop the application")
    print("\n" + "="*60)
    
    try:
        # Start Streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.port', '8501',
            '--server.address', 'localhost'
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

def main():
    """Main deployment function"""
    print_banner()
    
    print("🔍 Pre-deployment checks...")
    check_python_version()
    check_dependencies()
    
    print("\n📁 Environment setup...")
    setup_environment()
    check_file_permissions()
    validate_configuration()
    
    print("\n🎯 Ready to launch!")
    start_application()

if __name__ == "__main__":
    main() 