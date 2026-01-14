import os
import datetime
import time
import feedparser
import concurrent.futures
from groq import Groq

# --- CONFIGURAZIONE ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MAX_WORKERS = 5
LOOKBACK_HOURS = 28  # Finestra richiesta dall'utente
MAX_SECTION_CONTEXT = 15000 

if not GROQ_API_KEY:
    print("ERRORE CRITICO: Manca GROQ_API_KEY. Impostala come variabile d'ambiente.")
    exit(1)

# ================= FONTI (CLUSTERS) =================
CLUSTERS = {
    "01_AI_RESEARCH": {
        "name": "INTELLIGENZA ARTIFICIALE",
        "urls": [
            "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=50",
            "http://export.arxiv.org/api/query?search_query=cat:cs.LG&sortBy=submittedDate&sortOrder=descending&max_results=50",
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
        "urls": [
            "http://export.arxiv.org/api/query?search_query=cat:quant-ph&sortBy=submittedDate&sortOrder=descending&max_results=40",
            "https://www.nature.com/nphys.rss",
            "https://phys.org/rss-feed/physics-news/quantum-physics/",
            "https://qt.eu/feed/", 
            "https://scitechdaily.com/tag/quantum-physics/feed/",
            "https://www.quantamagazine.org/feed/"
        ]
    },
    "03_MATH_FRONTIER": {
        "name": "MATEMATICA",
        "urls": [
            "https://news.mit.edu/rss/topic/mathematics",
            "https://rss.ams.org/math-in-the-media.xml",
            "http://export.arxiv.org/api/query?search_query=cat:math.NA&sortBy=submittedDate&sortOrder=descending&max_results=20",
            "http://export.arxiv.org/api/query?search_query=cat:math.OC&sortBy=submittedDate&sortOrder=descending&max_results=20",
            "https://www.quantamagazine.org/feed/"
        ]
    },
    "04_BIO_SYNTHETIC": {
        "name": "BIOLOGIA & BIOTECNOLOGIE",
        "urls": [
            "https://connect.biorxiv.org/biorxiv_xml.php?subject=synthetic_biology",
            "https://www.nature.com/nbt.rss", 
            "https://www.genengnews.com/feed/",
            "https://www.fiercebiotech.com/rss/xml"
        ]
    },
    "05_CYBER_WARFARE": {
        "name": "CYBER-WARFARE & INTELLIGENCE",
        "urls": [
            "https://krebsonsecurity.com/feed/",
            "https://unit42.paloaltonetworks.com/feed/",
            "https://www.cisa.gov/uscert/ncas/alerts.xml", 
            "https://www.crowdstrike.com/blog/feed/",
            "https://www.darkreading.com/rss.xml"
        ]
    },
    "06_CHIP_FAB": {
        "name": "SILICIO & FONDERIE",
        "urls": [
            "https://semiengineering.com/feed/",
            "https://www.semiconductors.org/feed/",
            "https://www.digitimes.com/rss/daily.xml", 
            "https://semiwiki.com/feed/"
        ]
    },
    "07_CHIP_DESIGN": {
        "name": "HARDWARE",
        "urls": [
            "https://www.anandtech.com/rss/",
            "https://www.tomshardware.com/feeds/all",
            "https://www.servethehome.com/feed/", 
            "https://www.nextplatform.com/feed/"
        ]
    },
    "08_MATERIALS": {
        "name": "MATERIALI",
        "urls": [
            "https://www.anl.gov/rss/research-news/feed", 
            "https://www.nature.com/nmat.rss",
            "https://battery-news.com/feed/"
        ]
    },
    "09_SPACE_FRONTIER": {
        "name": "SPACE ECONOMY",
        "urls": [
            "https://spacenews.com/feed/",
            "https://www.esa.int/rssfeed/Our_Activities/Operations",
            "https://www.jpl.nasa.gov/feeds/news/",
            "https://spaceflightnow.com/feed/"
        ]
    },
    "10_GEO_DEFENSE": {
        "name": "DIFESA",
        "urls": [
            "https://warontherocks.com/feed/",
            "https://www.defensenews.com/arc/outboundfeeds/rss/",
            "https://news.usni.org/feed",
            "https://www.janes.com/feeds/news"
        ]
    },
    "11_GEO_STRATEGY": {
        "name": "GEOPOLITICA & DIPLOMAZIA",
        "urls": [
            "https://www.foreignaffairs.com/rss.xml", 
            "https://www.csis.org/rss/analysis",
            "https://thediplomat.com/feed/",
            "https://merics.org/en/rss.xml"
        ]
    },
    "12_CENTRAL_BANKS": {
        "name": "MACROECONOMIA & CAPITALE",
        "urls": [
            "https://www.federalreserve.gov/feeds/feds_rss.xml",
            "https://www.ecb.europa.eu/rss/wppub.xml",
            "https://www.imf.org/en/Publications/RSS?language=eng&series=IMF%20Working%20Papers",
            "https://www.project-syndicate.org/rss"
        ]
    },
    "13_GLOBAL_ENERGY": {
        "name": "ENERGIA & RISORSE",
        "urls": [
            "https://oilprice.com/rss/main",
            "https://iea.org/rss/news",
            "https://www.world-nuclear-news.org/RSS/WNN-News.xml",
            "https://gcaptain.com/feed/"
        ]
    }
}

# --- 2. ENGINE DI RACCOLTA ---
def fetch_feed(url):
    try:
        d = feedparser.parse(url, agent="Mozilla/5.0 (PolymathBot/3.0)")
        items = []
        now = datetime.datetime.now(datetime.timezone.utc)
        cutoff = now - datetime.timedelta(hours=LOOKBACK_HOURS)
        
        for entry in d.entries:
            pub_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                pub_date = datetime.datetime(*entry.updated_parsed[:6], tzinfo=datetime.timezone.utc)
            
            # Se non c'è data, assumiamo sia recente per sicurezza
            if not pub_date or pub_date > cutoff:
                content = "No content"
                if hasattr(entry, 'summary'): content = entry.summary
                elif hasattr(entry, 'content'): content = entry.content[0].value
                elif hasattr(entry, 'description'): content = entry.description
                
                # Pulizia base HTML
                content = content.replace("<p>", "").replace("</p>", "").replace("<div>", "").strip()[:2000]
                source = d.feed.get('title', 'Unknown Source')
                link = entry.link
                items.append(f"SRC: {source}\nLINK: {link}\nTITLE: {entry.title}\nTXT: {content}\n")
        return items
    except Exception as e:
        # Silenzioso su errore feed singolo, per non bloccare tutto
        return []

def get_cluster_data(urls):
    data = []
    # Ridotto i workers per stabilità
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = executor.map(fetch_feed, urls)
        for res in results:
            data.extend(res)
    return data

# --- 3. AGENTE ANALISTA (PROMPT RIGIDO V4) ---
def analyze_cluster(cluster_key, info, raw_text):
    if not raw_text: 
        return "Nessuna notizia rilevante trovata nelle ultime 28 ore."
    
    print(f"  > Analisi {cluster_key} ({len(raw_text)} chars)...")
    
    system_prompt = f"""
SEI: Un analista senior di intelligence tecnologica.
SETTORE: {info['name']}

OBIETTIVO: Selezionare le 4 notizie più rilevanti e riassumerle.

REGOLE DI FORMATO TASSATIVE (Il mancato rispetto comporta il fallimento):

1. **TITOLO:** Traducilo in Italiano. Deve essere in grassetto tra doppi asterischi (**Titolo**).
2. **A CAPO:** Vai a capo subito dopo il titolo.
3. **TESTO:** Scrivi 3-4 righe dense in italiano.
4. **A CAPO:** Vai a capo subito dopo il testo.
5. **FONTE (CRITICO):** Devi usare il formato Markdown per i link cliccabili. 
   Scrivi ESATTAMENTE: Fonte: [Link originale](URL_ORIGINALE)
6. **SEPARATORE:** Lascia una riga vuota tra una notizia e l'altra.

ESEMPIO PERFETTO DI OUTPUT:

**Nuova architettura per le GPU Blackwell**
Nvidia ha presentato i dettagli tecnici della nuova architettura che riduce i consumi del 30% aumentando il throughput per i calcoli in virgola mobile FP8.
Fonte: [https://nvidianews.com](https://nvidianews.com)

(riga vuota)

**Scoperta vulnerabilità critica in SSH**
È stata identificata una falla nel protocollo di handshake che permette attacchi Man-in-the-Middle su connessioni non patchate.
Fonte: [https://cve.mitre.org](https://cve.mitre.org)
"""
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"DATI INPUT:\n{raw_text[:MAX_SECTION_CONTEXT]}"}
            ],
            temperature=0.1, # Minima creatività per rispettare il formato
            max_tokens=2500
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error AI {cluster_key}: {e}")
        return "Errore nell'analisi AI per questo settore."

