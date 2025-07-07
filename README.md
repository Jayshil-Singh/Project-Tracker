# ProjectOps Assistant - Enterprise Project Management System

## 🚀 Overview

ProjectOps Assistant is a comprehensive, AI-powered project management dashboard designed for enterprise-level project tracking, client communication, and team collaboration. Built with Streamlit and featuring advanced analytics, the system provides a centralized platform for managing client projects, meetings, support issues, and real-time updates.

## ✨ Key Features

### 📊 Professional Dashboard
- **Real-time Metrics**: Live project statistics and KPIs
- **Interactive Charts**: Beautiful visualizations using Plotly
- **Status Tracking**: Visual project status distribution
- **Activity Feed**: Recent meetings and updates

### 🤖 AI-Powered Assistant
- **Natural Language Queries**: Ask questions about projects in plain English
- **Smart Insights**: Get instant project status and recommendations
- **Context-Aware Responses**: Understands project relationships and history

### 📁 Advanced Project Management
- **Multi-Software Support**: Epicor, MYOB, ODOO, PayGlobal, and more
- **File Management**: Upload and organize project documents
- **Client-Specific Folders**: Automatic organization by client
- **Status Tracking**: In Progress, Completed, On Hold

### 🗓️ Meeting & MoM Management
- **Comprehensive Logging**: Track all project meetings
- **Minutes of Meeting**: Detailed MoM recording
- **Follow-up Tracking**: Automated follow-up date management
- **Attendee Management**: Record meeting participants

### 🧾 Client Communication Hub
- **Update Logging**: Track all client communications
- **Feedback Management**: Record client feedback and responses
- **Communication History**: Complete audit trail
- **Multi-channel Support**: Email, Call, Meeting, Other

### 🛠️ Issue Tracking System
- **Issue Management**: Log and track project issues
- **Assignment Tracking**: Assign issues to team members
- **Resolution Tracking**: Monitor issue resolution progress
- **Status Updates**: Pending, In Progress, Resolved

### 📈 Advanced Analytics
- **Project Analytics**: Status distribution and trends
- **Client Analytics**: Project distribution by client
- **Software Analytics**: Technology stack analysis
- **Timeline Visualization**: Gantt chart project timelines
- **Performance Metrics**: Completion rates and KPIs

### 🔐 Enterprise Security
- **User Authentication**: Secure login system
- **Role-based Access**: Admin and user permissions
- **Data Protection**: Secure data storage and handling

## 🛠️ Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Backend**: SQLite database
- **AI/ML**: OpenAI GPT integration
- **Charts**: Plotly interactive visualizations
- **Authentication**: Streamlit-Authenticator
- **Reports**: PDF and Excel export capabilities

## 📦 Installation

### Prerequisites
- Python 3.8+
- Windows 10/11 (for C: drive organization)

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd ProjectOps-Assistant
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Directory Structure**
   ```bash
   python setup_directories.py
   ```

4. **Import Existing Projects** (Optional)
   ```bash
   python import_real_projects.py
   ```

5. **Run the Application**
   ```bash
   streamlit run app.py
   ```

## 🏗️ Directory Structure

```
C:\Projects\
├── ProjectOps-Assistant/
│   ├── app.py
│   ├── database.py
│   ├── chatbot.py
│   ├── reports.py
│   └── projectops.db
├── Client-Projects/
│   ├── Epicor/
│   │   ├── ATH/
│   │   ├── ATS/
│   │   ├── HFC/
│   │   └── LTA/
│   ├── MYOB/
│   ├── ODOO/
│   └── PayGlobal/
├── Backups/
└── Templates/
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Database Configuration
The system automatically creates and manages the SQLite database at:
```
C:\Projects\ProjectOps-Assistant\projectops.db
```

## 📊 Database Schema

### Projects Table
- `id`: Primary key
- `project_name`: Project identifier
- `client_name`: Client organization
- `software`: Technology platform
- `vendor`: Software vendor
- `start_date`: Project start date
- `deadline`: Project deadline
- `status`: Current status
- `description`: Project description
- `file_path`: Document storage path

### Meetings Table
- `id`: Primary key
- `project_id`: Foreign key to projects
- `meeting_date`: Meeting date
- `attendees`: Participant list
- `agenda`: Meeting agenda
- `mom`: Minutes of meeting
- `next_steps`: Action items
- `follow_up_date`: Follow-up deadline

### Client Updates Table
- `id`: Primary key
- `project_id`: Foreign key to projects
- `update_date`: Update date
- `summary`: Update summary
- `sent_by`: Sender information
- `mode`: Communication method
- `client_feedback`: Client response
- `next_step`: Next action

### Issues Table
- `id`: Primary key
- `project_id`: Foreign key to projects
- `date_reported`: Issue report date
- `description`: Issue description
- `status`: Current status
- `assigned_to`: Responsible person
- `resolution_date`: Resolution date

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Streamlit Cloud Deployment
1. Push code to GitHub repository
2. Connect repository to Streamlit Cloud
3. Deploy with environment variables

### Production Considerations
- Use PostgreSQL for production database
- Implement proper backup strategies
- Set up monitoring and logging
- Configure SSL certificates
- Implement rate limiting

## 🤖 AI Chatbot Usage

The AI assistant can handle queries like:
- "What's the status of Epicor for LTA?"
- "Show meetings for HFC"
- "What issues are unresolved?"
- "Show client updates for ATH"
- "Which projects are behind schedule?"

## 📈 Analytics Features

### Dashboard Metrics
- Total Projects Count
- Active Projects
- Total Meetings
- Pending Issues

### Visualizations
- Project Status Distribution (Pie Chart)
- Client Distribution (Pie Chart)
- Software Distribution (Bar Chart)
- Project Timeline (Gantt Chart)

### Performance Indicators
- Project Completion Rate
- Average Project Duration
- Meeting Frequency
- Issue Resolution Time

## 🔐 Security Features

- **Authentication**: Secure login system
- **Password Hashing**: bcrypt encryption
- **Session Management**: Secure session handling
- **Data Validation**: Input sanitization
- **File Upload Security**: Type and size validation

## 📋 Usage Examples

### Adding a New Project
1. Navigate to "Project Tracker"
2. Click "Add New Project"
3. Fill in project details
4. Upload relevant documents
5. Submit to create project

### Logging a Meeting
1. Go to "Meeting & MoM Log"
2. Select "Log New Meeting"
3. Choose project and date
4. Enter attendees and agenda
5. Record minutes and next steps

### Using the AI Assistant
1. Navigate to "AI Chatbot"
2. Type your question in natural language
3. Get instant insights and recommendations
4. Use quick action buttons for common queries

## 🐛 Troubleshooting

### Common Issues

**Authentication Error**
- Ensure credentials are properly configured
- Check password hashing

**Database Connection Error**
- Verify database file exists
- Check file permissions

**File Upload Issues**
- Ensure client directories exist
- Check disk space availability

**AI Chatbot Not Responding**
- Verify OpenAI API key
- Check internet connection

## 📞 Support

For technical support or feature requests:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 Version History

### v2.0.0 (Current)
- Professional UI redesign
- Advanced analytics dashboard
- Enhanced AI chatbot
- Improved file management
- Real-time metrics

### v1.0.0
- Basic project tracking
- Simple chatbot
- File uploads
- Authentication

## 📄 License

This project is proprietary software developed for enterprise use.

## 👥 Contributing

This is an internal enterprise tool. For modifications or enhancements, please contact the development team.

---

**ProjectOps Assistant** - Empowering Enterprise Project Management with AI 