# 🎨 Web UI Usage Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Your Settings
Edit `.env` file:
```env
# Your Mistral AI API Key (required)
MISTRAL_API_KEY=your_key_here

# Your ntfy.sh topic for notifications (required)
NTFY_TOPIC=your_topic_here

# YouTube Channel ID (optional - can be set via UI)
YOUTUBE_CHANNEL_ID=UCxxxxxxxxxxxx
```

### 3. Launch the Web UI
```bash
streamlit run app.py
```

This will open your browser at `http://localhost:8501`

---

## Features

### 📺 YouTube Analysis
- Enter any YouTube channel URL (e.g., `https://www.youtube.com/@berich467`)
- Click "Run Analysis" to analyze videos
- Get transcript-based stock mentions + AI recommendations

### 📰 News Analysis
- Automatically fetches from multiple RSS feeds:
  - Economic Times
  - Moneycontrol
  - LiveMint
  - NDTV Profit
  - Business Standard
- AI analyzes news sentiment
- Fetches real-time stock prices from NSE
- Gets fundamental data from screener.in

### 📊 Fundamental Analysis
Each stock shows:
- **P/E Ratio** - Valuation metric
- **ROE** - Return on Equity
- **Debt/Equity** - Financial health
- **Market Cap** - Company size
- **Price Target** - AI-predicted movement

### 🔔 Notifications
- Results sent to your phone via ntfy.sh
- Real-time alerts with stock picks
- Shows both news sources and YouTube mentions

---

## UI Components

### Left Panel: Actions
- **YouTube Channel URL Input** - Paste any channel URL
- **Run Analysis Button** - Triggers complete analysis
- **Progress Indicators** - See real-time status

### Right Panel: Tools
- **LLM Settings** - Choose Mistral or Ollama
- **Test Stock Lookup** - Quick price/fundamental check
- **Configuration** - ntfy.sh topic settings

---

## Running Modes

### 1. Web UI Mode (Interactive)
```bash
streamlit run app.py
```
- Best for: Manual analysis, testing, exploring
- Access: Browser-based interface
- Control: Click buttons to run

### 2. CLI Mode (Automated)
```bash
python agent.py
```
- Best for: Background monitoring, cron jobs
- Runs every 12 hours (configurable)
- Headless operation

---

## Example Workflow

1. **Launch UI**
   ```bash
   streamlit run app.py
   ```

2. **Enter YouTube Channel**
   - Paste: `https://www.youtube.com/@berich467`
   - Click "Run Analysis"

3. **View Results**
   - See live progress
   - Check stock recommendations
   - View fundamentals (P/E, ROE, Debt/Equity)

4. **Get Notifications**
   - Open ntfy.sh app on phone
   - Receive formatted alerts with:
     - Stocks mentioned in video
     - AI-recommended stocks
     - Price targets & confidence

---

## Troubleshooting

### UI won't start
```bash
# Reinstall streamlit
pip install -r requirements.txt

# Try again
streamlit run app.py
```

### No notifications
- Check `.env` has correct `NTFY_TOPIC`
- Verify ntfy.sh app is subscribed to same topic
- Test with: `curl -d "Test" ntfy.sh/your_topic`

### Missing fundamentals
- Some stocks may not have data on screener.in
- Commodities (GOLD, SILVER) don't have P/E ratios
- Check ticker format: `HAL.NS` (not just `HAL`)

### YouTube errors
- Ensure channel URL is correct format
- Some videos may not have transcripts
- Private videos are skipped automatically

---

## Advanced Features

### Test Individual Stocks
1. Enter ticker in "Test Stock Price" (e.g., `HAL.NS`)
2. Click "Get Price"
3. View current price + fundamentals instantly

### Change LLM Provider
- Switch between Mistral AI (cloud) and Ollama (local)
- Mistral: Better accuracy, requires API key
- Ollama: Free, runs locally, slower

---

## Tips

- **First run**: May take 2-3 minutes (fetching news, transcripts, fundamentals)
- **YouTube channels**: Works with any public channel
- **Stock tickers**: Always use `.NS` suffix for NSE stocks
- **Notifications**: Create unique ntfy.sh topic to avoid spam

---

## What Gets Analyzed

### News Sources (RSS)
- Economic Times - Market News
- Moneycontrol - Stock Updates
- LiveMint - Business Coverage
- NDTV Profit - Financial News
- Business Standard - Economy
- Financial Express - Markets
- The Hindu Business Line - Industry

### YouTube Analysis
- Video transcripts (English/Hindi)
- Stock mentions extraction
- Expert commentary analysis
- LLM-based recommendations

### Fundamental Metrics
- P/E Ratio, ROE, ROCE
- Debt-to-Equity, Market Cap
- Revenue/Profit Growth
- Dividend Yield

---

## Need Help?

Check the main `README.md` for:
- Environment setup
- API key configuration
- Troubleshooting guide
