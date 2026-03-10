"""
ADK Tools - Function declarations for the Indian Stock Agent
These tools are used by the ADK agent to fetch data and perform actions
"""
from __future__ import annotations

import feedparser
import re
import requests
from datetime import datetime
from typing import List, Dict, Optional, Any, TypedDict
import time
from bs4 import BeautifulSoup

from config import Config
from logger import log


# ─── Type Definitions for ADK Tool Inputs/Outputs ─────────────────────────────

class StockPrice(TypedDict):
    """Stock price information"""
    ticker: str
    price: Optional[float]
    company_name: str


class NewsArticle(TypedDict):
    """News article structure"""
    headline: str
    summary: str
    source: str
    article_type: str


class StockRecommendation(TypedDict):
    """Stock trading recommendation"""
    ticker: str
    direction: str
    expected_move_percent: float
    reason: str
    confidence: str
    timeframe: str


# ─── RSS News Feeds ───────────────────────────────────────────────────────────

RSS_FEEDS = [
    "https://economictimes.indiatimes.com/markets/rss.cms",
    "https://economictimes.indiatimes.com/news/economy/rss.cms",
    "https://economictimes.indiatimes.com/commoditysummary/symbol-GOLD.cms?format=rss",
    "https://economictimes.indiatimes.com/commoditysummary/symbol-SILVER.cms?format=rss",
    "https://timesofindia.indiatimes.com/rssfeeds/1898055.cms",
    "https://www.moneycontrol.com/rss/marketsnews.xml",
    "https://www.moneycontrol.com/rss/commodity.xml",
    "https://www.livemint.com/rss/markets",
    "https://www.livemint.com/rss/economy",
    "https://feeds.feedburner.com/ndtvprofit-latest",
]


# ─── ADK Tool: Fetch News Articles ───────────────────────────────────────────

def fetch_news_articles() -> List[Dict[str, Any]]:
    """
    Fetch latest Indian market news from RSS feeds.
    
    Returns:
        List of news articles with headline, summary, and source
    """
    articles = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:8]:
                headline = entry.get("title", "").strip()
                summary = entry.get("summary", "").strip()
                if headline:
                    articles.append({
                        "headline": headline,
                        "summary": summary[:300],
                        "source": feed.feed.get("title", feed_url),
                        "type": "news",
                    })
        except Exception as e:
            log(f"Feed error {feed_url}: {e}", "WARN")
    
    log(f"Fetched {len(articles)} news articles")
    return articles


# ─── ADK Tool: Fetch YouTube Videos ──────────────────────────────────────────

def fetch_youtube_videos() -> List[Dict[str, Any]]:
    """
    Fetch latest stock recommendation videos from YouTube channels.
    Only returns videos from the last 48 hours.
    
    Returns:
        List of video data with title, description, and URL
    """
    from datetime import datetime, timedelta
    import email.utils
    
    videos = []
    
    if not Config.YOUTUBE_CHANNEL_ID:
        return videos
    
    youtube_feeds = [f"https://www.youtube.com/feeds/videos.xml?channel_id={Config.YOUTUBE_CHANNEL_ID}"]
    cutoff_time = datetime.now() - timedelta(hours=48)
    
    for feed_url in youtube_feeds:
        try:
            feed = feedparser.parse(feed_url)
            recent_videos = 0
            
            for entry in feed.entries[:5]:
                title = entry.get("title", "").strip()
                description = entry.get("summary", "").strip()
                video_url = entry.get("link", "")
                published_str = entry.get("published", "")
                
                if not title:
                    continue
                
                try:
                    if published_str:
                        published_time = datetime(*email.utils.parsedate(published_str)[:6])
                        if published_time < cutoff_time:
                            continue
                        
                        recent_videos += 1
                        videos.append({
                            "headline": f"📺 {title}",
                            "summary": description[:500],
                            "source": feed.feed.get("title", "YouTube"),
                            "url": video_url,
                            "published": published_str,
                            "type": "youtube",
                        })
                    else:
                        recent_videos += 1
                        videos.append({
                            "headline": f"📺 {title}",
                            "summary": description[:500],
                            "source": feed.feed.get("title", "YouTube"),
                            "url": video_url,
                            "published": "",
                            "type": "youtube",
                        })
                except Exception as date_error:
                    log(f"Could not parse date for YouTube video: {date_error}", "WARN")
                    recent_videos += 1
                    videos.append({
                        "headline": f"📺 {title}",
                        "summary": description[:500],
                        "source": feed.feed.get("title", "YouTube"),
                        "url": video_url,
                        "published": published_str,
                        "type": "youtube",
                    })
            
            if recent_videos > 0:
                log(f"Fetched {recent_videos} recent YouTube videos")
        except Exception as e:
            log(f"YouTube feed error: {e}", "WARN")
    
    return videos


