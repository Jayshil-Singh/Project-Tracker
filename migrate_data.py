#!/usr/bin/env python3
"""
Data Migration Script for ProjectOps Assistant
Migrates data from local SQLite to Neon PostgreSQL database
"""

import sqlite3
import pandas as pd
from database_postgres import ProjectOpsDatabase
import streamlit as st
import os
from datetime import datetime

def migrate_from_sqlite_to_postgres():
    """Migrate data from local SQLite to PostgreSQL"""
    
    print("🚀 Starting data migration from SQLite to PostgreSQL...")
    
    # Local SQLite database path
    local_db_path = r"C:\Projects\ProjectOps-Assistant\projectops.db"
    
    if not os.path.exists(local_db_path):
        print(f"❌ Local database not found at: {local_db_path}")
        return False
    
    try:
        # Connect to local SQLite database
        print("📊 Connecting to local SQLite database...")
        sqlite_conn = sqlite3.connect(local_db_path)
        
        # Initialize PostgreSQL database
        print("🔗 Connecting to PostgreSQL database...")
        postgres_db = ProjectOpsDatabase()
        
        # Migrate projects
        print("📁 Migrating projects...")
        projects_df = pd.read_sql_query("SELECT * FROM projects", sqlite_conn)
        
        for _, project in projects_df.iterrows():
            success = postgres_db.add_project(
                project['project_name'],
                project['client_name'],
                project['software'],
                project['vendor'],
                project['start_date'],
                project['deadline'],
                project['status'],
                project['description'],
                project['file_path']
            )
            if success:
                print(f"✅ Migrated project: {project['project_name']}")
            else:
                print(f"❌ Failed to migrate project: {project['project_name']}")
        
        # Migrate meetings
        print("🗓️ Migrating meetings...")
        meetings_df = pd.read_sql_query("SELECT * FROM meetings", sqlite_conn)
        
        for _, meeting in meetings_df.iterrows():
            success = postgres_db.add_meeting(
                meeting['project_id'],
                meeting['meeting_date'],
                meeting['attendees'],
                meeting['agenda'],
                meeting['mom'],
                meeting['next_steps'],
                meeting['follow_up_date']
            )
            if success:
                print(f"✅ Migrated meeting for project ID: {meeting['project_id']}")
            else:
                print(f"❌ Failed to migrate meeting for project ID: {meeting['project_id']}")
        
        # Migrate client updates
        print("📧 Migrating client updates...")
        updates_df = pd.read_sql_query("SELECT * FROM client_updates", sqlite_conn)
        
        for _, update in updates_df.iterrows():
            success = postgres_db.add_client_update(
                update['project_id'],
                update['update_date'],
                update['summary'],
                update['sent_by'],
                update['mode'],
                update['client_feedback'],
                update['next_step']
            )
            if success:
                print(f"✅ Migrated client update for project ID: {update['project_id']}")
            else:
                print(f"❌ Failed to migrate client update for project ID: {update['project_id']}")
        
        # Migrate issues
        print("🛠️ Migrating issues...")
        issues_df = pd.read_sql_query("SELECT * FROM issues", sqlite_conn)
        
        for _, issue in issues_df.iterrows():
            success = postgres_db.add_issue(
                issue['project_id'],
                issue['date_reported'],
                issue['description'],
                issue['status'],
                issue['assigned_to'],
                issue['resolution_date']
            )
            if success:
                print(f"✅ Migrated issue for project ID: {issue['project_id']}")
            else:
                print(f"❌ Failed to migrate issue for project ID: {issue['project_id']}")
        
        sqlite_conn.close()
        
        print("\n🎉 Data migration completed successfully!")
        print(f"📊 Migrated {len(projects_df)} projects")
        print(f"📅 Migrated {len(meetings_df)} meetings")
        print(f"📧 Migrated {len(updates_df)} client updates")
        print(f"🛠️ Migrated {len(issues_df)} issues")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def add_sample_data():
    """Add sample data to the database for testing"""
    
    print("📝 Adding sample data to PostgreSQL database...")
    
    try:
        postgres_db = ProjectOpsDatabase()
        
        # Add sample projects
        sample_projects = [
            {
                'project_name': 'Epicor Implementation - ATH',
                'client_name': 'ATH',
                'software': 'Epicor',
                'vendor': 'Epicor',
                'start_date': '2024-01-15',
                'deadline': '2024-06-30',
                'status': 'In Progress',
                'description': 'Full Epicor ERP implementation for ATH manufacturing company'
            },
            {
                'project_name': 'MYOB Migration - ATS',
                'client_name': 'ATS',
                'software': 'MYOB',
                'vendor': 'MYOB',
                'start_date': '2024-02-01',
                'deadline': '2024-05-15',
                'status': 'In Progress',
                'description': 'MYOB Advanced migration and customization'
            },
            {
                'project_name': 'ODOO Setup - HFC',
                'client_name': 'HFC',
                'software': 'ODOO',
                'vendor': 'ODOO',
                'start_date': '2024-03-01',
                'deadline': '2024-08-31',
                'status': 'On Hold',
                'description': 'ODOO ERP implementation for HFC retail chain'
            }
        ]
        
        for project in sample_projects:
            success = postgres_db.add_project(
                project['project_name'],
                project['client_name'],
                project['software'],
                project['vendor'],
                project['start_date'],
                project['deadline'],
                project['status'],
                project['description']
            )
            if success:
                print(f"✅ Added sample project: {project['project_name']}")
            else:
                print(f"❌ Failed to add sample project: {project['project_name']}")
        
        # Add sample meetings
        sample_meetings = [
            {
                'project_id': 1,
                'meeting_date': '2024-01-20',
                'attendees': 'Jayshil Singh, ATH Team, Epicor Consultant',
                'agenda': 'Project kickoff and requirements gathering',
                'mom': 'Discussed project scope, timeline, and key deliverables. Team assigned roles and responsibilities.',
                'next_steps': 'Schedule follow-up meeting for technical architecture review',
                'follow_up_date': '2024-01-27'
            },
            {
                'project_id': 2,
                'meeting_date': '2024-02-05',
                'attendees': 'Jayshil Singh, ATS Management',
                'agenda': 'MYOB migration planning',
                'mom': 'Reviewed current system and migration requirements. Planned data migration strategy.',
                'next_steps': 'Begin data extraction and mapping',
                'follow_up_date': '2024-02-12'
            }
        ]
        
        for meeting in sample_meetings:
            success = postgres_db.add_meeting(
                meeting['project_id'],
                meeting['meeting_date'],
                meeting['attendees'],
                meeting['agenda'],
                meeting['mom'],
                meeting['next_steps'],
                meeting['follow_up_date']
            )
            if success:
                print(f"✅ Added sample meeting for project ID: {meeting['project_id']}")
            else:
                print(f"❌ Failed to add sample meeting for project ID: {meeting['project_id']}")
        
        # Add sample client updates
        sample_updates = [
            {
                'project_id': 1,
                'update_date': '2024-01-25',
                'summary': 'Completed initial requirements analysis',
                'sent_by': 'Jayshil Singh',
                'mode': 'Email',
                'client_feedback': 'Very satisfied with the approach. Looking forward to next phase.',
                'next_step': 'Begin technical design phase'
            },
            {
                'project_id': 2,
                'update_date': '2024-02-10',
                'summary': 'Data migration testing completed',
                'sent_by': 'Jayshil Singh',
                'mode': 'Call',
                'client_feedback': 'Test results look good. Ready to proceed with production migration.',
                'next_step': 'Schedule production migration window'
            }
        ]
        
        for update in sample_updates:
            success = postgres_db.add_client_update(
                update['project_id'],
                update['update_date'],
                update['summary'],
                update['sent_by'],
                update['mode'],
                update['client_feedback'],
                update['next_step']
            )
            if success:
                print(f"✅ Added sample client update for project ID: {update['project_id']}")
            else:
                print(f"❌ Failed to add sample client update for project ID: {update['project_id']}")
        
        # Add sample issues
        sample_issues = [
            {
                'project_id': 1,
                'date_reported': '2024-01-22',
                'description': 'Integration issue with legacy payroll system',
                'status': 'Pending',
                'assigned_to': 'Jayshil Singh'
            },
            {
                'project_id': 2,
                'date_reported': '2024-02-08',
                'description': 'Data validation errors in customer records',
                'status': 'Resolved',
                'assigned_to': 'Jayshil Singh',
                'resolution_date': '2024-02-09'
            }
        ]
        
        for issue in sample_issues:
            success = postgres_db.add_issue(
                issue['project_id'],
                issue['date_reported'],
                issue['description'],
                issue['status'],
                issue['assigned_to'],
                issue.get('resolution_date')
            )
            if success:
                print(f"✅ Added sample issue for project ID: {issue['project_id']}")
            else:
                print(f"❌ Failed to add sample issue for project ID: {issue['project_id']}")
        
        print("\n🎉 Sample data added successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to add sample data: {e}")
        return False

def main():
    """Main migration function"""
    print("=" * 60)
    print("🚀 ProjectOps Assistant - Data Migration Tool")
    print("=" * 60)
    
    print("\nChoose an option:")
    print("1. Migrate data from local SQLite database")
    print("2. Add sample data for testing")
    print("3. Both (migrate + add samples)")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        migrate_from_sqlite_to_postgres()
    elif choice == "2":
        add_sample_data()
    elif choice == "3":
        migrate_from_sqlite_to_postgres()
        print("\n" + "=" * 40)
        add_sample_data()
    else:
        print("❌ Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main() 