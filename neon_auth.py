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
                        is_active BOOLEAN DEFAULT TRUE
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
    
    def register_user(self, email, password, full_name):
        """Register a new user"""
        try:
            with self.db.engine.connect() as conn:
                # Check if user already exists
                check_query = text("SELECT id FROM users WHERE email = :email")
                existing_user = conn.execute(check_query, {'email': email}).fetchone()
                
                if existing_user:
                    return False, "User already exists"
                
                # Hash password and create user
                password_hash = self._hash_password(password)
                insert_query = text("""
                    INSERT INTO users (email, password_hash, full_name)
                    VALUES (:email, :password_hash, :full_name)
                    RETURNING id
                """)
                
                result = conn.execute(insert_query, {
                    'email': email,
                    'password_hash': password_hash,
                    'full_name': full_name
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

# Initialize auth instance
auth = NeonAuth() 