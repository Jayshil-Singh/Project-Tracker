#!/usr/bin/env python3
"""
Email Management Interface for ProjectOps
Provides UI components for email integration and management
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from email_integration import OutlookEmailIntegration

def render_email_setup_section():
    """Render email integration setup section"""
    st.markdown("### 📧 Email Integration Setup")
    st.markdown("Connect your Outlook account to automatically process client emails.")
    
    email_integration = OutlookEmailIntegration()
    
    # Check if already configured
    if email_integration.access_token:
        st.success("✅ Email integration is configured and active!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh Connection", key="refresh_email_connection"):
                if email_integration.refresh_access_token():
                    st.success("Connection refreshed successfully!")
                    st.rerun()
                else:
                    st.error("Failed to refresh connection. Please re-authenticate.")
        
        with col2:
            if st.button("🔓 Re-authenticate", key="reauth_email"):
                # Clear tokens
                if 'email_access_token' in st.session_state:
                    del st.session_state.email_access_token
                if 'email_refresh_token' in st.session_state:
                    del st.session_state.email_refresh_token
                st.rerun()
        
        return email_integration
    
    # Setup section
    st.info("To use email integration, you need to configure Microsoft Graph API credentials.")
    
    with st.expander("🔧 Setup Instructions", expanded=False):
        st.markdown("""
        **Step 1: Register your application in Azure AD**
        1. Go to [Azure Portal](https://portal.azure.com)
        2. Navigate to Azure Active Directory > App registrations
        3. Click "New registration"
        4. Name: "ProjectOps Email Integration"
        5. Supported account types: "Accounts in this organizational directory only"
        6. Redirect URI: Web > `http://localhost:8501`
        
        **Step 2: Configure API permissions**
        1. Go to API permissions
        2. Add permission: Microsoft Graph > Delegated permissions
        3. Select: Mail.Read, User.Read
        4. Grant admin consent
        
        **Step 3: Get credentials**
        1. Copy Application (client) ID
        2. Copy Directory (tenant) ID
        3. Create a client secret in Certificates & secrets
        4. Copy the client secret value
        """)
    
    # Configuration form
    with st.form("email_config_form"):
        st.subheader("Microsoft Graph API Configuration")
        
        client_id = st.text_input("Client ID", key="email_client_id", 
                                 help="Application (client) ID from Azure AD")
        client_secret = st.text_input("Client Secret", key="email_client_secret", 
                                     type="password", help="Client secret from Azure AD")
        tenant_id = st.text_input("Tenant ID", key="email_tenant_id", 
                                 help="Directory (tenant) ID from Azure AD")
        user_email = st.text_input("User Email", key="email_user_email", 
                                  help="Your company email address")
        
        submitted = st.form_submit_button("🔗 Connect Email Integration", use_container_width=True)
        
        if submitted:
            if not all([client_id, client_secret, tenant_id, user_email]):
                st.error("Please fill in all fields.")
            else:
                # Store configuration in session state (in production, use proper secrets management)
                st.session_state.email_config = {
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'tenant_id': tenant_id,
                    'user_email': user_email
                }
                st.success("Configuration saved! Please authenticate below.")
                st.rerun()
    
    # Authentication section
    if 'email_config' in st.session_state:
        st.subheader("🔐 Authentication")
        
        auth_url = email_integration.get_auth_url()
        if auth_url:
            st.markdown(f"**Step 1:** Click the link below to authorize access to your emails:")
            st.markdown(f"[🔗 Authorize Email Access]({auth_url})")
            
            st.markdown("**Step 2:** After authorization, copy the authorization code from the URL and paste it below:")
            
            auth_code = st.text_input("Authorization Code", key="email_auth_code", 
                                     help="Copy the 'code' parameter from the redirect URL")
            
            if st.button("✅ Complete Authentication", key="complete_email_auth"):
                if auth_code:
                    if email_integration.exchange_code_for_token(auth_code):
                        st.success("✅ Email integration authenticated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Authentication failed. Please try again.")
                else:
                    st.error("Please enter the authorization code.")
        else:
            st.error("Unable to generate authentication URL. Please check your configuration.")
    
    return None

def render_email_dashboard(email_integration):
    """Render email dashboard with statistics and controls"""
    st.markdown("### 📊 Email Dashboard")
    
    # Get email statistics
    with st.spinner("Loading email statistics..."):
        stats = email_integration.get_email_statistics()
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Emails (30 days)", stats['total'])
    
    with col2:
        st.metric("Client Emails", stats['client_emails'])
    
    with col3:
        issue_count = stats['by_type'].get('issue', 0)
        st.metric("Issues Detected", issue_count)
    
    with col4:
        update_count = stats['by_type'].get('update', 0) + stats['by_type'].get('query', 0)
        st.metric("Updates/Queries", update_count)
    
    # Email type breakdown
    if stats['by_type']:
        st.subheader("Email Classification Breakdown")
        type_df = pd.DataFrame(list(stats['by_type'].items()), columns=['Type', 'Count'])
        st.bar_chart(type_df.set_index('Type'))
    
    return stats

def render_email_processing_section(email_integration, db, user_id):
    """Render email processing controls and results"""
    st.markdown("### 🔄 Email Processing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        days_back = st.selectbox("Process emails from last:", 
                                [1, 3, 7, 14, 30], index=2, key="email_days_back")
    
    with col2:
        max_emails = st.selectbox("Maximum emails to process:", 
                                 [25, 50, 100, 200], index=1, key="email_max_count")
    
    # Process emails button
    if st.button("🚀 Process Emails for Projects", key="process_emails_btn", use_container_width=True):
        with st.spinner("Processing emails..."):
            results = email_integration.process_emails_for_projects(db, user_id)
        
        # Display results
        st.success(f"✅ Email processing completed!")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Processed", results['processed'])
        with col2:
            st.metric("Issues Created", results['issues'])
        with col3:
            st.metric("Updates Created", results['updates'])
        with col4:
            st.metric("Queries Created", results['queries'])
        
        if results['processed'] > 0:
            st.info("📝 Check the Issues Tracker and Client Update Log sections to review the processed emails.")
    
    return results

def render_email_preview_section(email_integration):
    """Render email preview section"""
    st.markdown("### 📧 Email Preview")
    
    # Get recent emails
    days_back = st.selectbox("Show emails from last:", 
                            [1, 3, 7, 14], index=1, key="preview_days_back")
    
    if st.button("🔄 Refresh Email Preview", key="refresh_email_preview"):
        with st.spinner("Loading emails..."):
            emails = email_integration.get_emails(days_back=days_back, max_emails=20)
        
        if not emails:
            st.info("No emails found for the selected period.")
            return
        
        # Display emails
        for i, email in enumerate(emails):
            classification = email_integration.classify_email_content(email)
            
            with st.expander(f"📧 {email['subject']} - {email['from']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**From:** {email['from_name']} ({email['from']})")
                    st.markdown(f"**Date:** {email['received_date']}")
                    st.markdown(f"**Importance:** {email['importance']}")
                    
                    # Show email body (truncated)
                    body_preview = email['body'][:500] + "..." if len(email['body']) > 500 else email['body']
                    st.markdown(f"**Content:**\n{body_preview}")
                
                with col2:
                    st.markdown("**Classification:**")
                    st.markdown(f"- Type: {classification['email_type']}")
                    st.markdown(f"- Confidence: {classification['confidence']:.1%}")
                    st.markdown(f"- Client Email: {'✅' if classification['is_client_email'] else '❌'}")
                    
                    if classification['project_name']:
                        st.markdown(f"- Project: {classification['project_name']}")
                    if classification['client_name']:
                        st.markdown(f"- Client: {classification['client_name']}")

def render_email_management_page(db, user_id):
    """Main email management page"""
    st.markdown('<h1 class="main-header">📧 Email Integration</h1>', unsafe_allow_html=True)
    
    # Initialize email integration
    email_integration = render_email_setup_section()
    
    if email_integration:
        # Email dashboard
        render_email_dashboard(email_integration)
        
        st.markdown("---")
        
        # Email processing
        render_email_processing_section(email_integration, db, user_id)
        
        st.markdown("---")
        
        # Email preview
        render_email_preview_section(email_integration)
        
        # Configuration management
        with st.expander("⚙️ Advanced Configuration", expanded=False):
            st.markdown("### Email Processing Rules")
            
            st.markdown("**Current Classification Keywords:**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Issue Keywords:**")
                st.code("bug, error, problem, issue, broken, not working, failed, crash, defect")
                
                st.markdown("**Query Keywords:**")
                st.code("question, query, help, support, how to, what is, clarification, advice")
            
            with col2:
                st.markdown("**Update Keywords:**")
                st.code("update, progress, status, milestone, completed, finished, delivered, review")
                
                st.markdown("**Meeting Keywords:**")
                st.code("meeting, call, discussion, agenda, schedule, appointment")
            
            st.info("💡 These keywords are used to automatically classify incoming emails. You can modify them in the email_integration.py file.")
    
    else:
        st.warning("⚠️ Please complete the email integration setup to access email features.") 