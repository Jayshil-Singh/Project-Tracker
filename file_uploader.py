import streamlit as st
import os
import tempfile
from datetime import datetime
import base64

class FileUploader:
    def __init__(self):
        """Initialize file uploader for cloud environment"""
        self.upload_dir = self._get_upload_directory()
    
    def _get_upload_directory(self):
        """Get upload directory for cloud environment"""
        # In cloud environment, use temporary directory
        upload_dir = os.path.join(tempfile.gettempdir(), "projectops_uploads")
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir
    
    def upload_file(self, uploaded_file, project_name, client_name):
        """Upload a file and return the file path"""
        if uploaded_file is not None:
            try:
                # Create client-specific directory
                client_dir = os.path.join(self.upload_dir, client_name.replace(" ", "_"))
                os.makedirs(client_dir, exist_ok=True)
                
                # Create project-specific subdirectory
                project_dir = os.path.join(client_dir, project_name.replace(" ", "_"))
                os.makedirs(project_dir, exist_ok=True)
                
                # Generate unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_extension = os.path.splitext(uploaded_file.name)[1]
                filename = f"{timestamp}_{uploaded_file.name}"
                file_path = os.path.join(project_dir, filename)
                
                # Save the file
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.success(f"✅ File uploaded successfully: {uploaded_file.name}")
                return file_path
                
            except Exception as e:
                st.error(f"❌ File upload failed: {e}")
                return None
        return None
    
    def get_file_download_link(self, file_path, file_name):
        """Generate a download link for a file"""
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            
            b64 = base64.b64encode(data).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}">📥 Download {file_name}</a>'
            return href
        except Exception as e:
            st.error(f"❌ Error generating download link: {e}")
            return None
    
    def list_project_files(self, project_name, client_name):
        """List all files for a specific project"""
        try:
            client_dir = os.path.join(self.upload_dir, client_name.replace(" ", "_"))
            project_dir = os.path.join(client_dir, project_name.replace(" ", "_"))
            
            if os.path.exists(project_dir):
                files = []
                for filename in os.listdir(project_dir):
                    file_path = os.path.join(project_dir, filename)
                    if os.path.isfile(file_path):
                        file_size = os.path.getsize(file_path)
                        file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                        files.append({
                            'name': filename,
                            'path': file_path,
                            'size': file_size,
                            'date': file_date
                        })
                return files
            return []
        except Exception as e:
            st.error(f"❌ Error listing files: {e}")
            return []
    
    def delete_file(self, file_path):
        """Delete a file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                st.success("✅ File deleted successfully")
                return True
            return False
        except Exception as e:
            st.error(f"❌ Error deleting file: {e}")
            return False

def render_file_upload_section(project_name, client_name):
    """Render file upload section in the app"""
    st.subheader("📁 File Upload")
    
    uploader = FileUploader()
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload project documents",
        type=['pdf', 'docx', 'doc', 'xlsx', 'xls', 'jpg', 'jpeg', 'png', 'txt'],
        help="Upload contracts, specifications, or other project documents"
    )
    
    if uploaded_file:
        st.info(f"📄 Selected file: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        if st.button("📤 Upload File", key="upload_btn"):
            file_path = uploader.upload_file(uploaded_file, project_name, client_name)
            if file_path:
                st.success(f"✅ File uploaded to: {file_path}")
                return file_path
    
    return None

def render_file_management_section(project_name, client_name):
    """Render file management section"""
    st.subheader("📂 Project Files")
    
    uploader = FileUploader()
    files = uploader.list_project_files(project_name, client_name)
    
    if files:
        st.write(f"Found {len(files)} files for this project:")
        
        for file_info in files:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.write(f"📄 {file_info['name']}")
            
            with col2:
                st.write(f"Size: {file_info['size']:,} bytes")
            
            with col3:
                st.write(f"Date: {file_info['date'].strftime('%Y-%m-%d %H:%M')}")
            
            with col4:
                # Download button
                download_link = uploader.get_file_download_link(file_info['path'], file_info['name'])
                if download_link:
                    st.markdown(download_link, unsafe_allow_html=True)
                
                # Delete button
                if st.button("🗑️", key=f"delete_{file_info['name']}", help="Delete file"):
                    if uploader.delete_file(file_info['path']):
                        st.rerun()
    else:
        st.info("📁 No files uploaded for this project yet.")

def render_bulk_file_upload():
    """Render bulk file upload section"""
    st.subheader("📦 Bulk File Upload")
    
    uploader = FileUploader()
    
    # Project selection
    from database_postgres import ProjectOpsDatabase
    db = ProjectOpsDatabase()
    projects = db.get_all_projects()
    
    if not projects.empty:
        project_options = projects[['id', 'project_name', 'client_name']].values.tolist()
        project_dict = {f"{name} ({client})": (id, name, client) for id, name, client in project_options}
        
        selected_project = st.selectbox(
            "Select project for file upload",
            list(project_dict.keys())
        )
        
        if selected_project:
            project_id, project_name, client_name = project_dict[selected_project]
            
            # Multiple file upload
            uploaded_files = st.file_uploader(
                "Upload multiple files",
                type=['pdf', 'docx', 'doc', 'xlsx', 'xls', 'jpg', 'jpeg', 'png', 'txt'],
                accept_multiple_files=True,
                help="Select multiple files to upload"
            )
            
            if uploaded_files:
                st.write(f"📄 Selected {len(uploaded_files)} files:")
                for file in uploaded_files:
                    st.write(f"- {file.name} ({file.size} bytes)")
                
                if st.button("📤 Upload All Files", key="bulk_upload"):
                    uploaded_count = 0
                    for file in uploaded_files:
                        file_path = uploader.upload_file(file, project_name, client_name)
                        if file_path:
                            uploaded_count += 1
                    
                    st.success(f"✅ Successfully uploaded {uploaded_count}/{len(uploaded_files)} files")
    else:
        st.warning("⚠️ No projects found. Please create a project first.")

def render_file_analytics():
    """Render file analytics section"""
    st.subheader("📊 File Analytics")
    
    uploader = FileUploader()
    
    # Get all files across all projects
    all_files = []
    upload_dir = uploader.upload_dir
    
    if os.path.exists(upload_dir):
        for client_dir in os.listdir(upload_dir):
            client_path = os.path.join(upload_dir, client_dir)
            if os.path.isdir(client_path):
                for project_dir in os.listdir(client_path):
                    project_path = os.path.join(client_path, project_dir)
                    if os.path.isdir(project_path):
                        for filename in os.listdir(project_path):
                            file_path = os.path.join(project_path, filename)
                            if os.path.isfile(file_path):
                                file_size = os.path.getsize(file_path)
                                file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                                all_files.append({
                                    'client': client_dir.replace("_", " "),
                                    'project': project_dir.replace("_", " "),
                                    'name': filename,
                                    'size': file_size,
                                    'date': file_date
                                })
    
    if all_files:
        # Convert to DataFrame for analysis
        import pandas as pd
        files_df = pd.DataFrame(all_files)
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Files", len(all_files))
        
        with col2:
            total_size = sum(file['size'] for file in all_files)
            st.metric("Total Size", f"{total_size:,} bytes")
        
        with col3:
            unique_clients = len(files_df['client'].unique())
            st.metric("Clients", unique_clients)
        
        with col4:
            unique_projects = len(files_df['project'].unique())
            st.metric("Projects", unique_projects)
        
        # File type analysis
        st.subheader("📈 File Type Distribution")
        file_extensions = [os.path.splitext(file['name'])[1].lower() for file in all_files]
        extension_counts = pd.Series(file_extensions).value_counts()
        
        if not extension_counts.empty:
            st.bar_chart(extension_counts)
        
        # Recent files
        st.subheader("🕒 Recent Files")
        recent_files = sorted(all_files, key=lambda x: x['date'], reverse=True)[:10]
        
        for file_info in recent_files:
            st.write(f"📄 {file_info['name']} - {file_info['client']}/{file_info['project']} - {file_info['date'].strftime('%Y-%m-%d %H:%M')}")
    
    else:
        st.info("📁 No files uploaded yet.") 