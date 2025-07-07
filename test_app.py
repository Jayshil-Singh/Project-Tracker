import streamlit as st

st.set_page_config(
    page_title="ProjectOps Test",
    page_icon="📊",
    layout="wide"
)

st.title("🚀 ProjectOps Assistant - Test Deployment")

st.success("✅ Streamlit Cloud deployment is working!")

st.markdown("""
## Test Components

### Basic Streamlit
- ✅ Page config
- ✅ Title and markdown
- ✅ Success message

### Next Steps
1. If this works, the issue is in the main app dependencies
2. We can then debug the specific import or database issues
3. Gradually add back features

### Current Status
- **Deployment**: Testing basic functionality
- **Database**: Not yet connected
- **Authentication**: Not yet implemented
""")

# Test basic components
if st.button("Test Button"):
    st.write("Button works! ✅")

# Test data display
import pandas as pd
test_data = pd.DataFrame({
    'Project': ['Test Project 1', 'Test Project 2'],
    'Status': ['In Progress', 'Completed']
})
st.dataframe(test_data)

st.info("If you can see this test app, the basic deployment is working!") 