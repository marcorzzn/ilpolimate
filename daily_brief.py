import os
import datetime
import time
import feedparser
import concurrent.futures
from groq import Groq

# --- CONFIGURAZIONE ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MAX_WORKERS = 50            # Alta parallelizzazione per 160 fonti
LOOKBACK_HOURS = 48         # Aumentato a 48h per garantire pienezza di notizie
MAX_SECTION_CONTEXT = 45000 # Contesto massiccio per leggere tutto

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

# --- 1. I 13 CLUSTER STRATEGICI (ARSENALE TITAN: 160+ FONTI) ---
CLUSTERS = {
    "01_AI_RESEARCH": {
        "name": "MENTE SINTETICA & LABORATORI AI",
        "desc": "MIT CSAIL, Stanford HAI, DeepMind, ArXiv, Meta AI.",
        "urls": [
            "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=20",
            "http://export.arxiv.org/api/query?search_query=cat:cs.LG&sortBy=submittedDate&sortOrder=descending&max_results=20",
            "http://export.arxiv.org/api/query?search_query=cat:cs.CL&sortBy=submittedDate&sortOrder=descending&max_results=10",
            "https://www.csail.mit.edu/news/feed", 
            "https://hai.stanford.edu/news/feed", 
            "https://bair.berkeley.edu/blog/feed.xml", 
            "https://www.cs.cmu.edu/news/feed", 
            "https://news.mit.edu/rss/topic/artificial-intelligence2", 
            "https://deepmind.google/blog/rss.xml",
            "https://openai.com/blog/rss.xml",
            "https://research.google/blog/rss",
            "https://ai.meta.com/blog/rss.xml",
            "https://www.microsoft.com/en-us/research/feed/",
            "https://www.amazon.science/index.rss",
            "https://huggingface.co/blog/feed.xml"
        ]
    },
    "02_QUANTUM": {
        "name": "FISICA DI FRONTIERA & QUANTUM COMPUTING",
        "desc": "Caltech, ETH Zurich, Quanta Mag, Nature Physics.",
        "urls": [
            "http://export.arxiv.org/api/query?search_query=cat:quant-ph&sortBy=submittedDate&sortOrder=descending&max_results=15",
            "https://www.nature.com/nphys.rss",
            "https://phys.org/rss-feed/physics-news/quantum-physics/",
            "https://www.caltech.edu/c/news/rss", 
            "https://ethz.ch/en/news-and-events/eth-news/news.rss", 
            "https://qt.eu/feed/", 
            "https://quantumcomputingreport.com/feed/",
            "https://scitechdaily.com/tag/quantum-physics/feed/",
            "https://www.quantamagazine.org/feed/" 
        ]
    },
    "03_CRYPTO_MATH": {
        "name": "CRITTOGRAFIA & MATEMATICA APPLICATA",
        "desc": "IACR, Ethereum Research, Matematica Pura.",
        "urls": [
            "https://eprint.iacr.org/rss/rss.xml", 
            "https://blog.cryptographyengineering.com/feed/",
            "https://schneier.com/blog/atom.xml",
            "https://ellipticnews.wordpress.com/feed/",
            "https://blog.ethereum.org/feed.xml", 
            "https://research.chain.link/feed.xml",
            "https://news.mit.edu/rss/topic/mathematics" 
        ]
    },
    "04_BIO_SYNTHETIC": {
        "name": "BIOLOGIA SINTETICA & MED-TECH",
        "desc": "Harvard Medicine, The Lancet, CRISPR, BioRxiv.",
        "urls": [
            "https://connect.biorxiv.org/biorxiv_xml.php?subject=synthetic_biology",
            "https://connect.biorxiv.org/biorxiv_xml.php?subject=genomics",
            "https://www.nature.com/nbt.rss", 
            "https://www.thelancet.com/rssfeed/lancet_current.xml", 
            "https://www.cell.com/cell/current.rss", 
            "https://hms.harvard.edu/news/rss", 
            "https://www.genengnews.com/feed/", 
            "https://synbiobeta.com/feed/",
            "https://www.fiercebiotech.com/rss/xml",
            "https://news.mit.edu/rss/topic/biology"
        ]
    },
    "05_CYBER_WARFARE": {
        "name": "CYBER-WARFARE & INTELLIGENCE",
        "desc": "NSA/CISA Alerts, Unit 42, Mandiant, Zero-Day.",
        "urls": [
            "https://googleprojectzero.blogspot.com/feeds/posts/default",
            "https://www.usenix.org/rss/conference/all-proceedings",
            "https://threatpost.com/feed/",
            "https://krebsonsecurity.com/feed/",
            "https://www.mandiant.com/resources/blog/rss.xml",
            "https://unit42.paloaltonetworks.com/feed/",
            "https://www.cisa.gov/uscert/ncas/alerts.xml", 
            "https://www.crowdstrike.com/blog/feed/",
            "https://www.sentinelone.com/blog/feed/",
            "https://www.darkreading.com/rss.xml"
        ]
    },
    "06_CHIP_FAB": {
        "name": "SILICIO & FONDERIE (MANUFACTURING)",
        "desc": "TSMC, ASML, MIT Engineering, Supply Chain Asiatica.",
        "urls": [
            "https://semiengineering.com/feed/",
            "https://www.imec-int.com/en/rss",
            "https://www.semiconductors.org/feed/",
            "https://www.digitimes.com/rss/daily.xml", 
            "https://semianalysis.com/feed/",
            "https://news.mit.edu/rss/topic/engineering", 
            "https://semiwiki.com/feed/"
        ]
    },
    "07_CHIP_DESIGN": {
        "name": "ARCHITETTURE HARDWARE & COMPUTING",
        "desc": "IEEE, GPU Design, Supercomputing.",
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
        "name": "SCIENZA DEI MATERIALI & CHIMICA",
        "desc": "Batterie, Argonne Lab, Advanced Materials.",
        "urls": [
            "https://chemrxiv.org/engage/chemrxiv/rss",
            "https://www.anl.gov/rss/research-news/feed", 
            "https://www.nature.com/nmat.rss",
            "https://onlinelibrary.wiley.com/feed/15214095/most-recent", 
            "https://cen.acs.org/rss/materials.xml", 
            "https://battery-news.com/feed/",
            "https://news.mit.edu/rss/topic/materials"
        ]
    },
    "09_SPACE_FRONTIER": {
        "name": "SPACE ECONOMY & ORBITAL WARFARE",
        "desc": "SpaceNews, ESA, NASA JPL, Harvard-Smithsonian.",
        "urls": [
            "https://spacenews.com/feed/",
            "https://www.esa.int/rssfeed/Our_Activities/Operations",
            "https://www.jpl.nasa.gov/feeds/news/", 
            "https://blogs.nasa.gov/station/feed/",
            "https://spaceflightnow.com/feed/",
            "https://www.cfa.harvard.edu/news/rss.xml", 
            "https://gsp.esa.int/documents/10180/0/rss"
        ]
    },
    "10_GEO_DEFENSE": {
        "name": "IL GRANDE GIOCO (DIFESA & MILITARY)",
        "desc": "RAND Corp, West Point, RUSI, Janes.",
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
        "desc": "Foreign Affairs, CSIS, Chatham House, Limes.",
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
        "name": "STRUTTURE DI CAPITALE & ECONOMIA",
        "desc": "NBER, BIS, FED, Harvard Business School, World Bank.",
        "urls": [
            "https://www.bis.org/doclist/research.rss",
            "https://www.nber.org/rss/new.xml", 
            "https://www.federalreserve.gov/feeds/feds_rss.xml",
            "https://libertystreeteconomics.newyorkfed.org/feed/",
            "https://www.ecb.europa.eu/rss/wppub.xml",
            "https://www.imf.org/en/Publications/RSS?language=eng&series=IMF%20Working%20Papers",
            "https://www.worldbank.org/en/rss/research",
            "https://hbswk.hbs.edu/rss/item/all.xml", 
            "https://www.project-syndicate.org/rss", 
            "https://www.bruegel.org/rss" 
        ]
    },
    "13_GLOBAL_ENERGY": {
        "name": "ENERGIA & RISORSE",
        "desc": "IEA, Oxford Energy, NREL, OilPrice.",
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

# --- 2. ENGINE DI RACCOLTA (HYDRA) ---
def fetch_feed(url):
    try:
        # User Agent simulato
        d = feedparser.parse(url, agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) PolymathBot/3.0")
        items = []
        now = datetime.datetime.now(datetime.timezone.utc)
        cutoff = now - datetime.timedelta(hours=LOOKBACK_HOURS)
        
        for entry in d.entries:
            # Gestione date robusta
            pub_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                pub_date = datetime.datetime(*entry.updated_parsed[:6], tzinfo=datetime.timezone.utc)
            
            # Se la data manca, accettiamo il contenuto
            if not pub_date or pub_date > cutoff:
                content = "No content"
                if hasattr(entry, 'summary'): content = entry.summary
                elif hasattr(entry, 'content'): content = entry.content[0].value
                elif hasattr(entry, 'description'): content = entry.description
                
                # Pulizia HTML base
                content = content.replace("<p>", "").replace("</p>", "").replace("<div>", "").strip()[:2000]
                
                source = d.feed.get('title', 'Fonte Sconosciuta')
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

# --- 3. ANALISTA AI (PROMPT CORRETTO PER LINK CLICCABILI) ---
def analyze_cluster(cluster_key, info, raw_text):
    if not raw_text: return ""
    
    print(f"  > Analisi {cluster_key} ({len(raw_text)} chars)...")
    
    system_prompt = f"""
    SEI: "Il Polimate", analista strategico senior.
    SETTORE: {info['name']}
    
    OBIETTIVO: Analisi MASSIVA di tutte le notizie. 
    NON FERMARTI ALLA PRIMA NOTIZIA. ELENCA TUTTO QUELLO CHE TROVI DI RILEVANTE.
    Se ci sono 10 notizie, scrivine 10. Se ce ne sono 5, scrivine 5.
    
    REGOLE DI FORMATTAZIONE (RISPETTA RIGOROSAMENTE):
    1. TITOLI: Usa lo stile italiano ("Sentence case").
       - Esempio: "La nuova strategia nucleare della Cina"
    
    2. FONTI CLICCABILI (IMPORTANTE):
       - Alla fine di ogni notizia, devi inserire il link in formato MARKDOWN CLICCABILE.
       - SCRIVI ESATTAMENTE COSÌ: **Fonte:** [Vedi Fonte](LINK_DELLA_NOTIZIA)
       - Il link tra parentesi tonde DEVE essere l'URL originale fornito.
    
    3. PULIZIA:
       - NESSUN tag <hr>.
       - NESSUNA introduzione o conclusione.
       - Testo allineato a sinistra (non giustificato).
    
    FORMATO DI OUTPUT PER OGNI NOTIZIA:
    ### [Titolo in italiano corretto]
    [Analisi tecnica dettagliata di 5-10 righe. Spiega il meccanismo e l'impatto.]
    
    **Fonte:** [Vedi Fonte](LINK_ORIGINALE)
    
    (Lascia una riga vuota tra una notizia e l'altra)
    """
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"INPUT DATI DA ANALIZZARE:\n{raw_text[:MAX_SECTION_CONTEXT]}"}
            ],
            temperature=0.2, 
            max_tokens=7000 # Aumentato per permettere output molto lunghi
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error {cluster_key}: {e}")
        return ""

