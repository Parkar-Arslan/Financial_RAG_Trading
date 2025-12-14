import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import Settings
from llm.chat_engine import TradingAssistant

# Page Configuration
st.set_page_config(
    page_title="TradingRAG Pro | AI Financial Assistant",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Dark Theme CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main App Container */
    .stApp {
        background: linear-gradient(180deg, #0f0f1e 0%, #1a1a2e 100%);
    }
    
    /* Custom Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        animation: slideDown 0.5s ease-out;
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    
    .header-stats {
        display: flex;
        gap: 2rem;
        margin-top: 1rem;
    }
    
    .stat-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.9rem;
    }
    
    .pulse-dot {
        width: 8px;
        height: 8px;
        background: #4ade80;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% {
            box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.7);
        }
        70% {
            box-shadow: 0 0 0 10px rgba(74, 222, 128, 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(74, 222, 128, 0);
        }
    }
    
    /* Card Styles */
    .custom-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .custom-card:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Message Styles */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        animation: fadeInRight 0.3s ease-out;
    }
    
    .ai-message {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #e0e0e0;
        padding: 1.2rem;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        animation: fadeInLeft 0.3s ease-out;
    }
    
    @keyframes fadeInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes fadeInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Input Field Styles */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Sidebar Styles */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1e 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .metric-label {
        color: #a0a0a0;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* Source Cards */
    .source-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .source-card:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: #667eea;
        transform: translateX(5px);
    }
    
    /* Trading Signal Pills */
    .signal-pill {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .signal-bullish {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .signal-bearish {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }
    
    /* Loading Animation */
    .loading-dots {
        display: inline-flex;
        gap: 0.3rem;
    }
    
    .loading-dots span {
        width: 8px;
        height: 8px;
        background: #667eea;
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out both;
    }
    
    .loading-dots span:nth-child(1) {
        animation-delay: -0.32s;
    }
    
    .loading-dots span:nth-child(2) {
        animation-delay: -0.16s;
    }
    
    @keyframes bounce {
        0%, 80%, 100% {
            transform: scale(0);
        }
        40% {
            transform: scale(1);
        }
    }
    
    /* Scrollbar Styles */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.5);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.7);
    }
    
    /* Expander Styles */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #e0e0e0 !important;
    }
    
    /* Tab Styles */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 0.25rem;
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #a0a0a0;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(147, 51, 234, 0.1) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(239, 68, 68, 0.1) 100%);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Multiselect Styles */
    .stMultiSelect > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    
    /* Slider Styles */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'trading_assistant' not in st.session_state:
    if Settings.validate():
        with st.spinner("🚀 Initializing AI Trading Assistant..."):
            st.session_state.trading_assistant = TradingAssistant()
    else:
        st.session_state.trading_assistant = None