# ─── ADK Tool: Get Stock Price ───────────────────────────────────────────────

def get_stock_price(ticker: str) -> Optional[float]:
    """
    Fetch current stock price from NSE.
    
    Args:
        ticker: Stock ticker symbol (e.g., "HAL.NS")
    
    Returns:
        Current price in INR or None if unavailable
    """
    # Commodities don't have NSE prices
    if ticker in ["GOLD", "SILVER"]:
        log(f"Skipping price fetch for commodity: {ticker}")
        return None
    
    try:
        if not ticker.endswith(".NS"):
            log(f"Ticker {ticker} is not an NSE stock", "WARN")
            return None
            
        nse_symbol = ticker.replace(".NS", "")
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json,text/plain,*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com/",
        }
        
        # NSE requires initial session setup
        session.get("https://www.nseindia.com/", headers=headers, timeout=10)
        
        # Fetch stock quote
        nse_resp = session.get(
            f"https://www.nseindia.com/api/quote-equity?symbol={nse_symbol}",
            headers=headers,
            timeout=10,
        )
        nse_resp.raise_for_status()
        nse_data = nse_resp.json()
        
        ltp = nse_data.get("priceInfo", {}).get("lastPrice")
        if ltp is not None:
            return round(float(ltp), 2)
            
        return None
    except Exception as e:
        log(f"NSE price fetch error for {ticker}: {e}", "ERROR")
        return None


# ─── ADK Tool: Get Fundamentals from Screener.in ─────────────────────────────

