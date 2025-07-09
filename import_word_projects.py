import os
import sys
from datetime import datetime, timedelta
import re
from docx import Document
import streamlit as st

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_postgres import ProjectOpsDatabase

def extract_projects_from_word_doc(docx_path):
    """Extract project information from Word document table"""
    projects = []
    
    try:
        doc = Document(docx_path)
        
        # Look for tables in the document
        for table in doc.tables:
            rows = list(table.rows)
            if len(rows) < 2:  # Need at least header and one data row
                continue
            
            # Get header row to understand column structure
            header_row = rows[0]
            headers = [cell.text.strip() for cell in header_row.cells]
            print(f"Table headers: {headers}")
            
            # Process data rows (skip header row)
            for row in rows[1:]:
                cells = [cell.text.strip() for cell in row.cells]
                if len(cells) < 3:  # Need at least project name, owner, and product
                    continue
                
                # Extract project information from table row
                project_name = cells[0] if len(cells) > 0 else "Unknown"
                owner = cells[1] if len(cells) > 1 else "Unknown"
                product = cells[2] if len(cells) > 2 else "Unknown"
                action_items = cells[3] if len(cells) > 3 else ""
                by_when = cells[4] if len(cells) > 4 else ""
                issues = cells[5] if len(cells) > 5 else ""
                percent_complete = cells[6] if len(cells) > 6 else ""
                total_billing = cells[7] if len(cells) > 7 else ""
                total_billed = cells[8] if len(cells) > 8 else ""
                
                # Skip empty rows
                if not project_name or project_name == "":
                    continue
                
                # Determine software and vendor based on product
                software, vendor = determine_software_vendor(product)
                
                # Determine status based on percent complete and issues
                status = determine_status(percent_complete, issues)
                
                # Parse deadline
                deadline = parse_deadline(by_when)
                
                # Create project description
                description = f"Product: {product}\nOwner: {owner}\nAction Items: {action_items}"
                if issues:
                    description += f"\nIssues: {issues}"
                if percent_complete:
                    description += f"\nProgress: {percent_complete}"
                if total_billing:
                    description += f"\nTotal Billing: {total_billing}"
                if total_billed:
                    description += f"\nTotal Billed: {total_billed}"
                
                project = {
                    'project_name': project_name,
                    'client_name': project_name,  # Use project name as client name
                    'software': software,
                    'vendor': vendor,
                    'start_date': datetime.now().strftime('%Y-%m-%d'),
                    'deadline': deadline,
                    'status': status,
                    'description': description,
                    'action_items': action_items,
                    'issues': issues,
                    'percent_complete': percent_complete,
                    'total_billing': total_billing,
                    'total_billed': total_billed
                }
                
                projects.append(project)
                print(f"Extracted project: {project_name} - {software}")
        
        return projects
        
    except Exception as e:
        print(f"Error reading Word document: {e}")
        return []

def determine_software_vendor(product):
    """Determine software and vendor based on product name"""
    product_lower = product.lower()
    
    software_keywords = {
        'epicor': ('Epicor', 'Epicor Ltd'),
        'myob': ('MYOB', 'MYOB Australia'),
        'odoo': ('ODOO', 'ODOO SA'),
        'payglobal': ('PayGlobal', 'PayGlobal Ltd'),
        'pay global': ('PayGlobal', 'PayGlobal Ltd'),
        'sage': ('Sage', 'Sage Group'),
        'quickbooks': ('QuickBooks', 'Intuit'),
        'xero': ('Xero', 'Xero Limited'),
        'netsuite': ('NetSuite', 'Oracle'),
        'dynamics': ('Microsoft Dynamics', 'Microsoft'),
        'salesforce': ('Salesforce', 'Salesforce.com'),
        'lta': ('LTA Report', 'Custom Development'),
        'report': ('Custom Report', 'Custom Development')
    }
    
    for keyword, (software, vendor) in software_keywords.items():
        if keyword in product_lower:
            return software, vendor
    
    return product, "Unknown Vendor"

def determine_status(percent_complete, issues):
    """Determine project status based on completion and issues"""
    if not percent_complete:
        return "In Progress"
    
    # Extract percentage number
    percent_match = re.search(r'(\d+)%', percent_complete)
    if percent_match:
        percent = int(percent_match.group(1))
        if percent >= 100:
            return "Completed"
        elif percent >= 80:
            return "Near Completion"
        elif percent >= 50:
            return "In Progress"
        else:
            return "Started"
    
    # Check for status keywords
    if "completed" in percent_complete.lower():
        return "Completed"
    elif "wip" in percent_complete.lower():
        return "In Progress"
    elif "pending" in percent_complete.lower():
        return "Pending"
    
    return "In Progress"

