import streamlit as st
import pandas as pd
from database_postgres import ProjectOpsDatabase
from neon_auth import auth

st.set_page_config(page_title="Project Details", page_icon="🔍", layout="wide")

db = ProjectOpsDatabase()

# Authentication
current_user = auth.get_current_user()
if not current_user:
    st.error("You must be logged in to view this page.")
    st.stop()

# Get project_id from query params
query_params = st.query_params if hasattr(st, 'query_params') else st.experimental_get_query_params()
project_id = query_params.get('project_id', [None])[0]
if not project_id:
    st.error("No project selected.")
    st.stop()

try:
    project_id = int(project_id)
except Exception:
    st.error("Invalid project ID.")
    st.stop()

project = db.get_project_by_id(project_id)
if not project:
    st.error("Project not found.")
    st.stop()

meetings = db.get_all_meetings(current_user['id'])
updates = db.get_client_updates_by_project(project_id, current_user['id'])
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
    project_meetings = meetings[meetings['project_id'] == project_id]
else:
    project_meetings = pd.DataFrame()
if not project_meetings.empty:
    for idx, meeting in project_meetings.iterrows():
        with st.expander(f"{meeting['meeting_date']} - {meeting['agenda']}"):
            st.markdown(f"**Attendees:** {meeting['attendees']}")
            st.markdown(f"**Minutes of Meeting:**\n{meeting['mom']}")
            st.markdown(f"**Next Steps:** {meeting['next_steps']}")
            st.markdown(f"**Follow-up Date:** {meeting['follow_up_date']}")
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
with st.expander("➕ Add New Meeting", expanded=False):
    with st.form(f"add_meeting_form_{project_id}"):
        meeting_date = st.date_input("Meeting Date")
        attendees = st.text_input("Attendees")
        agenda = st.text_input("Agenda")
        mom = st.text_area("Minutes of Meeting (MoM)")
        next_steps = st.text_area("Next Steps")
        follow_up_date = st.date_input("Follow-up Date")
        submitted = st.form_submit_button("Add Meeting")
        if submitted:
            db.add_meeting(project_id, meeting_date.strftime('%Y-%m-%d'), attendees, agenda, mom, next_steps, follow_up_date.strftime('%Y-%m-%d'), current_user['id'])
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
with st.expander("➕ Add New Update/Log", expanded=False):
    with st.form(f"add_update_form_{project_id}"):
        update_date = st.date_input("Update Date")
        summary = st.text_area("Summary")
        sent_by = st.text_input("Sent By", value=current_user['full_name'])
        mode = st.selectbox("Mode", ["Email", "Call", "Meeting", "Other"])
        client_feedback = st.text_area("Client Feedback")
        next_step = st.text_area("Next Step")
        submitted = st.form_submit_button("Add Update")
        if submitted:
            db.add_client_update(project_id, update_date.strftime('%Y-%m-%d'), summary, sent_by, mode, client_feedback, next_step, current_user['id'])
            st.success("Update added!")
            st.rerun()
st.markdown("---")

# Issues/Queries
st.markdown("### 🐞 Issues / Queries")
if not issues.empty:
    project_issues = issues[issues['project_id'] == project_id]
else:
    project_issues = pd.DataFrame()
if not project_issues.empty:
    for idx, issue in project_issues.iterrows():
        with st.expander(f"{issue['date_reported']} - {issue['description'][:40]}"):
            st.markdown(f"**Status:** {issue['status']}")
            st.markdown(f"**Assigned To:** {issue['assigned_to']}")
            st.markdown(f"**Resolution Date:** {issue['resolution_date']}")
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
with st.expander("➕ Add New Issue/Query", expanded=False):
    with st.form(f"add_issue_form_{project_id}"):
        date_reported = st.date_input("Date Reported")
        description = st.text_area("Description")
        status = st.selectbox("Status", ["Pending", "In Progress", "Resolved"])
        assigned_to = st.text_input("Assigned To")
        resolution_date = st.date_input("Resolution Date")
        submitted = st.form_submit_button("Add Issue")
        if submitted:
            db.add_issue(project_id, date_reported.strftime('%Y-%m-%d'), description, status, assigned_to, resolution_date.strftime('%Y-%m-%d'), current_user['id'])
            st.success("Issue added!")
            st.rerun()
st.markdown("---")

# Back button
st.page_link("streamlit_app.py", label="⬅️ Back to Project Tracker", icon=" 190") 