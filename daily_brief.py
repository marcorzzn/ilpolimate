import os
import json
import datetime
import time
import pytz
from dotenv import load_dotenv

# Load Env
load_dotenv()

# Imports from src
from src.fetcher import FeedFetcher
from src.analyzer import ContentAnalyzer
from src.generator import ReportGenerator

def main():
    print(">>> IL POLIMATE: System Start")
    
    # 1. Setup
    config_path = os.path.join("config", "clusters.json")
    with open(config_path, "r", encoding="utf-8") as f:
        clusters_config = json.load(f)
    
    fetcher = FeedFetcher()
    analyzer = ContentAnalyzer()
    generator = ReportGenerator()
    
    all_raw_items = []
    
    
    # 2. Gathering Phase (Tier -1 Sources)
    print(">>> Phase 1: Gathering Intelligence...")
    cluster_results = {}
    
    for key, info in clusters_config.items():
        print(f"   [{key}] Fetching {len(info['urls'])} sources...")
        items = fetcher.get_cluster_data(info['urls'])
        all_raw_items.extend(items)
        
        # Analyze Cluster immediately
        print(f"   [{key}] Analyzing {len(items)} items...")
        italian_title = info['name']
        analysis = analyzer.analyze_cluster_groq(italian_title, items)
        cluster_results[italian_title] = analysis
        time.sleep(2) # Politeness
        
    # 3. Holistic Phase (Meccanismi & Map)
    print(">>> Phase 2: Holistic Analysis (x.ai Grok)...")
    
    # Context aggregation (Title + Summary mainly to save tokens if massive)
    # Grok has 128k context, so we can pass A LOT.
    # We'll pass the string representation of all items.
    full_context_str = json.dumps(all_raw_items, default=str)[:3000000] # Hard cap just in case
    
    # A. Meccanismi
    print("   > Generating 'Meccanismi' Editorial...")
    mechanism_text = analyzer.analyze_mechanism_daily(full_context_str)
    
    # 5. Publishing Prep
    rome_tz = pytz.timezone('Europe/Rome')
    now = datetime.datetime.now(rome_tz)

    # B. Tensions Map
    print("   > Generating 'Mappa delle Tensioni' Data...")
    map_data = analyzer.analyze_tensions_map(full_context_str)
    generator.save_tensions_map(map_data, now)
    
    # 4. Fast Phase (Ticker Finanziario)
    print(">>> Phase 3: Market Data Generation (yfinance)...")
    ticker_data = analyzer.generate_ticker_headlines([]) # Pass empty list, it fetches independently
    generator.save_ticker_data(ticker_data)
    
    # 5. Publishing
    print(">>> Phase 4: Finalizing Report...")
    output_file = generator.save_daily_brief(now, cluster_results, mechanism_text)
    
    print(f"SUCCESS. Report saved to: {output_file}")

if __name__ == "__main__":
    main()
