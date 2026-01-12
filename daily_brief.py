import os
import datetime
import time
import feedparser
import concurrent.futures
from groq import Groq

# --- CONFIGURAZIONE ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MAX_WORKERS = 30           
MAX_CONTEXT_CHARS = 120000 
LOOKBACK_HOURS = 26        

if not GROQ_API_KEY:
    print("ERRORE: Manca la GROQ_API_KEY.")
    exit(1)

# --- 1. IL "MEGABLASTER" DATASET (Fonti Tier-0) ---
feeds = [
    # === FRONTIERA SCIENTIFICA (CODE & BIO) ===
    "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=15",
    "http://export.arxiv.org/api/query?search_query=cat:quant-ph&sortBy=submittedDate&sortOrder=descending&max_results=10",
    "https://eprint.iacr.org/rss/rss.xml", 
    "https://connect.biorxiv.org/biorxiv_xml.php?subject=synthetic_biology",
    "https://connect.biorxiv.org/biorxiv_xml.php?subject=genomics",
    "https://www.nature.com/nphys.rss", 
    "https://phys.org/rss-feed/physics-news/quantum-physics/",
    "https://www.usenix.org/rss/conference/all-proceedings", 
    "https://googleprojectzero.blogspot.com/feeds/posts/default",
    "https://threatpost.com/feed/",
    
    # === HARDWARE, MATERIALI & SUPPLY CHAIN ===
    "https://semiengineering.com/feed/", 
    "https://spectrum.ieee.org/feeds/topic/semiconductors/rss",
    "https://www.semiconductors.org/feed/",
    "https://www.imec-int.com/en/rss",
    "https://chemrxiv.org/engage/chemrxiv/rss", 
    "https://www.anl.gov/rss/research-news/feed", 
    "https://www.nist.gov/news-events/news/rss.xml", 
    
    # === GEOPOLITICA, INTELLIGENCE & DIFESA ===
    "https://rusi.org/rss.xml", 
    "https://www.csis.org/rss/analysis", 
    "https://jamestown.org/feed/", 
    "https://www.aspistrategist.org.au/feed/", 
    "https://thediplomat.com/feed/", 
    "https://warontherocks.com/feed/", 
    "https://www.defensenews.com/arc/outboundfeeds/rss/",
    "https://news.usni.org/feed", 
    
    # === MACROECONOMIA & STRUTTURA FINANZIARIA ===
    "https://www.bis.org/doclist/research.rss", 
    "https://www.federalreserve.gov/feeds/feds_rss.xml", 
    "https://libertystreeteconomics.newyorkfed.org/feed/", 
    "https://www.ecb.europa.eu/rss/wppub.xml", 
    "https://www.imf.org/en/Publications/RSS?language=eng&series=IMF%20Working%20Papers",
    "https://oilprice.com/rss/main",
    "https://www.oxfordenergy.org/feed/"
]

# --- 2. HYDRA ENGINE ---
def fetch_and_filter(url):
    try:
        d = feedparser.parse(url, agent="Mozilla/5.0 (compatible; PolymathBot/1.0)")
        valid_items = []
        now = datetime.datetime.now(datetime.timezone.utc)
        cutoff = now - datetime.timedelta(hours=LOOKBACK_HOURS)
        
        for entry in d.entries:
            pub_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                pub_date = datetime.datetime(*entry.updated_parsed[:6], tzinfo=datetime.timezone.utc)
            
            if pub_date and pub_date > cutoff:
                content = "No content"
                if hasattr(entry, 'summary'): content = entry.summary
                elif hasattr(entry, 'description'): content = entry.description
                elif hasattr(entry, 'content'): content = entry.content[0].value
                
                content = content.replace("<p>", "").replace("</p>", "").replace("<div>", "")[:800]
                valid_items.append(f"SOURCE: {d.feed.get('title', 'Unknown')}\nTITLE: {entry.title}\nABSTRACT: {content}\nLINK: {entry.link}\n")
                
        return valid_items
    except Exception:
        return []

print(f"Avvio HYDRA Extended su {len(feeds)} fonti...")
start = time.time()
full_context = []

with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    results = executor.map(fetch_and_filter, feeds)
    for res in results:
        full_context.extend(res)

print
