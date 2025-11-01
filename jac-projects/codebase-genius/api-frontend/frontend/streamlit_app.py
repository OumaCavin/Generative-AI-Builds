"""
Streamlit Frontend for Codebase Genius
Interactive web interface for repository documentation generation
"""

import streamlit as st;
import requests;
import json;
import time;
import os;
import tempfile;
import zipfile;
from typing import Dict, Any, Optional;
import pandas as pd;
import plotly.express as px;
import plotly.graph_objects as go;

# Page configuration
st.set_page_config(
    page_title="Codebase Genius",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
);

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1rem 0;
        color: #2E86AB;
    }
    
    .status-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #2E86AB;
        background-color: #f8f9fa;
        margin: 0.5rem 0;
    }
    
    .success-card {
        border-left-color: #28a745;
        background-color: #d4edda;
    }
    
    .error-card {
        border-left-color: #dc3545;
        background-color: #f8d7da;
    }
    
    .warning-card {
        border-left-color: #ffc107;
        background-color: #fff3cd;
    }
    
    .progress-container {
        background: #e9ecef;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True);

# Constants
API_BASE_URL = "http://localhost:8000";
DEFAULT_HEADERS = {"Content-Type": "application/json"};

# Initialize session state
if 'workflow_id' not in st.session_state:
    st.session_state.workflow_id = None;
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None;
if 'current_step' not in st.session_state:
    st.session_state.current_step = "";
if 'progress' not in st.session_state:
    st.session_state.progress = 0.0;

# Helper Functions
def call_api(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
    """Make API calls with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}";
        
        if method == "GET":
            response = requests.get(url, headers=DEFAULT_HEADERS, timeout=30);
        elif method == "POST":
            response = requests.post(url, json=data, headers=DEFAULT_HEADERS, timeout=30);
        elif method == "DELETE":
            response = requests.delete(url, headers=DEFAULT_HEADERS, timeout=30);
        else:
            raise ValueError(f"Unsupported method: {method}");
            
        response.raise_for_status();
        return response.json();
        
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}");
        return {"error": str(e), "success": False};
    except Exception as e:
        st.error(f"Unexpected Error: {str(e)}");
        return {"error": str(e), "success": False};

def check_api_health() -> bool:
    """Check if API server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5);
        return response.status_code == 200;
    except:
        return False;

def validate_repository_url(url: str) -> bool:
    """Basic URL validation"""
    import re;
    
    # GitHub, GitLab, Bitbucket patterns
    patterns = [
        r'^https?://github\.com/[^/]+/[^/]+/?$',
        r'^https?://gitlab\.com/[^/]+/[^/]+/?$',
        r'^https?://bitbucket\.org/[^/]+/[^/]+/?$',
        r'^https?://[^/]+\.github\.com/[^/]+/[^/]+/?$'
    ];
    
    return any(re.match(pattern, url) for pattern in patterns);

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B";
        
    size_names = ["B", "KB", "MB", "GB"];
    i = 0;
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024;
        i += 1;
        
    return f"{size_bytes:.1f} {size_names[i]}";

def create_workflow_status_chart(progress: float, status: str) -> go.Figure:
    """Create a progress chart for workflow status"""
    fig = go.Figure();
    
    # Add progress arc
    fig.add_trace(go.Scatterpolar(
        r=[progress * 100, progress * 100, 0],
        theta=[0, 120, 240],
        fill='toself',
        fillcolor='rgba(46, 134, 171, 0.3)',
        line_color='rgba(46, 134, 171, 0.8)',
        name='Progress'
    ));
    
    # Customize chart
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 100])
        ),
        showlegend=False,
        title=f"Analysis Progress: {progress*100:.0f}%",
        font=dict(size=14)
    );
    
    return fig;

# Main Functions
def show_api_status():
    """Display API server status"""
    with st.expander("🔧 System Status", expanded=True):
        col1, col2, col3 = st.columns(3);
        
        with col1:
            api_healthy = check_api_health();
            if api_healthy:
                st.success("✅ API Server: Online");
            else:
                st.error("❌ API Server: Offline");
                st.info("Please start the API server with: `python main_api.py`");
                
        with col2:
            if api_healthy:
                workflows = call_api("/api/workflows");
                if workflows.get("success", True):
                    st.info(f"📊 Active Workflows: {workflows.get('total_active', 0)}");
                else:
                    st.warning("⚠️  Workflow status unavailable");
                    
        with col3:
            if api_healthy:
                config = call_api("/api/config");
                if config.get("success", True):
                    supported_formats = config.get("supported_formats", []);
                    st.info(f"📄 Formats: {', '.join(supported_formats)}");
                else:
                    st.warning("⚠️  Config unavailable");
                    
