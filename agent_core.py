"""
ADK Agent Core - Indian Stock Alert Agent using Google ADK Framework
Orchestrates tools, LLM analysis, and notifications
"""
from __future__ import annotations

import hashlib
from typing import Dict, List, Any, Optional, Set
from datetime import datetime

from config import Config
from logger import log
from llm import analyze_news_with_llm
from tools import (
    fetch_news_articles,
    fetch_youtube_videos,
    get_stock_price,
    get_stock_name,
    get_stock_fundamentals,
    send_notification,
    get_youtube_transcript,
    extract_stock_mentions_from_transcript,
)


class IndianStockAgent:
    """
    ADK-based agent for Indian stock market alerts.
    
    This agent:
    1. Fetches news from RSS feeds and YouTube
    2. Analyzes news with LLM (Mistral) to identify stock impact
    3. Fetches real-time NSE stock prices
    4. Sends aggregated notifications to phone
    """
    
    def __init__(self):
        """Initialize the agent with state tracking"""
        self.seen_headlines: Set[str] = set()
        self.name = "Indian Stock Alert Agent"
        self.version = "2.0-ADK"
        
    def get_headline_id(self, headline: str) -> str:
        """Generate unique ID for headline deduplication"""
        return hashlib.md5(headline.encode()).hexdigest()
    
    def format_alert(
        self, 
        ticker: str, 
        headline: str, 
        analysis: dict, 
        current_price: Optional[float],
        article_type: str = "news",
        sources_list: Optional[List[str]] = None
    ) -> tuple[str, str]:
        """
        Format stock alert notification.
        
        Args:
            ticker: Stock ticker (e.g., "HAL.NS")
            headline: News headline
            analysis: LLM analysis result
            current_price: Current stock price
            article_type: "news" or "youtube"
            sources_list: List of news sources
        
        Returns:
            Tuple of (title, body) for notification
        """
        direction = analysis.get("direction", "UP")
        move_pct = analysis.get("expected_move_percent", 0)
        reason = analysis.get("reason", "")
        confidence = analysis.get("confidence", "Medium")
        timeframe = analysis.get("timeframe", "48hrs")
        
        company = get_stock_name(ticker)
        symbol = ticker.replace(".NS", "") if ticker not in ["GOLD", "SILVER"] else ticker
        conf_icon = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}.get(confidence, "🟡")
        
        # Different intro based on source
        if article_type == "youtube":
            expert_intro = "📺 YouTube Expert Recommends"
            why_prefix = f"Expert says: {reason}"
        else:
            expert_intro = "📰 Market News Alert"
            why_prefix = reason
            if sources_list and len(sources_list) > 1:
                expert_intro = f"📰 {len(sources_list)} News Sources"
        
        # Check if commodity
        is_commodity = ticker in ["GOLD", "SILVER"]
        
        if direction == "UP":
            arrow = "📈"
            if current_price is not None:
                expected = round(current_price * (1 + move_pct / 100), 2)
                price_text = f"💰 Now:    ₹{current_price:,.2f}\n🎯 Target: ₹{expected:,.2f} ({direction} {move_pct}%)"
            else:
                if is_commodity:
                    price_text = f"🪙 Commodity | 🎯 Expected move: +{move_pct}%"
                else:
                    price_text = f"💰 Price unavailable | 🎯 Expected +{move_pct}%"
            
            title = f"{arrow} {symbol} | {direction} {move_pct}% | {confidence} confidence"
            
            # Build sources text
            if sources_list and len(sources_list) > 1:
                sources_text = "\n\n📰 Multiple Sources Report:\n" + "\n".join([f"   • {s}" for s in sources_list[:5]])
            else:
                sources_text = f"\n\n📰 {headline}"
            
            body = (
                f"{expert_intro}\n"
                f"🏢 {company}\n"
                f"{price_text}\n"
                f"⏱ When:   {timeframe}\n"
                f"🧠 Why:    {why_prefix}"
                f"{sources_text}\n"
                f"{conf_icon} Confidence: {confidence}\n"
                f"\n"
                f"🕐 {datetime.now().strftime('%d %b %Y, %I:%M %p IST')}\n"
                f"⚠️ Not financial advice. DYOR."
            )
        else:  # DOWN - buying opportunity
            arrow = "💎"
            if current_price is not None:
                expected = round(current_price * (1 - move_pct / 100), 2)
                rebound = round(current_price * 1.05, 2)
                price_text = f"💰 Now:      ₹{current_price:,.2f}\n📉 May drop: ₹{expected:,.2f} (−{move_pct}%)\n🎯 Potential: ₹{rebound:,.2f}+ (recovery)"
            else:
                if is_commodity:
                    price_text = f"🪙 Commodity | 📉 Expected move: −{move_pct}%"
                else:
                    price_text = f"💰 Price unavailable | 📉 Expected −{move_pct}%"
            
            title = f"{arrow} {symbol} | BUY DIP? {move_pct}% down | {confidence}"
            
            # Build sources text
            if sources_list and len(sources_list) > 1:
                sources_text = "\n\n📰 Multiple Sources Report:\n" + "\n".join([f"   • {s}" for s in sources_list[:5]])
            else:
                sources_text = f"\n\n📰 {headline}"
            
            body = (
                f"{expert_intro}\n"
                f"🏢 {company}\n"
                f"{price_text}\n"
                f"⏱ Timeframe: {timeframe}\n"
                f"🧠 Why:      {why_prefix}"
                f"{sources_text}\n"
                f"{conf_icon} Confidence: {confidence}\n"
                f"\n"
                f"🕐 {datetime.now().strftime('%d %b %Y, %I:%M %p IST')}\n"
                f"⚠️ Not financial advice. DYOR."
            )
        
        return title, body
    
    def process_article(self, article: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process a single article with LLM analysis.
        
        Args:
            article: Article data dict
        
        Returns:
            List of stock recommendations with analysis
        """
        headline = article["headline"]
        hid = self.get_headline_id(headline)
        
        if hid in self.seen_headlines:
            return []
        self.seen_headlines.add(hid)
        
        log(f"Analyzing: {headline[:80]}...")
        
        # Call LLM for analysis (use transcript if available for YouTube videos)
        transcript = article.get("transcript", None)
        fundamentals = article.get("fundamentals", None)
        
        if transcript:
            log(f"Using transcript for LLM analysis ({len(transcript)} chars)")
        if fundamentals:
            log(f"Using fundamentals: P/E={fundamentals.get('pe_ratio')}, ROE={fundamentals.get('roe')}%")
        
        analysis = analyze_news_with_llm(headline, article["summary"], transcript, fundamentals)
        if not analysis:
            return []
        
        affected = analysis.get("affected_stocks", [])
        if not affected:
            log("No stocks affected, skipping.")
            return []
        
        article_type = article.get("type", "news")
        source = article.get("source", "")
        
        # Return list of recommendations
        results = []
        for ticker in affected[:3]:  # max 3 stocks per article
            results.append({
                "ticker": ticker,
                "headline": headline,
                "analysis": analysis,
                "article_type": article_type,
                "source": source,
            })
        
        return results
    
    def process_news_aggregated(self, news_articles: List[Dict[str, Any]]) -> None:
        """
        Process news articles and send aggregated notification.
        
        Args:
            news_articles: List of news article dicts
        """
        from collections import defaultdict
        
        # Collect all stock recommendations
        stock_data = {}  # ticker -> {analysis, sources, headlines, price}
        
        for article in news_articles:
            results = self.process_article(article)
            for result in results:
                ticker = result["ticker"]
                
                if ticker not in stock_data:
                    stock_data[ticker] = {
                        "analysis": result["analysis"],
                        "sources": [],
                        "headlines": [],
                        "price": None,
                    }
                
                # Collect unique sources and headlines
                if result["source"] not in stock_data[ticker]["sources"]:
                    stock_data[ticker]["sources"].append(result["source"])
                if result["headline"] not in stock_data[ticker]["headlines"]:
                    stock_data[ticker]["headlines"].append(result["headline"])
        
        if not stock_data:
            log("No stock recommendations from news")
            return
        
        # Fetch prices and rank stocks
        ranked_stocks = []
        for ticker, data in stock_data.items():
            price = get_stock_price(ticker)
            if price is None:
                log(f"Could not get price for {ticker}, using placeholder", "WARN")
            
            # Fetch fundamentals
            fundamentals = get_stock_fundamentals(ticker)
            
            data["price"] = price
            data["fundamentals"] = fundamentals
            analysis = data["analysis"]
            
            # Ranking score
            confidence_score = {"High": 3, "Medium": 2, "Low": 1}.get(
                analysis.get("confidence", "Medium"), 2
            )
            move_pct = analysis.get("expected_move_percent", 0)
            score = confidence_score * 10 + move_pct
            
            ranked_stocks.append({
                "ticker": ticker,
                "data": data,
                "score": score,
            })
        
        # Sort and take top 5
        ranked_stocks.sort(key=lambda x: x["score"], reverse=True)
        top_stocks = ranked_stocks[:5]
        
        if not top_stocks:
            log("No valid stock recommendations after filtering")
            return
        
        # Build consolidated notification
        title = f"📰 Market News: Top {len(top_stocks)} Stock Picks"
        
        body_parts = []
        body_parts.append(f"📊 Analysis of {len(news_articles)} news articles")
        body_parts.append(f"🎯 Top {len(top_stocks)} Recommendations:\n")
        
        for i, item in enumerate(top_stocks, 1):
            ticker = item["ticker"]
            data = item["data"]
            analysis = data["analysis"]
            price = data["price"]
            fundamentals = data.get("fundamentals")
            company = get_stock_name(ticker)
            symbol = ticker if ticker in ["GOLD", "SILVER"] else ticker.replace(".NS", "")
            
            direction = analysis.get("direction", "UP")
            move_pct = analysis.get("expected_move_percent", 0)
            reason = analysis.get("reason", "")
            confidence = analysis.get("confidence", "Medium")
            timeframe = analysis.get("timeframe", "48hrs")
            
            conf_icon = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}.get(confidence, "🟡")
            is_commodity = ticker in ["GOLD", "SILVER"]
            
            # Build fundamental data string
            fundamental_str = ""
            if fundamentals and not is_commodity:
                fund_parts = []
                if fundamentals.get("pe_ratio"):
                    fund_parts.append(f"P/E: {fundamentals['pe_ratio']:.1f}")
                if fundamentals.get("roe"):
                    fund_parts.append(f"ROE: {fundamentals['roe']:.1f}%")
                if fundamentals.get("debt_to_equity") is not None:
                    fund_parts.append(f"D/E: {fundamentals['debt_to_equity']:.2f}")
                if fund_parts:
                    fundamental_str = f"   📊 {' | '.join(fund_parts)}\n"
            
            if direction == "UP":
                arrow = "📈"
                if price is not None:
                    target = round(price * (1 + move_pct / 100), 2)
                    price_text = f"💰 ₹{price:,.2f} → 🎯 ₹{target:,.2f} (+{move_pct}%)"
                else:
                    if is_commodity:
                        price_text = f"🪙 Commodity | 🎯 +{move_pct}%"
                    else:
                        price_text = f"💰 Price unavailable | 🎯 +{move_pct}%"
                
                body_parts.append(
                    f"{i}. {arrow} {symbol} ({company})\n"
                    f"   {price_text}\n"
                    f"{fundamental_str}"
                    f"   📌 Why: {reason[:100]}\n"
                    f"   {conf_icon} {confidence} | ⏱ {timeframe}\n"
                    f"   📰 Sources: {', '.join(data['sources'][:3])}\n"
                )
            else:
                arrow = "💎"
                if price is not None:
                    dip = round(price * (1 - move_pct / 100), 2)
                    price_text = f"💰 ₹{price:,.2f} → 📉 ₹{dip:,.2f} (−{move_pct}%)"
                else:
                    if is_commodity:
                        price_text = f"🪙 Commodity | 📉 −{move_pct}%"
                    else:
                        price_text = f"💰 Price unavailable | 📉 −{move_pct}%"
                
                body_parts.append(
                    f"{i}. {arrow} {symbol} ({company}) - BUY DIP\n"
                    f"   {price_text}\n"
                    f"{fundamental_str}"
                    f"   📌 Why: {reason[:100]}\n"
                    f"   {conf_icon} {confidence} | ⏱ {timeframe}\n"
                    f"   📰 Sources: {', '.join(data['sources'][:3])}\n"
                )
        
        body_parts.append(f"\n🕐 {datetime.now().strftime('%d %b %Y, %I:%M %p IST')}")
        body_parts.append("⚠️ Not financial advice. DYOR.")
        
        body = "\n".join(body_parts)
        
        send_notification(title, body, "UP")
        log(f"📰 News summary sent: {len(top_stocks)} stocks recommended")
    
    def process_youtube_videos(self, youtube_videos: List[Dict[str, Any]]) -> None:
        """
        Process YouTube videos and send consolidated notification.
        Includes: 1) Stocks mentioned in video transcript, 2) LLM recommendations
        
        Args:
            youtube_videos: List of video data dicts
        """
        # Extract stocks mentioned in video transcript
        mentioned_stocks = set()
        video_url = None
        video_title = None
        
        for video in youtube_videos:
            video_url = video.get("url", "")
            video_title = video.get("headline", "")
            
            # Get YouTube transcript
            if video_url:
                log(f"Fetching transcript for: {video_title[:50]}...")
                transcript = get_youtube_transcript(video_url)
                
                if transcript:
                    # Attach transcript to video for LLM analysis
                    video["transcript"] = transcript
                    
                    # Extract stock mentions from transcript
                    stocks_in_transcript = extract_stock_mentions_from_transcript(transcript)
                    mentioned_stocks.update(stocks_in_transcript)
                    log(f"Found {len(stocks_in_transcript)} stocks mentioned in video")
        
        # Get LLM recommendations (now with transcript attached)
        all_llm_stocks = {}  # ticker -> {analysis, video_title, price}
        
        for video in youtube_videos:
            results = self.process_article(video)
            
            for result in results:
                ticker = result["ticker"]
                
                # Avoid duplicates
                if ticker not in all_llm_stocks:
                    all_llm_stocks[ticker] = {
                        "analysis": result["analysis"],
                        "video_title": result["headline"],
                        "price": None,
                    }
        
        # If no stocks found anywhere, exit
        if not mentioned_stocks and not all_llm_stocks:
            log("No stock recommendations from YouTube")
            return
        
        # Fetch prices for mentioned stocks
        mentioned_with_prices = []
        for ticker in mentioned_stocks:
            price = get_stock_price(ticker)
            fundamentals = get_stock_fundamentals(ticker)
            company = get_stock_name(ticker)
            mentioned_with_prices.append({
                "ticker": ticker,
                "price": price,
                "fundamentals": fundamentals,
                "company": company,
            })
        
        # Fetch prices for LLM stocks
        llm_stocks_with_prices = []
        for ticker, data in all_llm_stocks.items():
            price = get_stock_price(ticker)
            if price is None:
                log(f"Could not get price for {ticker}, using placeholder", "WARN")
            
            fundamentals = get_stock_fundamentals(ticker)
            
            data["price"] = price
            data["fundamentals"] = fundamentals
            llm_stocks_with_prices.append({"ticker": ticker, "data": data})
        
        # Build consolidated notification
        total_count = len(mentioned_stocks) + len(all_llm_stocks)
        title = f"📺 YouTube Analysis: {len(mentioned_stocks)} Mentioned + {len(all_llm_stocks)} AI Picks"
        
        body_parts = []
        body_parts.append("📺 YouTube Stock Analysis")
        if video_title:
            body_parts.append(f"🎬 Video: {video_title[:80]}")
        body_parts.append("")
        
        # Section 1: Stocks mentioned in video
        if mentioned_stocks:
            body_parts.append("━━━ 🗣️ STOCKS MENTIONED IN VIDEO ━━━")
            body_parts.append(f"(From transcript analysis)\n")
            
            for i, item in enumerate(mentioned_with_prices, 1):
                ticker = item["ticker"]
                price = item["price"]
                fundamentals = item.get("fundamentals")
                company = item["company"]
                symbol = ticker if ticker in ["GOLD", "SILVER"] else ticker.replace(".NS", "")
                
                if price is not None:
                    price_text = f"💰 Current: ₹{price:,.2f}"
                else:
                    price_text = "💰 Price unavailable"
                
                # Build fundamental string
                fund_str = ""
                if fundamentals and ticker not in ["GOLD", "SILVER"]:
                    fund_parts = []
                    if fundamentals.get("pe_ratio"):
                        fund_parts.append(f"P/E: {fundamentals['pe_ratio']:.1f}")
                    if fundamentals.get("roe"):
                        fund_parts.append(f"ROE: {fundamentals['roe']:.1f}%")
                    if fundamentals.get("debt_to_equity") is not None:
                        fund_parts.append(f"D/E: {fundamentals['debt_to_equity']:.2f}")
                    if fund_parts:
                        fund_str = f"   📊 {' | '.join(fund_parts)}\n"
                
                body_parts.append(
                    f"{i}. 🎤 {symbol} ({company})\n"
                    f"   {price_text}\n"
                    f"{fund_str}"
                )
        
        # Section 2: LLM Recommended Stocks
        if llm_stocks_with_prices:
            body_parts.append("\n━━━ 🤖 AI RECOMMENDED STOCKS ━━━")
            body_parts.append(f"(Based on video analysis)\n")
            
            for i, item in enumerate(llm_stocks_with_prices, 1):
                ticker = item["ticker"]
                data = item["data"]
                analysis = data["analysis"]
                price = data["price"]
                fundamentals = data.get("fundamentals")
                company = get_stock_name(ticker)
                symbol = ticker if ticker in ["GOLD", "SILVER"] else ticker.replace(".NS", "")
                
                direction = analysis.get("direction", "UP")
                move_pct = analysis.get("expected_move_percent", 0)
                reason = analysis.get("reason", "")
                confidence = analysis.get("confidence", "Medium")
                timeframe = analysis.get("timeframe", "48hrs")
                
                conf_icon = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}.get(confidence, "🟡")
                is_commodity = ticker in ["GOLD", "SILVER"]
                
                # Build fundamental string
                fund_str = ""
                if fundamentals and not is_commodity:
                    fund_parts = []
                    if fundamentals.get("pe_ratio"):
                        fund_parts.append(f"P/E: {fundamentals['pe_ratio']:.1f}")
                    if fundamentals.get("roe"):
                        fund_parts.append(f"ROE: {fundamentals['roe']:.1f}%")
                    if fundamentals.get("debt_to_equity") is not None:
                        fund_parts.append(f"D/E: {fundamentals['debt_to_equity']:.2f}")
                    if fund_parts:
                        fund_str = f"   📊 {' | '.join(fund_parts)}\n"
                
                if direction == "UP":
                    arrow = "📈"
                    if price is not None:
                        target = round(price * (1 + move_pct / 100), 2)
                        price_text = f"💰 ₹{price:,.2f} → 🎯 ₹{target:,.2f} (+{move_pct}%)"
                    else:
                        if is_commodity:
                            price_text = f"🪙 Commodity | 🎯 +{move_pct}%"
                        else:
                            price_text = f"💰 Price unavailable | 🎯 +{move_pct}%"
                    
                    body_parts.append(
                        f"{i}. {arrow} {symbol} ({company})\n"
                        f"   {price_text}\n"
                        f"{fund_str}"
                        f"   📊 ACCUMULATE\n"
                        f"   💡 AI says: {reason[:80]}\n"
                        f"   {conf_icon} {confidence} | ⏱ {timeframe}\n"
                    )
                else:
                    arrow = "💎"
                    if price is not None:
                        dip = round(price * (1 - move_pct / 100), 2)
                        price_text = f"💰 ₹{price:,.2f} → 📉 ₹{dip:,.2f} (−{move_pct}%)"
                    else:
                        if is_commodity:
                            price_text = f"🪙 Commodity | 📉 −{move_pct}%"
                        else:
                            price_text = f"💰 Price unavailable | 📉 −{move_pct}%"
                    
                    body_parts.append(
                        f"{i}. {arrow} {symbol} ({company}) - BUY DIP\n"
                        f"   {price_text}\n"
                        f"{fund_str}"
                        f"   📊 ACCUMULATE ON DIP\n"
                        f"   💡 AI says: {reason[:80]}\n"
                        f"   {conf_icon} {confidence} | ⏱ {timeframe}\n"
                    )
        
        body_parts.append(f"🕐 {datetime.now().strftime('%d %b %Y, %I:%M %p IST')}")
        body_parts.append("⚠️ Not financial advice. DYOR.")
        
        body = "\n".join(body_parts)
        
        send_notification(title, body, "UP")
        log(f"📺 YouTube summary sent: {len(mentioned_stocks)} mentioned + {len(all_llm_stocks)} AI picks")
    
    def run_cycle(self) -> None:
        """
        Run one complete agent cycle:
        1. Fetch news and videos
        2. Analyze with LLM
        3. Fetch stock prices
        4. Send notifications
        """
        log("─" * 40)
        log(f"Fetching news at {datetime.now().strftime('%I:%M %p')}...")
        
        # Fetch news articles using ADK tools
        news_articles = fetch_news_articles()
        log(f"Found {len(news_articles)} news articles")
        
        # Fetch YouTube videos using ADK tools
        youtube_videos = fetch_youtube_videos()
        if youtube_videos:
            log(f"Found {len(youtube_videos)} YouTube videos")
        
        # Process news with aggregation
        if news_articles:
            log("Processing news articles (with aggregation)...")
            self.process_news_aggregated(news_articles)
        
        # Process YouTube videos
        if youtube_videos:
            log("Processing YouTube videos...")
            self.process_youtube_videos(youtube_videos)
