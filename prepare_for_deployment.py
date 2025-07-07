#!/usr/bin/env python3
"""
Prepare ProjectOps Assistant for Streamlit Cloud Deployment
Creates necessary files and validates the deployment setup
"""

import os
import shutil
from pathlib import Path

def print_deployment_banner():
    """Print deployment preparation banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║         🚀 Streamlit Cloud Deployment Preparation           ║
    ║                                                              ║
    ║         ProjectOps Assistant v2.0.0                         ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_required_files():
    """Check if all required files exist for deployment"""
    print("🔍 Checking required files...")
    
    required_files = [
        "streamlit_app.py",
        "requirements.txt",
        "database.py",
        "chatbot.py",
        "reports.py",
        ".streamlit/config.toml",
        "packages.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("\n✅ All required files present")
        return True

def create_gitignore():
    """Create .gitignore file for the project"""
    print("\n📝 Creating .gitignore...")
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
*.db
*.sqlite
*.sqlite3
temp/
tmp/
uploads/

# Local configuration
.env
config_local.py

# Logs
*.log
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    
    print("✅ .gitignore created")

def create_readme_deployment():
    """Create deployment-specific README"""
    print("\n📖 Creating deployment README...")
    
    readme_content = """# ProjectOps Assistant - Streamlit Cloud Deployment

## 🚀 Quick Start

This repository contains the ProjectOps Assistant, a professional project management system deployed on Streamlit Cloud.

### Access the App
- **Live Demo**: [Your Streamlit Cloud URL]
- **Login**: admin / admin

### Features
- 📊 Professional Dashboard with Analytics
- 🤖 AI-Powered Chatbot
- 📁 Project Management
- 🗓️ Meeting & MoM Tracking
- 🧾 Client Update Logging
- 🛠️ Issue Tracking
- 📈 Advanced Analytics

### Technology Stack
- **Frontend**: Streamlit
- **Backend**: SQLite (temporary in cloud)
- **Charts**: Plotly
- **Authentication**: Streamlit Authenticator

### Local Development
```bash
git clone https://github.com/YOUR_USERNAME/projectops-assistant.git
cd projectops-assistant
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Deployment
This app is automatically deployed on Streamlit Cloud. Any changes pushed to the main branch will trigger a redeployment.

---
**ProjectOps Assistant** - Enterprise Project Management with AI
"""
    
    with open("README_DEPLOYMENT.md", "w") as f:
        f.write(readme_content)
    
    print("✅ Deployment README created")

def validate_dependencies():
    """Validate requirements.txt"""
    print("\n📦 Validating dependencies...")
    
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read()
        
        # Check for critical packages
        critical_packages = ["streamlit", "pandas", "plotly"]
        missing_critical = []
        
        for package in critical_packages:
            if package not in requirements:
                missing_critical.append(package)
        
        if missing_critical:
            print(f"❌ Missing critical packages: {', '.join(missing_critical)}")
            return False
        else:
            print("✅ All critical dependencies present")
            return True
            
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def create_deployment_checklist():
    """Create deployment checklist"""
    print("\n📋 Creating deployment checklist...")
    
    checklist_content = """# 🚀 Deployment Checklist

## Pre-Deployment
- [ ] All required files present
- [ ] Dependencies validated
- [ ] Code tested locally
- [ ] Git repository created
- [ ] Code pushed to GitHub

## Streamlit Cloud Setup
- [ ] Account created at share.streamlit.io
- [ ] GitHub repository connected
- [ ] App configured (streamlit_app.py)
- [ ] Deployment successful
- [ ] App accessible via URL

## Post-Deployment
- [ ] Authentication working
- [ ] All features functional
- [ ] Performance acceptable
- [ ] Security configured
- [ ] Monitoring set up

## Files to Verify
- [ ] streamlit_app.py (main app)
- [ ] requirements.txt (dependencies)
- [ ] .streamlit/config.toml (config)
- [ ] packages.txt (system deps)
- [ ] database.py (database module)
- [ ] chatbot.py (AI module)
- [ ] reports.py (reporting module)

## Security Notes
- [ ] Change default credentials
- [ ] Configure environment variables
- [ ] Set up external database (if needed)
- [ ] Review access permissions

---
**Status**: Ready for deployment ✅
"""
    
    with open("DEPLOYMENT_CHECKLIST.md", "w") as f:
        f.write(checklist_content)
    
    print("✅ Deployment checklist created")

def main():
    """Main preparation function"""
    print_deployment_banner()
    
    print("🔧 Preparing for Streamlit Cloud deployment...")
    
    # Check files
    if not check_required_files():
        print("\n❌ Deployment preparation failed - missing files")
        return
    
    # Validate dependencies
    if not validate_dependencies():
        print("\n❌ Deployment preparation failed - dependency issues")
        return
    
    # Create additional files
    create_gitignore()
    create_readme_deployment()
    create_deployment_checklist()
    
    print("\n" + "="*60)
    print("🎉 Deployment preparation completed successfully!")
    print("\n📋 Next steps:")
    print("1. Initialize git repository: git init")
    print("2. Add files: git add .")
    print("3. Commit: git commit -m 'Initial commit'")
    print("4. Create GitHub repository")
    print("5. Push to GitHub: git push -u origin main")
    print("6. Deploy on Streamlit Cloud")
    print("\n📖 See DEPLOYMENT_GUIDE.md for detailed instructions")
    print("="*60)

if __name__ == "__main__":
    main() 