def show_repository_form():
    """Show repository input form"""
    st.markdown('<div class="section-header">🚀 Start New Analysis</div>', unsafe_allow_html=True);
    
    with st.form("analysis_form"):
        # Repository URL input
        repo_url = st.text_input(
            "Repository URL",
            placeholder="https://github.com/username/repository",
            help="Enter the URL of the repository you want to analyze"
        );
        
        # Column layout for form options
        col1, col2 = st.columns(2);
        
        with col1:
            branch = st.text_input(
                "Branch",
                value="main",
                help="Branch to analyze (default: main)"
            );
            
            analysis_depth = st.selectbox(
                "Analysis Depth",
                options=["basic", "full", "comprehensive"],
                index=1,
                help="Level of analysis detail"
            );
            
        with col2:
            format_options = st.selectbox(
                "Output Format",
                options=["markdown", "html", "pdf"],
                index=0,
                help="Documentation format"
            );
            
            include_diagrams = st.checkbox(
                "Include Diagrams",
                value=True,
                help="Generate code relationship diagrams"
            );
            
        # Submit button
        submitted = st.form_submit_button(
            "🧠 Start Analysis",
            type="primary",
            use_container_width=True
        );
        
        if submitted:
            # Validate inputs
            if not repo_url:
                st.error("❌ Repository URL is required");
                return;
                
            if not validate_repository_url(repo_url):
                st.error("❌ Invalid repository URL format");
                st.info("Supported formats: GitHub, GitLab, Bitbucket repositories");
                return;
                
            # Prepare request
            request_data = {
                "repository_url": repo_url,
                "branch": branch,
                "analysis_depth": analysis_depth,
                "include_diagrams": include_diagrams,
                "format": format_options
            };
            
            # Start analysis
            with st.spinner("Starting analysis..."):
                response = call_api("/api/analyze", method="POST", data=request_data);
                
            if response.get("success", True):
                workflow_id = response.get("workflow_id");
                if workflow_id:
                    st.session_state.workflow_id = workflow_id;
                    st.success(f"✅ Analysis started! Workflow ID: {workflow_id}");
                    st.rerun();
                else:
                    st.error("❌ Failed to get workflow ID");
            else:
                st.error(f"❌ Failed to start analysis: {response.get('error', 'Unknown error')}");

def show_workflow_status():
    """Display current workflow status"""
    if not st.session_state.workflow_id:
        return;
        
    workflow_id = st.session_state.workflow_id;
    
    st.markdown('<div class="section-header">📊 Analysis Status</div>', unsafe_allow_html=True);
    
    # Get workflow status
    status_response = call_api(f"/api/status/{workflow_id}");
    
    if not status_response.get("success", True):
        st.error(f"❌ Failed to get status: {status_response.get('error', 'Unknown error')}");
        return;
        
    status_data = status_response.get("data", status_response);
    
    # Extract status information
    status = status_data.get("status", "unknown");
    progress = status_data.get("progress", 0.0);
    current_step = status_data.get("current_step", "Unknown");
    error_message = status_data.get("error_message");
    
    # Update session state
    st.session_state.progress = progress;
    st.session_state.current_step = current_step;
    
    # Status cards
    col1, col2, col3 = st.columns(3);
    
    with col1:
        if status == "pending":
            st.markdown('<div class="status-card warning-card">⏳ Status: Pending</div>', unsafe_allow_html=True);
        elif status == "running":
            st.markdown('<div class="status-card">🔄 Status: Running</div>', unsafe_allow_html=True);
        elif status == "completed":
            st.markdown('<div class="status-card success-card">✅ Status: Completed</div>', unsafe_allow_html=True);
        elif status == "failed":
            st.markdown('<div class="status-card error-card">❌ Status: Failed</div>', unsafe_allow_html=True);
        else:
            st.markdown(f'<div class="status-card">❓ Status: {status}</div>', unsafe_allow_html=True);
            
    with col2:
        st.markdown(f'<div class="status-card">📍 Current Step: {current_step}</div>', unsafe_allow_html=True);
        
    with col3:
        st.markdown(f'<div class="status-card">📈 Progress: {progress*100:.0f}%</div>', unsafe_allow_html=True);
    
    # Progress bar and chart
    st.progress(progress);
    
    # Create and display progress chart
    if status in ["pending", "running", "completed"]:
        fig = create_workflow_status_chart(progress, status);
        st.plotly_chart(fig, use_container_width=True);
        
    # Error message
    if error_message:
        st.error(f"❌ Error: {error_message}");
        
    # Handle completed workflow
    if status == "completed" and "result" in status_data:
        st.session_state.analysis_results = status_data["result"];
        show_analysis_results();
        
    # Auto-refresh for running workflows
    if status in ["pending", "running"]:
        st.info("🔄 Refreshing status every 5 seconds...");
        time.sleep(5);
        st.rerun();

