#!/usr/bin/env python3
"""
Test script to verify project deletion functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_postgres import PostgreSQLDatabase
import streamlit as st
import pandas as pd

def test_project_deletion():
    """Test the project deletion functionality"""
    
    # Initialize database
    db = PostgreSQLDatabase()
    
    # Test data
    test_project = {
        'project_name': 'Test Project for Deletion',
        'client_name': 'Test Client',
        'software': 'Epicor',
        'vendor': 'Test Vendor',
        'start_date': '2024-01-01',
        'deadline': '2024-12-31',
        'status': 'In Progress',
        'description': 'This is a test project for deletion',
        'file_path': None
    }
    
    print("🧪 Testing Project Deletion Functionality")
    print("=" * 50)
    
    # Step 1: Add a test project
    print("1. Adding test project...")
    success = db.add_project(
        test_project['project_name'],
        test_project['client_name'],
        test_project['software'],
        test_project['vendor'],
        test_project['start_date'],
        test_project['deadline'],
        test_project['status'],
        test_project['description'],
        test_project['file_path']
    )
    
    if success:
        print("✅ Test project added successfully")
    else:
        print("❌ Failed to add test project")
        return False
    
    # Step 2: Verify project exists
    print("2. Verifying project exists...")
    projects = db.get_all_projects()
    test_project_row = projects[projects['project_name'] == test_project['project_name']]
    
    if not test_project_row.empty:
        project_id = test_project_row.iloc[0]['id']
        print(f"✅ Test project found with ID: {project_id}")
    else:
        print("❌ Test project not found")
        return False
    
    # Step 3: Add some related data (meeting, update, issue)
    print("3. Adding related data...")
    
    # Add a meeting
    meeting_success = db.add_meeting(
        project_id,
        '2024-01-15',
        'Test Attendees',
        'Test Agenda',
        'Test MoM',
        'Test Next Steps',
        '2024-01-20'
    )
    
    # Add a client update
    update_success = db.add_client_update(
        project_id,
        '2024-01-10',
        'Test Summary',
        'Test Sender',
        'Email',
        'Test Feedback',
        'Test Next Step'
    )
    
    # Add an issue
    issue_success = db.add_issue(
        project_id,
        '2024-01-05',
        'Test Issue Description',
        'Pending',
        'Test Assignee',
        None
    )
    
    print(f"✅ Related data added - Meeting: {meeting_success}, Update: {update_success}, Issue: {issue_success}")
    
    # Step 4: Delete the project
    print("4. Deleting test project...")
    delete_success = db.delete_project(project_id)
    
    if delete_success:
        print("✅ Test project deleted successfully")
    else:
        print("❌ Failed to delete test project")
        return False
    
    # Step 5: Verify project and related data are deleted
    print("5. Verifying deletion...")
    
    # Check if project is deleted
    projects_after = db.get_all_projects()
    test_project_after = projects_after[projects_after['project_name'] == test_project['project_name']]
    
    if test_project_after.empty:
        print("✅ Project successfully deleted")
    else:
        print("❌ Project still exists after deletion")
        return False
    
    # Check if related data is deleted
    meetings_after = db.get_all_meetings()
    project_meetings = meetings_after[meetings_after['project_id'] == project_id] if not meetings_after.empty else pd.DataFrame()
    
    updates_after = pd.DataFrame()
    if not projects_after.empty:
        updates_after = pd.concat([
            db.get_client_updates_by_project(pid) for pid in projects_after['id'].tolist()
        ], ignore_index=True)
    project_updates = updates_after[updates_after['project_id'] == project_id] if not updates_after.empty else pd.DataFrame()
    
    issues_after = db.get_all_issues()
    project_issues = issues_after[issues_after['project_id'] == project_id] if not issues_after.empty else pd.DataFrame()
    
    if project_meetings.empty and project_updates.empty and project_issues.empty:
        print("✅ All related data successfully deleted")
    else:
        print("❌ Some related data still exists")
        print(f"   - Meetings: {len(project_meetings)}")
        print(f"   - Updates: {len(project_updates)}")
        print(f"   - Issues: {len(project_issues)}")
        return False
    
    print("\n🎉 All tests passed! Project deletion functionality is working correctly.")
    return True

if __name__ == "__main__":
    try:
        test_project_deletion()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 