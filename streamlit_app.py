#!/usr/bin/env python3
"""
ProjectOps Assistant - Streamlit App
A comprehensive project management system with AI chatbot integration
"""

import streamlit as st

# Page configuration - MUST be the first Streamlit command
st.set_page_config(
    page_title="ProjectOps Assistant",
    page_icon=":rocket:",
    layout="wide",
    initial_sidebar_state="collapsed"  # Collapsed by default
)

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys
from file_uploader import render_file_upload_section

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules
from database_postgres import ProjectOpsDatabase
from chatbot import ProjectChatbot
from reports import ReportGenerator
from neon_auth import auth
from login_page import render_login_page, check_if_admin_exists, render_force_password_change
from email_management import render_email_management_page

# --- Authentication check (must be at the very top) ---
def check_authentication():
    if st.session_state.get('pending_password_change'):
        render_force_password_change()
        st.stop()
    current_user = auth.get_current_user()
    if not current_user:
        if not check_if_admin_exists():
            st.markdown('<h1 class="main-header">🔐 Project Tracker Setup</h1>', unsafe_allow_html=True)
            from login_page import render_admin_setup
            render_admin_setup()
            st.stop()
        else:
            render_login_page()
            st.stop()
    return current_user

current_user = check_authentication()

# --- rest of your code (navbar, sidebar, etc.) ---

