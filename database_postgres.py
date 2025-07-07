import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import streamlit as st
from datetime import datetime
import os

Base = declarative_base()

class ProjectOpsDatabase:
    def __init__(self, connection_string=None):
        """Initialize PostgreSQL database connection"""
        if connection_string is None:
            # Try to get from Streamlit secrets, fallback to environment variable
            try:
                connection_string = st.secrets["DB_URL"]
            except:
                connection_string = os.getenv("DB_URL", "sqlite:///projectops.db")
        
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)
        self.metadata = MetaData()
        
        # Create tables if they don't exist
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        try:
            # Projects table
            projects_table = Table('projects', self.metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('project_name', String(255), nullable=False),
                Column('client_name', String(255), nullable=False),
                Column('software', String(100), nullable=False),
                Column('vendor', String(255)),
                Column('start_date', String(20)),
                Column('deadline', String(20)),
                Column('status', String(50), default='In Progress'),
                Column('description', Text),
                Column('file_path', String(500)),
                Column('user_id', Integer)
            )
            
            # Meetings table
            meetings_table = Table('meetings', self.metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('project_id', Integer, nullable=False),
                Column('meeting_date', String(20), nullable=False),
                Column('attendees', String(500)),
                Column('agenda', String(500)),
                Column('mom', Text),
                Column('next_steps', Text),
                Column('follow_up_date', String(20)),
                Column('user_id', Integer)
            )
            
            # Client updates table
            client_updates_table = Table('client_updates', self.metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('project_id', Integer, nullable=False),
                Column('update_date', String(20), nullable=False),
                Column('summary', Text),
                Column('sent_by', String(255)),
                Column('mode', String(50)),
                Column('client_feedback', Text),
                Column('next_step', Text),
                Column('user_id', Integer)
            )
            
            # Issues table
            issues_table = Table('issues', self.metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('project_id', Integer, nullable=False),
                Column('date_reported', String(20), nullable=False),
                Column('description', Text),
                Column('status', String(50), default='Pending'),
                Column('assigned_to', String(255)),
                Column('resolution_date', String(20)),
                Column('user_id', Integer)
            )
            
            # Create all tables
            self.metadata.create_all(self.engine)
            
        except Exception as e:
            st.error(f"Error creating tables: {e}")
    
    def add_project(self, project_name, client_name, software, vendor, start_date, deadline, status, description, file_path=None, user_id=None):
        """Add a new project"""
        try:
            with self.engine.connect() as conn:
                query = text("""
                    INSERT INTO projects (project_name, client_name, software, vendor, start_date, deadline, status, description, file_path, user_id)
                    VALUES (:project_name, :client_name, :software, :vendor, :start_date, :deadline, :status, :description, :file_path, :user_id)
                """)
                conn.execute(query, {
                    'project_name': project_name,
                    'client_name': client_name,
                    'software': software,
                    'vendor': vendor,
                    'start_date': start_date,
                    'deadline': deadline,
                    'status': status,
                    'description': description,
                    'file_path': file_path,
                    'user_id': user_id
                })
                conn.commit()
                return True
        except Exception as e:
            st.error(f"Error adding project: {e}")
            return False
    
    def get_all_projects(self, user_id=None):
        """Get all projects (optionally filtered by user)"""
        try:
            if user_id:
                query = text("SELECT * FROM projects WHERE user_id = :user_id ORDER BY id DESC")
                with self.engine.connect() as conn:
                    result = conn.execute(query, {'user_id': user_id})
                    rows = result.fetchall()
                    if rows:
                        columns = ['id', 'project_name', 'client_name', 'software', 'vendor', 'start_date', 'deadline', 'status', 'description', 'file_path', 'user_id']
                        return pd.DataFrame(rows, columns=columns)
                    return pd.DataFrame()
            else:
                query = text("SELECT * FROM projects ORDER BY id DESC")
                with self.engine.connect() as conn:
                    result = conn.execute(query)
                    rows = result.fetchall()
                    if rows:
                        columns = ['id', 'project_name', 'client_name', 'software', 'vendor', 'start_date', 'deadline', 'status', 'description', 'file_path', 'user_id']
                        return pd.DataFrame(rows, columns=columns)
                    return pd.DataFrame()
        except Exception as e:
            st.error(f"Error getting projects: {e}")
            return pd.DataFrame()
    
    def add_meeting(self, project_id, meeting_date, attendees, agenda, mom, next_steps, follow_up_date, user_id=None):
        """Add a new meeting"""
        try:
            with self.engine.connect() as conn:
                query = text("""
                    INSERT INTO meetings (project_id, meeting_date, attendees, agenda, mom, next_steps, follow_up_date, user_id)
                    VALUES (:project_id, :meeting_date, :attendees, :agenda, :mom, :next_steps, :follow_up_date, :user_id)
                """)
                conn.execute(query, {
                    'project_id': project_id,
                    'meeting_date': meeting_date,
                    'attendees': attendees,
                    'agenda': agenda,
                    'mom': mom,
                    'next_steps': next_steps,
                    'follow_up_date': follow_up_date,
                    'user_id': user_id
                })
                conn.commit()
                return True
        except Exception as e:
            st.error(f"Error adding meeting: {e}")
            return False
    
    def get_all_meetings(self, user_id=None):
        """Get all meetings with project names (optionally filtered by user)"""
        try:
            if user_id:
                query = text("""
                    SELECT m.*, p.project_name 
                    FROM meetings m 
                    JOIN projects p ON m.project_id = p.id 
                    WHERE m.user_id = :user_id
                    ORDER BY m.meeting_date DESC
                """)
                with self.engine.connect() as conn:
                    result = conn.execute(query, {'user_id': user_id})
                    rows = result.fetchall()
                    if rows:
                        columns = ['id', 'project_id', 'meeting_date', 'attendees', 'agenda', 'mom', 'next_steps', 'follow_up_date', 'user_id', 'project_name']
                        return pd.DataFrame(rows, columns=columns)
                    return pd.DataFrame()
            else:
                query = text("""
                    SELECT m.*, p.project_name 
                    FROM meetings m 
                    JOIN projects p ON m.project_id = p.id 
                    ORDER BY m.meeting_date DESC
                """)
                with self.engine.connect() as conn:
                    result = conn.execute(query)
                    rows = result.fetchall()
                    if rows:
                        columns = ['id', 'project_id', 'meeting_date', 'attendees', 'agenda', 'mom', 'next_steps', 'follow_up_date', 'user_id', 'project_name']
                        return pd.DataFrame(rows, columns=columns)
                    return pd.DataFrame()
        except Exception as e:
            st.error(f"Error getting meetings: {e}")
            return pd.DataFrame()
    
    def add_client_update(self, project_id, update_date, summary, sent_by, mode, client_feedback, next_step, user_id=None):
        """Add a new client update"""
        try:
            with self.engine.connect() as conn:
                query = text("""
                    INSERT INTO client_updates (project_id, update_date, summary, sent_by, mode, client_feedback, next_step, user_id)
                    VALUES (:project_id, :update_date, :summary, :sent_by, :mode, :client_feedback, :next_step, :user_id)
                """)
                conn.execute(query, {
                    'project_id': project_id,
                    'update_date': update_date,
                    'summary': summary,
                    'sent_by': sent_by,
                    'mode': mode,
                    'client_feedback': client_feedback,
                    'next_step': next_step,
                    'user_id': user_id
                })
                conn.commit()
                return True
        except Exception as e:
            st.error(f"Error adding client update: {e}")
            return False
    
    def get_client_updates_by_project(self, project_id, user_id=None):
        """Get client updates for a specific project"""
        try:
            if user_id:
                query = text("""
                    SELECT cu.*, p.project_name 
                    FROM client_updates cu 
                    JOIN projects p ON cu.project_id = p.id 
                    WHERE cu.project_id = :project_id AND cu.user_id = :user_id
                    ORDER BY cu.update_date DESC
                """)
                with self.engine.connect() as conn:
                    result = conn.execute(query, {'project_id': project_id, 'user_id': user_id})
                    rows = result.fetchall()
                    if rows:
                        columns = ['id', 'project_id', 'update_date', 'summary', 'sent_by', 'mode', 'client_feedback', 'next_step', 'user_id', 'project_name']
                        return pd.DataFrame(rows, columns=columns)
                    return pd.DataFrame()
            else:
                query = text("""
                    SELECT cu.*, p.project_name 
                    FROM client_updates cu 
                    JOIN projects p ON cu.project_id = p.id 
                    WHERE cu.project_id = :project_id 
                    ORDER BY cu.update_date DESC
                """)
                with self.engine.connect() as conn:
                    result = conn.execute(query, {'project_id': project_id})
                    rows = result.fetchall()
                    if rows:
                        columns = ['id', 'project_id', 'update_date', 'summary', 'sent_by', 'mode', 'client_feedback', 'next_step', 'user_id', 'project_name']
                        return pd.DataFrame(rows, columns=columns)
                    return pd.DataFrame()
        except Exception as e:
            st.error(f"Error getting client updates: {e}")
            return pd.DataFrame()
    
    def add_issue(self, project_id, date_reported, description, status, assigned_to, resolution_date=None, user_id=None):
        """Add a new issue"""
        try:
            with self.engine.connect() as conn:
                query = text("""
                    INSERT INTO issues (project_id, date_reported, description, status, assigned_to, resolution_date, user_id)
                    VALUES (:project_id, :date_reported, :description, :status, :assigned_to, :resolution_date, :user_id)
                """)
                conn.execute(query, {
                    'project_id': project_id,
                    'date_reported': date_reported,
                    'description': description,
                    'status': status,
                    'assigned_to': assigned_to,
                    'resolution_date': resolution_date,
                    'user_id': user_id
                })
                conn.commit()
                return True
        except Exception as e:
            st.error(f"Error adding issue: {e}")
            return False
    
    def get_all_issues(self, user_id=None):
        """Get all issues with project names (optionally filtered by user)"""
        try:
            if user_id:
                query = text("""
                    SELECT i.*, p.project_name 
                    FROM issues i 
                    JOIN projects p ON i.project_id = p.id 
                    WHERE i.user_id = :user_id
                    ORDER BY i.date_reported DESC
                """)
                with self.engine.connect() as conn:
                    result = conn.execute(query, {'user_id': user_id})
                    rows = result.fetchall()
                    if rows:
                        columns = ['id', 'project_id', 'date_reported', 'description', 'status', 'assigned_to', 'resolution_date', 'user_id', 'project_name']
                        return pd.DataFrame(rows, columns=columns)
                    return pd.DataFrame()
            else:
                query = text("""
                    SELECT i.*, p.project_name 
                    FROM issues i 
                    JOIN projects p ON i.project_id = p.id 
                    ORDER BY i.date_reported DESC
                """)
                with self.engine.connect() as conn:
                    result = conn.execute(query)
                    rows = result.fetchall()
                    if rows:
                        columns = ['id', 'project_id', 'date_reported', 'description', 'status', 'assigned_to', 'resolution_date', 'user_id', 'project_name']
                        return pd.DataFrame(rows, columns=columns)
                    return pd.DataFrame()
        except Exception as e:
            st.error(f"Error getting issues: {e}")
            return pd.DataFrame()
    
    def search_projects(self, search_term):
        """Search projects by name or client"""
        try:
            query = text("""
                SELECT * FROM projects 
                WHERE project_name ILIKE :search_term OR client_name ILIKE :search_term
                ORDER BY id DESC
            """)
            with self.engine.connect() as conn:
                result = conn.execute(query, {'search_term': f'%{search_term}%'})
                rows = result.fetchall()
                if rows:
                    columns = ['id', 'project_name', 'client_name', 'software', 'vendor', 'start_date', 'deadline', 'status', 'description', 'file_path', 'user_id']
                    return pd.DataFrame(rows, columns=columns)
                return pd.DataFrame()
        except Exception as e:
            st.error(f"Error searching projects: {e}")
            return pd.DataFrame()
    
    def delete_project(self, project_id):
        """Delete a project and all related data"""
        try:
            with self.engine.connect() as conn:
                # Delete related records first (foreign key constraints)
                # Delete issues
                delete_issues = text("DELETE FROM issues WHERE project_id = :project_id")
                conn.execute(delete_issues, {'project_id': project_id})
                
                # Delete client updates
                delete_updates = text("DELETE FROM client_updates WHERE project_id = :project_id")
                conn.execute(delete_updates, {'project_id': project_id})
                
                # Delete meetings
                delete_meetings = text("DELETE FROM meetings WHERE project_id = :project_id")
                conn.execute(delete_meetings, {'project_id': project_id})
                
                # Delete the project
                delete_project = text("DELETE FROM projects WHERE id = :project_id")
                result = conn.execute(delete_project, {'project_id': project_id})
                conn.commit()
                
                return result.rowcount > 0
        except Exception as e:
            st.error(f"Error deleting project: {e}")
            return False
    
    def get_project_by_id(self, project_id):
        """Get a specific project by ID"""
        try:
            query = text("SELECT * FROM projects WHERE id = :project_id")
            with self.engine.connect() as conn:
                result = conn.execute(query, {'project_id': project_id})
                row = result.fetchone()
                if row:
                    columns = ['id', 'project_name', 'client_name', 'software', 'vendor', 'start_date', 'deadline', 'status', 'description', 'file_path']
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            st.error(f"Error getting project: {e}")
            return None
    
    def get_project_summary(self, project_id):
        """Get comprehensive project summary (PostgreSQL version)"""
        try:
            # Ensure project_id is a native Python int
            project_id = int(project_id)
            with self.engine.connect() as conn:
                # Get project details
                project = pd.read_sql_query("SELECT * FROM projects WHERE id = %s", conn, params=(project_id,))
                # Get meetings count
                meetings_count = pd.read_sql_query("SELECT COUNT(*) as count FROM meetings WHERE project_id = %s", conn, params=(project_id,))
                # Get issues count
                issues_count = pd.read_sql_query("SELECT COUNT(*) as count FROM issues WHERE project_id = %s", conn, params=(project_id,))
                # Get pending issues count
                pending_issues = pd.read_sql_query("SELECT COUNT(*) as count FROM issues WHERE project_id = %s AND status = 'Pending'", conn, params=(project_id,))
                # Get recent updates
                recent_updates = pd.read_sql_query("""
                    SELECT * FROM client_updates 
                    WHERE project_id = %s 
                    ORDER BY update_date DESC 
                    LIMIT 5
                """, conn, params=(project_id,))
                return {
                    'project': project,
                    'meetings_count': meetings_count.iloc[0]['count'],
                    'issues_count': issues_count.iloc[0]['count'],
                    'pending_issues': pending_issues.iloc[0]['count'],
                    'recent_updates': recent_updates
                }
        except Exception as e:
            st.error(f"Error getting project summary: {e}")
            return None 