def show_analysis_results():
    """Display analysis results and download options"""
    if not st.session_state.analysis_results:
        return;
        
    st.markdown('<div class="section-header">📋 Analysis Results</div>', unsafe_allow_html=True);
    
    results = st.session_state.analysis_results;
    documentation = results.get("documentation", {});
    files = results.get("files", []);
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📁 File Analysis", "📄 Documentation", "⬇️ Downloads"]);
    
    with tab1:
        st.subheader("Repository Overview");
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4);
        
        with col1:
            st.metric("Total Files", len(files));
            
        with col2:
            file_types = {};
            for file_info in files:
                ext = os.path.splitext(file_info["path"])[1] or "no_extension";
                file_types[ext] = file_types.get(ext, 0) + 1;
            st.metric("File Types", len(file_types));
            
        with col3:
            total_size = sum(file_info["size"] for file_info in files);
            st.metric("Total Size", format_file_size(total_size));
            
        with col4:
            analysis_details = documentation.get("analysis_details", {});
            st.metric("Repository URL", analysis_details.get("repository_url", "Unknown"));
            
        # File type distribution chart
        if file_types:
            fig = px.pie(
                values=list(file_types.values()),
                names=list(file_types.keys()),
                title="File Type Distribution"
            );
            st.plotly_chart(fig, use_container_width=True);
            
    with tab2:
        st.subheader("File Analysis");
        
        if files:
            # Create DataFrame for file data
            df = pd.DataFrame([
                {
                    "File Path": file_info["path"],
                    "Size": format_file_size(file_info["size"]),
                    "Type": file_info["type"]
                }
                for file_info in files
            ]);
            
            # Display with filtering
            col1, col2 = st.columns([2, 1]);
            
            with col1:
                filter_type = st.selectbox(
                    "Filter by Type",
                    options=["All"] + list(df["Type"].unique()),
                    index=0
                );
                
                if filter_type != "All":
                    df_filtered = df[df["Type"] == filter_type];
                else:
                    df_filtered = df;
                    
                st.dataframe(df_filtered, use_container_width=True, height=400);
                
            with col2:
                st.subheader("Summary");
                st.info(f"Showing {len(df_filtered)} of {len(df)} files");
                
                # File type breakdown
                type_counts = df_filtered["Type"].value_counts();
                for file_type, count in type_counts.items():
                    st.write(f"**{file_type}:** {count} files");
        else:
            st.info("No file data available");
            
    with tab3:
        st.subheader("Generated Documentation");
        
        doc_content = documentation.get("content", "No documentation content available");
        
        # Display preview
        st.markdown(doc_content);
        
        # Show metadata
        with st.expander("📋 Metadata"):
            st.json(documentation);
            
    with tab4:
        st.subheader("Download Documentation");
        
        download_url = results.get("download_url");
        
        if download_url:
            col1, col2 = st.columns(2);
            
            with col1:
                st.info("📦 Generated Package Includes:");
                st.markdown("""
                - **Main Documentation** (selected format)
                - **Metadata** (JSON)
                - **Analysis Results**
                """);
                
            with col2:
                if st.button("⬇️ Download Documentation", type="primary", use_container_width=True):
                    try:
                        # Create download link
                        download_link = f"{API_BASE_URL}{download_url}";
                        st.markdown(f'''
                        <a href="{download_link}" download>
                            <button style="background-color: #2E86AB; color: white; padding: 10px 20px; 
                                         border: none; border-radius: 5px; cursor: pointer; width: 100%;">
                                📥 Click to Download
                            </button>
                        </a>
                        ''', unsafe_allow_html=True);
                        
                    except Exception as e:
                        st.error(f"Download failed: {str(e)}");
        else:
            st.warning("Download URL not available");
            
    # Clear workflow button
    if st.button("🗑️ Clear Results"):
        st.session_state.workflow_id = None;
        st.session_state.analysis_results = None;
        st.rerun();

