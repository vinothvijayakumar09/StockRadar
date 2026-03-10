"""
LLM Module — Mistral API (primary) + Ollama (local fallback)
"""
from __future__ import annotations

import json
import requests
from config import Config
from logger import log

SYSTEM_PROMPT = """You are an expert Indian stock market analyst with deep knowledge of NSE-listed companies and fundamental analysis.

Given a news headline/video content AND fundamental data (when available), analyze its impact on Indian stocks AND commodities.

Rules:
- Suggest ANY relevant NSE listed stocks (ticker format: SYMBOL.NS)
- For commodities like gold/silver, use: GOLD or SILVER (no .NS suffix)
- Use your full knowledge of Indian companies across all sectors: defense, oil & gas, IT, pharma, banking, auto, renewable energy, FMCG, telecom, infrastructure, metals, real estate, chemicals, agriculture, textiles, cement, power, aviation, hospitality, retail, etc.
- **CONSIDER FUNDAMENTALS**: If P/E, ROE, Debt/Equity ratios are provided, factor them into your confidence and expected move
- High ROE (>15%), Low Debt/Equity (<1.0), reasonable P/E (<30) = Higher confidence
- Poor fundamentals = Lower confidence or avoid
- Be SPECIFIC — not every news affects stocks
- If news is about ONE specific company, return ONLY that one stock
- If news affects multiple companies in a sector, suggest 1-3 most impacted stocks
- If news is about gold/silver prices or trends, include GOLD or SILVER in recommendations
- Focus on direct, clear impact
- Consider both large-cap and mid-cap stocks that are directly affected

Direction Guidelines:
- "UP" = Stock likely to rise (positive news, contracts, growth, profit increase)
- "DOWN" = Stock likely to fall BUT with BUY opportunity (temporary dip, good fundamentals, overreaction to minor negative news)
- Don't suggest stocks with no recovery potential or fundamental issues

Fundamental Analysis (when data available):
- P/E Ratio: <20 (undervalued), 20-30 (fair), >30 (expensive)
- ROE: >15% (good), >25% (excellent)
- Debt/Equity: <0.5 (low debt), 0.5-1.0 (moderate), >1.0 (high debt)
- Profit/Sales Growth: >15% (strong growth)
- Consider fundamentals when setting confidence and expected_move_percent

Examples (not exhaustive):
- Defense contracts → HAL, BEL, BEML, MTAR, PARAS
- Oil & gas policy → RELIANCE, ONGC, IOC, BPCL, GAIL
- IT/rupee/exports → TCS, INFY, WIPRO, HCLTECH, TECHM
- Banking/rates → HDFCBANK, ICICIBANK, SBIN, KOTAKBANK, AXISBANK
- Pharma/FDA → SUNPHARMA, DRREDDY, CIPLA, DIVISLAB, AUROPHARMA
- Auto/EV → TATAMOTORS, MARUTI, M&M, BAJAJ-AUTO, HEROMOTOCO
- Renewable/solar → ADANIGREEN, TATAPOWER, SUZLON, NTPC
- Metals → TATASTEEL, JSWSTEEL, HINDALCO, VEDL, SAIL
- Infrastructure → LT, ADANIPORTS, IRFC, PFC
- Gold prices rising → GOLD (commodity recommendation)
- Silver prices/demand → SILVER (commodity recommendation)

Return ONLY valid JSON, no explanation, no markdown:
{
  "affected_stocks": ["TICKER.NS"],
  "direction": "UP",
  "expected_move_percent": 3.5,
  "reason": "Strong fundamentals with expected growth in revenue due to new contracts",
  "confidence": "High",
  "timeframe": "24hrs"
}

Note: The "reason" should be a clear, actionable insight (not starting with "because" or "due to").

If news has NO clear stock impact, return:
{"affected_stocks": []}
"""

