#!/usr/bin/env python3
"""
Email Integration Module for ProjectOps
Connects to Outlook via Microsoft Graph API to read emails and extract project-related content
"""

import streamlit as st
import requests
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import os
import time

class OutlookEmailIntegration:
    def __init__(self):
        """Initialize Outlook email integration"""
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.access_token = None
        self.refresh_token = None
        self.client_id = None
        self.client_secret = None
        self.tenant_id = None
        self.user_email = None
        
        # Load configuration from Streamlit secrets
        self._load_config()
    
    def _load_config(self):
        """Load Microsoft Graph API configuration from secrets"""
        try:
            secrets = st.secrets
            self.client_id = secrets.get("MS_GRAPH_CLIENT_ID")
            self.client_secret = secrets.get("MS_GRAPH_CLIENT_SECRET")
            self.tenant_id = secrets.get("MS_GRAPH_TENANT_ID")
            self.user_email = secrets.get("MS_GRAPH_USER_EMAIL")
            
            # Check if we have stored tokens
            if 'email_access_token' in st.session_state:
                self.access_token = st.session_state.email_access_token
            if 'email_refresh_token' in st.session_state:
                self.refresh_token = st.session_state.email_refresh_token
                
            st.write("Client ID:", self.client_id)
            st.write("Tenant ID:", self.tenant_id)
            
        except Exception as e:
            st.error(f"Error loading email configuration: {e}")
    
    def get_auth_url(self) -> str:
        """Generate Microsoft Graph OAuth URL"""
        if not all([self.client_id, self.tenant_id]):
            return None
            
        redirect_uri = "http://localhost:8501"  # Streamlit default
        scope = "https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/User.Read"
        
        auth_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"
        auth_url += f"?client_id={self.client_id}"
        auth_url += f"&response_type=code"
        auth_url += f"&redirect_uri={redirect_uri}"
        auth_url += f"&scope={scope}"
        auth_url += "&response_mode=query"
        
        return auth_url
    
    def exchange_code_for_token(self, auth_code: str) -> bool:
        """Exchange authorization code for access token"""
        try:
            token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': auth_code,
                'redirect_uri': 'http://localhost:8501',
                'grant_type': 'authorization_code'
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.refresh_token = token_data['refresh_token']
            
            # Store tokens in session state
            st.session_state.email_access_token = self.access_token
            st.session_state.email_refresh_token = self.refresh_token
            
            return True
            
        except Exception as e:
            st.error(f"Error exchanging code for token: {e}")
            return False
    
    def refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token"""
        try:
            if not self.refresh_token:
                return False
                
            token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            
            # Update session state
            st.session_state.email_access_token = self.access_token
            
            return True
            
        except Exception as e:
            st.error(f"Error refreshing token: {e}")
            return False
    
    def _make_api_request(self, endpoint: str, method: str = 'GET', data: dict = None) -> Optional[dict]:
        """Make authenticated request to Microsoft Graph API"""
        if not self.access_token:
            return None
            
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            else:
                return None
                
            if response.status_code == 401:
                # Token expired, try to refresh
                if self.refresh_access_token():
                    headers['Authorization'] = f'Bearer {self.access_token}'
                    response = requests.get(url, headers=headers)
                else:
                    return None
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            st.error(f"API request error: {e}")
            return None
    
    def get_emails(self, days_back: int = 7, max_emails: int = 50) -> List[Dict]:
        """Get emails from the last N days"""
        if not self.access_token:
            return []
        
        # Calculate date filter
        filter_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        endpoint = f"/users/{self.user_email}/messages"
        endpoint += f"?$filter=receivedDateTime ge {filter_date}"
        endpoint += f"&$orderby=receivedDateTime desc"
        endpoint += f"&$top={max_emails}"
        endpoint += "&$select=id,subject,from,receivedDateTime,body,hasAttachments,importance"
        
        result = self._make_api_request(endpoint)
        
        if not result or 'value' not in result:
            return []
        
        emails = []
        for email in result['value']:
            email_data = {
                'id': email['id'],
                'subject': email['subject'],
                'from': email['from']['emailAddress']['address'],
                'from_name': email['from']['emailAddress']['name'],
                'received_date': email['receivedDateTime'],
                'body': email['body']['content'],
                'has_attachments': email['hasAttachments'],
                'importance': email['importance']
            }
            emails.append(email_data)
        
        return emails
    
    def classify_email_content(self, email: Dict) -> Dict:
        """Classify email content to determine if it's project-related and what type"""
        subject = email['subject'].lower()
        body = email['body'].lower()
        from_email = email['from'].lower()
        
        # Keywords for different types of project communications
        issue_keywords = ['bug', 'error', 'problem', 'issue', 'broken', 'not working', 'failed', 'crash', 'defect']
        query_keywords = ['question', 'query', 'help', 'support', 'how to', 'what is', 'clarification', 'advice']
        update_keywords = ['update', 'progress', 'status', 'milestone', 'completed', 'finished', 'delivered', 'review']
        meeting_keywords = ['meeting', 'call', 'discussion', 'agenda', 'schedule', 'appointment']
        
        # Check if email is from a client (external domain)
        is_client_email = not any(domain in from_email for domain in ['@yourcompany.com', '@internal.com'])
        
        # Determine email type
        email_type = 'general'
        confidence = 0.0
        
        if any(keyword in subject or keyword in body for keyword in issue_keywords):
            email_type = 'issue'
            confidence = 0.8
        elif any(keyword in subject or keyword in body for keyword in query_keywords):
            email_type = 'query'
            confidence = 0.7
        elif any(keyword in subject or keyword in body for keyword in update_keywords):
            email_type = 'update'
            confidence = 0.6
        elif any(keyword in subject or keyword in body for keyword in meeting_keywords):
            email_type = 'meeting'
            confidence = 0.5
        
        # Extract potential project name from subject or body
        project_name = self._extract_project_name(subject, body)
        
        # Extract client name from email
        client_name = self._extract_client_name(from_email, email['from_name'])
        
        return {
            'email_type': email_type,
            'confidence': confidence,
            'is_client_email': is_client_email,
            'project_name': project_name,
            'client_name': client_name,
            'priority': email['importance']
        }
    
    def _extract_project_name(self, subject: str, body: str) -> str:
        """Extract potential project name from email content"""
        # Common project name patterns
        patterns = [
            r'project[:\s]+([A-Za-z0-9\s\-_]+)',
            r'\[([A-Za-z0-9\s\-_]+)\]',
            r'\(([A-Za-z0-9\s\-_]+)\)',
            r're: ([A-Za-z0-9\s\-_]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_client_name(self, email: str, name: str) -> str:
        """Extract client name from email address or sender name"""
        if name and name != email:
            return name
        
        # Extract from email domain
        domain = email.split('@')[1] if '@' in email else ""
        if domain:
            return domain.split('.')[0].title()
        
        return "Unknown Client"
    
    def process_emails_for_projects(self, db, user_id: int = None) -> Dict:
        """Process emails and store relevant content in database"""
        emails = self.get_emails(days_back=7, max_emails=100)
        
        if not emails:
            return {'processed': 0, 'issues': 0, 'updates': 0, 'queries': 0}
        
        processed_count = 0
        issues_count = 0
        updates_count = 0
        queries_count = 0
        
        for email in emails:
            classification = self.classify_email_content(email)
            
            # Only process client emails with reasonable confidence
            if not classification['is_client_email'] or classification['confidence'] < 0.3:
                continue
            
            processed_count += 1
            
            # Find or create project
            project_id = self._find_or_create_project(db, classification['project_name'], 
                                                    classification['client_name'], user_id)
            
            if not project_id:
                continue
            
            # Store based on email type
            if classification['email_type'] == 'issue':
                self._store_as_issue(db, email, classification, project_id, user_id)
                issues_count += 1
            elif classification['email_type'] == 'update':
                self._store_as_client_update(db, email, classification, project_id, user_id)
                updates_count += 1
            elif classification['email_type'] == 'query':
                self._store_as_client_update(db, email, classification, project_id, user_id)
                queries_count += 1
        
        return {
            'processed': processed_count,
            'issues': issues_count,
            'updates': updates_count,
            'queries': queries_count
        }
    
    def _find_or_create_project(self, db, project_name: str, client_name: str, user_id: int) -> Optional[int]:
        """Find existing project or create new one"""
        if not project_name:
            return None
        
        # Try to find existing project
        projects_df = db.get_all_projects(user_id)
        if not projects_df.empty:
            matching_projects = projects_df[
                (projects_df['project_name'].str.contains(project_name, case=False, na=False)) |
                (projects_df['client_name'].str.contains(client_name, case=False, na=False))
            ]
            
            if not matching_projects.empty:
                return int(matching_projects.iloc[0]['id'])
        
        # Create new project if not found
        success = db.add_project(
            project_name=project_name,
            client_name=client_name,
            software="Unknown",
            vendor="Unknown",
            start_date=datetime.now().strftime('%Y-%m-%d'),
            deadline="",
            status="In Progress",
            description=f"Auto-created from email integration",
            user_id=user_id
        )
        
        if success:
            # Get the newly created project ID
            projects_df = db.get_all_projects(user_id)
            if not projects_df.empty:
                return int(projects_df.iloc[0]['id'])
        
        return None
    
    def _store_as_issue(self, db, email: Dict, classification: Dict, project_id: int, user_id: int):
        """Store email as an issue"""
        description = f"Email Subject: {email['subject']}\n\nFrom: {email['from']}\n\nContent:\n{email['body'][:1000]}"
        
        db.add_issue(
            project_id=project_id,
            date_reported=datetime.now().strftime('%Y-%m-%d'),
            description=description,
            status="New",
            assigned_to="Unassigned",
            user_id=user_id
        )
    
    def _store_as_client_update(self, db, email: Dict, classification: Dict, project_id: int, user_id: int):
        """Store email as a client update"""
        summary = f"Email from {email['from']}: {email['subject']}"
        
        db.add_client_update(
            project_id=project_id,
            update_date=datetime.now().strftime('%Y-%m-%d'),
            summary=summary,
            sent_by=email['from'],
            mode="Email",
            client_feedback=email['body'][:2000],
            next_step="Review and respond",
            user_id=user_id
        )
    
    def get_email_statistics(self) -> Dict:
        """Get email processing statistics"""
        emails = self.get_emails(days_back=30, max_emails=200)
        
        if not emails:
            return {'total': 0, 'client_emails': 0, 'by_type': {}}
        
        client_emails = [e for e in emails if self.classify_email_content(e)['is_client_email']]
        
        type_counts = {}
        for email in client_emails:
            classification = self.classify_email_content(email)
            email_type = classification['email_type']
            type_counts[email_type] = type_counts.get(email_type, 0) + 1
        
        return {
            'total': len(emails),
            'client_emails': len(client_emails),
            'by_type': type_counts
        } 