# --- 4. SEQUENCER ---
print("Avvio MOTORE EPOCHALE...")
today = datetime.datetime.now().strftime("%Y-%m-%d")

today_date = datetime.datetime.now()
month_name = today_date.strftime("%B")
month_italian = {
    "January": "gennaio", "February": "febbraio", "March": "marzo",
    "April": "aprile", "May": "maggio", "June": "giugno",
    "July": "luglio", "August": "agosto", "September": "settembre",
    "October": "ottobre", "November": "novembre", "December": "dicembre"
}.get(month_name, month_name)
display_date = f"{today_date.day} {month_italian} {today_date.year}"

full_report = f"""---
title: "La rassegna del {display_date}"
date: {today}
layout: post
---

> Report di intelligence sui segnali rilevanti delle ultime 28 ore.

---
"""

for key, info in CLUSTERS.items():
    print(f"\n--- Processando Cluster: {info['name']} ---")
    
    clean_urls = [url.strip() for url in info['urls']]
    raw_data = get_cluster_data(clean_urls)
    
    analysis = ""
    
    # Logica modificata: Processa sempre, se vuoto mette il testo di fallback
    if raw_data:
        print(f"  > Trovati {len(raw_data)} articoli raw.")
        # Limitiamo a 40 articoli per non confondere l'AI e non sforare i token
        limited_raw_data = raw_data[:40]
        raw_text = "\n---\n".join(limited_raw_data)
        analysis = analyze_cluster(key, info, raw_text)
    else:
        print("  > 0 articoli trovati (Feed vuoti o vecchi).")
        analysis = "Nessuna notizia rilevante trovata nelle ultime 28 ore in questo settore."

    # Se l'AI ha fallito o ritornato stringa vuota, metti fallback
    if not analysis:
        analysis = "Nessuna notizia rilevante trovata nelle ultime 28 ore in questo settore."

    # Scrittura nel report: Il titolo del settore c'è SEMPRE
    full_report += f"\n\n## {info['name']}\n\n{analysis}\n\n"
    
    # Pausa per evitare rate limit di Groq (fondamentale)
    print("  > Cooling down (10s)...")
    time.sleep(10)

# --- 5. SALVATAGGIO ---
if not os.path.exists("_posts"): os.makedirs("_posts")
filename = f"_posts/{today}-brief.md"

with open(filename, "w", encoding='utf-8') as f:
    f.write(full_report)

print(f"Dossier salvato in: {filename}")
