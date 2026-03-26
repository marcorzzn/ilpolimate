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
    
    # Look back only 2 hours for the hourly update to catch anything recent but avoid overload
    fetcher = FeedFetcher(lookback_hours=2)
    analyzer = ContentAnalyzer()
    generator = ReportGenerator()
    
    # 1. Tier-1 News Agencies Source List
    # As requested: ANSA, AGI Italia, Adn Kronos, LaPresse, Associated Press, Reuters, AFP Presse.
    wire_agencies_urls = [
        # ANSA
        "https://www.ansa.it/sito/notizie/topnews/topnews_rss.xml",
        "https://www.ansa.it/sito/notizie/mondo/mondo_rss.xml",
        # AGI Italia
        "https://www.agi.it/estero/rss",
        "https://www.agi.it/politica/rss",
        "https://www.agi.it/cronaca/rss",
        # Adn Kronos
        "https://www.adnkronos.com/Rss/Esteri.xml",
        "https://www.adnkronos.com/Rss/Cronaca.xml",
        # LaPresse
        "https://news.google.com/rss/search?q=site:lapresse.it+when:1d&hl=it&gl=IT&ceid=IT:it",
        # Associated Press
        "https://news.google.com/rss/search?q=site:apnews.com+when:1d&hl=en-US&gl=US&ceid=US:en",
        # Reuters
        "https://news.google.com/rss/search?q=site:reuters.com+when:1d&hl=en-US&gl=US&ceid=US:en",
        # AFP
        "https://news.google.com/rss/search?q=site:afp.com+when:1d&hl=en-US&gl=US&ceid=US:en"
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
    
    
    import re
    # Strictly filter sources for Ultima Ora to exactly the requested 7 agencies.
    allowed_sources = ["ansa", "agi", "adn kronos", "adnkronos", "lapresse", "associated press", "ap", "reuters", "afp", "google news"]
    allowed_pattern = re.compile('|'.join(re.escape(a) for a in allowed_sources), re.IGNORECASE)
    filtered_items = []

    # Pre-translate Google News RSS sources back to their real names for clarity
    for item in all_raw_items:
        link = item.get('link', '').lower()

        real_source = item['source']
        if "lapresse.it" in link: real_source = "LaPresse"
        elif "apnews.com" in link: real_source = "Associated Press"
        elif "reuters.com" in link: real_source = "Reuters"
        elif "afp.com" in link: real_source = "AFP Presse"
        elif "adnkronos.com" in link: real_source = "Adn Kronos"

        item['source'] = real_source

        # Ensure it belongs to one of the agencies using pre-compiled regex
        if allowed_pattern.search(real_source):
            filtered_items.append(item)
            
    # Deduplicate items in "Ultima Ora"
    # Basic deduplication using difflib to remove very similar titles
    import difflib
    deduped_items = []
    for item in filtered_items:
        is_duplicate = False
        for d_item in deduped_items:
            # Check for identical links
            if item['link'] == d_item['link']:
                is_duplicate = True
                break
            # Check for very similar titles
            similarity = difflib.SequenceMatcher(None, item['title'].lower(), d_item['title'].lower()).ratio()
            if similarity > 0.8:
                is_duplicate = True
                break
        if not is_duplicate:
            deduped_items.append(item)

    filtered_items = deduped_items

    # Sort items purely by timestamp descending (newest first)
    # The `published` field is a datetime.datetime object
    filtered_items.sort(key=lambda x: x['published'], reverse=True)

    # Translate Ultima Ora titles AND contents
    print(f">>> Translating {len(filtered_items)} Ultima Ora items to Italian...")
    filtered_items = analyzer.translate_ultima_ora(filtered_items)
    
    # Append to existing latest_news.json to keep a longer history of the day
    # since we only fetch the last 2 hours. We want to keep up to 50 items.
    ultima_ora_path = os.path.join(generator.site_data_dir, "latest_news.json")
    existing_items = []
    if os.path.exists(ultima_ora_path):
        try:
            with open(ultima_ora_path, "r", encoding="utf-8") as f:
                existing_items = json.load(f)

            # Convert existing string dates back to datetime for sorting/dedup
            from dateutil import parser as date_parser
            for item in existing_items:
                if isinstance(item.get('published'), str):
                    try:
                        item['published'] = date_parser.parse(item['published'])
                    except:
                        item['published'] = datetime.datetime.now(datetime.timezone.utc)
        except Exception:
            pass

    # Combine and deduplicate across existing and new
    all_combined_items = filtered_items + existing_items
    final_deduped_items = []
    for item in all_combined_items:
        is_duplicate = False
        for d_item in final_deduped_items:
            if item['link'] == d_item['link']:
                is_duplicate = True
                break
            similarity = difflib.SequenceMatcher(None, item['title'].lower(), d_item['title'].lower()).ratio()
            if similarity > 0.8:
                is_duplicate = True
                break
        if not is_duplicate:
            final_deduped_items.append(item)

    # Sort again and keep the latest 50
    final_deduped_items.sort(key=lambda x: x['published'], reverse=True)
    final_deduped_items = final_deduped_items[:50]

    with open(ultima_ora_path, "w", encoding="utf-8") as f:
        json.dump(final_deduped_items, f, ensure_ascii=False, default=str)
    
    # Force Citation Check on Features
    if "features" in map_data:
        for f in map_data["features"]:
            if "properties" in f and "description" in f["properties"]:
                desc = f["properties"]["description"]
                desc_upper = desc.upper()
                if "FONTE:" not in desc_upper and "AGENCY:" not in desc_upper:
                    # Fallback append if model missed the explicit instruction
                    f["properties"]["description"] += " (Fonte: Agenzie Stampa Internazionali)"

    # Read existing map data for today to append new features
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    tensions_path = os.path.join(generator.site_data_dir, "tensions.json")

    if os.path.exists(tensions_path):
        try:
            with open(tensions_path, "r", encoding="utf-8") as f:
                history = json.load(f)
                if date_str in history and "features" in history[date_str]:
                    existing_features = history[date_str]["features"]
                    # Simple dedup by location and category
                    for new_f in map_data.get("features", []):
                        is_dup = False
                        new_props = new_f.get("properties", {})
                        for ex_f in existing_features:
                            ex_props = ex_f.get("properties", {})
                            if new_props.get("location_name") == ex_props.get("location_name") and new_props.get("category") == ex_props.get("category"):
                                is_dup = True
                                break
                        if not is_dup:
                            existing_features.append(new_f)

                    map_data["features"] = existing_features
        except Exception as e:
            print(f"Error reading existing map data: {e}")

    generator.save_tensions_map(map_data, now)
    
    print(f">>> SUCCESS. Map Update complete for {now.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
