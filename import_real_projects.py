import os
import sys
from datetime import datetime, timedelta
import re

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import ProjectOpsDatabase

def extract_project_info_from_directory(dir_path, dir_name, parent_dir=""):
    """Extract project information from directory name and contents"""
    
    # Default project info
    project_info = {
        "project_name": dir_name,
        "client_name": "Unknown",
        "software": "Unknown",
        "vendor": "Unknown",
        "start_date": datetime.now().strftime('%Y-%m-%d'),
        "deadline": (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'),
        "status": "In Progress",
        "description": f"Project files for {dir_name}"
    }
    
    # Software detection based on parent directory
    parent_lower = parent_dir.lower()
    if 'epicor' in parent_lower:
        project_info["software"] = "Epicor"
        project_info["vendor"] = "Epicor Ltd"
    elif 'myob' in parent_lower:
        project_info["software"] = "MYOB"
        project_info["vendor"] = "MYOB Australia"
    elif 'odoo' in parent_lower:
        project_info["software"] = "ODOO"
        project_info["vendor"] = "ODOO SA"
    elif 'payglobal' in parent_lower or 'pay global' in parent_lower:
        project_info["software"] = "PayGlobal"
        project_info["vendor"] = "PayGlobal Ltd"
    else:
        project_info["software"] = "Other"
        project_info["vendor"] = "Various"
    
    # Extract client name from directory name (remove "Project" suffix)
    client_name = dir_name
    if client_name.endswith(" Project"):
        client_name = client_name[:-8]  # Remove " Project"
    elif client_name.endswith(" Projects"):
        client_name = client_name[:-9]  # Remove " Projects"
    
    project_info["client_name"] = client_name
    
    # Create project name by combining software and client
    project_info["project_name"] = f"{project_info['software']} for {client_name}"
    
    # Look for project files to get more info
    try:
        files = os.listdir(dir_path)
        for file in files:
            file_lower = file.lower()
            
            # Look for status indicators in filenames
            if 'completed' in file_lower or 'done' in file_lower:
                project_info["status"] = "Completed"
            elif 'hold' in file_lower or 'pending' in file_lower:
                project_info["status"] = "On Hold"
            
            # Look for date patterns in filenames
            date_pattern = r'(\d{4})[-_](\d{1,2})[-_](\d{1,2})'
            date_match = re.search(date_pattern, file)
            if date_match:
                year, month, day = date_match.groups()
                project_info["start_date"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            # Look for README or project description files
            if 'readme' in file_lower or 'description' in file_lower or file.endswith('.txt'):
                try:
                    with open(os.path.join(dir_path, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                        if len(content) > 20:  # Only use if it has substantial content
                            project_info["description"] = content[:500] + "..." if len(content) > 500 else content
                except:
                    pass
    except:
        pass
    
    return project_info

def create_realistic_meetings(project_id, project_name, client_name, software):
    """Create realistic meeting data based on project info"""
    meetings = []
    
    # Create 2-4 meetings per project
    num_meetings = 2 + (project_id % 3)  # Varies between 2-4
    
    for i in range(num_meetings):
        # Create dates in the past few months
        meeting_date = datetime.now() - timedelta(days=30 + (i * 15))
        
        meeting_types = [
            {
                "agenda": f"{software} Project Kickoff Meeting",
                "attendees": f"Jayshil, {client_name} IT Team, {software} Vendor Representative",
                "mom": f"Discussed {software} project scope, timeline, and deliverables for {client_name}. Agreed on key milestones and communication protocols.",
                "next_steps": "Schedule follow-up meeting and begin initial setup"
            },
            {
                "agenda": f"{software} Requirements Gathering",
                "attendees": f"Jayshil, {client_name} Business Users, Technical Team",
                "mom": f"Collected detailed requirements for {software} implementation at {client_name}. Identified key pain points and success criteria.",
                "next_steps": "Document requirements and create project plan"
            },
            {
                "agenda": f"{software} System Configuration Review",
                "attendees": f"Jayshil, {client_name} Admin Team, {software} Support",
                "mom": f"Reviewed {software} system configuration for {client_name}. Discussed customization needs and integration requirements.",
                "next_steps": "Implement configurations and schedule testing"
            },
            {
                "agenda": f"{software} User Training Session",
                "attendees": f"Jayshil, {client_name} End Users, Training Team",
                "mom": f"Conducted {software} user training for {client_name}. Covered key features and workflows. Users provided positive feedback.",
                "next_steps": "Schedule additional training sessions and prepare go-live"
            }
        ]
        
        meeting = meeting_types[i % len(meeting_types)]
        follow_up_date = meeting_date + timedelta(days=7)
        
        meetings.append({
            "project_id": project_id,
            "meeting_date": meeting_date.strftime('%Y-%m-%d'),
            "attendees": meeting["attendees"],
            "agenda": meeting["agenda"],
            "mom": meeting["mom"],
            "next_steps": meeting["next_steps"],
            "follow_up_date": follow_up_date.strftime('%Y-%m-%d')
        })
    
    return meetings

def create_realistic_updates(project_id, project_name, client_name, software):
    """Create realistic client update data"""
    updates = []
    
    # Create 1-3 updates per project
    num_updates = 1 + (project_id % 3)
    
    update_types = [
        {
            "summary": f"{software} project kickoff completed successfully for {client_name}",
            "sent_by": "Jayshil",
            "mode": "Email",
            "client_feedback": f"Very satisfied with the initial {software} setup and timeline",
            "next_step": "Begin requirements gathering phase"
        },
        {
            "summary": f"{software} configuration phase completed for {client_name}",
            "sent_by": "Jayshil", 
            "mode": "Call",
            "client_feedback": f"{software} system configuration meets our requirements",
            "next_step": "Schedule user training sessions"
        },
        {
            "summary": f"{software} user training completed for {client_name}",
            "sent_by": "Jayshil",
            "mode": "Meeting",
            "client_feedback": f"{software} training was excellent, users are ready for go-live",
            "next_step": "Prepare for system go-live"
        }
    ]
    
    for i in range(num_updates):
        update_date = datetime.now() - timedelta(days=20 + (i * 10))
        update = update_types[i % len(update_types)]
        
        updates.append({
            "project_id": project_id,
            "update_date": update_date.strftime('%Y-%m-%d'),
            "summary": update["summary"],
            "sent_by": update["sent_by"],
            "mode": update["mode"],
            "client_feedback": update["client_feedback"],
            "next_step": update["next_step"]
        })
    
    return updates

def create_realistic_issues(project_id, project_name, client_name, software):
    """Create realistic issue data"""
    issues = []
    
    # Create 0-2 issues per project
    num_issues = project_id % 3
    
    issue_types = [
        {
            "description": f"{software} data migration error for {client_name}",
            "status": "Resolved",
            "assigned_to": "Jayshil",
            "resolution_date": (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        },
        {
            "description": f"{software} user access permissions issue for {client_name}",
            "status": "Pending",
            "assigned_to": f"{software} Vendor Support",
            "resolution_date": None
        },
        {
            "description": f"{software} integration testing failed for {client_name}",
            "status": "Resolved",
            "assigned_to": "Jayshil",
            "resolution_date": (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        }
    ]
    
    for i in range(num_issues):
        issue_date = datetime.now() - timedelta(days=15 + (i * 5))
        issue = issue_types[i % len(issue_types)]
        
        issues.append({
            "project_id": project_id,
            "date_reported": issue_date.strftime('%Y-%m-%d'),
            "issue_description": issue["description"],
            "status": issue["status"],
            "assigned_to": issue["assigned_to"],
            "resolution_date": issue["resolution_date"]
        })
    
    return issues

def import_real_projects():
    """Import real projects from organized directories"""
    
    # Initialize database
    db_path = os.path.join(r"C:\Projects", "ProjectOps-Assistant", "projectops.db")
    db = ProjectOpsDatabase(db_path)
    
    # Clear existing data
    print("🗑️ Clearing existing data...")
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM issues")
    cursor.execute("DELETE FROM client_updates") 
    cursor.execute("DELETE FROM meetings")
    cursor.execute("DELETE FROM projects")
    conn.commit()
    conn.close()
    
    print("🔍 Scanning real project directories...")
    
    # Scan all client project directories
    client_projects_dir = os.path.join(r"C:\Projects", "Client-Projects")
    
    if not os.path.exists(client_projects_dir):
        print(f"❌ Client projects directory not found: {client_projects_dir}")
        return
    
    # Directories to exclude
    exclude_dirs = ['Others', 'Timesheet', 'SAP Crystal Reports 2016 SP09 (x86)']
    
    total_projects = 0
    total_meetings = 0
    total_updates = 0
    total_issues = 0
    
    # Scan each software type directory
    for software_dir in os.listdir(client_projects_dir):
        software_path = os.path.join(client_projects_dir, software_dir)
        
        if not os.path.isdir(software_path) or software_dir in exclude_dirs:
            continue
            
        print(f"\n📁 Processing {software_dir} projects...")
        
        # Scan each subdirectory within the software directory
        for sub_dir in os.listdir(software_path):
            sub_path = os.path.join(software_path, sub_dir)
            
            if not os.path.isdir(sub_path):
                continue
            
            # Check if this is a projects container directory (like "Epicor Projects")
            if "Projects" in sub_dir:
                # Scan inside this projects directory for actual client projects
                for client_dir in os.listdir(sub_path):
                    client_path = os.path.join(sub_path, client_dir)
                    
                    if not os.path.isdir(client_path):
                        continue
                    
                    # If the subdirectory contains "Project" in its name, it's a client project
                    if "Project" in client_dir:
                        # This is a client project directory
                        project_info = extract_project_info_from_directory(client_path, client_dir, software_dir)
                        
                        # Add project to database
                        project_id = db.add_project(
                            project_info["project_name"],
                            project_info["client_name"],
                            project_info["software"],
                            project_info["vendor"],
                            project_info["start_date"],
                            project_info["deadline"],
                            project_info["status"],
                            project_info["description"]
                        )
                        
                        print(f"✅ Added project: {project_info['project_name']} ({project_info['client_name']})")
                        total_projects += 1
                        
                        # Create realistic meetings
                        meetings = create_realistic_meetings(project_id, project_info["project_name"], project_info["client_name"], project_info["software"])
                        for meeting in meetings:
                            db.add_meeting(
                                meeting["project_id"],
                                meeting["meeting_date"],
                                meeting["attendees"],
                                meeting["agenda"],
                                meeting["mom"],
                                meeting["next_steps"],
                                meeting["follow_up_date"]
                            )
                            total_meetings += 1
                        
                        # Create realistic updates
                        updates = create_realistic_updates(project_id, project_info["project_name"], project_info["client_name"], project_info["software"])
                        for update in updates:
                            db.add_client_update(
                                update["project_id"],
                                update["update_date"],
                                update["summary"],
                                update["sent_by"],
                                update["mode"],
                                update["client_feedback"],
                                update["next_step"]
                            )
                            total_updates += 1
                        
                        # Create realistic issues
                        issues = create_realistic_issues(project_id, project_info["project_name"], project_info["client_name"], project_info["software"])
                        for issue in issues:
                            db.add_issue(
                                issue["project_id"],
                                issue["date_reported"],
                                issue["issue_description"],
                                issue["status"],
                                issue["assigned_to"],
                                issue["resolution_date"]
                            )
                            total_issues += 1
    
    print(f"\n🎉 Real project import completed!")
    print(f"📊 Summary:")
    print(f"   Projects: {total_projects}")
    print(f"   Meetings: {total_meetings}")
    print(f"   Client Updates: {total_updates}")
    print(f"   Issues: {total_issues}")
    
    print(f"\n🔍 You can now test the chatbot with queries like:")
    print(f"   - 'Show all projects'")
    print(f"   - 'What's the status of [project name]?'")
    print(f"   - 'Show meetings for [client name]'")
    print(f"   - 'What issues are unresolved?'")
    print(f"   - 'Show client updates for [project]'")

if __name__ == "__main__":
    import_real_projects() 