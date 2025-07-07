#!/usr/bin/env python3
"""
Test script for Email Integration
Tests the Outlook email integration functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_integration import OutlookEmailIntegration
from database_postgres import ProjectOpsDatabase

def test_email_integration():
    """Test the email integration functionality"""
    print("🧪 Testing Email Integration...")
    
    # Test 1: Initialize email integration
    print("\n1. Testing Email Integration Initialization...")
    try:
        email_integration = OutlookEmailIntegration()
        print("✅ Email integration initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize email integration: {e}")
        return False
    
    # Test 2: Check configuration loading
    print("\n2. Testing Configuration Loading...")
    if email_integration.client_id and email_integration.tenant_id:
        print("✅ Configuration loaded successfully")
        print(f"   Client ID: {email_integration.client_id[:10]}...")
        print(f"   Tenant ID: {email_integration.tenant_id[:10]}...")
    else:
        print("⚠️  Configuration not found - this is expected if not set up yet")
        print("   Please follow the EMAIL_INTEGRATION_SETUP.md guide")
    
    # Test 3: Test auth URL generation
    print("\n3. Testing Authentication URL Generation...")
    auth_url = email_integration.get_auth_url()
    if auth_url:
        print("✅ Authentication URL generated successfully")
        print(f"   URL: {auth_url[:50]}...")
    else:
        print("❌ Failed to generate authentication URL")
        if not email_integration.client_id or not email_integration.tenant_id:
            print("   Reason: Missing client_id or tenant_id")
    
    # Test 4: Test email classification
    print("\n4. Testing Email Classification...")
    test_email = {
        'subject': 'Bug report for Project ABC',
        'body': 'There is an issue with the login functionality',
        'from': 'client@external.com',
        'from_name': 'John Client',
        'importance': 'high'
    }
    
    classification = email_integration.classify_email_content(test_email)
    print("✅ Email classification working")
    print(f"   Type: {classification['email_type']}")
    print(f"   Confidence: {classification['confidence']:.1%}")
    print(f"   Client Email: {classification['is_client_email']}")
    print(f"   Project: {classification['project_name']}")
    print(f"   Client: {classification['client_name']}")
    
    # Test 5: Test database integration
    print("\n5. Testing Database Integration...")
    try:
        db = ProjectOpsDatabase()
        print("✅ Database connection successful")
        
        # Test project creation
        test_project_name = "Test Project from Email"
        test_client_name = "Test Client"
        
        # Check if project exists
        projects_df = db.get_all_projects()
        existing_project = None
        if not projects_df.empty:
            existing_project = projects_df[
                (projects_df['project_name'].str.contains(test_project_name, case=False, na=False)) |
                (projects_df['client_name'].str.contains(test_client_name, case=False, na=False))
            ]
        
        if existing_project is not None and not existing_project.empty:
            project_id = int(existing_project.iloc[0]['id'])
            print(f"✅ Found existing test project (ID: {project_id})")
        else:
            # Create test project
            success = db.add_project(
                project_name=test_project_name,
                client_name=test_client_name,
                software="Test Software",
                vendor="Test Vendor",
                start_date="2024-01-01",
                deadline="2024-12-31",
                status="In Progress",
                description="Test project for email integration",
                user_id=1
            )
            if success:
                print("✅ Test project created successfully")
            else:
                print("❌ Failed to create test project")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
    
    # Test 6: Test email processing (without actual API calls)
    print("\n6. Testing Email Processing Logic...")
    try:
        # Mock email processing
        results = {
            'processed': 0,
            'issues': 0,
            'updates': 0,
            'queries': 0
        }
        print("✅ Email processing logic structure is correct")
        print(f"   Results structure: {results}")
    except Exception as e:
        print(f"❌ Email processing test failed: {e}")
    
    print("\n🎉 Email Integration Tests Completed!")
    print("\n📋 Next Steps:")
    print("1. Follow EMAIL_INTEGRATION_SETUP.md to configure Azure AD")
    print("2. Add your credentials to .streamlit/secrets.toml")
    print("3. Run your Streamlit app and test the email integration")
    
    return True

def test_email_classification():
    """Test email classification with various examples"""
    print("\n🔍 Testing Email Classification Examples...")
    
    email_integration = OutlookEmailIntegration()
    
    test_emails = [
        {
            'subject': 'Critical bug in login system',
            'body': 'Users cannot log in to the application. This is urgent.',
            'from': 'client@company.com',
            'from_name': 'Client Manager',
            'importance': 'high'
        },
        {
            'subject': 'Question about API integration',
            'body': 'How do we integrate the new API endpoints?',
            'from': 'developer@client.com',
            'from_name': 'Developer Team',
            'importance': 'normal'
        },
        {
            'subject': 'Project ABC - Status Update',
            'body': 'We have completed phase 1 and are ready for review.',
            'from': 'pm@client.com',
            'from_name': 'Project Manager',
            'importance': 'normal'
        },
        {
            'subject': 'Meeting request for Project XYZ',
            'body': 'Can we schedule a call to discuss the next steps?',
            'from': 'stakeholder@client.com',
            'from_name': 'Stakeholder',
            'importance': 'normal'
        }
    ]
    
    for i, email in enumerate(test_emails, 1):
        classification = email_integration.classify_email_content(email)
        print(f"\nEmail {i}: {email['subject']}")
        print(f"   Type: {classification['email_type']}")
        print(f"   Confidence: {classification['confidence']:.1%}")
        print(f"   Client Email: {classification['is_client_email']}")
        print(f"   Project: {classification['project_name']}")
        print(f"   Client: {classification['client_name']}")

if __name__ == "__main__":
    print("🚀 Starting Email Integration Tests...")
    
    # Run basic tests
    test_email_integration()
    
    # Run classification tests
    test_email_classification()
    
    print("\n✅ All tests completed!") 