# --- 4. SEQUENCER PRINCIPALE ---
print("Avvio IL POLIMATE TITAN ENGINE...")
start_time = time.time()

# Generazione Data Italiana
italian_date = get_italian_date()
today_iso = datetime.datetime.now().strftime("%Y-%m-%d")

full_report = "" 

for key, info in CLUSTERS.items():
    print(f"\n--- Elaborazione Cluster: {info['name']} ---")
    
    # 1. Scarica
    raw_data = get_cluster_data(info['urls'])
    
    if raw_data:
        raw_text = "\n---\n".join(raw_data)
        # 2. Analizza
        analysis = analyze_cluster(key, info, raw_text)
        
        # 3. Aggiungi al report
        if analysis and len(analysis) > 50:
            full_report += f"\n\n## {info['name']}\n\n{analysis}\n"
        else:
            print("  > Nessun output rilevante dall'AI.")
    else:
        print("  > Nessun dato grezzo trovato per questo settore.")
    
    time.sleep(15)

# --- 5. SALVATAGGIO ---
if not os.path.exists("_posts"):
    os.makedirs("_posts")

filename = f"_posts/{today_iso}-brief.md"

# Markdown con Titolo Italiano Corretto
markdown_file = f"""---
title: "La Rassegna del {italian_date}"
date: {today_iso}
layout: post
excerpt: "Edizione Titan. Analisi strategica su 160+ fonti d'élite: MIT, DARPA, Banche Centrali e Laboratori Globali."
---

{full_report}
"""

with open(filename, "w", encoding='utf-8') as f:
    f.write(markdown_file)

duration = (time.time() - start_time) / 60
print(f"\nDossier Titan completato in {duration:.1f} minuti. Salvato in: {filename}")
