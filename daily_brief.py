import os
import datetime
import time
import feedparser
import concurrent.futures
from groq import Groq

# --- CONFIGURAZIONE STRATEGICA ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MAX_WORKERS = 20            
LOOKBACK_HOURS = 40         # Copertura globale garantita
MAX_SECTION_CONTEXT = 55000 

if not GROQ_API_KEY:
    print("ERRORE CRITICO: Manca la GROQ_API_KEY.")
    exit(1)

# --- FUNZIONE DATA ITALIANA ---
def get_italian_date():
    months = {
        1: "gennaio", 2: "febbraio", 3: "marzo", 4: "aprile", 5: "maggio", 6: "giugno",
        7: "luglio", 8: "agosto", 9: "settembre", 10: "ottobre", 11: "novembre", 12: "dicembre"
    }
    now = datetime.datetime.now()
    return f"{now.day} {months[now.month]} {now.year}"

# --- 1. FONTI D'ELITE (ARSENALE COMPLETO) ---
CLUSTERS = {
    "01_AI_RESEARCH": {
        "name": "INTELLIGENZA ARTIFICIALE",
        "desc": "Breakthroughs tecnici e nuovi paradigmi.",
        "urls": [
            "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=50",
            "http://export.arxiv.org/api/query?search_query=cat:cs.LG&sortBy=submittedDate&sortOrder=descending&max_results=50",
            "https://www.csail.mit.edu/news/feed", 
            "https://hai.stanford.edu/news/feed", 
            "https://bair.berkeley.edu/blog/feed.xml", 
            "https://deepmind.google/blog/rss.xml",
            "https://openai.com/blog/rss.xml",
            "https://research.google/blog/rss",
            "https://ai.meta.com/blog/rss.xml",
            "https://huggingface.co/blog/feed.xml",
            "https://www.microsoft.com/en-us/research/feed/"
        ]
    },
    "02_QUANTUM": {
        "name": "FISICA DI FRONTIERA",
        "desc": "Calcolo quantistico e fisica dei materiali.",
        "urls": [
            "http://export.arxiv.org/api/query?search_query=cat:quant-ph&sortBy=submittedDate&sortOrder=descending&max_results=40",
            "https://www.nature.com/nphys.rss",
            "https://phys.org/rss-feed/physics-news/quantum-physics/",
            "https://www.caltech.edu/c/news/rss", 
            "https://ethz.ch/en/news-and-events/eth-news/news.rss", 
            "https://qt.eu/feed/", 
            "https://scitechdaily.com/tag/quantum-physics/feed/",
            "https://www.quantamagazine.org/feed/"
        ]
    },
    "03_MATH_FRONTIER": {
        "name": "MATEMATICA",
        "desc": "Ottimizzazione, Analisi Numerica, Complessità, Crypto.",
        "urls": [
            "https://eprint.iacr.org/rss/rss.xml",
            "https://blog.cryptographyengineering.com/feed/",
            "https://research.chain.link/feed.xml",
            "https://news.mit.edu/rss/topic/mathematics",
            "https://sinews.siam.org/rss/sn_rss.aspx",
            "https://rss.ams.org/math-in-the-media.xml",
            "http://export.arxiv.org/api/query?search_query=cat:math.NA&sortBy=submittedDate&sortOrder=descending&max_results=20", # Numerical Analysis
            "http://export.arxiv.org/api/query?search_query=cat:math.OC&sortBy=submittedDate&sortOrder=descending&max_results=20", # Optimization & Control
            "http://export.arxiv.org/api/query?search_query=cat:math.DS&sortBy=submittedDate&sortOrder=descending&max_results=15", # Dynamical Systems
            "http://export.arxiv.org/api/query?search_query=cat:math.ST&sortBy=submittedDate&sortOrder=descending&max_results=15", # Statistics Theory
            "https://www.quantamagazine.org/feed/",
            "https://www.santafe.edu/news/rss",
            "http://export.arxiv.org/api/query?search_query=cat:cs.GT&sortBy=submittedDate&sortOrder=descending&max_results=15" # Game Theory
        ]
    },
    "04_BIO_SYNTHETIC": {
        "name": "BIOLOGIA E BIOTECNOLOGIE",
        "desc": "Genomica, CRISPR, Biotech.",
        "urls": [
            "https://connect.biorxiv.org/biorxiv_xml.php?subject=synthetic_biology",
            "https://connect.biorxiv.org/biorxiv_xml.php?subject=genomics",
            "https://www.nature.com/nbt.rss", 
            "https://www.thelancet.com/rssfeed/lancet_current.xml", 
            "https://www.cell.com/cell/current.rss", 
            "https://hms.harvard.edu/news/rss", 
            "https://www.genengnews.com/feed/",
            "https://www.fiercebiotech.com/rss/xml"
        ]
    },
    "05_CYBER_WARFARE": {
        "name": "CYBER-WARFARE & INTELLIGENCE",
        "desc": "Minacce APT, Zero-Day, InfoSec.",
        "urls": [
            "https://googleprojectzero.blogspot.com/feeds/posts/default",
            "https://threatpost.com/feed/",
            "https://krebsonsecurity.com/feed/",
            "https://www.mandiant.com/resources/blog/rss.xml",
            "https://unit42.paloaltonetworks.com/feed/",
            "https://www.cisa.gov/uscert/ncas/alerts.xml", 
            "https://www.crowdstrike.com/blog/feed/",
            "https://www.darkreading.com/rss.xml",
            "https://www.sentinelone.com/blog/feed/"
        ]
    },
    "06_CHIP_FAB": {
        "name": "SILICIO & FONDERIE",
        "desc": "TSMC, ASML, Supply Chain.",
        "urls": [
            "https://semiengineering.com/feed/",
            "https://www.imec-int.com/en/rss",
            "https://www.semiconductors.org/feed/",
            "https://www.digitimes.com/rss/daily.xml", 
            "https://semianalysis.com/feed/",
            "https://semiwiki.com/feed/",
            "https://news.mit.edu/rss/topic/engineering"
        ]
    },
    "07_CHIP_DESIGN": {
        "name": "HARDWARE",
        "desc": "GPU Design, HPC, Neuromorphic.",
        "urls": [
            "https://spectrum.ieee.org/feeds/topic/semiconductors/rss",
            "https://www.anandtech.com/rss/",
            "https://www.tomshardware.com/feeds/all",
            "https://www.servethehome.com/feed/", 
            "https://chipsandcheese.com/feed/", 
            "https://www.nextplatform.com/feed/" 
        ]
    },
    "08_MATERIALS": {
        "name": "MATERIALI",
        "desc": "Batterie, Superconduttori, Chimica.",
        "urls": [
            "https://chemrxiv.org/engage/chemrxiv/rss",
            "https://www.anl.gov/rss/research-news/feed", 
            "https://www.nature.com/nmat.rss",
            "https://cen.acs.org/rss/materials.xml", 
            "https://battery-news.com/feed/",
            "https://onlinelibrary.wiley.com/feed/15214095/most-recent"
        ]
    },
    "09_SPACE_FRONTIER": {
        "name": "SPACE ECONOMY",
        "desc": "Infrastruttura orbitale, ESA, NASA.",
        "urls": [
            "https://spacenews.com/feed/",
            "https://www.esa.int/rssfeed/Our_Activities/Operations",
            "https://www.jpl.nasa.gov/feeds/news/", 
            "https://blogs.nasa.gov/station/feed/",
            "https://spaceflightnow.com/feed/",
            "https://gsp.esa.int/documents/10180/0/rss",
            "https://www.cfa.harvard.edu/news/rss.xml"
        ]
    },
    "10_GEO_DEFENSE": {
        "name": "IL GRANDE GIOCO (DIFESA)",
        "desc": "Strategie militari, DARPA, RAND.",
        "urls": [
            "https://rusi.org/rss.xml",
            "https://warontherocks.com/feed/",
            "https://www.rand.org/news/politics-and-government.xml", 
            "https://mwi.westpoint.edu/feed/", 
            "https://www.defensenews.com/arc/outboundfeeds/rss/",
            "https://news.usni.org/feed",
            "https://www.understandingwar.org/feeds.xml", 
            "https://www.janes.com/feeds/news",
            "https://www.darpa.mil/rss/news" 
        ]
    },
    "11_GEO_STRATEGY": {
        "name": "GEOPOLITICA & DIPLOMAZIA",
        "desc": "Analisi globale, Think Tanks.",
        "urls": [
            "https://www.foreignaffairs.com/rss.xml", 
            "https://www.chathamhouse.org/rss/research/all", 
            "https://www.cfr.org/feed/all", 
            "https://www.aspistrategist.org.au/feed/",
            "https://jamestown.org/feed/",
            "https://www.csis.org/rss/analysis",
            "https://thediplomat.com/feed/",
            "https://merics.org/en/rss.xml",
            "https://legrandcontinent.eu/fr/feed/"
        ]
    },
    "12_CENTRAL_BANKS": {
        "name": "MACROECONOMIA & CAPITALE",
        "desc": "Banche Centrali, NBER, FMI.",
        "urls": [
            "https://www.bis.org/doclist/research.rss",
            "https://www.nber.org/rss/new.xml", 
            "https://www.federalreserve.gov/feeds/feds_rss.xml",
            "https://libertystreeteconomics.newyorkfed.org/feed/",
            "https://www.ecb.europa.eu/rss/wppub.xml",
            "https://www.imf.org/en/Publications/RSS?language=eng&series=IMF%20Working%20Papers",
            "https://www.worldbank.org/en/rss/research",
            "https://www.project-syndicate.org/rss",
            "https://www.bruegel.org/rss"
        ]
    },
    "13_GLOBAL_ENERGY": {
        "name": "ENERGIA & RISORSE",
        "desc": "Mercati energetici, Nucleare, Rinnovabili.",
        "urls": [
            "https://oilprice.com/rss/main",
            "https://www.oxfordenergy.org/feed/",
            "https://iea.org/rss/news",
            "https://www.nrel.gov/news/rss.xml", 
            "https://www.world-nuclear-news.org/RSS/WNN-News.xml",
            "https://gcaptain.com/feed/",
            "https://news.mit.edu/rss/topic/energy"
        ]
    }
}