# Initialize components
db = ProjectOpsDatabase()
chatbot = ProjectChatbot(db)
reports = ReportGenerator()

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
    .project-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        padding: 1.8rem;
        margin-bottom: 1.8rem;
        border-left: 6px solid VAR_STATUS_COLOR;
        transition: transform 0.18s, box-shadow 0.18s;
        position: relative;
    }
    .project-card:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 8px 24px rgba(31,119,180,0.18);
        border-left: 6px solid #1f77b4;
    }
    .project-details-btn {
        width: 100%;
        padding: 0.7rem 0.5rem;
        margin-top: 0.5rem;
        background: linear-gradient(90deg,#1f77b4 0%,#764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 1rem;
        transition: background 0.18s;
    }
    .project-details-btn:hover {
        background: linear-gradient(90deg,#764ba2 0%,#1f77b4 100%);
    }
</style>
""", unsafe_allow_html=True)

# --- Add custom CSS for navbar and dropdown ---
st.markdown("""
<style>
.navbar {
    width: 100vw;
    background: linear-gradient(90deg, #1f77b4 0%, #764ba2 100%);
    padding: 0.7rem 2rem 0.7rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000;
    box-shadow: 0 2px 8px rgba(31,119,180,0.08);
}
.navbar-logo {
    font-size: 1.5rem;
    font-weight: bold;
    color: #fff;
    letter-spacing: 1px;
    display: flex;
    align-items: center;
    gap: 0.7rem;
}
.navbar-menu {
    display: flex;
    gap: 1.5rem;
}
.navbar-link {
    color: #fff;
    font-size: 1.08rem;
    font-weight: 500;
    text-decoration: none;
    padding: 0.4rem 1.1rem;
    border-radius: 8px;
    transition: background 0.18s, color 0.18s;
    cursor: pointer;
}
.navbar-link:hover, .navbar-link.active {
    background: rgba(255,255,255,0.18);
    color: #ffd700;
}
.profile-dropdown {
    position: relative;
    display: inline-block;
}
.profile-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 1.2rem;
    font-weight: bold;
    cursor: pointer;
    border: 2px solid #fff;
    box-shadow: 0 2px 8px rgba(31,119,180,0.12);
}
.dropdown-content {
    display: none;
    position: absolute;
    right: 0;
    background: #fff;
    min-width: 160px;
    box-shadow: 0 8px 24px rgba(31,119,180,0.18);
    border-radius: 10px;
    z-index: 1001;
    margin-top: 0.5rem;
}
.profile-dropdown:hover .dropdown-content, .profile-dropdown:focus-within .dropdown-content {
    display: block;
}
.dropdown-item {
    color: #1f77b4;
    padding: 0.9rem 1.2rem;
    text-decoration: none;
    display: block;
    font-size: 1.05rem;
    border-bottom: 1px solid #f0f0f0;
    cursor: pointer;
    background: #fff;
    border-radius: 10px 10px 0 0;
}
.dropdown-item:last-child {
    border-bottom: none;
    border-radius: 0 0 10px 10px;
}
.dropdown-item:hover {
    background: #f0f4fa;
    color: #764ba2;
}
.stApp {
    padding-top: 70px !important;
}
</style>
""", unsafe_allow_html=True)

# --- Top Navbar ---
def render_navbar(current_user):
    menu_options = [
        ("🏠 Dashboard", "Dashboard"),
        ("📁 Project Tracker", "Project Tracker"),
        ("🗓️ Meeting & MoM Log", "Meeting & MoM Log"),
        ("🧾 Client Update Log", "Client Update Log"),
        ("🛠️ Issue Tracker", "Issue Tracker"),
        ("🤖 AI Chatbot", "AI Chatbot"),
        ("📈 Analytics", "Analytics"),
        ("📧 Email Integration", "Email Integration")
    ]
    if current_user['role'] == 'admin':
        menu_options.append(("👥 User Management", "User Management"))
    active_menu = st.query_params.get("nav", [menu_options[0][1]])[0]
    st.session_state['active_menu'] = active_menu
    navbar_html = '''<div class="navbar">
        <div class="navbar-logo">
            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/Meetup_Logo.png" width="36" style="border-radius: 8px;">
            ProjectOps Assistant
        </div>
        <div class="navbar-menu">'''
    for icon, label in menu_options:
        active_class = "active" if active_menu == label else ""
        navbar_html += f'<a class="navbar-link {active_class}" href="?nav={label}">{icon} {label}</a>'
    navbar_html += '''</div>
        <div class="profile-dropdown" tabindex="0">
            <div class="profile-avatar">''' + current_user['full_name'][:2].upper() + '''</div>
            <div class="dropdown-content">
                <div class="dropdown-item" onclick="window.location.href='?nav=profile'">Edit Profile</div>
                <div class="dropdown-item" onclick="window.location.href='?nav=logout'">Logout</div>
            </div>
        </div>
    </div>'''
    st.markdown(navbar_html, unsafe_allow_html=True)

# Remove JS postMessage logic and event handler
# --- Navigation logic based on query param ---
menu = st.session_state['active_menu']

# --- Main content rendering (unchanged) ---
# Profile Picture Management Page
if st.session_state.get('show_profile_page', False):
    st.markdown('<h1 class="main-header">🖼️ Profile Picture Management</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Current Picture")
        if st.session_state['profile_picture'] is not None:
            st.image(st.session_state['profile_picture'], width=200, use_column_width=True)
        else:
            st.markdown("""
            <div style='width: 200px; height: 200px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        display: flex; align-items: center; justify-content: center; color: white; font-size: 48px; font-weight: bold; margin: 0 auto;'>
                {initials}
            </div>
            """.format(initials=current_user['full_name'][:2].upper()), unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Upload New Picture")
        st.markdown("Choose a profile picture that represents you professionally.")
        
        new_upload = st.file_uploader(
            "Select Image", 
            type=['png', 'jpg', 'jpeg'], 
            key="profile_page_upload",
            help="Upload a profile picture (PNG, JPG, JPEG)"
        )
        
        if new_upload is not None:
            st.session_state['profile_picture'] = new_upload
            st.success("✅ Profile picture updated successfully!")
            st.rerun()
        
        st.markdown("---")
        
        # Picture management options
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("🔄 Reset to Default", key="reset_profile_pic", use_container_width=True):
                st.session_state['profile_picture'] = None
                st.success("✅ Profile picture reset to default!")
                st.rerun()
        
        with col_b:
            if st.button("⬅️ Back to Dashboard", key="back_to_dashboard", use_container_width=True):
                st.session_state['show_profile_page'] = False
                st.rerun()
    
    st.stop()

# Admin-only User Management
if menu == "👥 User Management" and current_user['role'] == 'admin':
    st.markdown('<h1 class="main-header">User Management</h1>', unsafe_allow_html=True)
    st.markdown("Add new users. They will receive a temporary password and must change it on first login.")
    with st.form("add_user_form"):
        new_email = st.text_input("User Email", placeholder="user@example.com", key="new_user_email")
        new_name = st.text_input("Full Name", placeholder="Full Name", key="new_user_name")
        new_role = st.selectbox("Role", ["user", "admin"], key="new_user_role")
        submitted = st.form_submit_button("➕ Create User", use_container_width=True)
        if submitted:
            if not new_email or not new_name:
                st.error("Please fill in all fields.")
            else:
                success, msg = auth.create_user_with_temp_password(new_email, new_name, new_role)
                if success:
                    # Log action
                    auth.log_admin_action(current_user['id'], current_user['email'], "create_user", None, new_email, f"role={new_role}")
                    st.success(msg)
                else:
                    st.error(msg)
    st.markdown("---")
    st.subheader("All Users")
    users_df = auth.get_all_users()
    if not users_df.empty:
        users_df['Status'] = users_df['is_active'].map(lambda x: 'Active' if x else 'Inactive')
        for idx, user in users_df.iterrows():
            col1, col2, col3, col4, col5, col6, col7 = st.columns([3, 2, 2, 2, 2, 2, 2])
            col1.markdown(f"**{user['email']}**")
            col2.markdown(user['full_name'])
            # Role change dropdown
            if user['email'] != current_user['email']:
                new_role = col3.selectbox("Role", ["user", "admin"], index=0 if user['role']=="user" else 1, key=f"role_{user['id']}")
                if new_role != user['role']:
                    if col3.button("Update Role", key=f"update_role_{user['id']}"):
                        auth.change_user_role(user['id'], new_role, current_user['id'], current_user['email'])
                        st.success(f"Role updated for {user['email']}.")
                        st.rerun()
            else:
                col3.markdown(user['role'])
            col4.markdown(user['Status'])
            # Deactivate/reactivate
            if user['email'] != current_user['email']:
                if user['is_active']:
                    if col5.button("Deactivate", key=f"deactivate_{user['id']}"):
                        auth.set_user_active(user['id'], False, current_user['id'], current_user['email'])
                        st.success(f"User {user['email']} deactivated.")
                        st.rerun()
                else:
                    if col5.button("Reactivate", key=f"reactivate_{user['id']}"):
                        auth.set_user_active(user['id'], True, current_user['id'], current_user['email'])
                        st.success(f"User {user['email']} reactivated.")
                        st.rerun()
            else:
                col5.markdown("-")
            # Password reset
            if user['email'] != current_user['email']:
                if col6.button("Reset Password", key=f"resetpw_{user['id']}"):
                    success, msg = auth.reset_user_password(user['id'], current_user['id'], current_user['email'])
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                    st.rerun()
            else:
                col6.markdown("-")
            # User deletion
            if user['email'] != current_user['email']:
                if col7.button("Delete", key=f"delete_{user['id']}"):
                    if st.session_state.get(f"confirm_delete_{user['id']}"):
                        if auth.delete_user(user['id'], current_user['id'], current_user['email']):
                            st.success(f"User {user['email']} deleted.")
                            st.rerun()
                        else:
                            st.error("Failed to delete user.")
                    else:
                        st.session_state[f"confirm_delete_{user['id']}"] = True
                        st.warning(f"Click again to confirm deletion of {user['email']}")
                        st.stop()
            else:
                col7.markdown("-")
    else:
        st.info("No users found.")
    st.markdown("---")
    st.subheader("Audit Logs (last 100 actions)")
    logs_df = auth.get_audit_logs(limit=100)
    if not logs_df.empty:
        logs_df = logs_df[['timestamp', 'admin_email', 'action', 'target_email', 'details']]
        logs_df.columns = ['Time', 'Admin', 'Action', 'Target', 'Details']
        st.dataframe(logs_df, use_container_width=True)
    else:
        st.info("No audit logs found.")
    st.stop()

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
    st.markdown('<h1 class="main-header">📁 Project Tracker</h1>', unsafe_allow_html=True)
    
    # Add some spacing and visual separation
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["➕ Add New Project", "📋 All Projects", "📁 File Management"])
    
    with tab1:
        st.markdown("### 🆕 Create New Project")
        st.markdown("Fill in the details below to create a new project entry.")
        
        # File upload section OUTSIDE the form
        with st.expander("📎 File Upload (Optional)", expanded=False):
            uploaded_file_path = render_file_upload_section(None, None)
        
        # Project form in a clean container
        with st.container():
            st.markdown("#### Project Information")
            with st.form("project_form", clear_on_submit=True):
                # Project details in organized columns
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Basic Information**")
                    project_name = st.text_input("Project Name *", placeholder="Enter project name", key="project_name_input")
                    client_name = st.text_input("Client Name *", placeholder="Enter client name", key="client_name_input")
                    software = st.selectbox("Software *", ["Epicor", "MYOB", "ODOO", "PayGlobal", "Sage 300", "Other"], key="software_select")
                    vendor = st.text_input("Vendor *", placeholder="Enter vendor name", key="vendor_input")
                
                with col2:
                    st.markdown("**Timeline & Status**")
                    start_date = st.date_input("Start Date *", key="start_date_input")
                    deadline = st.date_input("Deadline *", key="deadline_input")
                    status = st.selectbox("Status *", ["In Progress", "On Hold", "Completed", "Planning"], key="status_select")
                
                # Description and file upload
                st.markdown("**Project Details**")
                description = st.text_area("Description *", placeholder="Enter detailed project description", key="description_input", height=100)
                
                # Form validation and submission
                if not project_name or not client_name or not vendor or not description:
                    st.warning("⚠️ Please fill in all required fields marked with *")
                
                # Submit button with better styling
                col1b, col2b, col3b = st.columns([1, 2, 1])
                with col2b:
                    submitted = st.form_submit_button("➕ Create Project", use_container_width=True, type="primary")
                
                if submitted:
                    if not project_name or not client_name or not vendor or not description:
                        st.error("❌ Please fill in all required fields marked with *")
                    elif start_date >= deadline:
                        st.error("❌ Deadline must be after start date")
                    else:
                        # Prefer file uploaded in form, else use uploaded_file_path from outside
                        file_path = None
                        if uploaded_file_path:
                            file_path = uploaded_file_path
                        
                        success = db.add_project(
                            project_name, client_name, software, vendor,
                            start_date.strftime('%Y-%m-%d'), deadline.strftime('%Y-%m-%d'),
                            status, description, file_path, current_user['id']
                        )
                        if success:
                            st.success(f"✅ Project '{project_name}' created successfully!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Failed to create project. Please try again.")
    
    with tab2:
        st.markdown("### 📋 Project Overview")
        
        # Get data
        projects = db.get_all_projects(current_user['id'])
        meetings = db.get_all_meetings(current_user['id'])
        issues = db.get_all_issues(current_user['id'])
        
        if not projects.empty:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_projects = len(projects)
                st.metric("Total Projects", total_projects)
            with col2:
                active_projects = len(projects[projects['status'] == 'In Progress'])
                st.metric("Active Projects", active_projects)
            with col3:
                completed_projects = len(projects[projects['status'] == 'Completed'])
                st.metric("Completed", completed_projects)
            with col4:
                on_hold_projects = len(projects[projects['status'] == 'On Hold'])
                st.metric("On Hold", on_hold_projects)
            
            st.markdown("---")
            
            # Filters in a clean layout
            st.markdown("#### 🔍 Filter & Search")
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.selectbox("Status Filter", ["All"] + list(projects['status'].unique()), key="status_filter_projects")
            with col2:
                software_filter = st.selectbox("Software Filter", ["All"] + list(projects['software'].unique()), key="software_filter_projects")
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
            
            st.markdown(f"#### 📊 Projects ({len(filtered_projects)} found)")
            
            # Card view with improved styling
            seen_ids = set()
            card_cols = st.columns(2)
            card_count = 0
            
            for idx, project in filtered_projects.iterrows():
                pname = project.get('project_name')
                pid = project.get('id')
                
                if (
                    pd.notnull(pname) and
                    pd.notnull(pid) and
                    isinstance(pname, str) and
                    str(pname).strip() and
                    str(pid).strip() and
                    pid not in seen_ids
                ):
                    seen_ids.add(pid)
                    col = card_cols[card_count % 2]
                    
                    with col:
                        # Enhanced card styling
                        status = project.get('status', 'In Progress')
                        status_color = {
                            'Completed': '#4CAF50',
                            'In Progress': '#2196F3',
                            'Pending': '#FFC107',
                            'On Hold': '#FF5722',
                            'Near Completion': '#00BCD4',
                            'Planning': '#9C27B0',
                        }.get(status, '#607D8B')
                        
                        percent = project.get('percent_complete', '')
                        if percent and isinstance(percent, str) and '%' in percent:
                            percent_val = percent
                        else:
                            percent_val = ''
                        
                        # Enhanced card HTML with better spacing and icons
                        st.markdown(f'''
                        <div class="project-card" style="border-left: 6px solid {status_color};">
                            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
                                <div style="font-size: 1.3rem; font-weight: bold; color: #1a1a1a;">{pname}</div>
                                <div style="font-size: 0.9rem; font-weight: 600; color: {status_color}; background: {status_color}15; padding: 0.3rem 0.8rem; border-radius: 20px;">{status}</div>
                            </div>
                            <div style="margin-bottom: 1rem; color: #555; font-size: 0.95rem; line-height: 1.5;">
                                <div style="margin-bottom: 0.5rem;"><b>🖥️ Software:</b> {project.get('software', '')}</div>
                                <div style="margin-bottom: 0.5rem;"><b>👥 Client:</b> {project.get('client_name', '')}</div>
                                <div style="margin-bottom: 0.5rem;"><b>🏢 Vendor:</b> {project.get('vendor', '')}</div>
                                <div style="margin-bottom: 0.5rem;"><b>📅 Deadline:</b> {project.get('deadline', '')}</div>
                                <div style="margin-bottom: 0.5rem;"><b>📊 Progress:</b> {percent_val if percent_val else 'Not specified'}</div>
                            </div>
                            <div style="margin-bottom: 1rem; color: #444; font-size: 0.9rem; line-height: 1.4; background: #f8f9fa; padding: 0.8rem; border-radius: 8px;">
                                <b>📝 Description:</b> {project.get('description', '')[:150]}{'...' if len(str(project.get('description', ''))) > 150 else ''}
                            </div>
                            <div style="display: flex; gap: 1.2rem; font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
                                <span>📅 <b>{len(meetings[meetings['project_id'] == pid]) if not meetings.empty else 0}</b> Meetings</span>
                                <span>📝 <b>{len(db.get_client_updates_by_project(pid, current_user['id']))}</b> Updates</span>
                                <span>🐞 <b>{len(issues[issues['project_id'] == pid]) if not issues.empty else 0}</b> Issues</span>
                            </div>
                            {st.markdown(
    f'<a href="/ProjectDetails?project_id={pid}">'
    '<button class="project-details-btn">🔍 View Details</button>'
    '</a>',
    unsafe_allow_html=True
)}
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    card_count += 1
            
            # Export options with better styling
            st.markdown("---")
            st.markdown("#### 📤 Export Options")
            col1e, col2e = st.columns(2)
            with col1e:
                if st.button("📊 Export to PDF", key="projects_export_pdf", use_container_width=True):
                    filename = reports.export_projects_to_pdf(filtered_projects, "projects_report.pdf")
                    with open(filename, "rb") as f:
                        st.download_button("📥 Download PDF", f, file_name="projects_report.pdf", use_container_width=True)
            with col2e:
                if st.button("📈 Export to Excel", key="projects_export_excel", use_container_width=True):
                    filename = reports.export_to_excel(filtered_projects, "projects_report.xlsx")
                    with open(filename, "rb") as f:
                        st.download_button("📥 Download Excel", f, file_name="projects_report.xlsx", use_container_width=True)
        else:
            st.info("📭 No projects found. Create your first project using the 'Add New Project' tab!")
    
    with tab3:
        st.markdown("### 📁 File Management")
        st.markdown("Upload and manage project-related files.")
        
        from file_uploader import render_bulk_file_upload, render_file_analytics
        
        # File management options
        file_option = st.selectbox(
            "Choose File Management Option",
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
            st.info("No updates found")

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
                    date_reported = st.date_input("Date Reported", key="issue_date_input")
                    status = st.selectbox("Status", ["Pending", "In Progress", "Resolved"], key="issue_status_select")
                
                with col2:
                    assigned_to = st.text_input("Assigned To", placeholder="Enter assignee name", key="issue_assigned_input")
                    resolution_date = st.date_input("Resolution Date", key="issue_resolution_input")
                
                description = st.text_area("Description", placeholder="Enter issue description", key="issue_description_input")
                
                submitted = st.form_submit_button("🐞 Log Issue", use_container_width=True)
                
                if submitted:
                    db.add_issue(
                        project_dict[project_name],
                        date_reported.strftime('%Y-%m-%d'),
                        description, status, assigned_to,
                        resolution_date.strftime('%Y-%m-%d'),
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
                    filename = reports.export_projects_to_pdf(issues, "issues_report.pdf")
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
    st.markdown("Ask questions about your projects, get insights, and receive AI-powered recommendations.")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me about your projects..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            response = chatbot.get_response(prompt, current_user['id'])
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

    # Clear chat button
    if st.button("🗑️ Clear Chat", key="clear_chat"):
        st.session_state.messages = []
        st.rerun()

elif menu == "📈 Analytics":
    st.markdown('<h1 class="main-header">Project Analytics</h1>', unsafe_allow_html=True)
    
    # Get data
    projects = db.get_all_projects(current_user['id'])
    meetings = db.get_all_meetings(current_user['id'])
    issues = db.get_all_issues(current_user['id'])
    
    if not projects.empty:
        # Project Status Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Project Status Distribution")
            status_counts = projects['status'].value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Project Status Breakdown"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📈 Projects Over Time")
            projects['start_date'] = pd.to_datetime(projects['start_date'])
            monthly_projects = projects.groupby(projects['start_date'].dt.to_period('M')).size()
            fig = px.line(
                x=monthly_projects.index.astype(str),
                y=monthly_projects.values,
                title="New Projects per Month"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Software Distribution
        st.subheader("🖥️ Software Distribution")
        software_counts = projects['software'].value_counts()
        fig = px.bar(
            x=software_counts.index,
            y=software_counts.values,
            title="Projects by Software"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Client Analysis
        st.subheader("👥 Top Clients")
        client_counts = projects['client_name'].value_counts().head(10)
        fig = px.bar(
            x=client_counts.index,
            y=client_counts.values,
            title="Projects by Client"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No projects found for analytics.")

elif menu == "📧 Email Integration":
    render_email_management_page(db, current_user['id'])

# Project Detail Page
if st.session_state.get('show_project_detail', False):
    pid = st.session_state.get('selected_project_id')
    project = db.get_project_by_id(pid)
    meetings = db.get_all_meetings(current_user['id'])
    updates = db.get_client_updates_by_project(pid, current_user['id'])
    issues = db.get_all_issues(current_user['id'])
    
    st.markdown(f'<h1 class="main-header">🔍 Project Details: {project["project_name"]}</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Project Info
    st.markdown("### 📝 Project Information")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Client:** {project['client_name']}")
        st.markdown(f"**Software:** {project['software']}")
        st.markdown(f"**Vendor:** {project['vendor']}")
        st.markdown(f"**Status:** {project['status']}")
        st.markdown(f"**Start Date:** {project['start_date']}")
        st.markdown(f"**Deadline:** {project['deadline']}")
    with col2:
        st.markdown(f"**Description:**\n{project['description']}")
        if project['file_path']:
            st.markdown(f"**File:** {project['file_path']}")
    st.markdown("---")
    
    # Meetings (MoM)
    st.markdown("### 📅 Meetings & MoM")
    if not meetings.empty:
        project_meetings = meetings[meetings['project_id'] == pid]
    else:
        project_meetings = pd.DataFrame()
    if not project_meetings.empty:
        for idx, meeting in project_meetings.iterrows():
            with st.expander(f"{meeting['meeting_date']} - {meeting['agenda']}"):
                st.markdown(f"**Attendees:** {meeting['attendees']}")
                st.markdown(f"**Minutes of Meeting:**\n{meeting['mom']}")
                st.markdown(f"**Next Steps:** {meeting['next_steps']}")
                st.markdown(f"**Follow-up Date:** {meeting['follow_up_date']}")
                # Edit/Delete buttons (future: implement edit logic)
                colm1, colm2 = st.columns(2)
                with colm1:
                    if st.button("✏️ Edit MoM", key=f"edit_mom_{meeting['id']}"):
                        st.warning("Edit MoM feature coming soon!")
                with colm2:
                    if st.button("🗑️ Delete MoM", key=f"delete_mom_{meeting['id']}"):
                        db.delete_meeting(meeting['id'])
                        st.success("Meeting deleted!")
                        st.rerun()
    else:
        st.info("No meetings found for this project.")
    # Add new meeting
    with st.expander("➕ Add New Meeting", expanded=False):
        with st.form(f"add_meeting_form_{pid}"):
            meeting_date = st.date_input("Meeting Date")
            attendees = st.text_input("Attendees")
            agenda = st.text_input("Agenda")
            mom = st.text_area("Minutes of Meeting (MoM)")
            next_steps = st.text_area("Next Steps")
            follow_up_date = st.date_input("Follow-up Date")
            submitted = st.form_submit_button("Add Meeting")
            if submitted:
                db.add_meeting(pid, meeting_date.strftime('%Y-%m-%d'), attendees, agenda, mom, next_steps, follow_up_date.strftime('%Y-%m-%d'), current_user['id'])
                st.success("Meeting added!")
                st.rerun()
    st.markdown("---")
    
    # Updates/Logs
    st.markdown("### 📝 Client Updates / Logs")
    if not updates.empty:
        for idx, update in updates.iterrows():
            with st.expander(f"{update['update_date']} - {update['summary'][:40]}"):
                st.markdown(f"**Sent By:** {update['sent_by']}")
                st.markdown(f"**Mode:** {update['mode']}")
                st.markdown(f"**Client Feedback:** {update['client_feedback']}")
                st.markdown(f"**Next Step:** {update['next_step']}")
                # Edit/Delete buttons (future: implement edit logic)
                colu1, colu2 = st.columns(2)
                with colu1:
                    if st.button("✏️ Edit Update", key=f"edit_update_{update['id']}"):
                        st.warning("Edit update feature coming soon!")
                with colu2:
                    if st.button("🗑️ Delete Update", key=f"delete_update_{update['id']}"):
                        db.delete_client_update(update['id'])
                        st.success("Update deleted!")
                        st.rerun()
    else:
        st.info("No updates found for this project.")
    # Add new update
    with st.expander("➕ Add New Update/Log", expanded=False):
        with st.form(f"add_update_form_{pid}"):
            update_date = st.date_input("Update Date")
            summary = st.text_area("Summary")
            sent_by = st.text_input("Sent By", value=current_user['full_name'])
            mode = st.selectbox("Mode", ["Email", "Call", "Meeting", "Other"])
            client_feedback = st.text_area("Client Feedback")
            next_step = st.text_area("Next Step")
            submitted = st.form_submit_button("Add Update")
            if submitted:
                db.add_client_update(pid, update_date.strftime('%Y-%m-%d'), summary, sent_by, mode, client_feedback, next_step, current_user['id'])
                st.success("Update added!")
                st.rerun()
    st.markdown("---")
    
    # Issues/Queries
    st.markdown("### 🐞 Issues / Queries")
    if not issues.empty:
        project_issues = issues[issues['project_id'] == pid]
    else:
        project_issues = pd.DataFrame()
    if not project_issues.empty:
        for idx, issue in project_issues.iterrows():
            with st.expander(f"{issue['date_reported']} - {issue['description'][:40]}"):
                st.markdown(f"**Status:** {issue['status']}")
                st.markdown(f"**Assigned To:** {issue['assigned_to']}")
                st.markdown(f"**Resolution Date:** {issue['resolution_date']}")
                # Edit/Delete buttons (future: implement edit logic)
                coli1, coli2 = st.columns(2)
                with coli1:
                    if st.button("✏️ Edit Issue", key=f"edit_issue_{issue['id']}"):
                        st.warning("Edit issue feature coming soon!")
                with coli2:
                    if st.button("🗑️ Delete Issue", key=f"delete_issue_{issue['id']}"):
                        db.delete_issue(issue['id'])
                        st.success("Issue deleted!")
                        st.rerun()
    else:
        st.info("No issues found for this project.")
    # Add new issue
    with st.expander("➕ Add New Issue/Query", expanded=False):
        with st.form(f"add_issue_form_{pid}"):
            date_reported = st.date_input("Date Reported")
            description = st.text_area("Description")
            status = st.selectbox("Status", ["Pending", "In Progress", "Resolved"])
            assigned_to = st.text_input("Assigned To")
            resolution_date = st.date_input("Resolution Date")
            submitted = st.form_submit_button("Add Issue")
            if submitted:
                db.add_issue(pid, date_reported.strftime('%Y-%m-%d'), description, status, assigned_to, resolution_date.strftime('%Y-%m-%d'), current_user['id'])
                st.success("Issue added!")
                st.rerun()
    st.markdown("---")
    
    # Back button
    if st.button("⬅️ Back to Project Tracker", key="back_to_tracker"):
        st.session_state['show_project_detail'] = False
        st.session_state['selected_project_id'] = None
        st.rerun()
    st.stop() 