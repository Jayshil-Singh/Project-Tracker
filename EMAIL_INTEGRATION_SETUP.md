# 📧 Email Integration Setup Guide

This guide will help you set up the email integration feature to automatically read and process client emails from your Outlook company domain.

## 🎯 Overview

The email integration feature allows your Project Tracker to:
- Connect to your Outlook account via Microsoft Graph API
- Automatically read emails from the last 7-30 days
- Classify emails as issues, queries, updates, or meetings
- Extract project names and client information
- Automatically create projects and store relevant content in your database

## 🔧 Prerequisites

1. **Microsoft 365 Business Account** with admin access
2. **Azure Active Directory** access for your organization
3. **Admin permissions** to register applications

## 📋 Step-by-Step Setup

### Step 1: Register Application in Azure AD

1. **Go to Azure Portal**
   - Navigate to [Azure Portal](https://portal.azure.com)
   - Sign in with your Microsoft 365 admin account

2. **Create App Registration**
   - Search for "Azure Active Directory" in the search bar
   - Click on "Azure Active Directory" in the results
   - In the left menu, click "App registrations"
   - Click "New registration"

3. **Configure App Registration**
   - **Name**: `ProjectOps Email Integration`
   - **Supported account types**: Select "Accounts in this organizational directory only"
   - **Redirect URI**: 
     - Type: Web
     - URI: `http://localhost:8501` (for local development)
     - For production: Use your actual Streamlit deployment URL

4. **Click "Register"**

### Step 2: Configure API Permissions

1. **Navigate to API Permissions**
   - In your newly created app registration
   - Click "API permissions" in the left menu
   - Click "Add a permission"

2. **Add Microsoft Graph Permissions**
   - Select "Microsoft Graph"
   - Choose "Delegated permissions"
   - Search for and select the following permissions:
     - `Mail.Read` - Read user mail
     - `User.Read` - Sign in and read user profile

3. **Grant Admin Consent**
   - Click "Grant admin consent for [Your Organization]"
   - Confirm the action

### Step 3: Create Client Secret

1. **Navigate to Certificates & Secrets**
   - In your app registration
   - Click "Certificates & secrets" in the left menu
   - Click "New client secret"

2. **Configure Secret**
   - **Description**: `ProjectOps Email Integration Secret`
   - **Expires**: Choose an appropriate expiration (recommend 12 months)
   - Click "Add"

3. **Copy the Secret Value**
   - **IMPORTANT**: Copy the secret value immediately - you won't be able to see it again
   - Store it securely for the next step

### Step 4: Get Application Credentials

1. **Copy Application (Client) ID**
   - In your app registration overview
   - Copy the "Application (client) ID"

2. **Copy Directory (Tenant) ID**
   - In your app registration overview
   - Copy the "Directory (tenant) ID"

3. **Note Your Email**
   - Your company email address (e.g., `yourname@yourcompany.com`)

## 🔐 Configure Streamlit Secrets

### Option A: Local Development (.streamlit/secrets.toml)

Add the following to your `.streamlit/secrets.toml` file:

```toml
# Email Integration Configuration
MS_GRAPH_CLIENT_ID = "your-client-id-here"
MS_GRAPH_CLIENT_SECRET = "your-client-secret-here"
MS_GRAPH_TENANT_ID = "your-tenant-id-here"
MS_GRAPH_USER_EMAIL = "your-email@yourcompany.com"
```

### Option B: Production Deployment

For production deployments (Streamlit Cloud, etc.), add these secrets in your deployment platform's secrets management section.

## 🚀 Using the Email Integration

### First-Time Setup

1. **Launch Your Project Tracker App**
   - Run your Streamlit app locally or access your deployed version

2. **Navigate to Email Integration**
   - Click on "📧 Email Integration" in the sidebar

3. **Complete Authentication**
   - Click the authorization link
   - Sign in with your Microsoft 365 account
   - Grant permissions when prompted
   - Copy the authorization code from the redirect URL
   - Paste the code in the app and complete authentication

### Regular Usage

1. **Process Emails**
   - Go to "📧 Email Integration"
   - Click "🚀 Process Emails for Projects"
   - Review the results

2. **Review Processed Content**
   - Check "🛠️ Issue Tracker" for emails classified as issues
   - Check "🧾 Client Update Log" for emails classified as updates/queries
   - Check "📁 Project Tracker" for auto-created projects

## 🔍 Email Classification

The system automatically classifies emails based on keywords:

### Issue Keywords
- bug, error, problem, issue, broken, not working, failed, crash, defect

### Query Keywords
- question, query, help, support, how to, what is, clarification, advice

### Update Keywords
- update, progress, status, milestone, completed, finished, delivered, review

### Meeting Keywords
- meeting, call, discussion, agenda, schedule, appointment

## ⚙️ Customization

### Modify Classification Keywords

Edit the `classify_email_content` method in `email_integration.py`:

```python
# Keywords for different types of project communications
issue_keywords = ['bug', 'error', 'problem', 'issue', 'broken', 'not working', 'failed', 'crash', 'defect']
query_keywords = ['question', 'query', 'help', 'support', 'how to', 'what is', 'clarification', 'advice']
update_keywords = ['update', 'progress', 'status', 'milestone', 'completed', 'finished', 'delivered', 'review']
meeting_keywords = ['meeting', 'call', 'discussion', 'agenda', 'schedule', 'appointment']
```

### Modify Company Domain Filter

Edit the `classify_email_content` method to filter your company domains:

```python
# Check if email is from a client (external domain)
is_client_email = not any(domain in from_email for domain in ['@yourcompany.com', '@internal.com'])
```

## 🔒 Security Considerations

1. **Client Secret Security**
   - Never commit client secrets to version control
   - Use environment variables or secure secret management
   - Rotate secrets regularly

2. **Permission Scope**
   - The app only requests `Mail.Read` and `User.Read` permissions
   - It cannot send emails or modify your mailbox
   - Only reads emails for processing

3. **Data Privacy**
   - Email content is processed locally
   - Only relevant project information is stored in your database
   - Original emails are not stored

## 🛠️ Troubleshooting

### Common Issues

1. **"Invalid client" error**
   - Verify your Client ID is correct
   - Ensure the app registration is in the correct tenant

2. **"Invalid redirect URI" error**
   - Check that the redirect URI in Azure matches your app URL
   - For local development: `http://localhost:8501`
   - For production: Your actual deployment URL

3. **"Insufficient privileges" error**
   - Ensure admin consent has been granted for the API permissions
   - Contact your Azure AD administrator if needed

4. **"Token expired" error**
   - The app will automatically refresh tokens
   - If persistent, re-authenticate using the "Re-authenticate" button

### Debug Mode

Enable debug logging by adding to your Streamlit app:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your Azure AD configuration
3. Ensure all required permissions are granted
4. Check the Streamlit app logs for detailed error messages

## 🔄 Maintenance

### Regular Tasks

1. **Monitor Client Secret Expiration**
   - Set calendar reminders for secret renewal
   - Create new secrets before old ones expire

2. **Review Email Processing Results**
   - Regularly check the accuracy of email classification
   - Adjust keywords if needed

3. **Update Permissions**
   - Review API permissions annually
   - Remove unused permissions

### Backup and Recovery

1. **Backup Configuration**
   - Store your Azure AD configuration details securely
   - Document the setup process for your team

2. **Recovery Process**
   - If tokens are lost, re-authenticate using the setup process
   - If app registration is deleted, recreate following this guide

---

**Note**: This integration is designed for business use with proper Microsoft 365 licensing. Ensure compliance with your organization's data policies and Microsoft's terms of service. 