def build_user_prompt(headline: str, summary: str, transcript: str = None, fundamentals: Dict[str, Any] = None) -> str:
    if transcript:
        # Use full transcript for detailed analysis (YouTube videos)
        prompt = f"""Video Title: {headline}

Video Transcript:
{transcript[:8000]}
"""
    else:
        # Use summary for news articles
        prompt = f"""News Headline: {headline}

Summary: {summary}
"""
    
    # Add fundamental data if available
    if fundamentals:
        prompt += "\n\nFUNDAMENTAL DATA:\n"
        if fundamentals.get("market_cap"):
            prompt += f"Market Cap: {fundamentals['market_cap']}\n"
        if fundamentals.get("pe_ratio"):
            prompt += f"P/E Ratio: {fundamentals['pe_ratio']}\n"
        if fundamentals.get("pb_ratio"):
            prompt += f"P/B Ratio: {fundamentals['pb_ratio']}\n"
        if fundamentals.get("roe"):
            prompt += f"ROE: {fundamentals['roe']}%\n"
        if fundamentals.get("roce"):
            prompt += f"ROCE: {fundamentals['roce']}%\n"
        if fundamentals.get("debt_to_equity") is not None:
            prompt += f"Debt/Equity: {fundamentals['debt_to_equity']}\n"
        if fundamentals.get("sales_growth_3yr"):
            prompt += f"Sales Growth (3Y): {fundamentals['sales_growth_3yr']}%\n"
        if fundamentals.get("profit_growth_3yr"):
            prompt += f"Profit Growth (3Y): {fundamentals['profit_growth_3yr']}%\n"
        if fundamentals.get("dividend_yield"):
            prompt += f"Dividend Yield: {fundamentals['dividend_yield']}%\n"
    
    if transcript:
        prompt += "\nBased on this detailed video transcript and fundamental data (if provided), which NSE stocks are being discussed or recommended? Analyze the expert's commentary and return JSON only."
    else:
        prompt += "\nWhich NSE stocks are affected and how? Consider fundamental data if provided. Return JSON only."
    
    return prompt


def parse_llm_response(raw: str) -> dict | None:
    """Extract JSON from LLM response, handling markdown fences etc."""
    try:
        return json.loads(raw.strip())
    except:
        pass
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(raw[start:end])
    except:
        pass
    log(f"Could not parse LLM response: {raw[:100]}", "WARN")
    return None


# ─── Mistral API ──────────────────────────────────────────────────────────────

def call_mistral(headline: str, summary: str, transcript: str = None, fundamentals: Dict[str, Any] = None) -> dict | None:
    if not Config.MISTRAL_API_KEY:
        log("MISTRAL_API_KEY not set in .env", "ERROR")
        return None

    headers = {
        "Authorization": f"Bearer {Config.MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": Config.MISTRAL_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": build_user_prompt(headline, summary, transcript, fundamentals)},
        ],
        "temperature": 0.1,
        "max_tokens": 300,
        "response_format": {"type": "json_object"},  # Mistral supports JSON mode
    }
    last_error = None
    for attempt in range(1, 4):
        try:
            resp = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            return parse_llm_response(content)
        except Exception as e:
            last_error = e
            log(f"Mistral attempt {attempt}/3 failed: {e}", "WARN")

    log(f"Mistral error: {last_error}", "ERROR")
    return None


# ─── Ollama (Local Fallback) ──────────────────────────────────────────────────

def call_ollama(headline: str, summary: str, transcript: str = None, fundamentals: Dict[str, Any] = None) -> dict | None:
    payload = {
        "model": Config.OLLAMA_MODEL,
        "prompt": f"{SYSTEM_PROMPT}\n\n{build_user_prompt(headline, summary, transcript, fundamentals)}",
        "stream": False,
        "options": {"temperature": 0.1},
    }
    try:
        resp = requests.post(
            f"{Config.OLLAMA_URL}/api/generate",
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        content = resp.json().get("response", "")
        return parse_llm_response(content)
    except Exception as e:
        log(f"Ollama error: {e}", "ERROR")
        return None


# ─── Main Entry ───────────────────────────────────────────────────────────────

def analyze_news_with_llm(headline: str, summary: str, transcript: str = None, fundamentals: Dict[str, Any] = None) -> dict | None:
    if Config.LLM_MODE == "mistral":
        return call_mistral(headline, summary, transcript, fundamentals)
    elif Config.LLM_MODE == "ollama":
        return call_ollama(headline, summary, transcript, fundamentals)
    else:
        log(f"Unknown LLM_MODE: {Config.LLM_MODE}", "ERROR")
        return None
