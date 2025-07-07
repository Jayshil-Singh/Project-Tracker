# 🔐 Project Tracker Authentication Setup

This guide will help you set up user authentication for your Project Tracker application using Neon Auth integration.

## 🚀 Quick Start

### 1. Prerequisites
- ✅ PostgreSQL database (Neon, AWS RDS, or local)
- ✅ Python 3.8+ installed
- ✅ Streamlit installed

### 2. Database Configuration
Make sure your database URL is configured in one of these ways:

**For Streamlit Cloud:**
```bash
# In Streamlit Cloud secrets
DB_URL = "postgresql://username:password@host:port/database"
```

**For Local Development:**
```bash
# Set environment variable
export DB_URL="postgresql://username:password@host:port/database"
```

### 3. Install Dependencies
```bash
pip install streamlit pandas sqlalchemy psycopg2-binary plotly
```

## 🔧 Setup Process

### Step 1: Run Authentication Setup
```bash
streamlit run setup_auth.py
```

This will:
- ✅ Connect to your database
- ✅ Create authentication tables
- ✅ Guide you through creating the first admin user

### Step 2: Create Admin User
1. Open the setup page in your browser
2. Fill in the admin user details:
   - **Email**: admin@yourcompany.com
   - **Name**: Administrator
   - **Password**: Choose a strong password (8+ characters)
3. Click "Create Admin User"

### Step 3: Access Main Application
```bash
streamlit run streamlit_app.py
```

## 🔐 Authentication Features

### User Management
- **User Registration**: New users can register accounts
- **User Login**: Secure login with email/password
- **Session Management**: 24-hour session tokens
- **Password Security**: SHA-256 hashed passwords

### User Roles
- **Admin**: Full access to all features and user management
- **User**: Access to their own projects and data only

### Data Isolation
- Each user sees only their own projects
- Meetings, issues, and updates are user-specific
- Secure multi-tenant architecture

## 📁 File Structure

```
Project Tracker/
├── streamlit_app.py          # Main application with auth
├── setup_auth.py            # Authentication setup script
├── neon_auth.py             # Authentication module
├── login_page.py            # Login/register UI components
├── database_postgres.py     # Database with user support
├── chatbot.py               # AI chatbot with user context
├── reports.py               # Report generation
├── file_uploader.py         # File management
└── README_AUTH.md           # This file
```

## 🔒 Security Features

### Password Security
- **Hashing**: SHA-256 password hashing
- **Validation**: Minimum 8 characters required
- **Strength Indicator**: Real-time password strength feedback

### Session Security
- **Token-based**: Secure session tokens
- **Expiration**: 24-hour session timeout
- **Validation**: Server-side session verification

### Data Protection
- **User Isolation**: Complete data separation between users
- **SQL Injection Protection**: Parameterized queries
- **Input Validation**: Form validation and sanitization

## 🛠️ Database Schema

### Authentication Tables
```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- User sessions table
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Updated Data Tables
All existing tables now include `user_id` column for data isolation:
- `projects` table: `user_id INTEGER REFERENCES users(id)`
- `meetings` table: `user_id INTEGER REFERENCES users(id)`
- `client_updates` table: `user_id INTEGER REFERENCES users(id)`
- `issues` table: `user_id INTEGER REFERENCES users(id)`

## 🚀 Deployment

### Streamlit Cloud Deployment
1. **Configure Secrets**:
   ```toml
   # .streamlit/secrets.toml
   DB_URL = "postgresql://username:password@host:port/database"
   ```

2. **Deploy Setup Script**:
   - Upload `setup_auth.py` to Streamlit Cloud
   - Run it first to create admin user

3. **Deploy Main App**:
   - Upload all files to Streamlit Cloud
   - Set `streamlit_app.py` as the main file

### Local Development
1. **Set Environment**:
   ```bash
   export DB_URL="postgresql://username:password@host:port/database"
   ```

2. **Run Setup**:
   ```bash
   streamlit run setup_auth.py
   ```

3. **Run Main App**:
   ```bash
   streamlit run streamlit_app.py
   ```

## 🔧 Configuration Options

### Neon Auth Integration (Optional)
If you want to use Neon's built-in auth service:

```python
# In Streamlit secrets
NEON_PROJECT_ID = "your-neon-project-id"
NEON_API_KEY = "your-neon-api-key"
```

### Custom Authentication
The system falls back to local authentication if Neon Auth is not configured.

## 📊 User Experience

### Login Flow
1. **First Visit**: Redirected to login page
2. **Registration**: New users can create accounts
3. **Login**: Email/password authentication
4. **Dashboard**: User-specific data and features

### User Interface
- **Clean Login Page**: Professional authentication UI
- **User Info Sidebar**: Shows current user details
- **Logout Button**: Secure session termination
- **Role-based Access**: Different features for admin vs users

## 🛡️ Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check your DB_URL format
DB_URL = "postgresql://username:password@host:port/database"
```

**Authentication Tables Not Created**
```bash
# Run setup script first
streamlit run setup_auth.py
```

**User Can't Log In**
- Check if user exists in database
- Verify password is correct
- Ensure user account is active

**Session Expired**
- Sessions expire after 24 hours
- User will be redirected to login page
- Re-authentication required

### Debug Mode
Enable debug logging by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Support

If you encounter issues:

1. **Check Database Connection**: Verify DB_URL is correct
2. **Run Setup Script**: Ensure authentication tables exist
3. **Check Logs**: Look for error messages in console
4. **Verify Dependencies**: Ensure all packages are installed

## 🔄 Migration from Non-Auth Version

If you're upgrading from a version without authentication:

1. **Backup Data**: Export existing data
2. **Run Setup**: Execute `setup_auth.py`
3. **Create Admin**: Set up admin user
4. **Migrate Data**: Assign existing data to admin user (if needed)

## 📈 Next Steps

After setting up authentication:

1. **Create Users**: Add team members through admin panel
2. **Configure Permissions**: Set up role-based access
3. **Import Data**: Migrate existing project data
4. **Train Team**: Onboard users to the system

---

**🎉 Congratulations!** Your Project Tracker now has secure, multi-user authentication with data isolation and professional user management. 