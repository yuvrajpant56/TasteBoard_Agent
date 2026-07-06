import os
import sys
import asyncio
import streamlit as st

# Add the parent directory to the path so we can import the coordinator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from coordinator import Coordinator

def run_tasteboard(idea):
    server_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp_server", "server.py")
    coordinator = Coordinator(server_path)
    return asyncio.run(coordinator.run_pipeline(idea))

# Configure page settings
st.set_page_config(page_title="TasteBoard | Market Intelligence", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for better aesthetics
st.markdown("""
<style>
    .reportview-container .main .block-container{
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3rem;
        font-weight: 600;
        font-size: 1.1rem;
    }
    .stTextArea textarea {
        border-radius: 8px;
    }
    h1, h2, h3 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #2e86de, #ff9f43);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for Input
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/10101/10101015.png", width=60) # Placeholder logo
    st.markdown("### **TasteBoard Agent**")
    st.caption("Data-Backed Market Research")
    st.divider()
    
    st.markdown("**Product Idea**")
    idea_input = st.text_area(
        "Describe your product idea in plain English:", 
        value="I want to build an AI tool that helps creators repurpose long YouTube videos into short clips, captions, and social posts.",
        height=150,
        label_visibility="collapsed"
    )
    
    run_btn = st.button("🚀 Run Analysis", type="primary")
    
    st.divider()
    st.markdown("### How it works")
    st.markdown("""
    1. **Query Agent**: Extracts keywords & targets.
    2. **Search Agent**: Finds live competitors.
    3. **Evidence Agent**: Scrapes pricing & ratings.
    4. **Review Agent**: Mines user complaints.
    5. **Scoring Agent**: Computes feasibility.
    6. **Report Agent**: Synthesizes the data.
    """)

# Main Content Area
if not run_btn:
    st.markdown('<p class="hero-title">TasteBoard</p>', unsafe_allow_html=True)
    st.markdown("### Turn your raw product idea into an actionable feasibility report in minutes.")
    st.info("👈 Enter your product idea in the sidebar and click **Run Analysis** to start the multi-agent pipeline.")
    
    # Placeholder layout
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Agents", value="8 Specialized")
    col2.metric(label="Data Sources", value="Live Web + Reviews")
    col3.metric(label="Output", value="12-Section Report")

else:
    if not idea_input.strip():
        st.sidebar.error("Please enter a product idea.")
    else:
        st.markdown('<p class="hero-title">Analysis Results</p>', unsafe_allow_html=True)
        st.caption(f"**Analyzing Idea:** {idea_input}")
        st.divider()
        
        with st.spinner("TasteBoard Multi-Agent Pipeline is running... This will take a couple of minutes."):
            report, charts = run_tasteboard(idea_input)
            
            if report:
                # Top metrics from the report could go here, but we'll show charts
                st.subheader("📊 Market Visualizations")
                
                if charts:
                    tab1, tab2, tab3, tab4 = st.tabs(["⭐ Ratings", "📈 Volume", "🗣️ Complaints", "🎯 Radar"])
                    
                    if "Rating Chart" in charts:
                        with tab1:
                            st.image(charts["Rating Chart"], use_container_width=True)
                    if "Review Volume Chart" in charts:
                        with tab2:
                            st.image(charts["Review Volume Chart"], use_container_width=True)
                    if "Complaint Frequency Chart" in charts:
                        with tab3:
                            st.image(charts["Complaint Frequency Chart"], use_container_width=True)
                    if "Opportunity Radar Chart" in charts:
                        with tab4:
                            st.image(charts["Opportunity Radar Chart"], use_container_width=True)
                else:
                    st.info("No charts were generated.")
                
                st.divider()
                
                st.subheader("📝 Founder Feasibility Report")
                with st.container(border=True):
                    st.markdown(report, unsafe_allow_html=True)
                
                st.sidebar.success("✅ Analysis Complete!")
            else:
                st.error("Pipeline failed to generate the report. Please check the logs.")