# --- 2. ENGINE DI RACCOLTA (STEALTH MODE) ---
def fetch_feed(url):
    try:
        # User Agent simulato come Browser Reale per evitare blocchi IP
        d = feedparser.parse(url, agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        items = []
        now = datetime.datetime.now(datetime.timezone.utc)
        cutoff = now - datetime.timedelta(hours=LOOKBACK_HOURS)
        
        for entry in d.entries:
            pub_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                pub_date = datetime.datetime(*entry.updated_parsed[:6], tzinfo=datetime.timezone.utc)
            
            # FILTRO PERMISSIVO: Se la data manca, includiamo (meglio un falso positivo che un buco)
            if not pub_date or pub_date > cutoff:
                content = "No content"
                if hasattr(entry, 'summary'): content = entry.summary
                elif hasattr(entry, 'content'): content = entry.content[0].value
                elif hasattr(entry, 'description'): content = entry.description
                
                content = content.replace("<p>", "").replace("</p>", "").replace("<div>", "").strip()[:3000]
                source = d.feed.get('title', 'Fonte')
                link = entry.link
                items.append(f"SRC: {source}\nLINK: {link}\nTITLE: {entry.title}\nTXT: {content}\n")
        return items
    except:
        return []

def get_cluster_data(urls):
    data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = executor.map(fetch_feed, urls)
        for res in results:
            data.extend(res)
    return data

# --- 3. IL CERVELLO VISIONARIO (IBRIDO) ---
def analyze_cluster(cluster_key, info, raw_text):
    if not raw_text: return ""
    
    print(f"  > Analisi {cluster_key} ({len(raw_text)} chars)...")
    
    # PROMPT IBRIDO: "Cerca il Miracolo, ma accetta il Progresso"
    system_prompt = f"""
    SEI: "Il Polimate". SETTORE: {info['name']}
    
    OBIETTIVO: Selezionare notizie di ALTO VALORE STRATEGICO o TECNICO.
    
    PRIORITÀ DI SELEZIONE:
    1. LIVELLO ORACOLO: Notizie che cambiano il paradigma (Visionarie).
    2. LIVELLO TECNICO: Progressi solidi, nuovi paper, aggiornamenti importanti.
    
    IMPORTANTE: 
    - NON restituire vuoto se ci sono notizie tecniche valide. 
    - Il lettore vuole sapere cosa succede, anche se oggi non è stato inventato il teletrasporto.
    - Seleziona ALMENO 2-3 notizie se presenti nel testo.
    
    STILE:
    - Titoli: Italiano, Sentence case (Eleganti).
    - Analisi: Spiega l'impatto. "Questo permette di...", "Cruciale perché...".
    
    FORMATO:
    ### [Titolo Elegante]
    [Analisi densa.]
    
    **Fonte:** [Link](URL)
    
    (Riga vuota)
    """
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"DATI DISPONIBILI:\n{raw_text[:MAX_SECTION_CONTEXT]}"}
            ],
            temperature=0.3, 
            max_tokens=7000 
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error {cluster_key}: {e}")
        return ""

