import streamlit as st
import pandas as pd
from database_postgres import ProjectOpsDatabase
from chatbot import ProjectOpsChatbot
import reports
import os
from datetime import datetime
import streamlit_authenticator as stauth
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="ProjectOps Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .status-in-progress {
        background-color: #ffd700;
        color: #000;
    }
    
    .status-completed {
        background-color: #28a745;
        color: white;
    }
    
    .status-on-hold {
        background-color: #dc3545;
        color: white;
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .bot-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- AUTHENTICATION ---
credentials = {
    "usernames": {
        "admin": {
            "name": "admin",
            "password": "$2b$12$40mIeAd..6Vxumgh22GJyObRourSvBms26ddHZL9kxlpjtA5.J16C"
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "projectops",  # cookie_name
    "abcdef",      # key
    1               # cookie_expiry_days
)
name, authentication_status, username = authenticator.login('Login')

if authentication_status is False:
    st.error('Username/password is incorrect')
    st.stop()
elif authentication_status is None:
    st.warning('Please enter your username and password')
    st.stop()

# --- END AUTHENTICATION ---

# Initialize PostgreSQL database
try:
    db = ProjectOpsDatabase()  # Will use st.secrets["DB_URL"] or fallback to SQLite
    chatbot = ProjectOpsChatbot(db)
    st.success("✅ Connected to database successfully!")
except Exception as e:
    st.error(f"❌ Database connection failed: {e}")
    st.info("💡 Make sure to configure your database URL in Streamlit Cloud secrets")
    st.stop()

# Sidebar with professional styling
with st.sidebar:
    st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
    st.markdown("### 📊 ProjectOps Assistant")
    st.markdown("Enterprise Project Management")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("**👤 Admin:** Jayshil Singh")
    st.markdown("---")
    
    # Navigation
    menu = st.selectbox(
        "Navigation",
        ["📊 Dashboard", "📁 Project Tracker", "🗓️ Meeting & MoM Log", "🧾 Client Update Log", "🛠️ Issue Tracker", "🤖 AI Chatbot", "📈 Analytics"]
    )

# Main content area
if menu == "📊 Dashboard":
    st.markdown('<h1 class="main-header">ProjectOps Assistant Dashboard</h1>', unsafe_allow_html=True)
    
    # Get data for metrics
    projects = db.get_all_projects()
    meetings = db.get_all_meetings()
    issues = db.get_all_issues()
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(projects)}</div>
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
    
    tab1, tab2 = st.tabs(["➕ Add New Project", "📋 All Projects"])
    
    with tab1:
        with st.expander("Add New Project", expanded=True):
            with st.form("project_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    project_name = st.text_input("Project Name", placeholder="Enter project name")
                    client_name = st.text_input("Client Name", placeholder="Enter client name")
                    software = st.selectbox("Software", ["Epicor", "MYOB", "ODOO", "PayGlobal", "Other"])
                    vendor = st.text_input("Vendor", placeholder="Enter vendor name")
                
                with col2:
                    start_date = st.date_input("Start Date")
                    deadline = st.date_input("Deadline")
                    status = st.selectbox("Status", ["In Progress", "On Hold", "Completed"])
                
                description = st.text_area("Description", placeholder="Enter project description")
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    submitted = st.form_submit_button("➕ Add Project", use_container_width=True)
                
                if submitted:
                    db.add_project(
                        project_name, client_name, software, vendor,
                        start_date.strftime('%Y-%m-%d'), deadline.strftime('%Y-%m-%d'),
                        status, description, None  # No file path in cloud
                    )
                    st.success(f"✅ Project '{project_name}' added successfully!")
    
    with tab2:
        projects = db.get_all_projects()
        if not projects.empty:
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.selectbox("Filter by Status", ["All"] + list(projects['status'].unique()))
            with col2:
                software_filter = st.selectbox("Filter by Software", ["All"] + list(projects['software'].unique()))
            with col3:
                search_term = st.text_input("Search Projects", placeholder="Search by name or client")
            
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
            
            # Display filtered results
            st.dataframe(filtered_projects, use_container_width=True)
            
            # Export options
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Export to PDF", use_container_width=True):
                    filename = reports.export_projects_to_pdf(filtered_projects, "projects_report.pdf")
                    with open(filename, "rb") as f:
                        st.download_button("📥 Download PDF", f, file_name="projects_report.pdf", use_container_width=True)
            with col2:
                if st.button("📈 Export to Excel", use_container_width=True):
                    filename = reports.export_to_excel(filtered_projects, "projects_report.xlsx")
                    with open(filename, "rb") as f:
                        st.download_button("📥 Download Excel", f, file_name="projects_report.xlsx", use_container_width=True)
        else:
            st.info("No projects found")

elif menu == "🗓️ Meeting & MoM Log":
    st.markdown('<h1 class="main-header">Meeting & MoM Log</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["➕ Log New Meeting", "📋 All Meetings"])
    
    with tab1:
        with st.expander("Log New Meeting", expanded=True):
            with st.form("meeting_form"):
                projects = db.get_all_projects()
                project_options = projects[["id", "project_name"]].values.tolist()
                project_dict = {name: pid for pid, name in project_options}
                
                col1, col2 = st.columns(2)
                with col1:
                    project_name = st.selectbox("Project", list(project_dict.keys()))
                    meeting_date = st.date_input("Date")
                    attendees = st.text_input("Attendees", placeholder="Enter attendee names")
                
                with col2:
                    agenda = st.text_input("Agenda", placeholder="Enter meeting agenda")
                    follow_up_date = st.date_input("Follow-up Date")
                
                mom = st.text_area("Minutes of Meeting (MoM)", placeholder="Enter meeting minutes")
                next_steps = st.text_area("Next Steps", placeholder="Enter next steps")
                
                submitted = st.form_submit_button("📝 Log Meeting", use_container_width=True)
                
                if submitted:
                    db.add_meeting(
                        project_dict[project_name],
                        meeting_date.strftime('%Y-%m-%d'),
                        attendees, agenda, mom, next_steps,
                        follow_up_date.strftime('%Y-%m-%d')
                    )
                    st.success(f"✅ Meeting for '{project_name}' logged successfully!")
    
    with tab2:
        meetings = db.get_all_meetings()
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
                projects = db.get_all_projects()
                project_options = projects[["id", "project_name"]].values.tolist()
                project_dict = {name: pid for pid, name in project_options}
                
                col1, col2 = st.columns(2)
                with col1:
                    project_name = st.selectbox("Project", list(project_dict.keys()))
                    update_date = st.date_input("Date")
                    sent_by = st.text_input("Sent By", placeholder="Enter sender name")
                
                with col2:
                    mode = st.selectbox("Mode", ["Email", "Call", "Meeting", "Other"])
                
                summary = st.text_area("Summary", placeholder="Enter update summary")
                client_feedback = st.text_area("Client Feedback", placeholder="Enter client feedback")
                next_step = st.text_area("Next Step", placeholder="Enter next step")
                
                submitted = st.form_submit_button("📧 Log Update", use_container_width=True)
                
                if submitted:
                    db.add_client_update(
                        project_dict[project_name],
                        update_date.strftime('%Y-%m-%d'),
                        summary, sent_by, mode, client_feedback, next_step
                    )
                    st.success(f"✅ Update for '{project_name}' logged successfully!")
    
    with tab2:
        updates = pd.DataFrame()
        if not projects.empty:
            updates = pd.concat([
                db.get_client_updates_by_project(pid) for pid in projects['id'].tolist()
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
                projects = db.get_all_projects()
                project_options = projects[["id", "project_name"]].values.tolist()
                project_dict = {name: pid for pid, name in project_options}
                
                col1, col2 = st.columns(2)
                with col1:
                    project_name = st.selectbox("Project", list(project_dict.keys()))
                    date_reported = st.date_input("Date Reported")
                    status = st.selectbox("Status", ["Pending", "Resolved"])
                
                with col2:
                    assigned_to = st.text_input("Assigned To", placeholder="Enter assignee name")
                    resolution_date = st.date_input("Resolution Date", value=datetime.today())
                
                issue_description = st.text_area("Issue Description", placeholder="Enter detailed issue description")
                
                submitted = st.form_submit_button("🚨 Log Issue", use_container_width=True)
                
                if submitted:
                    db.add_issue(
                        project_dict[project_name],
                        date_reported.strftime('%Y-%m-%d'),
                        issue_description, status, assigned_to,
                        resolution_date.strftime('%Y-%m-%d') if status == "Resolved" else None
                    )
                    st.success(f"✅ Issue for '{project_name}' logged successfully!")
    
    with tab2:
        issues = db.get_all_issues()
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
            response = chatbot.process_query(user_input)
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
        
        if st.button("📊 Show All Projects", use_container_width=True):
            response = chatbot.process_query("Show all projects")
            st.session_state['chat_history'].append(("Show all projects", response))
            st.rerun()
        
        if st.button("📅 Recent Meetings", use_container_width=True):
            response = chatbot.process_query("Show last meetings")
            st.session_state['chat_history'].append(("Show last meetings", response))
            st.rerun()
        
        if st.button("🚨 Pending Issues", use_container_width=True):
            response = chatbot.process_query("What issues are unresolved?")
            st.session_state['chat_history'].append(("What issues are unresolved?", response))
            st.rerun()
        
        if st.button("📧 Latest Updates", use_container_width=True):
            response = chatbot.process_query("Show recent client updates")
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
        
        if st.button("🆘 Show Help", use_container_width=True):
            help_msg = chatbot._get_help_message()
            st.session_state['chat_history'].append(("Show help", help_msg))
            st.rerun()

elif menu == "📈 Analytics":
    st.markdown('<h1 class="main-header">Analytics & Insights</h1>', unsafe_allow_html=True)
    
    # Get data
    projects = db.get_all_projects()
    meetings = db.get_all_meetings()
    issues = db.get_all_issues()
    
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