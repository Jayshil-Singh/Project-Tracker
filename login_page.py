#!/usr/bin/env python3
"""
Login Page Component for Project Tracker
Handles user authentication UI
"""

import streamlit as st
from neon_auth import auth

def render_login_page():
    """Render the login/register page"""
    
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
    .auth-tabs {
        display: flex;
        margin-bottom: 2rem;
    }
    .auth-tab {
        flex: 1;
        padding: 1rem;
        text-align: center;
        cursor: pointer;
        border-bottom: 2px solid transparent;
    }
    .auth-tab.active {
        border-bottom-color: #1f77b4;
        color: #1f77b4;
        font-weight: bold;
    }
    .form-group {
        margin-bottom: 1rem;
    }
    .form-group label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    .form-group input {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #ddd;
        border-radius: 5px;
        font-size: 1rem;
    }
    .btn-primary {
        width: 100%;
        padding: 0.75rem;
        background: #1f77b4;
        color: white;
        border: none;
        border-radius: 5px;
        font-size: 1rem;
        cursor: pointer;
        margin-top: 1rem;
    }
    .btn-primary:hover {
        background: #1565c0;
    }
    .error-message {
        color: #d32f2f;
        background: #ffebee;
        padding: 0.75rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .success-message {
        color: #2e7d32;
        background: #e8f5e8;
        padding: 0.75rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # App title
        st.markdown('<h1 style="text-align: center; color: #1f77b4;">🔐 Project Tracker</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #666;">Sign in to access your projects</p>', unsafe_allow_html=True)
        
        # Tab selection
        if 'auth_tab' not in st.session_state:
            st.session_state.auth_tab = 'login'
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔑 Login", key="login_tab_btn", use_container_width=True):
                st.session_state.auth_tab = 'login'
        with col2:
            if st.button("📝 Register", key="register_tab_btn", use_container_width=True):
                st.session_state.auth_tab = 'register'
        
        # Show active tab
        if st.session_state.auth_tab == 'login':
            render_login_form()
        else:
            render_register_form()
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_login_form():
    """Render the login form"""
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
                    # Store session token
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

def render_register_form():
    """Render the registration form"""
    st.markdown('<h3 style="text-align: center;">📝 Register</h3>', unsafe_allow_html=True)
    
    with st.form("register_form", clear_on_submit=True):
        full_name = st.text_input("👤 Full Name", placeholder="Enter your full name", key="register_name")
        email = st.text_input("📧 Email", placeholder="Enter your email", key="register_email")
        password = st.text_input("🔒 Password", type="password", placeholder="Create a password", key="register_password")
        confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password", key="register_confirm_password")
        
        # Password strength indicator
        if password:
            strength = check_password_strength(password)
            st.markdown(f"Password strength: {strength}")
        
        submitted = st.form_submit_button("📝 Create Account", use_container_width=True)
        
        if submitted:
            if not full_name or not email or not password or not confirm_password:
                st.error("❌ Please fill in all fields")
            elif password != confirm_password:
                st.error("❌ Passwords do not match")
            elif len(password) < 8:
                st.error("❌ Password must be at least 8 characters long")
            else:
                success, result = auth.register_user(email, password, full_name)
                if success:
                    st.success("✅ Account created successfully! Please log in.")
                    st.session_state.auth_tab = 'login'
                    st.rerun()
                else:
                    st.error(f"❌ {result}")

def check_password_strength(password):
    """Check password strength and return indicator"""
    score = 0
    feedback = []
    
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("At least 8 characters")
    
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("Uppercase letter")
    
    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("Lowercase letter")
    
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("Number")
    
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 1
    else:
        feedback.append("Special character")
    
    if score == 5:
        return "🟢 Strong"
    elif score >= 3:
        return "🟡 Medium"
    else:
        return "🔴 Weak"

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