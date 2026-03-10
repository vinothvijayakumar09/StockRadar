# 📺 YouTube Channel Monitoring Setup

Monitor stock recommendations from YouTube channels like @berich467 and get instant alerts!

## Quick Setup

### 1. Get the Channel ID

Run this helper script with the YouTube handle:

```bash
python3 get_youtube_channel_id.py @berich467
```

This will output:

```
✅ Channel ID found: UCZ-RwglseBp2cAuHwYGb91Q

Add this to your .env file:
YOUTUBE_CHANNEL_ID=UCZ-RwglseBp2cAuHwYGb91Q
```

### 2. Add to .env

Open your `.env` file and add:

```bash
YOUTUBE_CHANNEL_ID=UCZ-RwglseBp2cAuHwYGb91Q
```

### 3. Restart the Agent

```bash
python agent.py
```

You'll see in the logs:

```
YouTube Channel: Enabled
```

## How It Works

1. **Fetches latest videos** - Gets the 2 most recent uploads via RSS feed
2. **AI analyzes content** - Examines video title & description for stock mentions
3. **Sends alerts** - Notifications with stock recommendations appear on your phone

## Example Alert

```
📺 Top 3 Stocks to Buy Today | Defense Sector Analysis

📈 HAL | UP 8% | High confidence

🏢 Hindustan Aeronautics Ltd
💰 Now:    ₹4,230.50
🎯 Target: ₹4,568.94 (UP 8%)
⏱ When:   48hrs
🧠 Why:    YouTube analyst recommends defense sector stocks
🟢 Confidence: High

📰 📺 Top 3 Stocks to Buy Today | Defense Sector Analysis
```

## Add Multiple Channels

To monitor multiple YouTube channels, you can:

1. Get each channel ID using the helper script
2. Modify `config.py` to support a list of channels (currently supports one)

Or manually combine RSS feeds by editing the `get_youtube_feeds()` function in `agent.py`.

## Supported Channels

Works with **any** YouTube channel that:

- Posts about stocks/investing
- Has daily or regular uploads
- Mentions stock tickers or company names

## Troubleshooting

**Channel ID not found?**

- Make sure the handle is correct (e.g., `@berich467`)
- Try visiting the channel page and viewing source
- Search for "channelId" in the page source and copy it manually

**No videos fetched?**

- Check if the channel has recent uploads (within last few days)
- Verify the channel ID is correct
- Check logs for errors

**Alerts not working?**

- Ensure the AI can detect stock mentions in video titles/descriptions
- Some channels may not mention specific tickers - AI will try to infer
- Check that your MISTRAL_API_KEY is working

## Privacy Note

YouTube RSS feeds are public and don't require authentication. No YouTube account needed!
