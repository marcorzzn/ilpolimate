import os
import datetime
import time
import feedparser
import concurrent.futures
from groq import Groq

# --- CONFIGURAZIONE ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MAX_WORKERS = 30           # Parallelismo aggressivo
MAX_CONTEXT_CHARS = 120000 # Massimizziamo la finestra di contesto di Llama 3.3
LOOKBACK_HOURS = 26        # Finestra temporale (24h + 2h di margine)

if not GROQ_API_KEY:
    print("ERRORE: Manca la GROQ_API_KEY.")
    exit(1)

# --- 1. IL "MEGABLASTER" DATASET (Tutte le Fonti High-Fidelity) ---
feeds = [
    # ==========================================
    # DOMINIO 1: FRONTIERA SCIENTIFICA (CODE & BIO)
    # ==========================================
    # --- CS & AI Theory ---
    "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=15",
    "http://export.arxiv.org/api/query?search_query=cat:cs.LG&sortBy=submittedDate&sortOrder=descending&max_results=10", # Machine Learning
    "http://export.arxiv.org/api/query?search_query=cat:cs.CR&sortBy=submittedDate&sortOrder=descending&max_results=10", # Crypto & Security
    # --- Quantum Physics & Computing ---
    "http://export.arxiv.org/api/query?search_query=cat:quant-ph&sortBy=submittedDate&sortOrder=descending&max_results=10",
    "https://www.nature.com/nphys.rss", # Nature Physics
    "https://phys.org/rss-feed/physics-news/quantum-physics/",
    # --- Deep Cryptography (The Math) ---
    "https://eprint.iacr.org/rss/rss.xml", # IACR (International Association for Cryptologic Research)
    # --- Synthetic Biology & Genomics ---
    "https://connect.biorxiv.org/biorxiv_xml.php?subject=synthetic_biology",
    "https://connect.biorxiv.org/biorxiv_xml.php?subject=genomics",
    "https://connect.biorxiv.org/biorxiv_xml.php?subject=bioengineering",
    # --- Offensive Cyber-Security (Exploit 0-day) ---
    "https://www.usenix.org/rss/conference/all-proceedings", # USENIX Security Symposium
    "https://googleprojectzero.blogspot.com/feeds/posts/default", # Project Zero (Google Elite Hunter)
    "https://threatpost.com/feed/",
    "https://krebsonsecurity.com/feed/",
    "https://www.schneier.com/feed/atom/", 
    
    # ==========================================
    # DOMINIO 2: HARDWARE, MATERIALI & SUPPLY CHAIN
    # ==========================================
    # --- Semiconductor Industry (Lithography & Fab) ---
    "https://semiengineering.com/feed/", # La Bibbia del silicio
    "https://spectrum.ieee.org/feeds/topic/semiconductors/rss",
    "https://www.semiconductors.org/feed/", # SIA Industry Data
    "https://www.imec-int.com/en/rss", # IMEC (Belgio - Centro R&D n.1 al mondo)
    "https://www.tsmc.com/rss/english/newsReleases",
    # --- Advanced Materials & Chemistry ---
    "https://chemrxiv.org/engage/chemrxiv/rss", # Pre-print chimica materiali
    "https://www.nature.com/nmat.rss", # Nature Materials
    # --- National Labs & Standards ---
    "https://www.anl.gov/rss/research-news/feed", # Argonne National Lab (Batterie)
    "https://www.nist.gov/news-events/news/rss.xml", # NIST (Standard PQC & AI)
    "https://www.ornl.gov/feeds/news-releases.xml", # Oak Ridge Lab (Supercomputing)
    
    # ==========================================
    # DOMINIO 3: GEOPOLITICA, INTELLIGENCE & DIFESA
    # ==========================================
    # --- Global Intelligence & Doctrine ---
    "https://rusi.org/rss.xml", # RUSI (UK - Top Tier Military Intel)
    "https://www.csis.org/rss/analysis", # CSIS (USA Defense)
    "https://www.rand.org/content/rand/pubs.xml", # RAND Corp (Strategy)
    "https://carnegieendowment.org/rss/solr/get/all-content", # Nuclear Policy
    "https://www.atlanticcouncil.org/feed/",
    "https://www.chathamhouse.org/rss/research",
    # --- Area Specific (Eurasia/China/Pacific) ---
    "https://jamestown.org/feed/", # Eurasia Monitor (Russia/Cina Expert Level)
    "https://www.aspistrategist.org.au/feed/", # ASPI (Australia/Pacific/Submarine Cables)
    "https://thediplomat.com/feed/", # Asia-Pacific Current Affairs
    "https://warontherocks.com/feed/", # Military Operators & Vets
    # --- Defense Industry & Logistics ---
    "https://www.defensenews.com/arc/outboundfeeds/rss/",
    "https://www.sipri.org/rss.xml", # Arms Trade Data
    "https://news.usni.org/feed", # US Naval Institute (Maritime Security)
    
    # ==========================================
    # DOMINIO 4: MACROECONOMIA & STRUTTURA FINANZIARIA
    # ==========================================
    # --- Central Banks Research (The Source Code of Money) ---
    "https://www.bis.org/doclist/research.rss", # Bank for International Settlements
    "https://www.federalreserve.gov/feeds/feds_rss.xml", # FED Board Papers
    "https://libertystreeteconomics.newyorkfed.org/feed/", # NY Fed (Repo Markets)
    "https://www.ecb.europa.eu/rss/wppub.xml", # BCE Working Papers
    # --- Global Institutions ---
    "https://www.imf.org/en/Publications/RSS?language=eng&series=IMF%20Working%20Papers",
    "https://www.nber.org/rss/new.xml", # NBER (Recession Dating)
    "https://www.bruegel.org/feed", # EU Economic Policy
    "https://cepr.org/voxeu/rss.xml",
    # --- Energy & Commodities (The Physical Economy) ---
    "https://oilprice.com/rss/main",
    "https://www.oxfordenergy.org/feed/", # Oxford Institute (Technical Energy Analysis)
    "https://www.iea.org/rss/news"
]

