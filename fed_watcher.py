"""
fed_watcher.py

For fetching and parsing macroeconomic announcements and Fed statement catalysts.
"""

import os
import xml.etree.ElementTree as ET
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def verify_env_loading():
    """
    Safely verifies that the necessary environment keys are loaded,
    printing confirmation without disclosing secrets.
    """
    qwen_key = os.getenv("QWEN_API_KEY")
    bitget_uid = os.getenv("BITGET_UID")
    
    if qwen_key:
        masked_key = f"{qwen_key[:3]}...{qwen_key[-3:]}" if len(qwen_key) > 6 else "***"
        print(f"[SUCCESS] QWEN_API_KEY loaded securely. (Verification pattern: {masked_key})")
    else:
        print("[WARNING] QWEN_API_KEY is missing from environment.")
        
    if bitget_uid:
        masked_uid = f"{bitget_uid[:3]}...{bitget_uid[-3:]}" if len(bitget_uid) > 6 else "***"
        print(f"[SUCCESS] BITGET_UID loaded securely. (Verification pattern: {masked_uid})")
    else:
        print("[WARNING] BITGET_UID is missing from environment.")

def fetch_macro_catalysts():
    """
    Retrieves latest Federal Reserve monetary policy press releases from the official XML feed.
    
    Returns:
        list of dict: List containing titles, descriptions, and publish dates of macroeconomic updates.
    """
    url = "https://www.federalreserve.gov/feeds/press_monetary.xml"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        catalysts = []
        
        # Find all <item> tags in the RSS feed
        for item in root.findall(".//item"):
            title = item.find("title")
            description = item.find("description")
            link = item.find("link")
            pub_date = item.find("pubDate")
            
            catalysts.append({
                "title": title.text.strip() if title is not None and title.text else "",
                "description": description.text.strip() if description is not None and description.text else "",
                "link": link.text.strip() if link is not None and link.text else "",
                "pub_date": pub_date.text.strip() if pub_date is not None and pub_date.text else ""
            })
            
        return catalysts
    except Exception as e:
        print(f"[ERROR] Failed to fetch macro catalysts: {e}")
        return []

def get_mock_fomc_statement(sentiment="hawkish"):
    """
    Returns a mock Federal Reserve FOMC interest rate decision statement.
    Used for local testing when economic calendars are quiet.
    
    Args:
        sentiment (str): Either 'hawkish' (raising rates / tight policy) or 'dovish' (moderating rates / loose policy).
        
    Returns:
        str: A raw text block simulating an FOMC statement.
    """
    if sentiment.lower() == "hawkish":
        return (
            "Federal Reserve Issues FOMC Statement\n\n"
            "Recent indicators suggest that economic activity has been expanding at a solid pace. "
            "Job gains have remained strong in recent months, and the unemployment rate has remained low. "
            "Inflation has eased over the past year but remains elevated.\n\n"
            "The Committee seeks to achieve maximum employment and inflation at the rate of 2 percent over the longer run. "
            "In support of these goals, the Committee decided to raise the target range for the federal funds rate to 5.50 to 5.75 percent. "
            "The Committee will closely monitor the implications of incoming information for the economic outlook. "
            "In determining the extent of additional policy firming that may be appropriate to return inflation to 2 percent over time, "
            "the Committee will take into account the cumulative tightening of monetary policy, the lags with which monetary policy "
            "affects economic activity and inflation, and economic and financial developments. "
            "In addition, the Committee will continue reducing its holdings of Treasury securities and agency debt and agency "
            "mortgage-backed securities, as described in its previously announced plans. "
            "The Committee is strongly committed to returning inflation to its 2 percent objective."
        )
    else:
        return (
            "Federal Reserve Issues FOMC Statement\n\n"
            "Recent indicators suggest that economic activity has expanded at a moderate pace. "
            "Job gains have moderated in recent months, and the unemployment rate has nudged higher, though remaining low. "
            "Inflation has continued to ease toward the Committee's 2 percent objective.\n\n"
            "The Committee seeks to achieve maximum employment and inflation at the rate of 2 percent over the longer run. "
            "In support of these goals, the Committee decided to maintain the target range for the federal funds rate at 4.75 to 5.00 percent. "
            "The Committee will carefully assess incoming data, the evolving outlook, and the balance of risks. "
            "In light of the progress on inflation and the cooling labor market, the Committee will consider the appropriate "
            "adjustments to the stance of monetary policy. The Committee stands ready to adjust the stance of monetary policy "
            "as appropriate if risks emerge that could impede the attainment of the Committee's goals. "
            "The Committee is strongly committed to supporting maximum employment and returning inflation to its 2 percent objective."
        )

if __name__ == "__main__":
    print("=== Testing fed_watcher.py ===")
    verify_env_loading()
    
    print("\n--- Testing fetch_macro_catalysts() ---")
    catalysts = fetch_macro_catalysts()
    print(f"Fetched {len(catalysts)} catalysts from the FOMC XML Feed.")
    for idx, cat in enumerate(catalysts[:3], 1):
        print(f"\n[{idx}] {cat['title']} ({cat['pub_date']})")
        print(f"Link: {cat['link']}")
        print(f"Summary: {cat['description'][:150]}...")

    print("\n--- Testing get_mock_fomc_statement('hawkish') ---")
    hawkish_stmt = get_mock_fomc_statement("hawkish")
    print(hawkish_stmt[:300] + "...")

    print("\n--- Testing get_mock_fomc_statement('dovish') ---")
    dovish_stmt = get_mock_fomc_statement("dovish")
    print(dovish_stmt[:300] + "...")
    print("===============================")
