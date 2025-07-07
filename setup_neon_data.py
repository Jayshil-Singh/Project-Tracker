#!/usr/bin/env python3
"""
Quick Setup Script for Neon Database
Adds sample project data to get you started immediately
"""

import streamlit as st
from database_postgres import ProjectOpsDatabase
from datetime import datetime, timedelta

def setup_sample_data():
    """Add sample project data to Neon database"""
    
    st.title("🚀 ProjectOps Assistant - Data Setup")
    st.markdown("This will add sample project data to your Neon database.")
    
    if st.button("📝 Add Sample Data", use_container_width=True):
        
        try:
            db = ProjectOpsDatabase()
            
            # Sample projects
            sample_projects = [
                {
                    'project_name': 'Epicor ERP Implementation - ATH',
                    'client_name': 'ATH Manufacturing',
                    'software': 'Epicor',
                    'vendor': 'Epicor',
                    'start_date': '2024-01-15',
                    'deadline': '2024-06-30',
                    'status': 'In Progress',
                    'description': 'Complete Epicor ERP implementation for ATH manufacturing company including financials, inventory, and production modules.'
                },
                {
                    'project_name': 'MYOB Advanced Migration - ATS',
                    'client_name': 'ATS Solutions',
                    'software': 'MYOB',
                    'vendor': 'MYOB',
                    'start_date': '2024-02-01',
                    'deadline': '2024-05-15',
                    'status': 'In Progress',
                    'description': 'MYOB Advanced migration from legacy system with custom reporting and workflow automation.'
                },
                {
                    'project_name': 'ODOO ERP Setup - HFC',
                    'client_name': 'HFC Retail',
                    'software': 'ODOO',
                    'vendor': 'ODOO',
                    'start_date': '2024-03-01',
                    'deadline': '2024-08-31',
                    'status': 'On Hold',
                    'description': 'ODOO ERP implementation for HFC retail chain with multi-location inventory and POS integration.'
                },
                {
                    'project_name': 'PayGlobal HR System - LTA',
                    'client_name': 'LTA Logistics',
                    'software': 'PayGlobal',
                    'vendor': 'PayGlobal',
                    'start_date': '2024-01-20',
                    'deadline': '2024-04-30',
                    'status': 'Completed',
                    'description': 'PayGlobal HR and payroll system implementation for LTA logistics company.'
                }
            ]
            
            # Add projects
            project_ids = []
            for project in sample_projects:
                success = db.add_project(
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
                    project_ids.append(len(project_ids) + 1)
                    st.success(f"✅ Added project: {project['project_name']}")
                else:
                    st.error(f"❌ Failed to add project: {project['project_name']}")
            
            # Add sample meetings
            sample_meetings = [
                {
                    'project_id': 1,
                    'meeting_date': '2024-01-20',
                    'attendees': 'Jayshil Singh, ATH Management, Epicor Consultant',
                    'agenda': 'Project kickoff and requirements gathering',
                    'mom': 'Discussed project scope, timeline, and key deliverables. Team assigned roles and responsibilities. Epicor consultant provided technical overview.',
                    'next_steps': 'Schedule follow-up meeting for technical architecture review and begin requirements documentation.',
                    'follow_up_date': '2024-01-27'
                },
                {
                    'project_id': 1,
                    'meeting_date': '2024-01-27',
                    'attendees': 'Jayshil Singh, ATH IT Team, Epicor Consultant',
                    'agenda': 'Technical architecture review',
                    'mom': 'Reviewed system architecture, database design, and integration requirements. Discussed hardware requirements and deployment strategy.',
                    'next_steps': 'Begin development environment setup and start custom module development.',
                    'follow_up_date': '2024-02-03'
                },
                {
                    'project_id': 2,
                    'meeting_date': '2024-02-05',
                    'attendees': 'Jayshil Singh, ATS Management, MYOB Specialist',
                    'agenda': 'MYOB migration planning and data mapping',
                    'mom': 'Reviewed current system structure and planned data migration strategy. Identified key data fields and mapping requirements.',
                    'next_steps': 'Begin data extraction and validation process.',
                    'follow_up_date': '2024-02-12'
                },
                {
                    'project_id': 3,
                    'meeting_date': '2024-03-05',
                    'attendees': 'Jayshil Singh, HFC Management',
                    'agenda': 'Project status review and timeline adjustment',
                    'mom': 'Discussed current project status and identified delays in hardware procurement. Agreed to put project on hold until hardware is available.',
                    'next_steps': 'Resume project once hardware procurement is completed.',
                    'follow_up_date': '2024-04-05'
                }
            ]
            
            for meeting in sample_meetings:
                success = db.add_meeting(
                    meeting['project_id'],
                    meeting['meeting_date'],
                    meeting['attendees'],
                    meeting['agenda'],
                    meeting['mom'],
                    meeting['next_steps'],
                    meeting['follow_up_date']
                )
                if success:
                    st.success(f"✅ Added meeting for project {meeting['project_id']}")
                else:
                    st.error(f"❌ Failed to add meeting for project {meeting['project_id']}")
            
            # Add sample client updates
            sample_updates = [
                {
                    'project_id': 1,
                    'update_date': '2024-01-25',
                    'summary': 'Completed initial requirements analysis and project planning',
                    'sent_by': 'Jayshil Singh',
                    'mode': 'Email',
                    'client_feedback': 'Very satisfied with the approach and timeline. Looking forward to the technical implementation phase.',
                    'next_step': 'Begin technical design and development phase'
                },
                {
                    'project_id': 2,
                    'update_date': '2024-02-10',
                    'summary': 'Data migration testing completed successfully',
                    'sent_by': 'Jayshil Singh',
                    'mode': 'Call',
                    'client_feedback': 'Test results look excellent. Data integrity maintained at 99.9%. Ready to proceed with production migration.',
                    'next_step': 'Schedule production migration window and begin user training'
                },
                {
                    'project_id': 4,
                    'update_date': '2024-04-25',
                    'summary': 'Project completed successfully - system go-live',
                    'sent_by': 'Jayshil Singh',
                    'mode': 'Meeting',
                    'client_feedback': 'System is working perfectly. All users are trained and productive. Very happy with the implementation.',
                    'next_step': 'Begin post-implementation support and monitoring'
                }
            ]
            
            for update in sample_updates:
                success = db.add_client_update(
                    update['project_id'],
                    update['update_date'],
                    update['summary'],
                    update['sent_by'],
                    update['mode'],
                    update['client_feedback'],
                    update['next_step']
                )
                if success:
                    st.success(f"✅ Added client update for project {update['project_id']}")
                else:
                    st.error(f"❌ Failed to add client update for project {update['project_id']}")
            
            # Add sample issues
            sample_issues = [
                {
                    'project_id': 1,
                    'date_reported': '2024-01-22',
                    'description': 'Integration issue with legacy payroll system - data format mismatch',
                    'status': 'Pending',
                    'assigned_to': 'Jayshil Singh'
                },
                {
                    'project_id': 1,
                    'date_reported': '2024-01-25',
                    'description': 'Hardware compatibility issue with existing network infrastructure',
                    'status': 'Resolved',
                    'assigned_to': 'Jayshil Singh',
                    'resolution_date': '2024-01-26'
                },
                {
                    'project_id': 2,
                    'date_reported': '2024-02-08',
                    'description': 'Data validation errors in customer records - duplicate entries found',
                    'status': 'Resolved',
                    'assigned_to': 'Jayshil Singh',
                    'resolution_date': '2024-02-09'
                },
                {
                    'project_id': 3,
                    'date_reported': '2024-03-10',
                    'description': 'Hardware procurement delay - vendor supply chain issues',
                    'status': 'Pending',
                    'assigned_to': 'HFC IT Team'
                }
            ]
            
            for issue in sample_issues:
                success = db.add_issue(
                    issue['project_id'],
                    issue['date_reported'],
                    issue['description'],
                    issue['status'],
                    issue['assigned_to'],
                    issue.get('resolution_date')
                )
                if success:
                    st.success(f"✅ Added issue for project {issue['project_id']}")
                else:
                    st.error(f"❌ Failed to add issue for project {issue['project_id']}")
            
            st.balloons()
            st.success("🎉 Sample data setup completed successfully!")
            st.info("You can now view your projects, meetings, updates, and issues in the main app.")
            
        except Exception as e:
            st.error(f"❌ Setup failed: {e}")
            st.info("Make sure your Neon database is properly configured in Streamlit Cloud secrets.")

if __name__ == "__main__":
    setup_sample_data() 