# Animated Header
st.markdown("""
<div class="main-header">
    <h1>💹 TradingRAG Pro</h1>
    <p>AI-Powered Financial Research & Trading Intelligence</p>
    <div class="header-stats">
        <div class="stat-item">
            <div class="pulse-dot"></div>
            <span>Live System</span>
        </div>
        <div class="stat-item">
            <span>🔥 Powered by Advanced AI</span>
        </div>
        <div class="stat-item">
            <span>📊 Real-Time Analysis</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Check configuration
if st.session_state.trading_assistant is None:
    st.markdown("""
    <div class="warning-box">
        <h3>⚠️ Configuration Required</h3>
        <p>Please set up your API keys to start using TradingRAG Pro:</p>
        <ol>
            <li>Get a FREE Groq API key from console.groq.com/keys</li>
            <li>Add it to your .env file</li>
            <li>Restart the application</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Sidebar with Glass Morphism
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <h2 style="color: #667eea; margin: 0;">⚙️ Control Panel</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Market Selection
    st.markdown("### 📈 Market Selection")
    selected_tickers = st.multiselect(
        "Choose Stocks",
        Settings.DEFAULT_TICKERS,
        default=["AAPL", "NVDA", "TSLA"],
        help="Select up to 5 stocks for analysis"
    )
    
    # Document Filters
    st.markdown("### 📄 Data Sources")
    doc_types = st.multiselect(
        "Document Types",
        Settings.DOCUMENT_TYPES,
        default=Settings.DOCUMENT_TYPES[:2],
        help="Select data sources to search"
    )
    
    # Analysis Configuration
    st.markdown("### 🎯 Analysis Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        retrieval_k = st.slider(
            "Sources",
            min_value=3,
            max_value=10,
            value=5,
            help="Number of documents to retrieve"
        )
    
    with col2:
        st.metric("Quality", "High", delta="+95%")
    
    analysis_mode = st.selectbox(
        "Analysis Type",
        ["Comprehensive", "Quick Summary", "Risk-Focused", "Growth-Focused"],
        help="Choose analysis depth and focus"
    )
    
    # System Stats
    st.markdown("---")
    st.markdown("### 📊 System Status")
    
    if st.session_state.trading_assistant:
        stats = st.session_state.trading_assistant.chroma_manager.get_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{stats.get('total_documents', 0):,}</div>
                <div class="metric-label">Documents</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">500+</div>
                <div class="metric-label">Companies</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Model Info
    st.markdown("---")
    st.markdown("### 🤖 AI Model")
    st.info(f"**Model:** {Settings.LLM_MODEL}\n**Provider:** {Settings.LLM_PROVIDER.upper()}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <small style="color: #a0a0a0;">
            Made with ❤️ using Free Tools<br/>
            Groq • ChromaDB • Yahoo Finance
        </small>
    </div>
    """, unsafe_allow_html=True)

# Main Content Area
tab1, tab2, tab3 = st.tabs(["💬 Chat Analysis", "📊 Market Dashboard", "📈 Technical Charts"])

with tab1:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Query Section
        st.markdown("""
        <div class="custom-card">
            <h3 style="color: #667eea; margin-top: 0;">🔍 Ask Your Trading Questions</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Example queries in expandable section
        with st.expander("💡 Example Questions", expanded=False):
            example_cols = st.columns(2)
            with example_cols[0]:
                st.markdown("""
                **Fundamental Analysis:**
                - What are NVDA's main risk factors?
                - Compare Apple vs Microsoft financials
                - Which tech stock has best margins?
                """)
            with example_cols[1]:
                st.markdown("""
                **Trading Signals:**
                - Find undervalued stocks in my list
                - Which stock shows bullish momentum?
                - Best growth opportunities?
                """)
        
        # Query Input with custom styling
        query = st.text_input(
            "",
            placeholder="💭 Ask about risks, opportunities, comparisons, or trading signals...",
            key="query_input",
            label_visibility="collapsed"
        )
        
        # Action Buttons
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        with col_btn1:
            analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True)
        with col_btn2:
            clear_button = st.button("🗑️ Clear", use_container_width=True)
        
        # Process Query
        if analyze_button and query:
            with st.status("🤖 AI Analysis in Progress...", expanded=True) as status:
                st.write("📡 Connecting to AI model...")
                time.sleep(0.5)
                st.write("🔍 Searching financial documents...")
                time.sleep(0.5)
                st.write("📊 Analyzing data...")
                
                response = st.session_state.trading_assistant.get_response(
                    query=query,
                    tickers=selected_tickers,
                    doc_types=doc_types,
                    mode=analysis_mode,
                    top_k=retrieval_k
                )
                
                st.write("✅ Analysis complete!")
                status.update(label="✅ Analysis Complete", state="complete", expanded=False)
                
                st.session_state.messages.append({"role": "user", "content": query})
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        if clear_button:
            st.session_state.messages = []
            st.rerun()
        
        # Chat Display
        st.markdown("---")
        
        # Messages Container - Displaying in REVERSE order (Newest First)
        messages_container = st.container()
        with messages_container:
            # Iterate through messages in reverse to show newest at the top
            for message in reversed(st.session_state.messages):
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="user-message">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="font-size: 1.2rem;">👤</span>
                            <strong>You</strong>
                        </div>
                        <div style="margin-top: 0.5rem;">{message["content"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    content = message["content"]
                    if isinstance(content, dict):
                        st.markdown(f"""
                        <div class="ai-message">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <span style="font-size: 1.2rem;">🤖</span>
                                <strong style="color: #667eea;">AI Assistant</strong>
                            </div>
                            <div style="margin-top: 0.75rem; line-height: 1.6;">
                                {content.get('analysis', 'No analysis available')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display signals
                        if content.get('signals'):
                            signal_html = "<div style='margin-top: 1rem;'><strong>Trading Signals:</strong><br/>"
                            for signal in content['signals']:
                                signal_class = "signal-bullish" if signal['direction'] == 'bullish' else "signal-bearish"
                                signal_html += f"""
                                <span class="signal-pill {signal_class}">
                                    {signal['ticker']}: {signal['direction'].upper()}
                                </span>
                                """
                            signal_html += "</div>"
                            st.markdown(signal_html, unsafe_allow_html=True)
                        
                        # Display sources
                        if content.get('sources'):
                            with st.expander("📚 View Sources"):
                                for source in content['sources']:
                                    st.markdown(f"""
                                    <div class="source-card">
                                        <strong>{source['ticker']}</strong> • {source['type']}<br/>
                                        <small style="color: #a0a0a0;">Relevance: {source['relevance_score']:.1%}</small><br/>
                                        <small>{source['snippet']}</small>
                                    </div>
                                    """, unsafe_allow_html=True)
    
    with col2:
        # Quick Stats Panel
        st.markdown("""
        <div class="custom-card">
            <h4 style="color: #667eea; margin-top: 0;">📊 Quick Stats</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if selected_tickers:
            # Performance metrics
            for ticker in selected_tickers[:3]:
                change = 2.5  # Mock data
                color = "#10b981" if change > 0 else "#ef4444"
                arrow = "↑" if change > 0 else "↓"
                
                st.markdown(f"""
                <div class="custom-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 600; color: #e0e0e0;">{ticker}</span>
                        <span style="color: {color}; font-weight: 600;">
                            {arrow} {abs(change):.1f}%
                        </span>
                    </div>
                    <div style="margin-top: 0.5rem;">
                        <small style="color: #a0a0a0;">$145.32</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Market Sentiment
        st.markdown("""
        <div class="custom-card">
            <h4 style="color: #667eea; margin-top: 0;">🎭 Market Sentiment</h4>
            <div style="margin-top: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: #10b981;">Bullish</span>
                    <span style="color: #ef4444;">Bearish</span>
                </div>
                <div style="background: rgba(255,255,255,0.1); border-radius: 8px; height: 8px; overflow: hidden;">
                    <div style="width: 65%; height: 100%; background: linear-gradient(90deg, #10b981 0%, #059669 100%);"></div>
                </div>
                <div style="text-align: center; margin-top: 0.5rem;">
                    <small style="color: #a0a0a0;">65% Bullish</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Trading Tips
        st.markdown("""
        <div class="custom-card">
            <h4 style="color: #667eea; margin-top: 0;">💡 Trading Tips</h4>
            <ul style="margin: 0; padding-left: 1.5rem; color: #e0e0e0;">
                <li style="margin-bottom: 0.5rem;">Diversify across sectors</li>
                <li style="margin-bottom: 0.5rem;">Set stop-loss at -5%</li>
                <li style="margin-bottom: 0.5rem;">Review weekly trends</li>
                <li style="margin-bottom: 0.5rem;">Monitor volume spikes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div class="custom-card">
        <h3 style="color: #667eea; margin-top: 0;">📊 Market Overview Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Market metrics
    metrics_cols = st.columns(4)
    
    metrics_data = [
        ("S&P 500", "4,783.45", "+1.2%", "↑"),
        ("NASDAQ", "15,123.68", "+1.8%", "↑"),
        ("DOW", "37,545.33", "+0.8%", "↑"),
        ("VIX", "12.35", "-5.2%", "↓")
    ]
    
    for col, (name, value, change, arrow) in zip(metrics_cols, metrics_data):
        with col:
            color = "#10b981" if "+" in change else "#ef4444"
            st.markdown(f"""
            <div class="metric-card">
                <div style="color: #a0a0a0; font-size: 0.9rem;">{name}</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #e0e0e0; margin: 0.25rem 0;">{value}</div>
                <div style="color: {color}; font-size: 0.9rem;">{arrow} {change}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Charts
    if selected_tickers:
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Performance chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=selected_tickers[:5],
                y=[5.2, 3.8, -1.2, 2.5, 4.1],
                marker_color=['#10b981' if x > 0 else '#ef4444' for x in [5.2, 3.8, -1.2, 2.5, 4.1]],
                text=[f"{x:+.1f}%" for x in [5.2, 3.8, -1.2, 2.5, 4.1]],
                textposition='outside'
            ))
            fig.update_layout(
                title="Today's Performance",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e0e0e0'),
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with chart_col2:
            # Sector performance
            sectors = ["Tech", "Finance", "Healthcare", "Energy", "Consumer"]
            sector_performance = [3.2, 1.8, -0.5, 2.1, 1.5]
            
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=sectors,
                y=sector_performance,
                marker_color=['#10b981' if x > 0 else '#ef4444' for x in sector_performance],
                text=[f"{x:+.1f}%" for x in sector_performance],
                textposition='outside'
            ))
            fig2.update_layout(
                title="Sector Performance",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e0e0e0'),
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.markdown("""
    <div class="custom-card">
        <h3 style="color: #667eea; margin-top: 0;">📈 Technical Analysis Charts</h3>
        <p style="color: #a0a0a0;">Advanced charting and technical indicators coming soon...</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Placeholder for future technical analysis features
    st.info("🚧 Technical charts with candlesticks, moving averages, and indicators will be available in the next update!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem;">
    <p style="color: #a0a0a0; margin: 0;">
        <strong>⚠️ Disclaimer:</strong> This tool is for educational purposes only. Not financial advice.
        Always do your own research before making investment decisions.
    </p>
    <p style="color: #667eea; margin-top: 1rem; font-size: 0.9rem;">
        TradingRAG Pro v1.0 | Powered by Free & Open-Source Tools
    </p>
</div>
""", unsafe_allow_html=True)

# Hidden JS for additional effects (optional)
st.markdown("""
<script>
    // Add any custom JavaScript here if needed
</script>
""", unsafe_allow_html=True)