def show_workflow_management():
    """Show workflow management options"""
    st.markdown('<div class="section-header">🗂️ Workflow Management</div>', unsafe_allow_html=True);
    
    # Get all workflows
    workflows_response = call_api("/api/workflows");
    
    if not workflows_response.get("success", True):
        st.error(f"Failed to get workflows: {workflows_response.get('error', 'Unknown error')}");
        return;
        
    workflows_data = workflows_response.get("data", workflows_response);
    active_workflows = workflows_data.get("active_workflows", []);
    completed_workflows = workflows_data.get("completed_workflows", []);
    
    if not active_workflows and not completed_workflows:
        st.info("No workflows found. Start a new analysis above.");
        return;
        
    # Display workflows
    if active_workflows:
        st.subheader("🔄 Active Workflows");
        for workflow_id in active_workflows:
            col1, col2 = st.columns([3, 1]);
            
            with col1:
                st.code(workflow_id);
                
            with col2:
                if st.button("❌ Cancel", key=f"cancel_{workflow_id}"):
                    # Cancel workflow (implementation depends on API)
                    st.info(f"Workflow {workflow_id} cancellation requested");
                    
    if completed_workflows:
        st.subheader("✅ Completed Workflows");
        for workflow_id in completed_workflows:
            col1, col2, col3 = st.columns([2, 2, 1]);
            
            with col1:
                st.code(workflow_id);
                
            with col2:
                # Get status for download link
                status_response = call_api(f"/api/status/{workflow_id}");
                if status_response.get("success", True):
                    status_data = status_response.get("data", status_response);
                    if status_data.get("status") == "completed":
                        download_url = status_data.get("result", {}).get("download_url");
                        if download_url:
                            st.markdown(f"[📥 Download]({API_BASE_URL}{download_url})");
                            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{workflow_id}"):
                    # Delete workflow
                    delete_response = call_api(f"/api/workflows/{workflow_id}", method="DELETE");
                    if delete_response.get("success", True):
                        st.success("Workflow deleted");
                        st.rerun();
                    else:
                        st.error(f"Delete failed: {delete_response.get('error', 'Unknown error')}");

# Main UI
def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<div class="main-header">🧠 Codebase Genius</div>', unsafe_allow_html=True);
    st.markdown("### AI-Powered Codebase Documentation Generator");
    st.markdown("Transform any repository into comprehensive, professional documentation with our multi-agent system.");
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🔧 Navigation");
        
        page = st.selectbox(
            "Select Page",
            options=["🚀 New Analysis", "📊 Status", "📋 Results", "🗂️ Management", "ℹ️ About"]
        );
        
        st.markdown("---");
        
        # Quick stats
        st.markdown("### 📈 Quick Stats");
        
        if check_api_health():
            workflows = call_api("/api/workflows");
            if workflows.get("success", True):
                active = workflows.get("data", workflows).get("total_active", 0);
                completed = workflows.get("data", workflows).get("total_completed", 0);
                st.metric("Active", active);
                st.metric("Completed", completed);
        
    # Main content based on selected page
    if page == "🚀 New Analysis":
        show_api_status();
        show_repository_form();
        
    elif page == "📊 Status":
        if st.session_state.workflow_id:
            show_workflow_status();
        else:
            st.info("No active workflow. Start a new analysis first.");
            
    elif page == "📋 Results":
        if st.session_state.analysis_results:
            show_analysis_results();
        else:
            st.info("No analysis results available. Complete an analysis first.");
            
    elif page == "🗂️ Management":
        show_workflow_management();
        
    elif page == "ℹ️ About":
        st.markdown("### About Codebase Genius");
        st.markdown("""
        **Codebase Genius** is an AI-powered multi-agent system designed to automatically generate 
        comprehensive documentation for any codebase. The system consists of four specialized agents:
        
        #### 🗂️ Repository Mapper
        - Clones and analyzes repository structure
        - Generates file trees and summaries
        - Identifies project architecture
        
        #### 🔍 Code Analyzer
        - Parses source code using Tree-sitter
        - Constructs Code Context Graph (CCG)
        - Maps relationships between functions, classes, and modules
        
        #### 📝 DocGenie
        - Generates comprehensive markdown documentation
        - Creates code relationship diagrams
        - Adds citations and cross-references
        
        #### 🎯 Supervisor
        - Orchestrates the entire workflow
        - Manages task delegation
        - Ensures quality and consistency
        
        #### ✨ Features
        - **Multi-Repository Support**: GitHub, GitLab, Bitbucket
        - **Multiple Formats**: Markdown, HTML, PDF
        - **Real-time Progress**: Track analysis status
        - **Quality Validation**: Multi-dimensional assessment
        - **Scalable Architecture**: Handles large repositories
        """);
        
        st.markdown("#### 🔧 Technical Stack");
        st.markdown("""
        - **Backend**: Python, FastAPI, Jac (multi-agent framework)
        - **Frontend**: Streamlit, Plotly, Pandas
        - **Code Analysis**: Tree-sitter, AST parsing
        - **Documentation**: Markdown, HTML generation
        - **Testing**: Pytest, comprehensive test suite
        """);

if __name__ == "__main__":
    main();
