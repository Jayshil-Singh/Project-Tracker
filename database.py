import sqlite3
import os
from datetime import datetime
import pandas as pd

class ProjectOpsDatabase:
    def __init__(self, db_path="projectops.db"):
        self.db_path = db_path
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize the database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                client_name TEXT NOT NULL,
                software TEXT,
                vendor TEXT,
                start_date TEXT,
                deadline TEXT,
                status TEXT DEFAULT 'In Progress',
                description TEXT,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Meetings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                meeting_date TEXT NOT NULL,
                attendees TEXT,
                agenda TEXT,
                mom TEXT,
                next_steps TEXT,
                follow_up_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        # Client updates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS client_updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                update_date TEXT NOT NULL,
                summary TEXT,
                sent_by TEXT,
                mode TEXT,
                client_feedback TEXT,
                next_step TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        # Issues table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                date_reported TEXT NOT NULL,
                issue_description TEXT,
                status TEXT DEFAULT 'Pending',
                assigned_to TEXT,
                resolution_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_project(self, project_name, client_name, software, vendor, start_date, deadline, status, description, file_path=None):
        """Add a new project with optional file_path"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO projects (project_name, client_name, software, vendor, start_date, deadline, status, description, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (project_name, client_name, software, vendor, start_date, deadline, status, description, file_path))
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return project_id
    
    def get_all_projects(self):
        """Get all projects"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM projects ORDER BY created_at DESC", conn)
        conn.close()
        return df
    
    def get_project_by_id(self, project_id):
        """Get project by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        project = cursor.fetchone()
        conn.close()
        return project
    
    def add_meeting(self, project_id, meeting_date, attendees, agenda, mom, next_steps, follow_up_date):
        """Add a new meeting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO meetings (project_id, meeting_date, attendees, agenda, mom, next_steps, follow_up_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, meeting_date, attendees, agenda, mom, next_steps, follow_up_date))
        
        meeting_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return meeting_id
    
    def get_meetings_by_project(self, project_id):
        """Get meetings for a specific project"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("""
            SELECT m.*, p.project_name, p.client_name 
            FROM meetings m 
            JOIN projects p ON m.project_id = p.id 
            WHERE m.project_id = ? 
            ORDER BY m.meeting_date DESC
        """, conn, params=(project_id,))
        conn.close()
        return df
    
    def get_all_meetings(self):
        """Get all meetings"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("""
            SELECT m.*, p.project_name, p.client_name 
            FROM meetings m 
            JOIN projects p ON m.project_id = p.id 
            ORDER BY m.meeting_date DESC
        """, conn)
        conn.close()
        return df
    
    def add_client_update(self, project_id, update_date, summary, sent_by, mode, client_feedback, next_step):
        """Add a new client update"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO client_updates (project_id, update_date, summary, sent_by, mode, client_feedback, next_step)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, update_date, summary, sent_by, mode, client_feedback, next_step))
        
        update_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return update_id
    
    def get_client_updates_by_project(self, project_id):
        """Get client updates for a specific project"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("""
            SELECT cu.*, p.project_name, p.client_name 
            FROM client_updates cu 
            JOIN projects p ON cu.project_id = p.id 
            WHERE cu.project_id = ? 
            ORDER BY cu.update_date DESC
        """, conn, params=(project_id,))
        conn.close()
        return df
    
    def add_issue(self, project_id, date_reported, issue_description, status, assigned_to, resolution_date):
        """Add a new issue"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO issues (project_id, date_reported, issue_description, status, assigned_to, resolution_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (project_id, date_reported, issue_description, status, assigned_to, resolution_date))
        
        issue_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return issue_id
    
    def get_issues_by_project(self, project_id):
        """Get issues for a specific project"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("""
            SELECT i.*, p.project_name, p.client_name 
            FROM issues i 
            JOIN projects p ON i.project_id = p.id 
            WHERE i.project_id = ? 
            ORDER BY i.date_reported DESC
        """, conn, params=(project_id,))
        conn.close()
        return df
    
    def get_all_issues(self):
        """Get all issues"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("""
            SELECT i.*, p.project_name, p.client_name 
            FROM issues i 
            JOIN projects p ON i.project_id = p.id 
            ORDER BY i.date_reported DESC
        """, conn)
        conn.close()
        return df
    
    def search_projects(self, query):
        """Search projects by name, client, or description"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("""
            SELECT * FROM projects 
            WHERE project_name LIKE ? OR client_name LIKE ? OR description LIKE ?
            ORDER BY created_at DESC
        """, conn, params=(f'%{query}%', f'%{query}%', f'%{query}%'))
        conn.close()
        return df
    
    def get_project_summary(self, project_id):
        """Get comprehensive project summary"""
        conn = sqlite3.connect(self.db_path)
        
        # Get project details
        project = pd.read_sql_query("SELECT * FROM projects WHERE id = ?", conn, params=(project_id,))
        
        # Get meetings count
        meetings_count = pd.read_sql_query("SELECT COUNT(*) as count FROM meetings WHERE project_id = ?", conn, params=(project_id,))
        
        # Get issues count
        issues_count = pd.read_sql_query("SELECT COUNT(*) as count FROM issues WHERE project_id = ?", conn, params=(project_id,))
        
        # Get pending issues count
        pending_issues = pd.read_sql_query("SELECT COUNT(*) as count FROM issues WHERE project_id = ? AND status = 'Pending'", conn, params=(project_id,))
        
        # Get recent updates
        recent_updates = pd.read_sql_query("""
            SELECT * FROM client_updates 
            WHERE project_id = ? 
            ORDER BY update_date DESC 
            LIMIT 5
        """, conn, params=(project_id,))
        
        conn.close()
        
        return {
            'project': project,
            'meetings_count': meetings_count.iloc[0]['count'],
            'issues_count': issues_count.iloc[0]['count'],
            'pending_issues': pending_issues.iloc[0]['count'],
            'recent_updates': recent_updates
        } 