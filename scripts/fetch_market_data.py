import httpx
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MarketFetcher")

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def robust_parse(row_text):
    pattern = r'([\d,.]+)\s+([+-][\d,.]+)\s+\(([^)]+%)\)'
    match = re.search(pattern, row_text)
    if match:
        return match.groups()
    match_price = re.search(r'([\d,.]+)', row_text)
    price = match_price.group(1) if match_price else ""
    return price, "", ""

def fetch_market_data(url, is_stock=False):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}
    try:
        response = httpx.get(url, headers=headers, timeout=15.0, follow_redirects=True)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        table = soup.find('table')
        if not table: return []
        rows = table.find_all('tr')[1:]
        for row in rows:
            cols = [clean_text(td.text) for td in row.find_all('td')]
            if not cols: continue
            full_line = " ".join(cols)
            price, change, percent = robust_parse(full_line)
            if is_stock:
                results.append({"symbol": cols[0], "name": cols[1], "price": price, "change": change, "percent_change": percent})
            else:
                results.append({"name": cols[1], "price": price, "change": change, "percent_change": percent})
        return results
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return []

def fetch_reddit_category(subreddits):
    trends = []
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    for sub in subreddits:
        url = f"https://www.reddit.com/r/{sub}/hot.json?limit=6"
        try:
            response = httpx.get(url, headers=headers, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                for post in data['data']['children']:
                    pdata = post['data']
                    if not pdata.get('stickied'):
                        trends.append({
                            "subreddit": sub,
                            "title": pdata['title'],
                            "score": pdata['score'],
                            "num_comments": pdata['num_comments'],
                            "url": f"https://www.reddit.com{pdata['permalink']}"
                        })
        except Exception as e:
            logger.error(f"Error fetching r/{sub}: {e}")
    return sorted(trends, key=lambda x: x['score'], reverse=True)[:5]

def main():
    reddit_map = {
        "stocks": ["stocks", "pennystocks"],
        "market": ["investing", "wallstreetbets"],
        "tech": ["technology", "nvidia", "artificial"],
        "economy": ["economy", "economics"],
        "crypto": ["CryptoCurrency", "Bitcoin", "Ethereum"],
        "ai": ["Singularity", "OpenAI", "ChatGPT"],
        "finance": ["personalfinance", "FIRE", "financialindependence"],
        "dividends": ["dividends", "yieldmax"],
        "options": ["options", "Daytrading", "thetagang"]
    }

    data = {
        "timestamp": datetime.now().isoformat(),
        "indices": fetch_market_data("https://finance.yahoo.com/markets/world-indices/"),
        "trending_stocks": fetch_market_data("https://finance.yahoo.com/markets/stocks/most-active/", is_stock=True),
        "commodities": fetch_market_data("https://finance.yahoo.com/markets/commodities/"),
        "cryptos": fetch_market_data("https://finance.yahoo.com/markets/crypto/all/", is_stock=True),
        "reddit_categorized": {cat: fetch_reddit_category(subs) for cat, subs in reddit_map.items()}
    }
    
    output_path = "us-market-trends/data/market_data.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    logger.info(f"Market data saved to {output_path}")

if __name__ == "__main__":
    main()
