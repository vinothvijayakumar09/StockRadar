# 🇮🇳 Indian Stock Alert Agent (Google ADK Framework)

Get **instant phone notifications** when world events are likely to move NSE stocks.
100% free. No WhatsApp. No Telegram. No paid APIs.

**New:** Now built with Google ADK (Agentic Development Kit) for better modularity and scalability!

---

## What You Get On Your Phone

```
📈 HAL | UP 5% | High confidence

🏢 Hindustan Aeronautics Ltd
💰 Now:    ₹4,230.50
🎯 Target: ₹4,441.03 (UP 5%)
⏱ When:   48hrs
🧠 Why:    India signs $2B defense deal — directly boosts HAL order book
🟢 Confidence: High

📰 India inks major defense procurement deal with Israel
⚠️ Not financial advice. DYOR.
```

Notification lands on your phone like any other app — with sound, priority, and icon.

---

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│  Google ADK Framework (Agentic Development Kit)                │
│  ├─ Tools: News Fetching, Stock Data, Notifications            │
│  ├─ Agent Core: Orchestration & Analysis                       │
│  └─ LLM: Mistral AI for stock impact analysis                  │
└─────────────────────────────────────────────────────────────────┘
         ↓                           ↓
RSS News Feeds          →    AI Analysis (Mistral)    →    Phone Alerts
(ET, Moneycontrol)                                           (ntfy.sh)
         +                            ↓
YouTube Videos          →    NSE Stock Prices (Live)
(@berich467, etc)
```

**Architecture:**

- **Google ADK Framework** for agent orchestration
- **Mistral AI** for news analysis (same as before)
- **NSE API** for real-time stock prices
- **RSS Feeds** for news (Economic Times, Moneycontrol)
- **YouTube monitoring** for expert recommendations
- **ntfy.sh** for push notifications

All free. Runs every 12 hours (configurable).

---

## Setup Guide (10 minutes total)

### Step 1 — Install the ntfy app on your phone (2 min)

- **Android:** [Play Store → search "ntfy"](https://play.google.com/store/apps/details?id=io.heckel.ntfy)
- **iPhone:** [App Store → search "ntfy"](https://apps.apple.com/app/ntfy/id1625396347)

Open the app → tap **"+"** → type a unique topic name like `rahul-stocks-xk29a` → tap **Subscribe**

> Keep your topic name secret — anyone who knows it can read your alerts.

### Step 2 — Get a free Mistral API key (3 min)

- Go to [console.mistral.ai](https://console.mistral.ai)
- Sign up → Create API Key → copy it
- Free tier available (or pay as you go)

### Step 3 — Configure (1 min)

```bash
cp .env.example .env
```

Open `.env` and fill in:

```
MISTRAL_API_KEY=your_mistral_api_key_here
NTFY_TOPIC=rahul-stocks-xk29a   ← same topic you used in the app
```

### Step 4 — Install & Run (2 min)

```bash
pip install -r requirements.txt
python agent.py
```

Your phone will buzz with a test notification immediately. Then it checks news every 15 minutes.

---

## 🎨 Web UI (NEW!)

**Want a visual interface?** Launch the **Streamlit Web UI** for interactive analysis:

```bash
streamlit run app.py
```

This opens a browser-based dashboard where you can:

- ✅ **Paste YouTube Channel URL** directly (no need to find channel ID)
- ✅ **Click "Run Analysis"** to trigger on-demand analysis
- ✅ **View live progress** with real-time status updates
- ✅ **Test stock lookups** (get price + fundamentals instantly)
- ✅ **Configure settings** via UI (LLM provider, ntfy.sh topic)

### Web UI Features:

**Main Panel:**
- YouTube channel URL input
- One-click "Run Analysis" button
- Progress indicators (news fetching, AI analysis, etc.)
- Real-time results display

**Sidebar:**
- LLM provider settings (Mistral or Ollama)
- ntfy.sh topic configuration
- Quick stock price/fundamental lookup tool

### When to Use Which Mode:

| Mode | Best For | Command |
|------|----------|---------|
| **Web UI** | Manual analysis, testing, exploring | `streamlit run app.py` |
| **CLI/Background** | Automated monitoring, cron jobs | `python agent.py` |

**📖 Full UI documentation:** See [UI_GUIDE.md](UI_GUIDE.md)

---

## 📺 Bonus: Monitor YouTube Stock Channels (Optional)

Follow stock recommendations from your favorite YouTube channels!

### Add a YouTube Channel:

```bash
# Get the channel ID (for @berich467):
python3 get_youtube_channel_id.py @berich467
```

This will show:

```
✅ Channel ID found: UCZ-RwglseBp2cAuHwYGb91Q

Add this to your .env file:
YOUTUBE_CHANNEL_ID=UCZ-RwglseBp2cAuHwYGb91Q
```

Now add it to your `.env` file:

```
YOUTUBE_CHANNEL_ID=UCZ-RwglseBp2cAuHwYGb91Q
```

The agent will now analyze daily video uploads and send alerts for stock mentions! 🎉

**How it works:**

- Fetches latest 2 videos from the channel (RSS feed)
- AI analyzes video title & description for stock mentions
- Sends notifications with stock recommendations
- Works with any YouTube channel that talks about stocks

---

## Free Tools Used

| Tool                                                  | What it does             | Cost      |
| ----------------------------------------------------- | ------------------------ | --------- |
| [Mistral AI](https://console.mistral.ai)              | AI analysis brain        | Free tier |
| [NSE API](https://www.nseindia.com)                   | Live NSE stock prices    | Free      |
| [feedparser](https://github.com/kurtmckee/feedparser) | News RSS feeds           | Free      |
| [ntfy.sh](https://ntfy.sh)                            | Phone push notifications | Free      |
| [Ollama](https://ollama.com)                          | Local AI (optional)      | Free      |

---

## Want 100% Offline? Use Ollama Instead

```bash
# Install Ollama from https://ollama.com
ollama pull llama3.2

# In .env:
LLM_MODE=ollama
```

No internet needed for the AI part. NSE API and ntfy still need internet.

---

## Run 24/7 for Free

**Option 1 — Your own machine (background)**

```bash
nohup python agent.py > agent.log 2>&1 &
```

**Option 2 — Railway.app** (free cloud hosting)
Push to GitHub → connect Railway → deploy. Free tier is enough.

**Option 3 — Render.com**
Free background worker, always on.

---

## Project Structure

```
indian-stock-agent/
├── agent.py          ← main loop
├── llm.py            ← AI brain (Groq or Ollama)
├── config.py         ← all settings
├── logger.py         ← simple logging
├── requirements.txt  ← 4 packages only
└── .env.example      ← copy to .env and fill in
```

---

⚠️ **Disclaimer:** This tool is for educational purposes only. Not financial advice. Always do your own research before investing.