def get_stock_fundamentals(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetch fundamental data from screener.in
    
    Args:
        ticker: NSE ticker (e.g., "HAL.NS", "TCS.NS")
    
    Returns:
        Dict with P/E, ROE, Debt/Equity, margins, growth, etc. or None
    """
    # Skip commodities
    if ticker in ["GOLD", "SILVER"]:
        return None
    
    # Convert ticker to screener.in format (remove .NS)
    symbol = ticker.replace(".NS", "").replace("&", "").replace("-", "")
    
    try:
        url = f"https://www.screener.in/company/{symbol}/consolidated/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        # If consolidated doesn't exist, try standalone
        if response.status_code == 404:
            url = f"https://www.screener.in/company/{symbol}/"
            response = requests.get(url, headers=headers, timeout=15)
        
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract key ratios from the top section
        fundamentals = {
            "market_cap": None,
            "pe_ratio": None,
            "pb_ratio": None,
            "dividend_yield": None,
            "roe": None,
            "roce": None,
            "debt_to_equity": None,
            "sales_growth_3yr": None,
            "profit_growth_3yr": None,
            "stock_pe": None,
            "face_value": None,
        }
        
        # Find all list items with ratios
        ratio_items = soup.select('li.flex.flex-space-between')
        
        for item in ratio_items:
            name_elem = item.select_one('.name')
            value_elem = item.select_one('.number')
            
            if not name_elem or not value_elem:
                continue
            
            name = name_elem.get_text(strip=True)
            value = value_elem.get_text(strip=True)
            
            # Clean and parse values
            try:
                if name == "Market Cap":
                    fundamentals["market_cap"] = value
                elif name == "Stock P/E":
                    fundamentals["pe_ratio"] = float(value.replace(',', ''))
                elif name == "Price to Book Value" or name == "Book Value":
                    fundamentals["pb_ratio"] = float(value.replace(',', ''))
                elif name == "Dividend Yield":
                    fundamentals["dividend_yield"] = float(value.replace('%', '').replace(',', ''))
                elif name == "ROCE":
                    fundamentals["roce"] = float(value.replace('%', '').replace(',', ''))
                elif name == "ROE":
                    fundamentals["roe"] = float(value.replace('%', '').replace(',', ''))
                elif name == "Debt to Equity" or name == "Debt":
                    fundamentals["debt_to_equity"] = float(value.replace(',', ''))
                elif name == "Sales growth" and "3 Years" in item.get_text():
                    fundamentals["sales_growth_3yr"] = float(value.replace('%', '').replace(',', ''))
                elif name == "Profit growth" and "3 Years" in item.get_text():
                    fundamentals["profit_growth_3yr"] = float(value.replace('%', '').replace(',', ''))
                elif name == "Face Value":
                    fundamentals["face_value"] = float(value.replace(',', ''))
            except (ValueError, AttributeError):
                continue
        
        # Check if we got meaningful data
        if fundamentals["pe_ratio"] or fundamentals["roe"] or fundamentals["market_cap"]:
            log(f"✅ Fetched fundamentals for {symbol}: P/E={fundamentals.get('pe_ratio')}, ROE={fundamentals.get('roe')}%")
            return fundamentals
        
        log(f"No fundamental data found for {symbol}", "WARN")
        return None
        
    except Exception as e:
        log(f"Screener.in fetch error for {ticker}: {e}", "WARN")
        return None


# ─── ADK Tool: Get Stock Name ────────────────────────────────────────────────

# Cache for dynamically fetched stock names
_stock_name_cache = {}

# Static stock name mapping
STOCK_NAMES = {
    "GOLD": "Gold (Commodity)",
    "SILVER": "Silver (Commodity)",
    "HAL.NS": "Hindustan Aeronautics Ltd",
    "BEL.NS": "Bharat Electronics Ltd",
    "BEML.NS": "BEML Ltd",
    "MTAR.NS": "MTAR Technologies Ltd",
    "PARAS.NS": "Paras Defence and Space Technologies",
    "RELIANCE.NS": "Reliance Industries Ltd",
    "ONGC.NS": "Oil and Natural Gas Corporation",
    "IOC.NS": "Indian Oil Corporation",
    "BPCL.NS": "Bharat Petroleum Corporation",
    "GAIL.NS": "GAIL (India) Ltd",
    "TCS.NS": "Tata Consultancy Services",
    "INFY.NS": "Infosys Ltd",
    "WIPRO.NS": "Wipro Ltd",
    "HCLTECH.NS": "HCL Technologies Ltd",
    "TECHM.NS": "Tech Mahindra Ltd",
    "SUNPHARMA.NS": "Sun Pharmaceutical Industries",
    "DRREDDY.NS": "Dr. Reddy's Laboratories",
    "CIPLA.NS": "Cipla Ltd",
    "DIVISLAB.NS": "Divi's Laboratories",
    "HDFCBANK.NS": "HDFC Bank Ltd",
    "ICICIBANK.NS": "ICICI Bank Ltd",
    "SBIN.NS": "State Bank of India",
    "KOTAKBANK.NS": "Kotak Mahindra Bank",
    "AXISBANK.NS": "Axis Bank Ltd",
    "TATAMOTORS.NS": "Tata Motors Ltd",
    "MARUTI.NS": "Maruti Suzuki India Ltd",
    "M&M.NS": "Mahindra & Mahindra Ltd",
    "BAJAJ-AUTO.NS": "Bajaj Auto Ltd",
    "HEROMOTOCO.NS": "Hero MotoCorp Ltd",
    "ADANIGREEN.NS": "Adani Green Energy Ltd",
    "TATAPOWER.NS": "Tata Power Company Ltd",
    "SUZLON.NS": "Suzlon Energy Ltd",
    "HINDUNILVR.NS": "Hindustan Unilever Ltd",
    "ITC.NS": "ITC Ltd",
    "NESTLEIND.NS": "Nestle India Ltd",
    "BRITANNIA.NS": "Britannia Industries Ltd",
    "DABUR.NS": "Dabur India Ltd",
    "BHARTIARTL.NS": "Bharti Airtel Ltd",
    "IDEA.NS": "Vodafone Idea Ltd",
    "LT.NS": "Larsen & Toubro Ltd",
    "ADANIPORTS.NS": "Adani Ports and Special Economic Zone",
    "IRFC.NS": "Indian Railway Finance Corporation",
    "NTPC.NS": "NTPC Ltd",
    "POWERGRID.NS": "Power Grid Corporation of India",
    "TATASTEEL.NS": "Tata Steel Ltd",
    "JSWSTEEL.NS": "JSW Steel Ltd",
    "HINDALCO.NS": "Hindalco Industries Ltd",
    "VEDL.NS": "Vedanta Ltd",
    "SAIL.NS": "Steel Authority of India",
    "HINDZINC.NS": "Hindustan Zinc Ltd",
    "NMDC.NS": "NMDC Ltd",
    "COALINDIA.NS": "Coal India Ltd",
    "TITAN.NS": "Titan Company Ltd",
    "MUTHOOTFIN.NS": "Muthoot Finance Ltd",
    "MANAPPURAM.NS": "Manappuram Finance Ltd",
    "DLF.NS": "DLF Ltd",
    "GODREJPROP.NS": "Godrej Properties Ltd",
    "OBEROIRLTY.NS": "Oberoi Realty Ltd",
    "PIDILITIND.NS": "Pidilite Industries Ltd",
    "SRF.NS": "SRF Ltd",
    "AARTI.NS": "Aarti Industries Ltd",
    "DEEPAKNTR.NS": "Deepak Nitrite Ltd",
    "UPL.NS": "UPL Ltd",
    "COROMANDEL.NS": "Coromandel International Ltd",
    "RALLIS.NS": "Rallis India Ltd",
}


def get_stock_name(ticker: str) -> str:
    """
    Get company name from ticker symbol.
    
    Args:
        ticker: Stock ticker (e.g., "HAL.NS")
    
    Returns:
        Company name or ticker if not found
    """
    # Check static mapping
    if ticker in STOCK_NAMES:
        return STOCK_NAMES[ticker]
    
    # Check cache
    if ticker in _stock_name_cache:
        return _stock_name_cache[ticker]
    
    # Fallback: return ticker without .NS
    return ticker.replace(".NS", "")


# ─── ADK Tool: Send Notification ─────────────────────────────────────────────

def send_notification(title: str, body: str, direction: str = "UP") -> bool:
    """
    Send push notification to phone via ntfy.sh.
    
    Args:
        title: Notification title
        body: Notification body text
        direction: "UP" or "DOWN" for priority/tags
    
    Returns:
        True if sent successfully, False otherwise
    """
    if not Config.NTFY_TOPIC:
        # Fallback: print to terminal
        print(f"\n{'='*50}\n{title}\n{body}\n{'='*50}")
        return True

    priority = "high" if direction == "UP" else "default"
    tags = "chart_with_upwards_trend,india" if direction == "UP" else "gem,india,moneybag"

    try:
        clean_title = title.encode("latin-1", errors="ignore").decode("latin-1").strip()[:120]
        resp = requests.post(
            f"https://ntfy.sh/{Config.NTFY_TOPIC}",
            data=body.encode("utf-8"),
            headers={
                "Title": clean_title,
                "Priority": priority,
                "Tags": tags,
            },
            timeout=10,
        )
        if resp.status_code == 200:
            log("📲 Phone notification sent ✅")
            return True
        else:
            log(f"ntfy error {resp.status_code}: {resp.text}", "ERROR")
            return False
    except Exception as e:
        log(f"ntfy send failed: {e}", "ERROR")
        return False


# ─── ADK Tool: Get YouTube Transcript ────────────────────────────────────────

def get_youtube_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from URL.
    
    Args:
        url: YouTube video URL
    
    Returns:
        Video ID or None
    """
    import re
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_youtube_transcript(video_url: str) -> Optional[str]:
    """
    Fetch YouTube video transcript.
    
    Args:
        video_url: YouTube video URL
    
    Returns:
        Full transcript text or None
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        video_id = get_youtube_video_id(video_url)
        if not video_id:
            log(f"Could not extract video ID from: {video_url}", "WARN")
            return None
        
        # Fetch transcript (prefer English, then Hindi)
        transcript_list = YouTubeTranscriptApi.get_transcript(
            video_id, 
            languages=['en', 'hi', 'en-IN']
        )
        
        # Combine all text segments
        full_text = " ".join([entry['text'] for entry in transcript_list])
        log(f"Fetched transcript ({len(full_text)} chars) for video: {video_id}")
        return full_text
        
    except Exception as e:
        log(f"Could not fetch transcript: {e}", "WARN")
        return None


def extract_stock_mentions_from_transcript(transcript: str) -> List[str]:
    """
    Extract stock/company mentions from YouTube transcript.
    
    Args:
        transcript: Full transcript text
    
    Returns:
        List of stock tickers mentioned (e.g., ["HAL.NS", "RELIANCE.NS"])
    """
    import re
    
    # Common Indian stock names and their tickers
    stock_keywords = {
        # Defense
        "HAL": "HAL.NS", "Hindustan Aeronautics": "HAL.NS",
        "BEL": "BEL.NS", "Bharat Electronics": "BEL.NS",
        "BEML": "BEML.NS",
        "Mazagon Dock": "MAZDOCK.NS", "MDL": "MAZDOCK.NS",
        "Bharat Dynamics": "BDL.NS", "BDL": "BDL.NS",
        "Cochin Shipyard": "COCHINSHIP.NS",
        "GRSE": "GRSE.NS", "Garden Reach": "GRSE.NS",
        "MTAR": "MTARTECH.NS",
        "Paras Defence": "PARASDEF.NS",
        
        # IT
        "TCS": "TCS.NS", "Tata Consultancy": "TCS.NS",
        "Infosys": "INFY.NS", "INFY": "INFY.NS",
        "Wipro": "WIPRO.NS", "WIPRO": "WIPRO.NS",
        "HCL Tech": "HCLTECH.NS", "HCLTECH": "HCLTECH.NS",
        "Tech Mahindra": "TECHM.NS", "TECHM": "TECHM.NS",
        "LTI Mindtree": "LTIM.NS", "LTIM": "LTIM.NS",
        "Persistent": "PERSISTENT.NS",
        "Coforge": "COFORGE.NS",
        "Mphasis": "MPHASIS.NS",
        
        # Banking & Finance
        "HDFC Bank": "HDFCBANK.NS", "HDFCBANK": "HDFCBANK.NS",
        "ICICI Bank": "ICICIBANK.NS", "ICICIBANK": "ICICIBANK.NS",
        "SBI": "SBIN.NS", "State Bank": "SBIN.NS",
        "Kotak": "KOTAKBANK.NS", "KOTAKBANK": "KOTAKBANK.NS",
        "Axis Bank": "AXISBANK.NS", "AXISBANK": "AXISBANK.NS",
        "IndusInd Bank": "INDUSINDBK.NS",
        "Yes Bank": "YESBANK.NS",
        "Bank of Baroda": "BANKBARODA.NS", "BOB": "BANKBARODA.NS",
        "Punjab National Bank": "PNB.NS", "PNB": "PNB.NS",
        "Canara Bank": "CANBK.NS",
        "IDFC First": "IDFCFIRSTB.NS",
        "Bajaj Finance": "BAJFINANCE.NS",
        "Bajaj Finserv": "BAJAJFINSV.NS",
        "SBI Life": "SBILIFE.NS",
        "HDFC Life": "HDFCLIFE.NS",
        "ICICI Prudential": "ICICIPRULI.NS",
        
        # Oil & Gas
        "Reliance": "RELIANCE.NS", "RIL": "RELIANCE.NS",
        "ONGC": "ONGC.NS", "Oil and Natural Gas": "ONGC.NS",
        "IOC": "IOC.NS", "Indian Oil": "IOC.NS",
        "BPCL": "BPCL.NS", "Bharat Petroleum": "BPCL.NS",
        "HPCL": "HINDPETRO.NS", "Hindustan Petroleum": "HINDPETRO.NS",
        "GAIL": "GAIL.NS",
        "Oil India": "OIL.NS",
        "Petronet LNG": "PETRONET.NS",
        
        # Auto & EV
        "Tata Motors": "TATAMOTORS.NS", "TATAMOTORS": "TATAMOTORS.NS",
        "Maruti": "MARUTI.NS", "Maruti Suzuki": "MARUTI.NS",
        "Mahindra": "M&M.NS", "M&M": "M&M.NS",
        "Bajaj Auto": "BAJAJ-AUTO.NS",
        "Hero MotoCorp": "HEROMOTOCO.NS", "HEROMOTOCO": "HEROMOTOCO.NS",
        "Eicher Motors": "EICHERMOT.NS", "Royal Enfield": "EICHERMOT.NS",
        "TVS Motor": "TVSMOTOR.NS",
        "Ashok Leyland": "ASHOKLEY.NS",
        "Escorts": "ESCORTS.NS",
        "Motherson Sumi": "MOTHERSON.NS",
        "Bosch": "BOSCHLTD.NS",
        "MRF": "MRF.NS",
        "Apollo Tyres": "APOLLOTYRE.NS",
        "CEAT": "CEAT.NS",
        
        # Metals & Mining
        "Tata Steel": "TATASTEEL.NS", "TATASTEEL": "TATASTEEL.NS",
        "JSW Steel": "JSWSTEEL.NS", "JSWSTEEL": "JSWSTEEL.NS",
        "Hindalco": "HINDALCO.NS",
        "Vedanta": "VEDL.NS", "VEDL": "VEDL.NS",
        "SAIL": "SAIL.NS",
        "NMDC": "NMDC.NS",
        "MOIL": "MOIL.NS",
        "Hindustan Zinc": "HINDZINC.NS",
        "Coal India": "COALINDIA.NS",
        "Jindal Steel": "JINDALSTEL.NS", "JSPL": "JINDALSTEL.NS",
        "Hindalco": "HINDALCO.NS",
        
        # Pharma
        "Sun Pharma": "SUNPHARMA.NS", "SUNPHARMA": "SUNPHARMA.NS",
        "Dr Reddy": "DRREDDY.NS", "DRREDDY": "DRREDDY.NS",
        "Cipla": "CIPLA.NS",
        "Divi's Lab": "DIVISLAB.NS", "DIVISLAB": "DIVISLAB.NS",
        "Biocon": "BIOCON.NS",
        "Aurobindo": "AUROPHARMA.NS",
        "Lupin": "LUPIN.NS",
        "Torrent Pharma": "TORNTPHARM.NS",
        "Alkem": "ALKEM.NS",
        "Cadila": "ZYDUSLIFE.NS", "Zydus": "ZYDUSLIFE.NS",
        
        # FMCG
        "Hindustan Unilever": "HINDUNILVR.NS", "HUL": "HINDUNILVR.NS",
        "ITC": "ITC.NS",
        "Nestle": "NESTLEIND.NS",
        "Britannia": "BRITANNIA.NS",
        "Dabur": "DABUR.NS",
        "Marico": "MARICO.NS",
        "Godrej Consumer": "GODREJCP.NS",
        "Colgate": "COLPAL.NS",
        "Tata Consumer": "TATACONSUM.NS",
        "Varun Beverages": "VBL.NS",
        
        # Infrastructure & Construction
        "L&T": "LT.NS", "Larsen": "LT.NS", "Larsen and Toubro": "LT.NS",
        "Adani Ports": "ADANIPORTS.NS",
        "Adani Green": "ADANIGREEN.NS",
        "Adani Power": "ADANIPOWER.NS",
        "Adani Enterprises": "ADANIENT.NS",
        "UltraTech": "ULTRACEMCO.NS", "UltraTech Cement": "ULTRACEMCO.NS",
        "Ambuja Cement": "AMBUJACEM.NS",
        "ACC": "ACC.NS",
        "Shree Cement": "SHREECEM.NS",
        "Grasim": "GRASIM.NS",
        "IRB Infra": "IRB.NS",
        "NBCC": "NBCC.NS",
        
        # Power & Renewables
        "NTPC": "NTPC.NS",
        "Power Grid": "POWERGRID.NS",
        "Tata Power": "TATAPOWER.NS",
        "Adani Green": "ADANIGREEN.NS",
        "Adani Transmission": "ADANITRANS.NS",
        "Suzlon": "SUZLON.NS",
        "Torrent Power": "TORNTPOWER.NS",
        "JSW Energy": "JSWENERGY.NS",
        "CESC": "CESC.NS",
        
        # Telecom
        "Bharti Airtel": "BHARTIARTL.NS", "Airtel": "BHARTIARTL.NS",
        "Reliance Jio": "RELIANCE.NS", "Jio": "RELIANCE.NS",
        "Vodafone Idea": "IDEA.NS", "VI": "IDEA.NS",
        "Indus Towers": "INDUSTOWER.NS",
        
        # Chemicals
        "UPL": "UPL.NS",
        "PI Industries": "PIIND.NS",
        "Aarti Industries": "AARTIIND.NS",
        "Deepak Nitrite": "DEEPAKNTR.NS",
        "Balaji Amines": "BALAMINES.NS",
        "SRF": "SRF.NS",
        
        # Retail & E-commerce
        "DMart": "DMART.NS", "Avenue Supermarts": "DMART.NS",
        "Trent": "TRENT.NS",
        "Titan": "TITAN.NS",
        "Jubilant FoodWorks": "JUBLFOOD.NS",
        "Zomato": "ZOMATO.NS",
        "Nykaa": "NYKAA.NS",
        "Paytm": "PAYTM.NS",
        
        # Technology & Platforms
        "Dixon": "DIXON.NS", "Dixon Technologies": "DIXON.NS",
        "Amber Enterprises": "AMBER.NS",
        "KPIT": "KPITTECH.NS",
        "Happiest Minds": "HAPPSTMNDS.NS",
        
        # Railways
        "IRCTC": "IRCTC.NS",
        "RVNL": "RVNL.NS", "Rail Vikas": "RVNL.NS",
        "IRFC": "IRFC.NS",
        "IRCON": "IRCON.NS",
        "Jupiter Wagons": "JWL.NS",
        
        # Aviation & Hospitality
        "InterGlobe": "INDIGO.NS", "IndiGo": "INDIGO.NS",
        "SpiceJet": "SPICEJET.NS",
        "Indian Hotels": "INDHOTEL.NS", "Taj Hotels": "INDHOTEL.NS",
        "Lemon Tree": "LEMONTREE.NS",
        
        # Others
        "PFC": "PFC.NS", "Power Finance": "PFC.NS",
        "REC": "RECLTD.NS",
        "Solar Industries": "SOLARINDS.NS",
        "Polycab": "POLYCAB.NS",
        "Havells": "HAVELLS.NS",
        "Crompton": "CROMPTON.NS",
        "V-Guard": "VGUARD.NS",
        "Page Industries": "PAGEIND.NS",
        "Pidilite": "PIDILITIND.NS",
        "Asian Paints": "ASIANPAINT.NS",
        "Berger Paints": "BERGEPAINT.NS",
        
        # Commodities
        "Gold": "GOLD", "gold": "GOLD",
        "Silver": "SILVER", "silver": "SILVER",
    }
    
    mentioned_stocks = set()
    transcript_lower = transcript.lower()
    
    for keyword, ticker in stock_keywords.items():
        # Case-insensitive search for company names
        if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', transcript_lower):
            mentioned_stocks.add(ticker)
            log(f"Found mention: {keyword} → {ticker}")
    
    return list(mentioned_stocks)


# ─── Tool Registry (for ADK) ─────────────────────────────────────────────────

# Define tools that can be called by the ADK agent
TOOLS = {
    "fetch_news_articles": fetch_news_articles,
    "fetch_youtube_videos": fetch_youtube_videos,
    "get_stock_price": get_stock_price,
    "get_stock_name": get_stock_name,
    "get_stock_fundamentals": get_stock_fundamentals,
    "send_notification": send_notification,
    "get_youtube_transcript": get_youtube_transcript,
    "extract_stock_mentions_from_transcript": extract_stock_mentions_from_transcript,
}
