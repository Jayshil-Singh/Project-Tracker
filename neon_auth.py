#!/usr/bin/env python3
"""
Neon Auth Integration for Project Tracker
Handles user authentication and session management
"""

import streamlit as st
import requests
import json
import hashlib
import secrets
from datetime import datetime, timedelta
import os
import pandas as pd
from sqlalchemy import text
from database_postgres import ProjectOpsDatabase
import random
import string
import smtplib
from email.mime.text import MIMEText

class NeonAuth:
    def __init__(self):
        """Initialize Neon Auth with configuration"""
        self.db = ProjectOpsDatabase()
        self._create_auth_tables()
        
        # Get Neon Auth configuration
        try:
            self.neon_project_id = st.secrets.get("NEON_PROJECT_ID")
            self.neon_api_key = st.secrets.get("NEON_API_KEY")
            self.auth_enabled = bool(self.neon_project_id and self.neon_api_key)
        except:
            self.auth_enabled = False
            st.warning("⚠️ Neon Auth not configured. Using local authentication.")
    
    def _create_auth_tables(self):
        """Create authentication-related tables"""
        try:
            with self.db.engine.connect() as conn:
                # Users table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        full_name VARCHAR(255),
                        role VARCHAR(50) DEFAULT 'user',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        must_change_password BOOLEAN DEFAULT FALSE
                    )
                """))
                
                # Audit logs table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id SERIAL PRIMARY KEY,
                        admin_id INTEGER,
                        admin_email VARCHAR(255),
                        action VARCHAR(100),
                        target_user_id INTEGER,
                        target_email VARCHAR(255),
                        details TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # User sessions table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        session_token VARCHAR(255) UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """))
                
                # Add user_id to existing tables for multi-tenancy
                conn.execute(text("""
                    ALTER TABLE projects ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)
                """))
                conn.execute(text("""
                    ALTER TABLE meetings ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)
                """))
                conn.execute(text("""
                    ALTER TABLE client_updates ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)
                """))
                conn.execute(text("""
                    ALTER TABLE issues ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)
                """))
                
                conn.commit()
        except Exception as e:
            st.error(f"Error creating auth tables: {e}")
    
    def _hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_session_token(self):
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
    
    def register_user(self, email, password, full_name, role='user'):
        """Admin-only registration"""
        try:
            with self.db.engine.connect() as conn:
                # Check if user already exists
                check_query = text("SELECT id FROM users WHERE email = :email")
                existing_user = conn.execute(check_query, {'email': email}).fetchone()
                if existing_user:
                    return False, "User already exists"
                password_hash = self._hash_password(password)
                insert_query = text("""
                    INSERT INTO users (email, password_hash, full_name, role, must_change_password)
                    VALUES (:email, :password_hash, :full_name, :role, FALSE)
                    RETURNING id
                """)
                result = conn.execute(insert_query, {
                    'email': email,
                    'password_hash': password_hash,
                    'full_name': full_name,
                    'role': role
                })
                user_id = result.fetchone()[0]
                conn.commit()
                return True, f"User registered successfully with ID: {user_id}"
        except Exception as e:
            return False, f"Registration failed: {e}"
    
    def login_user(self, email, password):
        """Authenticate user and create session"""
        try:
            with self.db.engine.connect() as conn:
                # Get user by email
                user_query = text("""
                    SELECT id, email, password_hash, full_name, role, is_active
                    FROM users WHERE email = :email
                """)
                user = conn.execute(user_query, {'email': email}).fetchone()
                
                if not user:
                    return False, "Invalid email or password"
                
                if not user.is_active:
                    return False, "Account is deactivated"
                
                # Verify password
                password_hash = self._hash_password(password)
                if user.password_hash != password_hash:
                    return False, "Invalid email or password"
                
                # Create session
                session_token = self._generate_session_token()
                expires_at = datetime.now() + timedelta(hours=24)  # 24 hour session
                
                session_query = text("""
                    INSERT INTO user_sessions (user_id, session_token, expires_at)
                    VALUES (:user_id, :session_token, :expires_at)
                """)
                
                conn.execute(session_query, {
                    'user_id': user.id,
                    'session_token': session_token,
                    'expires_at': expires_at
                })
                
                # Update last login
                update_query = text("""
                    UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = :user_id
                """)
                conn.execute(update_query, {'user_id': user.id})
                
                conn.commit()
                
                # Return user info and session token
                user_info = {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': user.role,
                    'session_token': session_token
                }
                
                return True, user_info
        except Exception as e:
            return False, f"Login failed: {e}"
    
    def verify_session(self, session_token):
        """Verify session token and return user info"""
        try:
            with self.db.engine.connect() as conn:
                # Get active session
                session_query = text("""
                    SELECT s.user_id, s.expires_at, u.email, u.full_name, u.role
                    FROM user_sessions s
                    JOIN users u ON s.user_id = u.id
                    WHERE s.session_token = :session_token 
                    AND s.is_active = TRUE 
                    AND s.expires_at > CURRENT_TIMESTAMP
                """)
                
                session = conn.execute(session_query, {'session_token': session_token}).fetchone()
                
                if not session:
                    return False, "Invalid or expired session"
                
                user_info = {
                    'id': session.user_id,
                    'email': session.email,
                    'full_name': session.full_name,
                    'role': session.role
                }
                
                return True, user_info
        except Exception as e:
            return False, f"Session verification failed: {e}"
    
    def logout_user(self, session_token):
        """Logout user by deactivating session"""
        try:
            with self.db.engine.connect() as conn:
                logout_query = text("""
                    UPDATE user_sessions 
                    SET is_active = FALSE 
                    WHERE session_token = :session_token
                """)
                conn.execute(logout_query, {'session_token': session_token})
                conn.commit()
                return True
        except Exception as e:
            st.error(f"Logout failed: {e}")
            return False
    
    def get_current_user(self):
        """Get current user from session"""
        if 'session_token' not in st.session_state:
            return None
        
        success, result = self.verify_session(st.session_state.session_token)
        if success:
            return result
        else:
            # Clear invalid session
            if 'session_token' in st.session_state:
                del st.session_state.session_token
            return None
    
    def require_auth(self):
        """Decorator to require authentication for app sections"""
        user = self.get_current_user()
        if not user:
            st.error("🔒 Please log in to access this feature")
            st.stop()
        return user
    
    def create_admin_user(self, email, password, full_name="Admin"):
        """Create an admin user (for initial setup)"""
        try:
            with self.db.engine.connect() as conn:
                # Check if admin already exists
                check_query = text("SELECT id FROM users WHERE role = 'admin'")
                existing_admin = conn.execute(check_query).fetchone()
                
                if existing_admin:
                    return False, "Admin user already exists"
                
                # Create admin user
                password_hash = self._hash_password(password)
                insert_query = text("""
                    INSERT INTO users (email, password_hash, full_name, role)
                    VALUES (:email, :password_hash, :full_name, 'admin')
                    RETURNING id
                """)
                
                result = conn.execute(insert_query, {
                    'email': email,
                    'password_hash': password_hash,
                    'full_name': full_name
                })
                admin_id = result.fetchone()[0]
                conn.commit()
                
                return True, f"Admin user created with ID: {admin_id}"
        except Exception as e:
            return False, f"Admin creation failed: {e}"
    
    def get_user_projects(self, user_id):
        """Get projects for a specific user"""
        try:
            query = text("""
                SELECT * FROM projects 
                WHERE user_id = :user_id 
                ORDER BY id DESC
            """)
            with self.db.engine.connect() as conn:
                result = conn.execute(query, {'user_id': user_id})
                rows = result.fetchall()
                if rows:
                    columns = ['id', 'project_name', 'client_name', 'software', 'vendor', 'start_date', 'deadline', 'status', 'description', 'file_path', 'user_id']
                    return pd.DataFrame(rows, columns=columns)
                return pd.DataFrame()
        except Exception as e:
            st.error(f"Error getting user projects: {e}")
            return pd.DataFrame()

    def send_temp_password_email(self, to_email, temp_password, full_name):
        """Send temp password email if SMTP is configured in Streamlit secrets"""
        try:
            smtp_host = st.secrets.get("SMTP_HOST")
            smtp_port = int(st.secrets.get("SMTP_PORT", 587))
            smtp_user = st.secrets.get("SMTP_USER")
            smtp_pass = st.secrets.get("SMTP_PASS")
            from_email = st.secrets.get("SMTP_FROM", smtp_user)
            if not (smtp_host and smtp_user and smtp_pass):
                return False, "SMTP not configured."
            subject = "Your Project Tracker Account - Temporary Password"
            body = f"""
Hello {full_name},

Your Project Tracker account has been created.

Login Email: {to_email}
Temporary Password: {temp_password}

Please log in and set your own password as soon as possible.

Login URL: [Your App URL Here]

If you did not expect this email, please ignore it.
"""
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(from_email, [to_email], msg.as_string())
            return True, "Email sent."
        except Exception as e:
            return False, f"Email error: {e}"

    def create_user_with_temp_password(self, email, full_name, role='user'):
        """Admin creates a user with a temp password. Returns (success, temp_password/message)"""
        temp_password = self._generate_temp_password()
        password_hash = self._hash_password(temp_password)
        try:
            with self.db.engine.connect() as conn:
                # Check if user already exists
                check_query = text("SELECT id FROM users WHERE email = :email")
                existing_user = conn.execute(check_query, {'email': email}).fetchone()
                if existing_user:
                    return False, "User already exists"
                insert_query = text("""
                    INSERT INTO users (email, password_hash, full_name, role, must_change_password)
                    VALUES (:email, :password_hash, :full_name, :role, TRUE)
                    RETURNING id
                """)
                result = conn.execute(insert_query, {
                    'email': email,
                    'password_hash': password_hash,
                    'full_name': full_name,
                    'role': role
                })
                user_id = result.fetchone()[0]
                conn.commit()
                # Try to send email
                email_sent, email_msg = self.send_temp_password_email(email, temp_password, full_name)
                if email_sent:
                    return True, f"Temporary password sent to {email}."
                else:
                    return True, f"User created. Email not sent: {email_msg}. Temporary password: {temp_password}"
        except Exception as e:
            return False, f"User creation failed: {e}"

    def _generate_temp_password(self, length=10):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def set_user_password(self, user_id, new_password):
        """Set a new password for a user and clear must_change_password flag"""
        try:
            with self.db.engine.connect() as conn:
                password_hash = self._hash_password(new_password)
                update_query = text("""
                    UPDATE users SET password_hash = :password_hash, must_change_password = FALSE WHERE id = :user_id
                """)
                conn.execute(update_query, {'password_hash': password_hash, 'user_id': user_id})
                conn.commit()
                return True
        except Exception as e:
            st.error(f"Password update failed: {e}")
            return False

    def check_must_change_password(self, user_id):
        """Check if user must change password on next login"""
        try:
            with self.db.engine.connect() as conn:
                query = text("SELECT must_change_password FROM users WHERE id = :user_id")
                result = conn.execute(query, {'user_id': user_id}).fetchone()
                if result and result[0]:
                    return True
                return False
        except Exception as e:
            st.error(f"Error checking must_change_password: {e}")
            return False

    def get_all_users(self):
        """Return all users for admin listing"""
        try:
            with self.db.engine.connect() as conn:
                query = text("SELECT id, email, full_name, role, created_at, last_login, is_active FROM users ORDER BY created_at DESC")
                result = conn.execute(query)
                rows = result.fetchall()
                if rows:
                    columns = ['id', 'email', 'full_name', 'role', 'created_at', 'last_login', 'is_active']
                    return pd.DataFrame(rows, columns=columns)
                return pd.DataFrame()
        except Exception as e:
            st.error(f"Error getting users: {e}")
            return pd.DataFrame()

    def set_user_active(self, user_id, is_active, admin_id=None, admin_email=None):
        """Set user active/inactive (deactivate/reactivate) and log action"""
        try:
            with self.db.engine.connect() as conn:
                query = text("UPDATE users SET is_active = :is_active WHERE id = :user_id")
                conn.execute(query, {'is_active': is_active, 'user_id': user_id})
                conn.commit()
            # Log action
            if admin_id and admin_email:
                action = "activate" if is_active else "deactivate"
                target_email = self.get_user_email(user_id)
                self.log_admin_action(admin_id, admin_email, action, user_id, target_email)
            return True
        except Exception as e:
            st.error(f"Failed to update user status: {e}")
            return False

    def reset_user_password(self, user_id, admin_id=None, admin_email=None):
        """Admin resets a user's password, sends new temp password, and sets must_change_password. Logs action."""
        try:
            with self.db.engine.connect() as conn:
                # Get user info
                user_query = text("SELECT email, full_name FROM users WHERE id = :user_id")
                user = conn.execute(user_query, {'user_id': user_id}).fetchone()
                if not user:
                    return False, "User not found"
                temp_password = self._generate_temp_password()
                password_hash = self._hash_password(temp_password)
                update_query = text("""
                    UPDATE users SET password_hash = :password_hash, must_change_password = TRUE WHERE id = :user_id
                """)
                conn.execute(update_query, {'password_hash': password_hash, 'user_id': user_id})
                conn.commit()
                # Send email
                email_sent, email_msg = self.send_temp_password_email(user.email, temp_password, user.full_name)
                # Log action
                if admin_id and admin_email:
                    self.log_admin_action(admin_id, admin_email, "reset_password", user_id, user.email)
                if email_sent:
                    return True, f"Temporary password sent to {user.email}."
                else:
                    return True, f"Password reset. Email not sent: {email_msg}. Temporary password: {temp_password}"
        except Exception as e:
            return False, f"Password reset failed: {e}"

    def change_user_role(self, user_id, new_role, admin_id=None, admin_email=None):
        """Admin changes a user's role (user/admin) and logs action"""
        try:
            with self.db.engine.connect() as conn:
                update_query = text("UPDATE users SET role = :role WHERE id = :user_id")
                conn.execute(update_query, {'role': new_role, 'user_id': user_id})
                conn.commit()
            # Log action
            if admin_id and admin_email:
                target_email = self.get_user_email(user_id)
                self.log_admin_action(admin_id, admin_email, f"change_role_to_{new_role}", user_id, target_email)
            return True
        except Exception as e:
            st.error(f"Failed to change user role: {e}")
            return False

    def delete_user(self, user_id, admin_id=None, admin_email=None):
        """Admin deletes a user and all related data (projects, meetings, updates, issues). Logs action."""
        try:
            with self.db.engine.connect() as conn:
                # Get user email
                target_email = self.get_user_email(user_id)
                # Delete related data
                conn.execute(text("DELETE FROM issues WHERE user_id = :user_id"), {'user_id': user_id})
                conn.execute(text("DELETE FROM client_updates WHERE user_id = :user_id"), {'user_id': user_id})
                conn.execute(text("DELETE FROM meetings WHERE user_id = :user_id"), {'user_id': user_id})
                conn.execute(text("DELETE FROM projects WHERE user_id = :user_id"), {'user_id': user_id})
                # Delete user
                conn.execute(text("DELETE FROM users WHERE id = :user_id"), {'user_id': user_id})
                conn.commit()
            # Log action
            if admin_id and admin_email:
                self.log_admin_action(admin_id, admin_email, "delete_user", user_id, target_email)
            return True
        except Exception as e:
            st.error(f"Failed to delete user: {e}")
            return False

    def get_user_email(self, user_id):
        try:
            with self.db.engine.connect() as conn:
                query = text("SELECT email FROM users WHERE id = :user_id")
                result = conn.execute(query, {'user_id': user_id}).fetchone()
                return result[0] if result else None
        except Exception:
            return None

    def get_audit_logs(self, limit=100):
        try:
            with self.db.engine.connect() as conn:
                query = text("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT :limit")
                result = conn.execute(query, {'limit': limit})
                rows = result.fetchall()
                if rows:
                    columns = ['id', 'admin_id', 'admin_email', 'action', 'target_user_id', 'target_email', 'details', 'timestamp']
                    return pd.DataFrame(rows, columns=columns)
                return pd.DataFrame()
        except Exception as e:
            st.error(f"Error getting audit logs: {e}")
            return pd.DataFrame()

    def log_admin_action(self, admin_id, admin_email, action, target_user_id, target_email, details=None):
        try:
            with self.db.engine.connect() as conn:
                query = text("""
                    INSERT INTO audit_logs (admin_id, admin_email, action, target_user_id, target_email, details)
                    VALUES (:admin_id, :admin_email, :action, :target_user_id, :target_email, :details)
                """)
                conn.execute(query, {
                    'admin_id': admin_id,
                    'admin_email': admin_email,
                    'action': action,
                    'target_user_id': target_user_id,
                    'target_email': target_email,
                    'details': details
                })
                conn.commit()
        except Exception as e:
            st.error(f"Failed to log admin action: {e}")

# Initialize auth instance
auth = NeonAuth() 