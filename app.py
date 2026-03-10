"""
Streamlit Web UI for Indian Stock Agent
Run with: streamlit run app.py
"""
import streamlit as st
from datetime import datetime
import sys
from io import StringIO
import contextlib

from agent_core import IndianStockAgent
from tools import (
    fetch_news_articles,
    fetch_youtube_videos,
    get_stock_price,
    get_stock_name,
    get_stock_fundamentals,
    get_youtube_transcript,
    extract_stock_mentions_from_transcript,
)
from config import Config
from logger import log

# Configure page
st.set_page_config(
    page_title="Indian Stock Agent",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Indian Stock Alert Agent")
st.markdown("**AI-powered stock analysis from news and YouTube videos**")
st.markdown("---")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # YouTube Channel URL
    youtube_url = st.text_input(
        "YouTube Channel URL",
        value="https://www.youtube.com/@berich467",
        help="Enter YouTube channel URL (e.g., https://www.youtube.com/@berich467)"
    )
    
    # Extract channel ID from URL
    channel_id = None
    if youtube_url:
        if "@" in youtube_url:
            # Extract channel handle from URL
            handle = youtube_url.split("@")[-1].strip("/")
            st.info(f"Using channel: @{handle}")
            # Note: We'll need to convert handle to channel ID in the future
            # For now, use the default from config
            channel_id = Config.YOUTUBE_CHANNEL_ID
        elif "channel/" in youtube_url:
            channel_id = youtube_url.split("channel/")[-1].strip("/")
            st.success(f"Channel ID: {channel_id}")
    
    st.markdown("---")
    
    st.subheader("🔔 Notification Settings")
    ntfy_topic = st.text_input(
        "ntfy.sh Topic",
        value=Config.NTFY_TOPIC,
        help="Your ntfy.sh topic for phone notifications"
    )
    
    st.markdown("---")
    
    st.subheader("🤖 LLM Settings")
    llm_mode = st.selectbox(
        "LLM Provider",
        ["mistral", "ollama"],
        index=0 if Config.LLM_MODE == "mistral" else 1
    )
    
    st.info(f"Current: **{Config.MISTRAL_MODEL}**" if llm_mode == "mistral" else f"Current: **{Config.OLLAMA_MODEL}**")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🎯 Actions")
    
    # Run Analysis Button
    if st.button("▶️ Run Analysis", type="primary", use_container_width=True):
        st.markdown("---")
        st.subheader("📊 Analysis Results")
        
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Create output area
        output_container = st.container()
        
        with output_container:
            # Step 1: Fetch News
            status_text.text("📰 Fetching news articles...")
            progress_bar.progress(20)
            
            news_articles = fetch_news_articles()
            st.success(f"✅ Fetched {len(news_articles)} news articles")
            
            # Step 2: Fetch YouTube
            status_text.text("📺 Fetching YouTube videos...")
            progress_bar.progress(40)
            
            youtube_videos = fetch_youtube_videos()
            st.success(f"✅ Fetched {len(youtube_videos)} YouTube videos")
            
            # Step 3: Analyze with AI
            status_text.text("🤖 Analyzing with AI...")
            progress_bar.progress(60)
            
            # Initialize agent
            agent = IndianStockAgent()
            
            # Process news
            if news_articles:
                st.markdown("### 📰 News Analysis")
                with st.spinner("Analyzing news articles..."):
                    agent.process_news_aggregated(news_articles)
                st.success("✅ News analysis complete")
            
            progress_bar.progress(80)
            
            # Process YouTube
            if youtube_videos:
                st.markdown("### 📺 YouTube Analysis")
                with st.spinner("Analyzing YouTube videos..."):
                    agent.process_youtube_videos(youtube_videos)
                st.success("✅ YouTube analysis complete")
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis Complete!")
            
            st.balloons()
            st.markdown("---")
            st.info("📱 Check your phone for notifications via ntfy.sh!")

with col2:
    st.header("📊 Quick Stats")
    
    # Show current config
    st.metric("LLM Provider", Config.LLM_MODE.upper())
    st.metric("Notification Topic", ntfy_topic if ntfy_topic else "Not Set")
    
    st.markdown("---")
    
    st.subheader("🔍 Test Tools")
    
    # Test stock lookup
    test_ticker = st.text_input("Test Stock Price", value="HAL.NS", placeholder="Enter ticker (e.g., HAL.NS)")
    
    if st.button("Get Price", use_container_width=True):
        if test_ticker:
            with st.spinner("Fetching..."):
                price = get_stock_price(test_ticker)
                company = get_stock_name(test_ticker)
                fundamentals = get_stock_fundamentals(test_ticker)
                
                if price:
                    st.success(f"**{company}**")
                    st.metric("Current Price", f"₹{price:,.2f}")
                    
                    if fundamentals:
                        st.markdown("**Fundamentals:**")
                        cols = st.columns(2)
                        with cols[0]:
                            if fundamentals.get("pe_ratio"):
                                st.metric("P/E Ratio", f"{fundamentals['pe_ratio']:.1f}")
                            if fundamentals.get("roe"):
                                st.metric("ROE", f"{fundamentals['roe']:.1f}%")
                        with cols[1]:
                            if fundamentals.get("debt_to_equity") is not None:
                                st.metric("D/E", f"{fundamentals['debt_to_equity']:.2f}")
                            if fundamentals.get("market_cap"):
                                st.metric("Market Cap", fundamentals['market_cap'])
                else:
                    st.error("Could not fetch price")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p>Indian Stock Alert Agent v2.0-ADK</p>
        <p>⚠️ Not financial advice. DYOR (Do Your Own Research)</p>
    </div>
    """,
    unsafe_allow_html=True
)