# --- 4. MAIN SEQUENCER ---
print("Avvio IL POLIMATE (Protocollo Visionary Hybrid)...")
start_time = time.time()
italian_date = get_italian_date()
today_iso = datetime.datetime.now().strftime("%Y-%m-%d")

full_report = "" 

for key, info in CLUSTERS.items():
    print(f"\n--- Scansione: {info['name']} ---")
    raw_data = get_cluster_data(info['urls'])
    
    if raw_data:
        raw_text = "\n---\n".join(raw_data)
        analysis = analyze_cluster(key, info, raw_text)
        
        if analysis and len(analysis) > 30:
            full_report += f"\n\n## {info['name']}\n\n{analysis}\n"
        else:
            print("  > Contenuto insufficiente o filtrato.")
    else:
        print("  > Nessun dato grezzo rilevato.")
    
    # Pausa di sicurezza
    time.sleep(25)

# SALVATAGGIO
if not os.path.exists("_posts"):
    os.makedirs("_posts")

filename = f"_posts/{today_iso}-brief.md"

markdown_file = f"""---
title: "La Rassegna del {italian_date}"
date: {today_iso}
layout: post
excerpt: "Analisi strategica per menti polimatiche."
---

{full_report}
"""

if len(full_report) > 100:
    with open(filename, "w", encoding='utf-8') as f:
        f.write(markdown_file)
    print(f"\nDossier salvato: {filename}")
else:
    print("\nATTENZIONE: Report vuoto.")

duration = (time.time() - start_time) / 60
print(f"Tempo totale: {duration:.1f} minuti.")