def parse_deadline(by_when):
    """Parse deadline date from string"""
    if not by_when:
        return (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
    
    # Try to parse date in format DD/MM/YYYY
    date_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', by_when)
    if date_match:
        day, month, year = date_match.groups()
        try:
            date_obj = datetime(int(year), int(month), int(day))
            return date_obj.strftime('%Y-%m-%d')
        except:
            pass
    
    return (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')

def create_meetings_for_project(project_id, project_name, client_name, software):
    """Create realistic meeting data for a project"""
    meetings = []
    
    # Create 1-3 meetings per project
    num_meetings = 1 + (project_id % 3)
    
    meeting_types = [
        {
            "agenda": f"{software} Project Discussion",
            "attendees": f"Jayshil, {client_name} Team",
            "mom": f"Discussed {software} project for {client_name}. Reviewed current status and next steps.",
            "next_steps": "Continue with project implementation"
        },
        {
            "agenda": f"{software} Status Update Meeting",
            "attendees": f"Jayshil, {client_name} Management",
            "mom": f"Provided status update on {software} project for {client_name}. Discussed progress and challenges.",
            "next_steps": "Address identified issues and continue development"
        },
        {
            "agenda": f"{software} Final Review",
            "attendees": f"Jayshil, {client_name} Stakeholders",
            "mom": f"Final review of {software} project for {client_name}. Project completed successfully.",
            "next_steps": "Project handover and documentation"
        }
    ]
    
    for i in range(num_meetings):
        meeting_date = datetime.now() - timedelta(days=30 + (i * 15))
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

def create_updates_for_project(project_id, project_name, client_name, software, action_items, issues):
    """Create client updates based on project information"""
    updates = []
    
    # Create update based on action items
    if action_items:
        update_date = datetime.now() - timedelta(days=10)
        updates.append({
            "project_id": project_id,
            "update_date": update_date.strftime('%Y-%m-%d'),
            "summary": f"Action items for {software} project: {action_items[:200]}{'...' if len(action_items) > 200 else ''}",
            "sent_by": "Jayshil",
            "mode": "Email",
            "client_feedback": f"Working on action items for {client_name}",
            "next_step": "Continue with implementation"
        })
    
    # Create update based on issues if any
    if issues and issues.strip():
        update_date = datetime.now() - timedelta(days=5)
        updates.append({
            "project_id": project_id,
            "update_date": update_date.strftime('%Y-%m-%d'),
            "summary": f"Issue identified: {issues}",
            "sent_by": "Jayshil",
            "mode": "Email",
            "client_feedback": f"Addressing issue: {issues}",
            "next_step": "Resolve issue and continue"
        })
    
    # If no updates created, create a default one
    if not updates:
        update_date = datetime.now() - timedelta(days=10)
        updates.append({
            "project_id": project_id,
            "update_date": update_date.strftime('%Y-%m-%d'),
            "summary": f"{software} project in progress for {client_name}",
            "sent_by": "Jayshil",
            "mode": "Email",
            "client_feedback": f"Project progressing well for {client_name}",
            "next_step": "Continue with implementation"
        })
    
    return updates

def import_word_projects_to_database():
    """Import projects from Word document to PostgreSQL database"""
    
    # Initialize database
    db = ProjectOpsDatabase()
    
    # Extract projects from Word document
    docx_path = "My Projects.docx"
    if not os.path.exists(docx_path):
        print(f"Error: {docx_path} not found!")
        return
    
    print(f"Reading projects from {docx_path}...")
    projects = extract_projects_from_word_doc(docx_path)
    
    if not projects:
        print("No projects found in the Word document!")
        return
    
    print(f"Found {len(projects)} projects to import...")
    
    # Import each project
    for i, project in enumerate(projects, 1):
        print(f"\nImporting project {i}/{len(projects)}: {project['project_name']}")
        
        # Add project to database
        success = db.add_project(
            project_name=project['project_name'],
            client_name=project['client_name'],
            software=project['software'],
            vendor=project['vendor'],
            start_date=project['start_date'],
            deadline=project['deadline'],
            status=project['status'],
            description=project['description'],
            user_id=1  # Assuming user_id 1 for jayshil.singh@datec.com.fj
        )
        
        if success:
            # Get the project ID (we'll need to query for it)
            projects_df = db.get_all_projects(user_id=1)
            if not projects_df.empty:
                # Find the most recently added project (should be the one we just added)
                project_id = projects_df.iloc[0]['id']
                
                # Create meetings for this project
                meetings = create_meetings_for_project(
                    project_id, 
                    project['project_name'], 
                    project['client_name'], 
                    project['software']
                )
                
                for meeting in meetings:
                    db.add_meeting(
                        project_id=meeting['project_id'],
                        meeting_date=meeting['meeting_date'],
                        attendees=meeting['attendees'],
                        agenda=meeting['agenda'],
                        mom=meeting['mom'],
                        next_steps=meeting['next_steps'],
                        follow_up_date=meeting['follow_up_date'],
                        user_id=1
                    )
                
                # Create updates for this project
                updates = create_updates_for_project(
                    project_id,
                    project['project_name'],
                    project['client_name'],
                    project['software'],
                    project.get('action_items', ''),
                    project.get('issues', '')
                )
                
                for update in updates:
                    db.add_client_update(
                        project_id=update['project_id'],
                        update_date=update['update_date'],
                        summary=update['summary'],
                        sent_by=update['sent_by'],
                        mode=update['mode'],
                        client_feedback=update['client_feedback'],
                        next_step=update['next_step'],
                        user_id=1
                    )
                
                print(f"✓ Successfully imported project: {project['project_name']}")
                print(f"  - Added {len(meetings)} meetings")
                print(f"  - Added {len(updates)} updates")
            else:
                print(f"✗ Failed to get project ID for: {project['project_name']}")
        else:
            print(f"✗ Failed to import project: {project['project_name']}")
    
    print(f"\nImport completed! {len(projects)} projects processed.")

if __name__ == "__main__":
    import_word_projects_to_database() 