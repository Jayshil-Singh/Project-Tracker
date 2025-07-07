import re
from datetime import datetime, timedelta
import pandas as pd
from database_postgres import ProjectOpsDatabase

class ProjectOpsChatbot:
    def __init__(self, db):
        self.db = db
        
    def process_query(self, user_query, user_id=None):
        """Process user query and return appropriate response"""
        query = user_query.lower().strip()
        
        # Project status queries
        if any(word in query for word in ['status', 'progress', 'how is']):
            return self._handle_status_query(query, user_id)
        
        # Meeting queries
        elif any(word in query for word in ['meeting', 'mom', 'minutes']):
            return self._handle_meeting_query(query, user_id)
        
        # Issue queries
        elif any(word in query for word in ['issue', 'problem', 'bug', 'unresolved']):
            return self._handle_issue_query(query, user_id)
        
        # Client update queries
        elif any(word in query for word in ['update', 'communication', 'client']):
            return self._handle_update_query(query, user_id)
        
        # General project queries
        elif any(word in query for word in ['project', 'client']):
            return self._handle_project_query(query, user_id)
        
        # Help query
        elif 'help' in query:
            return self._get_help_message()
        
        else:
            return self._get_general_response(query)
    
    def _handle_status_query(self, query, user_id=None):
        """Handle project status queries"""
        # Extract project name or client name
        project_name = self._extract_project_name(query)
        
        if project_name:
            projects = self.db.search_projects(project_name)
            if not projects.empty:
                # Filter by user if specified
                if user_id:
                    projects = projects[projects['user_id'] == user_id]
                
                if not projects.empty:
                    project = projects.iloc[0]
                    summary = self.db.get_project_summary(project['id'])
                    
                    response = f"📊 **Project Status: {project['project_name']}**\n\n"
                    response += f"**Client:** {project['client_name']}\n"
                    response += f"**Status:** {project['status']}\n"
                    response += f"**Software:** {project['software']}\n"
                    response += f"**Vendor:** {project['vendor']}\n"
                    response += f"**Start Date:** {project['start_date']}\n"
                    response += f"**Deadline:** {project['deadline']}\n\n"
                    response += f"**Summary:**\n"
                    response += f"• Total Meetings: {summary['meetings_count']}\n"
                    response += f"• Total Issues: {summary['issues_count']}\n"
                    response += f"• Pending Issues: {summary['pending_issues']}\n"
                    
                    if not summary['recent_updates'].empty:
                        response += f"\n**Latest Update:**\n"
                        latest = summary['recent_updates'].iloc[0]
                        response += f"• {latest['summary']} (on {latest['update_date']})"
                    
                    return response
                else:
                    return f"❌ No project found matching '{project_name}' for your account."
            else:
                return f"❌ No project found matching '{project_name}'. Please check the project name."
        else:
            return "❓ Please specify which project you'd like to check the status for."
    
    def _handle_meeting_query(self, query, user_id=None):
        """Handle meeting-related queries"""
        project_name = self._extract_project_name(query)
        
        if 'this month' in query:
            # Get meetings from current month
            current_month = datetime.now().strftime('%Y-%m')
            meetings = self.db.get_all_meetings(user_id)
            if not meetings.empty:
                meetings['meeting_date'] = pd.to_datetime(meetings['meeting_date'])
                month_meetings = meetings[meetings['meeting_date'].dt.strftime('%Y-%m') == current_month]
                
                if not month_meetings.empty:
                    response = f"📅 **Meetings this month ({current_month}):**\n\n"
                    for _, meeting in month_meetings.iterrows():
                        response += f"• **{meeting['project_name']}** - {meeting['meeting_date'].strftime('%Y-%m-%d')}\n"
                        response += f"  Agenda: {meeting['agenda']}\n"
                        response += f"  Attendees: {meeting['attendees']}\n\n"
                    return response
                else:
                    return f"📅 No meetings scheduled for {current_month}."
            else:
                return "📅 No meetings found in the system."
        
        elif 'last' in query and 'meeting' in query:
            # Get last few meetings
            meetings = self.db.get_all_meetings(user_id)
            if not meetings.empty:
                response = "📅 **Recent Meetings:**\n\n"
                for i, (_, meeting) in enumerate(meetings.head(5).iterrows()):
                    response += f"• **{meeting['project_name']}** - {meeting['meeting_date']}\n"
                    response += f"  Agenda: {meeting['agenda']}\n"
                    response += f"  MoM: {meeting['mom'][:100]}...\n\n"
                return response
            else:
                return "📅 No meetings found in the system."
        
        elif project_name:
            # Get meetings for specific project
            projects = self.db.search_projects(project_name)
            if not projects.empty:
                # Filter by user if specified
                if user_id:
                    projects = projects[projects['user_id'] == user_id]
                
                if not projects.empty:
                    project = projects.iloc[0]
                    meetings = self.db.get_meetings_by_project(project['id'])
                    
                    if not meetings.empty:
                        response = f"📅 **Meetings for {project['project_name']}:**\n\n"
                        for _, meeting in meetings.iterrows():
                            response += f"• **{meeting['meeting_date']}**\n"
                            response += f"  Agenda: {meeting['agenda']}\n"
                            response += f"  Attendees: {meeting['attendees']}\n"
                            response += f"  MoM: {meeting['mom'][:150]}...\n"
                            response += f"  Next Steps: {meeting['next_steps']}\n\n"
                        return response
                    else:
                        return f"📅 No meetings found for {project['project_name']}."
                else:
                    return f"❌ No project found matching '{project_name}' for your account."
            else:
                return f"❌ No project found matching '{project_name}'."
        
        else:
            return "❓ Please specify which project's meetings you'd like to see, or ask for 'meetings this month' or 'last meetings'."
    
    def _handle_issue_query(self, query, user_id=None):
        """Handle issue-related queries"""
        project_name = self._extract_project_name(query)
        
        if 'unresolved' in query or 'pending' in query:
            issues = self.db.get_all_issues(user_id)
            if not issues.empty:
                pending_issues = issues[issues['status'] == 'Pending']
                
                if not pending_issues.empty:
                    response = "🚨 **Pending Issues:**\n\n"
                    for _, issue in pending_issues.iterrows():
                        response += f"• **{issue['project_name']}** - {issue['date_reported']}\n"
                        response += f"  Issue: {issue['issue_description']}\n"
                        response += f"  Assigned to: {issue['assigned_to']}\n\n"
                    return response
                else:
                    return "✅ No pending issues found."
            else:
                return "📋 No issues found in the system."
        
        elif project_name:
            # Get issues for specific project
            projects = self.db.search_projects(project_name)
            if not projects.empty:
                # Filter by user if specified
                if user_id:
                    projects = projects[projects['user_id'] == user_id]
                
                if not projects.empty:
                    project = projects.iloc[0]
                    issues = self.db.get_issues_by_project(project['id'])
                    
                    if not issues.empty:
                        response = f"🚨 **Issues for {project['project_name']}:**\n\n"
                        for _, issue in issues.iterrows():
                            status_emoji = "🟡" if issue['status'] == 'Pending' else "✅"
                            response += f"{status_emoji} **{issue['status']}** - {issue['date_reported']}\n"
                            response += f"  Issue: {issue['issue_description']}\n"
                            response += f"  Assigned to: {issue['assigned_to']}\n"
                            if issue['resolution_date']:
                                response += f"  Resolved: {issue['resolution_date']}\n"
                            response += "\n"
                        return response
                    else:
                        return f"📋 No issues found for {project['project_name']}."
                else:
                    return f"❌ No project found matching '{project_name}' for your account."
            else:
                return f"❌ No project found matching '{project_name}'."
        
        else:
            return "❓ Please specify which project's issues you'd like to see, or ask for 'unresolved issues'."
    
    def _handle_update_query(self, query, user_id=None):
        """Handle client update queries"""
        project_name = self._extract_project_name(query)
        
        if 'last' in query and 'update' in query:
            if project_name:
                projects = self.db.search_projects(project_name)
                if not projects.empty:
                    # Filter by user if specified
                    if user_id:
                        projects = projects[projects['user_id'] == user_id]
                    
                    if not projects.empty:
                        project = projects.iloc[0]
                        updates = self.db.get_client_updates_by_project(project['id'], user_id)
                        
                        if not updates.empty:
                            latest = updates.iloc[0]
                            response = f"📧 **Latest Update for {project['project_name']}:**\n\n"
                            response += f"**Date:** {latest['update_date']}\n"
                            response += f"**Summary:** {latest['summary']}\n"
                            response += f"**Sent by:** {latest['sent_by']}\n"
                            response += f"**Mode:** {latest['mode']}\n"
                            response += f"**Client Feedback:** {latest['client_feedback']}\n"
                            response += f"**Next Step:** {latest['next_step']}\n"
                            return response
                        else:
                            return f"📧 No updates found for {project['project_name']}."
                    else:
                        return f"❌ No project found matching '{project_name}' for your account."
                else:
                    return f"❌ No project found matching '{project_name}'."
            else:
                # Get recent updates for all projects
                projects = self.db.get_all_projects(user_id)
                if not projects.empty:
                    all_updates = []
                    for _, project in projects.iterrows():
                        updates = self.db.get_client_updates_by_project(project['id'], user_id)
                        if not updates.empty:
                            all_updates.extend(updates.to_dict('records'))
                    
                    if all_updates:
                        # Sort by date and get latest
                        all_updates.sort(key=lambda x: x['update_date'], reverse=True)
                        latest = all_updates[0]
                        
                        response = f"📧 **Latest Update:**\n\n"
                        response += f"**Project:** {latest['project_name']}\n"
                        response += f"**Date:** {latest['update_date']}\n"
                        response += f"**Summary:** {latest['summary']}\n"
                        response += f"**Sent by:** {latest['sent_by']}\n"
                        response += f"**Mode:** {latest['mode']}\n"
                        return response
                    else:
                        return "📧 No updates found in the system."
                else:
                    return "📧 No projects found in the system."
        
        elif project_name:
            # Get all updates for specific project
            projects = self.db.search_projects(project_name)
            if not projects.empty:
                # Filter by user if specified
                if user_id:
                    projects = projects[projects['user_id'] == user_id]
                
                if not projects.empty:
                    project = projects.iloc[0]
                    updates = self.db.get_client_updates_by_project(project['id'], user_id)
                    
                    if not updates.empty:
                        response = f"📧 **Updates for {project['project_name']}:**\n\n"
                        for _, update in updates.iterrows():
                            response += f"• **{update['update_date']}** - {update['mode']}\n"
                            response += f"  Summary: {update['summary']}\n"
                            response += f"  Sent by: {update['sent_by']}\n"
                            response += f"  Feedback: {update['client_feedback']}\n"
                            response += f"  Next Step: {update['next_step']}\n\n"
                        return response
                    else:
                        return f"📧 No updates found for {project['project_name']}."
                else:
                    return f"❌ No project found matching '{project_name}' for your account."
            else:
                return f"❌ No project found matching '{project_name}'."
        
        else:
            return "❓ Please specify which project's updates you'd like to see, or ask for 'last update'."
    
    def _handle_project_query(self, query, user_id=None):
        """Handle general project queries"""
        if 'all' in query and 'project' in query:
            projects = self.db.get_all_projects(user_id)
            if not projects.empty:
                response = "📋 **All Projects:**\n\n"
                for _, project in projects.iterrows():
                    status_emoji = {
                        'In Progress': '🟡',
                        'Completed': '✅',
                        'On Hold': '🔴'
                    }.get(project['status'], '⚪')
                    
                    response += f"{status_emoji} **{project['project_name']}**\n"
                    response += f"  Client: {project['client_name']}\n"
                    response += f"  Software: {project['software']}\n"
                    response += f"  Status: {project['status']}\n"
                    response += f"  Deadline: {project['deadline']}\n\n"
                return response
            else:
                return "📋 No projects found in the system."
        
        elif 'client' in query:
            # Extract client name and show their projects
            client_name = self._extract_project_name(query)
            if client_name:
                projects = self.db.search_projects(client_name)
                if not projects.empty:
                    # Filter by user if specified
                    if user_id:
                        projects = projects[projects['user_id'] == user_id]
                    
                    if not projects.empty:
                        response = f"📋 **Projects for {client_name}:**\n\n"
                        for _, project in projects.iterrows():
                            status_emoji = {
                                'In Progress': '🟡',
                                'Completed': '✅',
                                'On Hold': '🔴'
                            }.get(project['status'], '⚪')
                            
                            response += f"{status_emoji} **{project['project_name']}**\n"
                            response += f"  Software: {project['software']}\n"
                            response += f"  Status: {project['status']}\n"
                            response += f"  Deadline: {project['deadline']}\n\n"
                        return response
                    else:
                        return f"📋 No projects found for {client_name} in your account."
                else:
                    return f"📋 No projects found for {client_name}."
            else:
                return "❓ Please specify which client's projects you'd like to see."
        
        else:
            return "❓ Please specify what you'd like to know about projects. Try 'show all projects' or 'projects for [client name]'."
    
    def _extract_project_name(self, query):
        """Extract project or client name from query"""
        # Common patterns for project/client names
        patterns = [
            r'for\s+([A-Za-z0-9\s]+)',
            r'of\s+([A-Za-z0-9\s]+)',
            r'([A-Za-z0-9\s]+)\s+project',
            r'([A-Za-z0-9\s]+)\s+client'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _get_help_message(self):
        """Return help message with available commands"""
        return """
🤖 **ProjectOps Assistant - Help**

Here are some things you can ask me:

**📊 Project Status:**
- "What's the status of [project name]?"
- "How is [project name] progressing?"
- "Show status for [client name]"

**📅 Meetings:**
- "Show meetings for [project name]"
- "Meetings this month"
- "Last meetings"

**🚨 Issues:**
- "What issues are unresolved?"
- "Show issues for [project name]"
- "Pending issues"

**📧 Client Updates:**
- "Show recent client updates"
- "Last update for [project name]"
- "Updates for [client name]"

**📋 General:**
- "Show all projects"
- "Projects for [client name]"
- "Help"

Just ask me anything about your projects! 🚀
"""
    
    def _get_general_response(self, query):
        """Return a general response for unrecognized queries"""
        return f"I'm not sure how to help with '{query}'. Try asking about project status, meetings, issues, or updates. Type 'help' for more information! 🤖" 