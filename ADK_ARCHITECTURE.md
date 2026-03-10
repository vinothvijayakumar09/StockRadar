# Google ADK Framework - Architecture Documentation

## Overview

This Indian Stock Alert Agent has been restructured using **Google ADK (Agentic Development Kit)** principles while maintaining all original functionality:

- ✅ **Same LLM**: Mistral AI (no changes)
- ✅ **Same Channels**: NSE API, RSS feeds, YouTube
- ✅ **Same Notifications**: ntfy.sh phone alerts
- ✅ **Same Features**: Stock analysis, price tracking, aggregated alerts

## Framework Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Google ADK Framework                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────┐   │
│  │   tools.py   │───>│ agent_core.py│───>│  agent.py   │   │
│  │              │    │              │    │             │   │
│  │ - News fetch │    │ Agent        │    │ Main entry  │   │
│  │ - Stock data │    │ orchestration│    │ point       │   │
│  │ - Notify     │    │ - Analysis   │    │ - Loop      │   │
│  └──────────────┘    │ - Aggregation│    └─────────────┘   │
│         ↓            └──────────────┘                       │
│  ┌──────────────┐            ↓                              │
│  │   llm.py     │            ↓                              │
│  │ (Mistral AI) │<───────────┘                              │
│  └──────────────┘                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## File Structure

### 1. **agent.py** (Main Entry Point)

- Initializes the ADK agent
- Runs the main loop
- Handles startup and shutdown
- ~60 lines (previously 800+ lines)

### 2. **agent_core.py** (ADK Agent Core)

- `IndianStockAgent` class - main agent orchestrator
- Processes news articles with LLM analysis
- Aggregates stock recommendations
- Handles YouTube video analysis
- Formats and sends notifications
- ~370 lines of clean, modular code

### 3. **tools.py** (ADK Tools)

- **Tools** are reusable functions that the agent can call
- Pydantic models for type safety
- Functions:
  - `fetch_news_articles()` - Get RSS feeds
  - `fetch_youtube_videos()` - Get YouTube content
  - `get_stock_price()` - Fetch NSE prices
  - `get_stock_name()` - Company name lookup
  - `send_notification()` - Push to ntfy.sh
- ~360 lines

### 4. **llm.py** (LLM Integration)

- **Unchanged from original**
- Mistral AI for stock impact analysis
- Ollama local fallback option
- JSON response parsing

### 5. **config.py** (Configuration)

- **Unchanged from original**
- Environment variables
- Mistral API keys
- Same settings as before

### 6. **logger.py** (Logging)

- **Unchanged from original**
- Simple logging utility

## ADK Principles Applied

### 1. **Modularity**

- Tools are separated from agent logic
- Each component has a single responsibility
- Easy to extend with new tools

### 2. **Type Safety**

- Pydantic models for data validation
- Type hints throughout
- Structured data flow

### 3. **Reusability**

- Tools can be called independently
- Agent core can be used in different contexts
- LLM module is pluggable

### 4. **Scalability**

- Easy to add new data sources (tools)
- Can add multiple agents
- Configuration-driven behavior

## Key Improvements Over Original

| Aspect             | Before            | After (ADK)         |
| ------------------ | ----------------- | ------------------- |
| **Main file size** | 800+ lines        | 60 lines            |
| **Structure**      | Monolithic        | Modular (4 files)   |
| **Tools**          | Embedded in agent | Separate tools.py   |
| **Agent logic**    | Mixed with I/O    | Clean agent_core.py |
| **Type safety**    | Minimal           | Pydantic models     |
| **Testability**    | Hard to test      | Easy to unit test   |
| **Extensibility**  | Difficult         | Add tools easily    |

## How It Works (ADK Flow)

1. **agent.py** starts the main loop
2. Initializes **IndianStockAgent** from agent_core
3. Agent calls **tools** to fetch data:
   - `fetch_news_articles()`
   - `fetch_youtube_videos()`
4. For each article:
   - Agent calls **llm.py** (Mistral AI) for analysis
   - Gets stock recommendations
5. Agent aggregates recommendations:
   - Groups by stock ticker
   - Ranks by confidence and expected move
   - Fetches current prices using `get_stock_price()`
6. Agent formats and sends notifications using `send_notification()`
7. Repeat after configured interval

## Running the Agent

Same as before:

```bash
# Install dependencies (includes pydantic now)
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your MISTRAL_API_KEY and NTFY_TOPIC

# Run
python agent.py
```

## Configuration

**.env** (unchanged):

```
LLM_MODE=mistral                    # Same as before
MISTRAL_API_KEY=your_key_here       # Same Mistral AI
NTFY_TOPIC=your-topic               # Same notifications
YOUTUBE_CHANNEL_ID=channel_id       # Same YouTube monitoring
CHECK_INTERVAL_MINUTES=720          # Same interval (12 hours)
```

## Extending the Agent

### Adding New Tools

Create function in **tools.py**:

```python
def fetch_twitter_data() -> List[Dict[str, Any]]:
    """Fetch tweets about Indian stocks"""
    # Implementation
    return tweets
```

Register in **TOOLS** dict:

```python
TOOLS = {
    "fetch_news_articles": fetch_news_articles,
    "fetch_twitter_data": fetch_twitter_data,  # New tool
    # ...
}
```

Use in **agent_core.py**:

```python
from tools import fetch_twitter_data

# In agent run_cycle:
tweets = fetch_twitter_data()
self.process_news_aggregated(tweets)
```

### Adding New Agent Behaviors

Extend **IndianStockAgent** class in **agent_core.py**:

```python
def process_earnings_reports(self, reports: List[Dict]) -> None:
    """New agent behavior for earnings analysis"""
    # Implementation
```

## Benefits of ADK Framework

1. **Better Code Organization**: Clear separation of concerns
2. **Easier Debugging**: Isolated components
3. **Faster Development**: Add features without touching core logic
4. **Better Testing**: Mock tools easily for unit tests
5. **Team Collaboration**: Different people can work on tools vs agent logic
6. **Maintainability**: Changes in one module don't break others

## Migration Notes

All functionality preserved:

- ✅ RSS news feeds (same sources)
- ✅ YouTube channel monitoring (same channels)
- ✅ Mistral AI analysis (same LLM)
- ✅ NSE price fetching (same API)
- ✅ ntfy.sh notifications (same service)
- ✅ Aggregated alerts (same format)
- ✅ Stock recommendations (same logic)

**Nothing changed for the user** - just better code structure!

## Summary

This refactoring to Google ADK framework:

- Keeps **all original functionality**
- Uses **same LLM** (Mistral AI)
- Uses **same channels** (NSE, RSS, YouTube)
- Sends **same notifications** (ntfy.sh)
- Follows **ADK best practices**
- Improves **code quality** and **maintainability**

The agent now follows modern agentic framework patterns while preserving 100% of the features users love!