# --- 2. HYDRA ENGINE (Multi-Threaded Fetcher) ---
def fetch_and_filter(url):
    """Scarica, parsa e filtra per data (ultime 24h)"""
    try:
        # User agent personalizzato per evitare blocchi 403
        d = feedparser.parse(url, agent="Mozilla/5.0 (compatible; PolymathBot/1.0)")
        
        valid_items = []
        now = datetime.datetime.now(datetime.timezone.utc)
        cutoff = now - datetime.timedelta(hours=LOOKBACK_HOURS)
        
        for entry in d.entries:
            # Rilevamento data (formati multipli)
            pub_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                pub_date = datetime.datetime(*entry.updated_parsed[:6], tzinfo=datetime.timezone.utc)
            
            # Se la data manca, scartiamo per sicurezza (vogliamo solo news certe di oggi)
            # Se la data c'è, controlliamo se è > cutoff
            if pub_date and pub_date > cutoff:
                # Estrazione Contenuto
                content = "No content"
                if hasattr(entry, 'summary'): content = entry.summary
                elif hasattr(entry, 'description'): content = entry.description
                elif hasattr(entry, 'content'): content = entry.content[0].value
                
                # Pulizia HTML brutale
                content = content.replace("<p>", "").replace("</p>", "").replace("<div>", "")[:700]
                
                valid_items.append(f"SOURCE: {d.feed.get('title', 'Unknown')}\nTITLE: {entry.title}\nABSTRACT: {content}\nLINK: {entry.link}\n")
                
        return valid_items
    except Exception:
        return []

print(f"Avvio HYDRA su {len(feeds)} fonti Tier-0...")
start = time.time()
full_context = []

with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    results = executor.map(fetch_and_filter, feeds)
    for res in results:
        full_context.extend(res)

print(f"Scaricamento completato in {time.time() - start:.2f}s. Segnali trovati: {len(full_context)}")

if not full_context:
    print("NESSUN SEGNALE RECENTE. Generazione report vuoto.")
    full_context = ["NESSUN DATO RILEVATO NELLE ULTIME 24 ORE."]

# Preparazione Payload (Taglio per Context Window)
payload_text = "\n---\n".join(full_context)
if len(payload_text) > MAX_CONTEXT_CHARS:
    print(f"Payload troppo grande ({len(payload_text)} chars). Taglio ai primi {MAX_CONTEXT_CHARS}.")
    payload_text = payload_text[:MAX_CONTEXT_CHARS] + "\n[...DATA TRUNCATED...]"

# --- 3. ANALISI STRATEGICA (LLAMA 3.3) ---
today = datetime.datetime.now().strftime("%Y-%m-%d")

system_prompt = """
SEI: "The Polymath", Intelligenza Strategica.
RUOLO: Filtrare il rumore globale per un decisore di vertice.
DATA: {date}

INPUT: Rassegna stampa massiva da fonti primarie (arXiv, Intelligence, Banche Centrali).

COMPITO:
Identifica i 4 "Segnali Deboli" più critici che indicano un cambiamento strutturale imminente.
Non fare un riassunto delle notizie. Cerca anomalie, breakthrough e rischi sistemici.

REGOLE DI SCRITTURA:
- Tono: Accademico/Militare, asettico, denso.
- Seleziona SOLO notizie vere delle ultime 24h.
- Se una sezione è vuota di segnali rilevanti, scrivi "NESSUNA ANOMALIA STRUTTURALE".

FORMATO OUTPUT (Markdown):

## 1. FRONTIERA SCIENTIFICA (CODE & BIO)
**Il Segnale:** [Titolo Tecnico]
* **Evidence:** [Sintesi rigorosa dei dati]
* **Meccanismo:** [Perché cambia il paradigma tecnologico?]
* **Fonte:** [Link diretto]

## 2. HARDWARE & SUPPLY CHAIN (ATOMS)
**Il Segnale:** [Titolo Tecnico]
* **Evidence:** [Sintesi rigorosa dei dati]
* **Meccanismo:** [Impatto su produzione industriale o logistica]
* **Fonte:** [Link diretto]

## 3. GEOPOLITICA & DOTTRINA (POWER)
**Il Segnale:** [Titolo Strategico]
* **Evidence:** [Sintesi rigorosa dei dati]
* **Meccanismo:** [Impatto sugli equilibri di potere/deterrenza]
* **Fonte:** [Link diretto]

## 4. MACROECONOMIA & RISCHIO (MONEY)
**Il Segnale:** [Titolo Finanziario]
* **Evidence:** [Sintesi rigorosa dei dati]
* **Meccanismo:** [Impatto su liquidità o rischio sistemico]
* **Fonte:** [Link diretto]
"""

try:
    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt.format(date=today)},
            {"role": "user", "content": f"INTELLIGENCE DUMP:\n{payload_text}"}
        ],
        temperature=0.1,
        max_tokens=3000
    )
    report_content = completion.choices[0].message.content
except Exception as e:
    report_content = f"ERRORE ANALISI AI: {str(e)}"

# --- 4. PUBBLICAZIONE ---
markdown_file = f"""---
title: "Polymath Brief: {today}"
date: {today}
layout: post
---

{report_content}
"""

if not os.path.exists("_posts"):
    os.makedirs("_posts")

filename = f"_posts/{today}-brief.md"
with open(filename, "w", encoding='utf-8') as f:
    f.write(markdown_file)

print("Brief Tier-0 completato.")
