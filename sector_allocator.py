"""
sector_allocator.py

For applying LLM sentiment logic to macroeconomic texts and determining tokenized equity weights.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

QWEN_API_KEY = os.getenv("QWEN_API_KEY")

def analyze_macro_sentiment_fallback(text_content):
    """
    Local heuristic fallback analyzer based on keyword matching.
    Used if the Qwen API is unreachable or the credentials are mock.
    
    Args:
        text_content (str): The text content to analyze.
        
    Returns:
        str: 'Hawkish', 'Dovish', or 'Neutral'.
    """
    text = text_content.lower()
    
    # Define hawkish vs dovish keywords
    hawkish_words = ["raise", "raising", "hike", "hiking", "elevated", "tightening", "restrictive", "firming", "hawkish"]
    dovish_words = ["cut", "cutting", "easing", "ease", "moderate", "moderated", "lower", "support", "accommodative", "dovish"]
    
    hawkish_count = sum(text.count(word) for word in hawkish_words)
    dovish_count = sum(text.count(word) for word in dovish_words)
    
    if hawkish_count > dovish_count:
        return "Hawkish"
    elif dovish_count > hawkish_count:
        return "Dovish"
    else:
        return "Neutral"

def analyze_macro_sentiment(text_content):
    """
    Connects to the Qwen model API to categorize Federal Reserve sentiment.
    If the API call fails or credentials are not set, it degrades gracefully
    to a local keyword-based heuristic analysis.
    
    Args:
        text_content (str): Fed statement or macroeconomic text to analyze.
        
    Returns:
        str: 'Hawkish', 'Dovish', or 'Neutral'.
    """
    # Degrade gracefully if key is missing or mock
    if not QWEN_API_KEY or QWEN_API_KEY.startswith("mock") or len(QWEN_API_KEY) < 8:
        print("[WARNING] Invalid or missing QWEN_API_KEY. Running local heuristic analyzer fallback.")
        return analyze_macro_sentiment_fallback(text_content)
        
    # Standard Qwen compatible Chat Completion API endpoint
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = (
        "You are an expert macroeconomic analyst. Analyze the following macroeconomic announcement "
        "or Federal Reserve policy statement. Categorize the sentiment strictly as one of the "
        "following three options: 'Hawkish', 'Dovish', or 'Neutral'. "
        "Do not output anything else; respond with exactly one of those three words."
    )
    
    payload = {
        "model": "qwen-plus",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text_content}
        ],
        "temperature": 0.0
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            
            # Match the parsed response to our exact categories
            for category in ["Hawkish", "Dovish", "Neutral"]:
                if category.lower() in content.lower():
                    return category
                    
            print(f"[WARNING] API returned ambiguous content: '{content}'. Falling back to heuristics.")
            return analyze_macro_sentiment_fallback(text_content)
        else:
            print(f"[WARNING] Qwen API call failed (HTTP {response.status_code}): {response.text}. Falling back to heuristics.")
            return analyze_macro_sentiment_fallback(text_content)
            
    except Exception as e:
        print(f"[WARNING] Exception encountered during Qwen API call: {e}. Falling back to heuristics.")
        return analyze_macro_sentiment_fallback(text_content)

def calculate_target_allocation(sentiment):
    """
    Maps macroeconomic sentiment to target portfolio weights across Bitget's tokenized spot equities.
    
    Args:
        sentiment (str): 'Hawkish', 'Dovish', or 'Neutral'.
        
    Returns:
        dict: Allocation percentages for NVDA, TSLA, QQQ, TLT (treasuries), and USDT (cash).
    """
    sentiment_clean = sentiment.strip().capitalize()
    
    if sentiment_clean == "Dovish":
        # Accommodative policy -> Aggressively long growth equities
        return {
            "rNVDA": 0.40,
            "rTSLA": 0.20,
            "rQQQ": 0.30,
            "rTLT": 0.05,
            "rUSDT": 0.05
        }
    elif sentiment_clean == "Hawkish":
        # Restrictive policy -> Defensive stablecoins and long-term treasuries
        return {
            "rNVDA": 0.05,
            "rTSLA": 0.05,
            "rQQQ": 0.10,
            "rTLT": 0.30,
            "rUSDT": 0.50
        }
    else:  # Neutral
        # Balanced strategy
        return {
            "rNVDA": 0.20,
            "rTSLA": 0.10,
            "rQQQ": 0.20,
            "rTLT": 0.25,
            "rUSDT": 0.25
        }

if __name__ == "__main__":
    import fed_watcher
    
    print("=== Testing sector_allocator.py ===")
    
    # 1. Retrieve catalyst from fed_watcher
    print("\n[Step 1] Fetching live macro catalysts...")
    catalysts = fed_watcher.fetch_macro_catalysts()
    
    active_catalyst = ""
    source = ""
    
    if catalysts:
        latest = catalysts[0]
        active_catalyst = f"Title: {latest['title']}\nDescription: {latest['description']}"
        source = f"Live RSS: {latest['title']}"
    else:
        print("[INFO] No live catalysts available. Falling back to mock statement.")
        active_catalyst = fed_watcher.get_mock_fomc_statement("hawkish")
        source = "Mock Hawkish Statement"
        
    print(f"\n[Step 2] Processing catalyst source: {source}")
    print("-" * 60)
    print(active_catalyst[:200] + "...")
    print("-" * 60)
    
    # 2. Perform sentiment analysis
    sentiment = analyze_macro_sentiment(active_catalyst)
    print(f"\n[Step 3] Sentiment Result: {sentiment}")
    
    # 3. Calculate target allocation
    allocation = calculate_target_allocation(sentiment)
    print("\n[Step 4] Target Allocation Matrix:")
    print("=" * 35)
    for asset, weight in allocation.items():
        print(f" {asset:6} : {weight * 100:5.1f}%")
    print("=" * 35)
    
    # 4. Verify Dovish scenario path
    print("\n[Step 5] Verifying secondary (Dovish) pipeline path...")
    mock_dovish = fed_watcher.get_mock_fomc_statement("dovish")
    dovish_sentiment = analyze_macro_sentiment(mock_dovish)
    dovish_allocation = calculate_target_allocation(dovish_sentiment)
    
    print(f"Dovish Catalyst Sentiment: {dovish_sentiment}")
    print("=" * 35)
    for asset, weight in dovish_allocation.items():
        print(f" {asset:6} : {weight * 100:5.1f}%")
    print("=" * 35)
    print("\n====================================")
