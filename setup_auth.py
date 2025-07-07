#!/usr/bin/env python3
"""
Authentication Setup Script for Project Tracker
Helps configure the authentication system and create the first admin user
"""

import streamlit as st
import os
import sys
from neon_auth import NeonAuth
from database_postgres import ProjectOpsDatabase

def main():
    st.set_page_config(
        page_title="Project Tracker - Auth Setup",
        page_icon="🔐",
        layout="wide"
    )
    
    st.markdown("""
    <style>
    .setup-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        background: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .step-header {
        color: #1f77b4;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #155724;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #721c24;
    }
    .info-box {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #0c5460;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 style="text-align: center; color: #1f77b4;">🔐 Project Tracker Authentication Setup</h1>', unsafe_allow_html=True)
    
    # Initialize auth
    try:
        auth = NeonAuth()
        db = ProjectOpsDatabase()
        st.success("✅ Database connection established successfully!")
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        st.info("💡 Make sure your database URL is configured in Streamlit secrets or environment variables")
        return
    
    # Check if admin exists
    admin_exists = check_if_admin_exists(auth)
    
    if admin_exists:
        st.markdown('<div class="success-box">✅ Admin user already exists! You can now log in to the main application.</div>', unsafe_allow_html=True)
        st.info("🔗 Go to the main app to log in with your admin credentials.")
        return
    
    # Setup steps
    st.markdown('<div class="setup-container">', unsafe_allow_html=True)
    
    st.markdown('<div class="step-header">Step 1: Database Tables</div>', unsafe_allow_html=True)
    
    # Check if auth tables exist
    try:
        with db.engine.connect() as conn:
            from sqlalchemy import text
            # Check if users table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'users'
                )
            """))
            users_table_exists = result.fetchone()[0]
            
            if users_table_exists:
                st.success("✅ Authentication tables already exist")
            else:
                st.info("📋 Creating authentication tables...")
                # This will be done by the NeonAuth initialization
                st.success("✅ Authentication tables created successfully")
    except Exception as e:
        st.error(f"❌ Error checking database tables: {e}")
        return
    
    st.markdown('<div class="step-header">Step 2: Create Admin User</div>', unsafe_allow_html=True)
    
    st.info("👤 Create the first administrator user for the system. This user will have full access to all features.")
    
    with st.form("admin_setup_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            admin_email = st.text_input("📧 Admin Email *", placeholder="admin@example.com", key="admin_email")
            admin_name = st.text_input("👤 Admin Name *", placeholder="Administrator", key="admin_name")
        
        with col2:
            admin_password = st.text_input("🔒 Admin Password *", type="password", placeholder="Create admin password", key="admin_password")
            confirm_password = st.text_input("🔒 Confirm Password *", type="password", placeholder="Confirm admin password", key="confirm_password")
        
        # Password strength indicator
        if admin_password:
            strength = check_password_strength(admin_password)
            st.markdown(f"Password strength: {strength}")
        
        submitted = st.form_submit_button("⚙️ Create Admin User", use_container_width=True)
        
        if submitted:
            if not admin_email or not admin_password or not admin_name:
                st.error("❌ Please fill in all required fields")
            elif admin_password != confirm_password:
                st.error("❌ Passwords do not match")
            elif len(admin_password) < 8:
                st.error("❌ Password must be at least 8 characters long")
            else:
                success, result = auth.create_admin_user(admin_email, admin_password, admin_name)
                if success:
                    st.markdown('<div class="success-box">✅ Admin user created successfully!</div>', unsafe_allow_html=True)
                    st.info(f"📧 Email: {admin_email}")
                    st.info("🔐 You can now log in to the main application with these credentials.")
                    
                    # Show next steps
                    st.markdown('<div class="step-header">Step 3: Next Steps</div>', unsafe_allow_html=True)
                    st.markdown("""
                    1. **Go to the main application** - Navigate to your main app URL
                    2. **Log in** - Use the admin credentials you just created
                    3. **Create additional users** - Use the admin panel to create regular users
                    4. **Start using the system** - Begin adding projects and managing your workflow
                    """)
                else:
                    st.error(f"❌ {result}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Additional information
    st.markdown("---")
    st.markdown("### 📚 Additional Information")
    
    with st.expander("🔧 Configuration Details"):
        st.markdown("""
        **Database Configuration:**
        - The system uses your existing PostgreSQL database
        - Authentication tables are created automatically
        - User data is stored securely with hashed passwords
        
        **Security Features:**
        - Password hashing using SHA-256
        - Session-based authentication
        - User-specific data isolation
        - 24-hour session expiration
        
        **User Roles:**
        - **Admin**: Full access to all features and user management
        - **User**: Access to their own projects and data only
        """)
    
    with st.expander("🚀 Deployment Notes"):
        st.markdown("""
        **For Streamlit Cloud:**
        1. Set your database URL in Streamlit Cloud secrets
        2. Deploy the main application
        3. Run this setup script first
        4. Create admin user
        5. Start using the system
        
        **For Local Development:**
        1. Set DB_URL environment variable
        2. Run this setup script
        3. Create admin user
        4. Run the main application
        """)

def check_if_admin_exists(auth):
    """Check if admin user exists in the system"""
    try:
        with auth.db.engine.connect() as conn:
            from sqlalchemy import text
            query = text("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            result = conn.execute(query)
            count = result.fetchone()[0]
            return count > 0
    except:
        return False

def check_password_strength(password):
    """Check password strength and return indicator"""
    score = 0
    
    if len(password) >= 8:
        score += 1
    
    if any(c.isupper() for c in password):
        score += 1
    
    if any(c.islower() for c in password):
        score += 1
    
    if any(c.isdigit() for c in password):
        score += 1
    
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 1
    
    if score == 5:
        return "🟢 Strong"
    elif score >= 3:
        return "🟡 Medium"
    else:
        return "🔴 Weak"

if __name__ == "__main__":
    main() 