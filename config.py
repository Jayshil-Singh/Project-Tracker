"""
Configuration file for ProjectOps Assistant
Centralized settings for the enterprise project management system
"""

import os
from pathlib import Path

# Base paths
PROJECTS_ROOT = Path(r"C:\Projects")
CLIENT_PROJECTS_DIR = PROJECTS_ROOT / "Client-Projects"
BACKUPS_DIR = PROJECTS_ROOT / "Backups"
TEMPLATES_DIR = PROJECTS_ROOT / "Templates"
PROJECTOPS_DIR = PROJECTS_ROOT / "ProjectOps-Assistant"

# Database configuration
DATABASE_PATH = PROJECTOPS_DIR / "projectops.db"

# File upload settings
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.jpg', '.jpeg', '.png']

# Authentication settings
AUTHENTICATOR_CONFIG = {
    "cookie_name": "projectops",
    "key": "abcdef",
    "cookie_expiry_days": 1
}

# UI Configuration
UI_CONFIG = {
    "page_title": "ProjectOps Assistant",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Chart colors
CHART_COLORS = {
    'in_progress': '#ffd700',
    'completed': '#28a745',
    'on_hold': '#dc3545',
    'pending': '#ffc107',
    'resolved': '#28a745'
}

# Software options
SOFTWARE_OPTIONS = [
    "Epicor",
    "MYOB",
    "ODOO", 
    "PayGlobal",
    "Sage",
    "Xero",
    "QuickBooks",
    "Other"
]

# Project status options
PROJECT_STATUS_OPTIONS = [
    "In Progress",
    "On Hold", 
    "Completed",
    "Cancelled"
]

# Issue status options
ISSUE_STATUS_OPTIONS = [
    "Pending",
    "In Progress",
    "Resolved",
    "Closed"
]

# Communication modes
COMMUNICATION_MODES = [
    "Email",
    "Call",
    "Meeting",
    "Video Call",
    "Other"
]

# Create directories if they don't exist
def ensure_directories():
    """Create all necessary directories"""
    directories = [
        PROJECTS_ROOT,
        CLIENT_PROJECTS_DIR,
        BACKUPS_DIR,
        TEMPLATES_DIR,
        PROJECTOPS_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Client-specific software directories
def get_client_software_dirs():
    """Get list of client software directories"""
    software_dirs = []
    if CLIENT_PROJECTS_DIR.exists():
        for software_dir in CLIENT_PROJECTS_DIR.iterdir():
            if software_dir.is_dir():
                software_dirs.append(software_dir.name)
    return software_dirs

# Export settings
EXPORT_CONFIG = {
    "pdf": {
        "page_size": "A4",
        "margin": 20,
        "font_size": 10
    },
    "excel": {
        "sheet_name": "Data",
        "index": False
    }
}

# Analytics settings
ANALYTICS_CONFIG = {
    "chart_height": 400,
    "chart_width": "100%",
    "color_scale": "viridis"
} 