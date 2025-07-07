# 🚀 Neon PostgreSQL Database Setup Guide

## Overview
This guide will help you set up a Neon PostgreSQL database for your ProjectOps Assistant to enable persistent data storage on Streamlit Cloud.

## 📋 Prerequisites
- GitHub account
- Streamlit Cloud account
- Neon account (free tier available)

---

## 🔧 Step 1: Create Neon Database

### 1.1 Sign Up for Neon
1. Go to [neon.tech](https://neon.tech)
2. Click "Sign Up" and create an account
3. Complete the registration process

### 1.2 Create a New Project
1. Click "Create New Project"
2. Choose a project name (e.g., "projectops-assistant")
3. Select a region close to your users
4. Click "Create Project"

### 1.3 Get Connection Details
1. After project creation, you'll see the connection details
2. Note down the following information:
   - **Host**: `ep-something-123456.us-east-2.aws.neon.tech`
   - **Database**: `neondb` (default)
   - **Username**: Your username
   - **Password**: Your password
   - **Port**: `5432` (default)

### 1.4 Connection String Format
Your connection string will look like this:
```
postgresql://username:password@ep-something-123456.us-east-2.aws.neon.tech:5432/neondb
```

---

## 🔐 Step 2: Configure Streamlit Cloud Secrets

### 2.1 Access Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Find your ProjectOps Assistant app

### 2.2 Add Database Secret
1. Click on your app
2. Go to "Settings" → "Secrets"
3. Add the following secret:
   ```toml
   DB_URL = "postgresql://username:password@ep-something-123456.us-east-2.aws.neon.tech:5432/neondb"
   ```
4. Replace with your actual Neon connection string
5. Click "Save"

---

## 📦 Step 3: Update Your Repository

### 3.1 Files to Update
Make sure these files are in your repository:

1. **`requirements.txt`** - Contains PostgreSQL dependencies
2. **`database_postgres.py`** - PostgreSQL database module
3. **`streamlit_app.py`** - Updated to use PostgreSQL

### 3.2 Commit and Push
```bash
git add .
git commit -m "Add PostgreSQL support with Neon database"
git push
```

---

## 🧪 Step 4: Test the Connection

### 4.1 Deploy and Test
1. Streamlit Cloud will automatically redeploy
2. Check the app logs for connection status
3. You should see: "✅ Connected to database successfully!"

### 4.2 Add Test Data
1. Go to "Project Tracker" → "Add New Project"
2. Add a test project
3. Verify it appears in "All Projects"

---

## 🔍 Step 5: Verify Database Setup

### 5.1 Check Neon Dashboard
1. Go to your Neon project dashboard
2. Click on "Tables" to see created tables:
   - `projects`
   - `meetings`
   - `client_updates`
   - `issues`

### 5.2 Test Data Persistence
1. Add some test data through the app
2. Restart the Streamlit app
3. Verify data persists

---

## 🛠️ Troubleshooting

### Connection Issues
**Error**: "Database connection failed"
**Solution**:
1. Check your connection string format
2. Verify credentials in Streamlit secrets
3. Ensure Neon database is active

### Table Creation Issues
**Error**: "Error creating tables"
**Solution**:
1. Check database permissions
2. Verify connection string includes database name
3. Check Neon logs for errors

### Import Errors
**Error**: "Module not found"
**Solution**:
1. Ensure `psycopg2-binary` is in requirements.txt
2. Check all dependencies are installed
3. Verify file names match imports

---

## 📊 Database Schema

### Projects Table
```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
    client_name VARCHAR(255) NOT NULL,
    software VARCHAR(100) NOT NULL,
    vendor VARCHAR(255),
    start_date VARCHAR(20),
    deadline VARCHAR(20),
    status VARCHAR(50) DEFAULT 'In Progress',
    description TEXT,
    file_path VARCHAR(500)
);
```

### Meetings Table
```sql
CREATE TABLE meetings (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    meeting_date VARCHAR(20) NOT NULL,
    attendees VARCHAR(500),
    agenda VARCHAR(500),
    mom TEXT,
    next_steps TEXT,
    follow_up_date VARCHAR(20)
);
```

### Client Updates Table
```sql
CREATE TABLE client_updates (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    update_date VARCHAR(20) NOT NULL,
    summary TEXT,
    sent_by VARCHAR(255),
    mode VARCHAR(50),
    client_feedback TEXT,
    next_step TEXT
);
```

### Issues Table
```sql
CREATE TABLE issues (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    date_reported VARCHAR(20) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'Pending',
    assigned_to VARCHAR(255),
    resolution_date VARCHAR(20)
);
```

---

## 🔒 Security Best Practices

### 1. Environment Variables
- Never commit database credentials to Git
- Use Streamlit Cloud secrets for sensitive data
- Rotate passwords regularly

### 2. Database Access
- Use read-only connections when possible
- Limit database user permissions
- Monitor database access logs

### 3. Connection Security
- Use SSL connections (Neon provides this by default)
- Keep connection strings secure
- Use connection pooling for production

---

## 📈 Performance Optimization

### 1. Connection Pooling
For production apps, consider using connection pooling:
```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    connection_string,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10
)
```

### 2. Query Optimization
- Use indexes on frequently queried columns
- Limit result sets with pagination
- Use appropriate data types

### 3. Monitoring
- Monitor database performance
- Set up alerts for connection issues
- Track query performance

---

## 🎉 Success Checklist

- [ ] Neon account created
- [ ] Database project created
- [ ] Connection string obtained
- [ ] Streamlit Cloud secrets configured
- [ ] Code updated and deployed
- [ ] Database connection successful
- [ ] Tables created automatically
- [ ] Test data added successfully
- [ ] Data persistence verified

---

## 📞 Support

### Neon Support
- [Neon Documentation](https://neon.tech/docs)
- [Neon Community](https://community.neon.tech)
- [Neon Status](https://status.neon.tech)

### Streamlit Support
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Community](https://discuss.streamlit.io)

---

**🎯 Your ProjectOps Assistant now has persistent data storage with Neon PostgreSQL!**

Data will persist across deployments and be accessible from anywhere in the world. 