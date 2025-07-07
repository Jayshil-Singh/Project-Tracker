import os
import shutil
from datetime import datetime
import pandas as pd

def organize_projects():
    """
    Automatically organize projects from Desktop to C:\Projects structure
    """
    
    # Source and destination paths
    source_dir = r"C:\Users\jayshil.singh\Desktop\All Projects"
    projects_root = r"C:\Projects"
    client_projects_dir = os.path.join(projects_root, "Client-Projects")
    
    # Software type mappings
    software_mappings = {
        'epicor': 'Epicor',
        'myob': 'MYOB', 
        'odoo': 'ODOO',
        'payglobal': 'PayGlobal',
        'pay global': 'PayGlobal',
        'sap': 'Others',
        'crystal': 'Others',
        'timesheet': 'Others',
        'ops': 'Others'
    }
    
    # Create main directories
    os.makedirs(projects_root, exist_ok=True)
    os.makedirs(client_projects_dir, exist_ok=True)
    
    # Create software-specific directories
    for software_dir in software_mappings.values():
        os.makedirs(os.path.join(client_projects_dir, software_dir), exist_ok=True)
    
    print("🔍 Scanning existing projects...")
    
    # Get all items in source directory
    try:
        items = os.listdir(source_dir)
    except FileNotFoundError:
        print(f"❌ Source directory not found: {source_dir}")
        return
    
    moved_count = 0
    skipped_count = 0
    
    for item in items:
        source_path = os.path.join(source_dir, item)
        
        # Skip if it's a file (not a directory)
        if not os.path.isdir(source_path):
            continue
            
        # Determine destination based on item name
        item_lower = item.lower()
        destination_dir = None
        
        # Check software mappings
        for keyword, software_type in software_mappings.items():
            if keyword in item_lower:
                destination_dir = os.path.join(client_projects_dir, software_type, item)
                break
        
        # If no mapping found, put in Others
        if destination_dir is None:
            destination_dir = os.path.join(client_projects_dir, "Others", item)
        
        # Move the directory
        try:
            if os.path.exists(destination_dir):
                print(f"⚠️  Skipping {item} - destination already exists")
                skipped_count += 1
            else:
                shutil.move(source_path, destination_dir)
                print(f"✅ Moved {item} to {destination_dir}")
                moved_count += 1
        except Exception as e:
            print(f"❌ Error moving {item}: {str(e)}")
            skipped_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   Moved: {moved_count} projects")
    print(f"   Skipped: {skipped_count} projects")
    print(f"\n📁 New structure created at: {projects_root}")
    
    # Create a summary report
    create_organization_report(projects_root, moved_count, skipped_count)

def create_organization_report(projects_root, moved_count, skipped_count):
    """Create a summary report of the organization"""
    
    report_path = os.path.join(projects_root, "organization_report.txt")
    
    with open(report_path, 'w') as f:
        f.write("ProjectOps Assistant - Project Organization Report\n")
        f.write("=" * 50 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Projects moved: {moved_count}\n")
        f.write(f"Projects skipped: {skipped_count}\n\n")
        
        f.write("Directory Structure:\n")
        f.write("-" * 20 + "\n")
        
        for root, dirs, files in os.walk(projects_root):
            level = root.replace(projects_root, '').count(os.sep)
            indent = ' ' * 2 * level
            f.write(f"{indent}{os.path.basename(root)}/\n")
            for file in files:
                f.write(f"{indent}  {file}\n")
    
    print(f"📄 Report saved to: {report_path}")

def create_project_template():
    """Create a template for new projects"""
    
    template_dir = os.path.join(r"C:\Projects", "Templates")
    os.makedirs(template_dir, exist_ok=True)
    
    template_content = """# Project Template

## Project Information
- **Project Name:** [Enter Project Name]
- **Client:** [Enter Client Name]
- **Software:** [Enter Software]
- **Vendor:** [Enter Vendor]
- **Start Date:** [Enter Start Date]
- **Deadline:** [Enter Deadline]
- **Status:** [In Progress/On Hold/Completed]

## Project Description
[Enter detailed project description]

## Key Contacts
- **Client Contact:** [Name, Email, Phone]
- **Vendor Contact:** [Name, Email, Phone]
- **Internal Team:** [Names]

## Important Files
- [List important documents, contracts, etc.]

## Notes
[Any additional notes or requirements]
"""
    
    template_file = os.path.join(template_dir, "project_template.md")
    with open(template_file, 'w') as f:
        f.write(template_content)
    
    print(f"📋 Project template created: {template_file}")

if __name__ == "__main__":
    print("🚀 Starting Project Organization...")
    print("=" * 40)
    
    # Organize existing projects
    organize_projects()
    
    # Create project template
    create_project_template()
    
    print("\n✅ Project organization complete!")
    print("\nNext steps:")
    print("1. Review the organization_report.txt")
    print("2. Update your ProjectOps Assistant to use the new paths")
    print("3. Run: cd C:\\Projects\\ProjectOps-Assistant")
    print("4. Run: python -m streamlit run app.py") 