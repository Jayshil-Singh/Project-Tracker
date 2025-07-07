#!/usr/bin/env python3
"""
Login Page Component for Project Tracker
Handles user authentication UI
"""

import streamlit as st
from neon_auth import auth

def render_login_page():
    """Render the login page (no public registration)"""
    # Custom CSS for login page
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        background: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h1 style="text-align: center; color: #1f77b4;">🔐 Project Tracker</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #666;">Sign in to access your projects</p>', unsafe_allow_html=True)
        render_login_form()
        st.markdown('</div>', unsafe_allow_html=True)

def render_login_form():
    """Render the login form and handle must_change_password logic"""
    st.markdown('<h3 style="text-align: center;">🔑 Login</h3>', unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=True):
        email = st.text_input("📧 Email", placeholder="Enter your email", key="login_email")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="login_password")
        remember_me = st.checkbox("Remember me", key="remember_me")
        submitted = st.form_submit_button("🚀 Sign In", use_container_width=True)
        
        if submitted:
            if not email or not password:
                st.error("❌ Please fill in all fields")
            else:
                success, result = auth.login_user(email, password)
                if success:
                    # Check if user must change password
                    must_change = auth.check_must_change_password(result['id'])
                    if must_change:
                        st.session_state['pending_password_change'] = result['id']
                        st.session_state['pending_email'] = email
                        st.session_state['pending_token'] = result['session_token']
                        st.rerun()
                    else:
                        st.session_state.session_token = result['session_token']
                        st.session_state.user_info = result
                        st.success(f"✅ Welcome back, {result['full_name']}!")
                        st.rerun()
                else:
                    st.error(f"❌ {result}")
    # Forgot Password button outside the form
    forgot_password = st.button("Forgot Password?", key="forgot_password_btn")
    if forgot_password:
        st.info("Password reset is not implemented yet.")

# Force password change if required
def render_force_password_change():
    st.markdown('<h3 style="text-align: center;">🔒 Set New Password</h3>', unsafe_allow_html=True)
    st.info("You must set a new password before accessing the app.")
    with st.form("force_password_change_form"):
        new_password = st.text_input("New Password", type="password", key="force_new_password")
        confirm_password = st.text_input("Confirm New Password", type="password", key="force_confirm_password")
        submitted = st.form_submit_button("Set Password", use_container_width=True)
        if submitted:
            if not new_password or not confirm_password:
                st.error("Please fill in all fields.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            elif len(new_password) < 8:
                st.error("Password must be at least 8 characters.")
            else:
                user_id = st.session_state.get('pending_password_change')
                if user_id:
                    success = auth.set_user_password(user_id, new_password)
                    if success:
                        st.success("Password updated! Please log in again.")
                        # Clear pending state
                        for k in ['pending_password_change', 'pending_email', 'pending_token']:
                            if k in st.session_state:
                                del st.session_state[k]
                        st.rerun()
                    else:
                        st.error("Failed to update password. Please try again.")

def render_admin_setup():
    """Render admin setup form (for first-time setup)"""
    st.markdown('<h2 style="text-align: center;">⚙️ Admin Setup</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center;">Create the first admin user for the system</p>', unsafe_allow_html=True)
    
    with st.form("admin_setup_form"):
        admin_email = st.text_input("📧 Admin Email", placeholder="admin@example.com")
        admin_password = st.text_input("🔒 Admin Password", type="password", placeholder="Create admin password")
        admin_name = st.text_input("👤 Admin Name", placeholder="Administrator")
        
        submitted = st.form_submit_button("⚙️ Create Admin User", use_container_width=True)
        
        if submitted:
            if not admin_email or not admin_password or not admin_name:
                st.error("❌ Please fill in all fields")
            else:
                success, result = auth.create_admin_user(admin_email, admin_password, admin_name)
                if success:
                    st.success("✅ Admin user created successfully!")
                    st.info("You can now log in with the admin credentials.")
                else:
                    st.error(f"❌ {result}")

def check_if_admin_exists():
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