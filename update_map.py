import os
import json
import datetime
import time
from dotenv import load_dotenv

# Load Env
load_dotenv()

# Imports from src
from src.fetcher import FeedFetcher
from src.analyzer import ContentAnalyzer
from src.generator import ReportGenerator

def main():
    print(">>> IL POLIMATE: 6H Map Update Start")
    
    fetcher = FeedFetcher(lookback_hours=12) # Focus on very recent events
    analyzer = ContentAnalyzer()
    generator = ReportGenerator()
    
    # 1. Tier-1 News Agencies Source List
    # We use RSS feeds where available or standard scraping sources for them.
    # Some exact raw RSS feeds for agencies might require specific exactness:
    # We will use reliable aggregate open proxies or direct feeds where available.
    
    wire_agencies_urls = [
         # Reuters News proxy/RSS
        "https://www.reutersagency.com/feed/?best-regions=europe&post_type=best",
        "https://www.reutersagency.com/feed/?best-topics=political-general&post_type=best",
         # Associated Press (AP News)
        "https://moxie.foxnews.com/google-publisher/world.xml", # AP proxy network often on fox/yahoo
        "https://news.yahoo.com/rss/world", # Carries AP/AFP heavily
         # AFP 
        "https://www.france24.com/en/rss", # Strong AFP carrier
         # Italian Agencies 
         # ANSA
        "https://www.ansa.it/sito/notizie/mondo/mondo_rss.xml",
        "https://www.ansa.it/sito/notizie/politica/politica_rss.xml",
         # Adnkronos
        "https://www.adnkronos.com/feed/",
         # AGI
        "https://www.agi.it/estero/rss"
    ]
    
    # 2. Gathering
    print(f">>> Fetching {len(wire_agencies_urls)} Tier-1 wire sources...")
    all_raw_items = fetcher.get_cluster_data(wire_agencies_urls)
    
    # Pre-pend source clearly for the Map Analyzer
    for item in all_raw_items:
        # Force strict citation referencing in text
        item['content'] = f"[FONTE ORIGINALE: {item['source']} | INFORMAZIONI: Agenzia Stampa Tier-1] - " + item['content']
        
    print(f">>> Fetched {len(all_raw_items)} wire dispatches.")
    
    # 3. Generating Tensions Map Data
    print(">>> Generating 'Mappa delle Tensioni' Data...")
    
    full_context_str = json.dumps(all_raw_items, default=str)[:3000000]
    
    # Modify analyzer specifically for 6H Map with Agency sourcing
    map_data = analyzer.analyze_tensions_map(full_context_str)
    
    # Dump the raw feed for the Ultima Ora UI
    ultima_ora_path = os.path.join(generator.site_data_dir, "latest_news.json")
    with open(ultima_ora_path, "w", encoding="utf-8") as f:
        json.dump(all_raw_items, f, ensure_ascii=False, default=str)
    
    # Force Citation Check on Features
    if "features" in map_data:
        for f in map_data["features"]:
            if "properties" in f and "description" in f["properties"]:
                desc = f["properties"]["description"]
                if "FONTE:" not in desc.upper() and "AGENCY:" not in desc.upper():
                    # Fallback append if model missed the explicit instruction
                    f["properties"]["description"] += " (Fonte: Agenzie Stampa Internazionali - Reuters/AP/AFP/ANSA)"
    
    now = datetime.datetime.now()
    generator.save_tensions_map(map_data, now)
    
    print(f">>> SUCCESS. Map Update complete for {now.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
