#!/usr/bin/env python3
"""
ProjectOps Assistant - Streamlit App
A comprehensive project management system with AI chatbot integration
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules
from database_postgres import ProjectOpsDatabase
from chatbot import ProjectChatbot
from reports import ReportGenerator
from neon_auth import auth
from login_page import render_login_page, check_if_admin_exists

# Initialize components
db = ProjectOpsDatabase()
chatbot = ProjectChatbot(db)
reports = ReportGenerator()

# Page configuration
st.set_page_config(
    page_title="ProjectOps Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .user-message {
        background: #f0f8ff;
        border-left-color: #1f77b4;
    }
    .bot-message {
        background: #f8f9fa;
        border-left-color: #28a745;
    }
    .stButton > button {
        border-radius: 20px;
        font-weight: bold;
    }
    .stSelectbox > div > div {
        border-radius: 10px;
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Authentication check
def check_authentication():
    """Check if user is authenticated"""
    current_user = auth.get_current_user()
    
    if not current_user:
        # Check if admin exists, if not show admin setup
        if not check_if_admin_exists():
            st.markdown('<h1 class="main-header">🔐 Project Tracker Setup</h1>', unsafe_allow_html=True)
            from login_page import render_admin_setup
            render_admin_setup()
            st.stop()
        else:
            # Show login page
            render_login_page()
            st.stop()
    
    return current_user

# Get current user
current_user = check_authentication()

# User info in sidebar
with st.sidebar:
    st.markdown("### 👤 User Info")
    st.markdown(f"**Name:** {current_user['full_name']}")
    st.markdown(f"**Email:** {current_user['email']}")
    st.markdown(f"**Role:** {current_user['role'].title()}")
    
    st.markdown("---")
    
    # Logout button
    if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
        if 'session_token' in st.session_state:
            auth.logout_user(st.session_state.session_token)
            del st.session_state.session_token
            del st.session_state.user_info
        st.success("✅ Logged out successfully!")
        st.rerun()
    
    st.markdown("---")

# Main navigation
menu = st.sidebar.selectbox(
    "Navigation",
    ["🏠 Dashboard", "📁 Project Tracker", "🗓️ Meeting & MoM Log", "🧾 Client Update Log", "🛠️ Issue Tracker", "🤖 AI Chatbot", "📈 Analytics"],
    key="main_navigation"
)

# Main content area
if menu == "🏠 Dashboard":
    st.markdown('<h1 class="main-header">ProjectOps Assistant Dashboard</h1>', unsafe_allow_html=True)
    
    # Get user-specific data
    projects = db.get_all_projects(current_user['id'])
    meetings = db.get_all_meetings(current_user['id'])
    issues = db.get_all_issues(current_user['id'])
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_projects = len(projects) if not projects.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_projects}</div>
            <div class="metric-label">Total Projects</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        active_projects = len(projects[projects['status'] == 'In Progress']) if not projects.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{active_projects}</div>
            <div class="metric-label">Active Projects</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_meetings = len(meetings) if not meetings.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_meetings}</div>
            <div class="metric-label">Total Meetings</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        pending_issues = len(issues[issues['status'] == 'Pending']) if not issues.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{pending_issues}</div>
            <div class="metric-label">Pending Issues</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Project Status Distribution")
        if not projects.empty:
            status_counts = projects['status'].value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Project Status Breakdown",
                color_discrete_map={
                    'In Progress': '#ffd700',
                    'Completed': '#28a745',
                    'On Hold': '#dc3545'
                }
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No projects found")
    
    with col2:
        st.subheader("📅 Recent Activity")
        if not meetings.empty:
            recent_meetings = meetings.head(5)
            for _, meeting in recent_meetings.iterrows():
                st.markdown(f"""
                <div style="padding: 1rem; border: 1px solid #e0e0e0; border-radius: 8px; margin: 0.5rem 0;">
                    <strong>{meeting['project_name']}</strong><br>
                    <small>{meeting['meeting_date']} - {meeting['agenda']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent meetings")
    
    # Recent Projects Table
    st.subheader("🚀 Recent Projects")
    if not projects.empty:
        recent_projects = projects.head(10)
        
        # Create a styled dataframe
        def style_status(val):
            if val == 'In Progress':
                return 'background-color: #ffd700; color: black;'
            elif val == 'Completed':
                return 'background-color: #28a745; color: white;'
            elif val == 'On Hold':
                return 'background-color: #dc3545; color: white;'
            return ''
        
        styled_df = recent_projects[['project_name', 'client_name', 'software', 'status', 'start_date']].copy()
        styled_df = styled_df.style.map(style_status, subset=['status'])
        
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("No projects found")

elif menu == "📁 Project Tracker":
    st.markdown('<h1 class="main-header">Project Tracker</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["➕ Add New Project", "📋 All Projects", "📁 File Management"])
    
    with tab1:
        with st.expander("Add New Project", expanded=True):
            with st.form("project_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    project_name = st.text_input("Project Name *", placeholder="Enter project name", key="project_name_input")
                    client_name = st.text_input("Client Name *", placeholder="Enter client name", key="client_name_input")
                    software = st.selectbox("Software *", ["Epicor", "MYOB", "ODOO", "PayGlobal", "Other"], key="software_select")
                    vendor = st.text_input("Vendor *", placeholder="Enter vendor name", key="vendor_input")
                
                with col2:
                    start_date = st.date_input("Start Date *", key="start_date_input")
                    deadline = st.date_input("Deadline *", key="deadline_input")
                    status = st.selectbox("Status *", ["In Progress", "On Hold", "Completed"], key="status_select")
                
                description = st.text_area("Description *", placeholder="Enter project description", key="description_input")
                
                # File upload section
                from file_uploader import render_file_upload_section
                file_path = render_file_upload_section(project_name, client_name)
                
                # Validation message
                if not project_name or not client_name or not vendor or not description:
                    st.warning("⚠️ Please fill in all required fields marked with *")
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    submitted = st.form_submit_button("➕ Add Project", use_container_width=True)
                
                if submitted:
                    # Validate all required fields
                    if not project_name or not client_name or not vendor or not description:
                        st.error("❌ Please fill in all required fields marked with *")
                    elif start_date >= deadline:
                        st.error("❌ Deadline must be after start date")
                    else:
                        success = db.add_project(
                            project_name, client_name, software, vendor,
                            start_date.strftime('%Y-%m-%d'), deadline.strftime('%Y-%m-%d'),
                            status, description, file_path, current_user['id']
                        )
                        if success:
                            st.success(f"✅ Project '{project_name}' added successfully!")
                            st.rerun()  # Refresh the form
                        else:
                            st.error("❌ Failed to add project. Please try again.")
    
    with tab2:
        projects = db.get_all_projects(current_user['id'])
        if not projects.empty:
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.selectbox("Filter by Status", ["All"] + list(projects['status'].unique()), key="status_filter_projects")
            with col2:
                software_filter = st.selectbox("Filter by Software", ["All"] + list(projects['software'].unique()), key="software_filter_projects")
            with col3:
                search_term = st.text_input("Search Projects", placeholder="Search by name or client", key="search_projects")
            
            # Apply filters
            filtered_projects = projects.copy()
            if status_filter != "All":
                filtered_projects = filtered_projects[filtered_projects['status'] == status_filter]
            if software_filter != "All":
                filtered_projects = filtered_projects[filtered_projects['software'] == software_filter]
            if search_term:
                filtered_projects = filtered_projects[
                    filtered_projects['project_name'].str.contains(search_term, case=False) |
                    filtered_projects['client_name'].str.contains(search_term, case=False)
                ]
            
            # Display filtered results with delete buttons
            st.subheader(f"📋 Projects ({len(filtered_projects)} found)")
            
            for idx, project in filtered_projects.iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        st.markdown(f"**{project['project_name']}**")
                        st.markdown(f"*{project['client_name']} - {project['software']}*")
                    
                    with col2:
                        st.markdown(f"**Status:** {project['status']}")
                        st.markdown(f"**Vendor:** {project['vendor']}")
                    
                    with col3:
                        st.markdown(f"**Start:** {project['start_date']}")
                        st.markdown(f"**Deadline:** {project['deadline']}")
                    
                    with col4:
                        # Delete button
                        if st.button("🗑️", key=f"delete_project_{project['id']}", help="Delete project"):
                            if st.session_state.get(f"confirm_delete_{project['id']}", False):
                                # Second confirmation
                                if db.delete_project(project['id']):
                                    st.success(f"✅ Project '{project['project_name']}' deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to delete project")
                            else:
                                # First confirmation
                                st.session_state[f"confirm_delete_{project['id']}"] = True
                                st.warning(f"⚠️ Click again to confirm deletion of '{project['project_name']}'")
                                st.rerun()
                    
                    # Show project details in expander
                    with st.expander(f"📄 View Details - {project['project_name']}", key=f"details_{project['id']}"):
                        st.markdown(f"**Description:** {project['description']}")
                        if project['file_path']:
                            st.markdown(f"**File:** {project['file_path']}")
                        
                        # Show related data
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            project_meetings = meetings[meetings['project_id'] == project['id']] if not meetings.empty else pd.DataFrame()
                            st.markdown(f"**Meetings:** {len(project_meetings)}")
                        
                        with col2:
                            project_updates = db.get_client_updates_by_project(project['id'], current_user['id'])
                            st.markdown(f"**Updates:** {len(project_updates)}")
                        
                        with col3:
                            project_issues = issues[issues['project_id'] == project['id']] if not issues.empty else pd.DataFrame()
                            st.markdown(f"**Issues:** {len(project_issues)}")
                    
                    st.divider()
            
            # Export options
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Export to PDF", key="projects_export_pdf", use_container_width=True):
                    filename = reports.export_projects_to_pdf(filtered_projects, "projects_report.pdf")
                    with open(filename, "rb") as f:
                        st.download_button("📥 Download PDF", f, file_name="projects_report.pdf", use_container_width=True)
            with col2:
                if st.button("📈 Export to Excel", key="projects_export_excel", use_container_width=True):
                    filename = reports.export_to_excel(filtered_projects, "projects_report.xlsx")
                    with open(filename, "rb") as f:
                        st.download_button("📥 Download Excel", f, file_name="projects_report.xlsx", use_container_width=True)
        else:
            st.info("No projects found")
    
    with tab3:
        from file_uploader import render_bulk_file_upload, render_file_analytics
        
        # File management options
        file_option = st.selectbox(
            "File Management Options",
            ["📦 Bulk File Upload", "📊 File Analytics"],
            key="file_management_option"
        )
        
        if file_option == "📦 Bulk File Upload":
            render_bulk_file_upload()
        elif file_option == "📊 File Analytics":
            render_file_analytics()

elif menu == "🗓️ Meeting & MoM Log":
    st.markdown('<h1 class="main-header">Meeting & MoM Log</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["➕ Log New Meeting", "📋 All Meetings"])
    
    with tab1:
        with st.expander("Log New Meeting", expanded=True):
            with st.form("meeting_form"):
                projects = db.get_all_projects(current_user['id'])
                project_options = projects[["id", "project_name"]].values.tolist()
                project_dict = {name: pid for pid, name in project_options}
                
                col1, col2 = st.columns(2)
                with col1:
                    project_name = st.selectbox("Project", list(project_dict.keys()), key="meeting_project_select")
                    meeting_date = st.date_input("Date", key="meeting_date_input")
                    attendees = st.text_input("Attendees", placeholder="Enter attendee names", key="meeting_attendees_input")
                
                with col2:
                    agenda = st.text_input("Agenda", placeholder="Enter meeting agenda", key="meeting_agenda_input")
                    follow_up_date = st.date_input("Follow-up Date", key="meeting_followup_input")
                
                mom = st.text_area("Minutes of Meeting (MoM)", placeholder="Enter meeting minutes", key="meeting_mom_input")
                next_steps = st.text_area("Next Steps", placeholder="Enter next steps", key="meeting_next_steps_input")
                
                submitted = st.form_submit_button("📝 Log Meeting", use_container_width=True)
                
                if submitted:
                    db.add_meeting(
                        project_dict[project_name],
                        meeting_date.strftime('%Y-%m-%d'),
                        attendees, agenda, mom, next_steps,
                        follow_up_date.strftime('%Y-%m-%d'),
                        current_user['id']
                    )
                    st.success(f"✅ Meeting for '{project_name}' logged successfully!")
                    st.rerun()
    
    with tab2:
        meetings = db.get_all_meetings(current_user['id'])
        if not meetings.empty:
            st.dataframe(meetings, use_container_width=True)
            
            # Export options
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Export to PDF", key="meetings_pdf", use_container_width=True):
                    filename = reports.export_meetings_to_pdf(meetings, "meetings_report.pdf")
                    with open(filename, "rb") as f:
                        st.download_button("📥 Download PDF", f, file_name="meetings_report.pdf", use_container_width=True)
            with col2:
                if st.button("📈 Export to Excel", key="meetings_excel", use_container_width=True):
                    filename = reports.export_to_excel(meetings, "meetings_report.xlsx")
                    with open(filename, "rb") as f:
                        st.download_button("📥 Download Excel", f, file_name="meetings_report.xlsx", use_container_width=True)
        else:
            st.info("No meetings found")

elif menu == "🧾 Client Update Log":
    st.markdown('<h1 class="main-header">Client Update Log</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["➕ Log Client Update", "📋 All Updates"])
    
    with tab1:
        with st.expander("Log Client Update", expanded=True):
            with st.form("update_form"):
                projects = db.get_all_projects(current_user['id'])
                project_options = projects[["id", "project_name"]].values.tolist()
                project_dict = {name: pid for pid, name in project_options}
                
                col1, col2 = st.columns(2)
                with col1:
                    project_name = st.selectbox("Project", list(project_dict.keys()), key="update_project_select")
                    update_date = st.date_input("Date", key="update_date_input")
                    sent_by = st.text_input("Sent By", placeholder="Enter sender name", key="update_sent_by_input")
                
                with col2:
                    mode = st.selectbox("Mode", ["Email", "Call", "Meeting", "Other"], key="update_mode_select")
                
                summary = st.text_area("Summary", placeholder="Enter update summary", key="update_summary_input")
                client_feedback = st.text_area("Client Feedback", placeholder="Enter client feedback", key="update_feedback_input")
                next_step = st.text_area("Next Step", placeholder="Enter next step", key="update_next_step_input")
                
                submitted = st.form_submit_button("📧 Log Update", use_container_width=True)
                
                if submitted:
                    db.add_client_update(
                        project_dict[project_name],
                        update_date.strftime('%Y-%m-%d'),
                        summary, sent_by, mode, client_feedback, next_step,
                        current_user['id']
                    )
                    st.success(f"✅ Update for '{project_name}' logged successfully!")
                    st.rerun()
    
    with tab2:
        updates = pd.DataFrame()
        if not projects.empty:
            updates = pd.concat([
                db.get_client_updates_by_project(pid, current_user['id']) for pid in projects['id'].tolist()
            ], ignore_index=True)
        
        if not updates.empty:
            st.dataframe(updates, use_container_width=True)
            
            # Export options
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Export to PDF", key="updates_pdf", use_container_width=True):
                    filename = reports.export_projects_to_pdf(updates, "updates_report.pdf")
                    with open(filename, "rb") as f:
                        st.download_button("📥 Download PDF", f, file_name="updates_report.pdf", use_container_width=True)
            with col2:
                if st.button("📈 Export to Excel", key="updates_excel", use_container_width=True):
                    filename = reports.export_to_excel(updates, "updates_report.xlsx")
                    with open(filename, "rb") as f:
                        st.download_button("📥 Download Excel", f, file_name="updates_report.xlsx", use_container_width=True)
        else:
            st.info("No client updates found")

elif menu == "🛠️ Issue Tracker":
    st.markdown('<h1 class="main-header">Issue Tracker</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["➕ Log New Issue", "📋 All Issues"])
    
    with tab1:
        with st.expander("Log New Issue", expanded=True):
            with st.form("issue_form"):
                projects = db.get_all_projects(current_user['id'])
                project_options = projects[["id", "project_name"]].values.tolist()
                project_dict = {name: pid for pid, name in project_options}
                
                col1, col2 = st.columns(2)
                with col1:
                    project_name = st.selectbox("Project", list(project_dict.keys()), key="issue_project_select")
                    date_reported = st.date_input("Date Reported", key="issue_date_reported_input")
                    status = st.selectbox("Status", ["Pending", "Resolved"], key="issue_status_select")
                
                with col2:
                    assigned_to = st.text_input("Assigned To", placeholder="Enter assignee name", key="issue_assigned_to_input")
                    resolution_date = st.date_input("Resolution Date", value=datetime.today(), key="issue_resolution_date_input")
                
                issue_description = st.text_area("Issue Description", placeholder="Enter detailed issue description", key="issue_description_input")
                
                submitted = st.form_submit_button("🚨 Log Issue", use_container_width=True)
                
                if submitted:
                    db.add_issue(
                        project_dict[project_name],
                        date_reported.strftime('%Y-%m-%d'),
                        issue_description, status, assigned_to,
                        resolution_date.strftime('%Y-%m-%d') if status == "Resolved" else None,
                        current_user['id']
                    )
                    st.success(f"✅ Issue for '{project_name}' logged successfully!")
                    st.rerun()
    
    with tab2:
        issues = db.get_all_issues(current_user['id'])
        if not issues.empty:
            st.dataframe(issues, use_container_width=True)
            
            # Export options
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Export to PDF", key="issues_pdf", use_container_width=True):
                    filename = reports.export_issues_to_pdf(issues, "issues_report.pdf")
                    with open(filename, "rb") as f:
                        st.download_button("📥 Download PDF", f, file_name="issues_report.pdf", use_container_width=True)
            with col2:
                if st.button("📈 Export to Excel", key="issues_excel", use_container_width=True):
                    filename = reports.export_to_excel(issues, "issues_report.xlsx")
                    with open(filename, "rb") as f:
                        st.download_button("📥 Download Excel", f, file_name="issues_report.xlsx", use_container_width=True)
        else:
            st.info("No issues found")

elif menu == "🤖 AI Chatbot":
    st.markdown('<h1 class="main-header">AI Project Assistant</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💬 Chat Interface")
        st.markdown("Ask me anything about your projects, meetings, issues, or updates!")
        
        if 'chat_history' not in st.session_state:
            st.session_state['chat_history'] = []
        
        # Chat input
        user_input = st.text_input("Type your question and press Enter:", placeholder="e.g., What's the status of Epicor for LTA?")
        
        if user_input:
            # Pass user context to chatbot
            response = chatbot.process_query(user_input, user_id=current_user['id'])
            st.session_state['chat_history'].append((user_input, response))
        
        # Display chat history
        for user, bot in st.session_state['chat_history']:
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {user}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="chat-message bot-message">
                <strong>Assistant:</strong> {bot}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🎯 Quick Actions")
        
        if st.button("📊 Show All Projects", key="chat_show_projects", use_container_width=True):
            response = chatbot.process_query("Show all projects", user_id=current_user['id'])
            st.session_state['chat_history'].append(("Show all projects", response))
            st.rerun()
        
        if st.button("📅 Recent Meetings", key="chat_recent_meetings", use_container_width=True):
            response = chatbot.process_query("Show last meetings", user_id=current_user['id'])
            st.session_state['chat_history'].append(("Show last meetings", response))
            st.rerun()
        
        if st.button("🚨 Pending Issues", key="chat_pending_issues", use_container_width=True):
            response = chatbot.process_query("What issues are unresolved?", user_id=current_user['id'])
            st.session_state['chat_history'].append(("What issues are unresolved?", response))
            st.rerun()
        
        if st.button("📧 Latest Updates", key="chat_latest_updates", use_container_width=True):
            response = chatbot.process_query("Show recent client updates", user_id=current_user['id'])
            st.session_state['chat_history'].append(("Show recent client updates", response))
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 💡 Example Queries")
        st.markdown("""
        - "What's the status of Epicor for LTA?"
        - "Show meetings for HFC"
        - "What issues are unresolved?"
        - "Show client updates for ATH"
        """)
        
        if st.button("🆘 Show Help", key="chat_show_help", use_container_width=True):
            help_msg = chatbot._get_help_message()
            st.session_state['chat_history'].append(("Show help", help_msg))
            st.rerun()

elif menu == "📈 Analytics":
    st.markdown('<h1 class="main-header">Analytics & Insights</h1>', unsafe_allow_html=True)
    
    # Get user-specific data
    projects = db.get_all_projects(current_user['id'])
    meetings = db.get_all_meetings(current_user['id'])
    issues = db.get_all_issues(current_user['id'])
    
    if not projects.empty:
        # Project Analytics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Project Status Analytics")
            
            # Status distribution
            status_counts = projects['status'].value_counts()
            fig_status = px.bar(
                x=status_counts.index,
                y=status_counts.values,
                title="Project Status Distribution",
                color=status_counts.index,
                color_discrete_map={
                    'In Progress': '#ffd700',
                    'Completed': '#28a745',
                    'On Hold': '#dc3545'
                }
            )
            fig_status.update_layout(height=400)
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            st.subheader("🏢 Client Distribution")
            
            # Client distribution
            client_counts = projects['client_name'].value_counts()
            fig_client = px.pie(
                values=client_counts.values,
                names=client_counts.index,
                title="Projects by Client"
            )
            fig_client.update_layout(height=400)
            st.plotly_chart(fig_client, use_container_width=True)
        
        # Software Analytics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💻 Software Distribution")
            
            software_counts = projects['software'].value_counts()
            fig_software = px.bar(
                x=software_counts.index,
                y=software_counts.values,
                title="Projects by Software",
                color=software_counts.values,
                color_continuous_scale='viridis'
            )
            fig_software.update_layout(height=400)
            st.plotly_chart(fig_software, use_container_width=True)
        
        with col2:
            st.subheader("📅 Project Timeline")
            
            if not projects.empty:
                # Create timeline data
                timeline_data = []
                for _, project in projects.iterrows():
                    timeline_data.append({
                        'Project': project['project_name'],
                        'Start': project['start_date'],
                        'End': project['deadline'],
                        'Status': project['status']
                    })
                
                timeline_df = pd.DataFrame(timeline_data)
                
                # Gantt chart
                fig_timeline = px.timeline(
                    timeline_df,
                    x_start="Start",
                    x_end="End",
                    y="Project",
                    color="Status",
                    title="Project Timeline"
                )
                fig_timeline.update_layout(height=400)
                st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Key Metrics
        st.subheader("📈 Key Performance Indicators")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            completion_rate = len(projects[projects['status'] == 'Completed']) / len(projects) * 100
            st.metric("Completion Rate", f"{completion_rate:.1f}%")
        
        with col2:
            avg_project_duration = 0  # Calculate average project duration
            st.metric("Avg Project Duration", f"{avg_project_duration} days")
        
        with col3:
            total_meetings_count = len(meetings) if not meetings.empty else 0
            st.metric("Total Meetings", total_meetings_count)
        
        with col4:
            pending_issues_count = len(issues[issues['status'] == 'Pending']) if not issues.empty else 0
            st.metric("Pending Issues", pending_issues_count)
    
    else:
        st.info("No data available for analytics") 