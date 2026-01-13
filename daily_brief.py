import os
import datetime
import time
import feedparser
import concurrent.futures
from groq import Groq
from bs4 import BeautifulSoup
import pytz

# --- CONFIGURAZIONE ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MAX_WORKERS = 10
LOOKBACK_HOURS = 28
MAX_SECTION_CONTEXT = 30000

if not GROQ_API_KEY:
    print("ERRORE: Manca GROQ_API_KEY.")
    exit(1)

# --- DATA ITALIANA ---
def get_italian_date():
    mesi = {
        1: "gennaio", 2: "febbraio", 3: "marzo", 4: "aprile",
        5: "maggio", 6: "giugno", 7: "luglio", 8: "agosto",
        9: "settembre", 10: "ottobre", 11: "novembre", 12: "dicembre"
    }
    try:
        now = datetime.datetime.now(pytz.timezone("Europe/Rome"))
    except:
        now = datetime.datetime.now()
    return f"{now.day} {mesi[now.month]} {now.year}"

# --- DEFINIZIONE DEI CLUSTER (dalla versione di oggi) ---
CLUSTERS = {
    "01_AI_RESEARCH": {
        "name": "INTELLIGENZA ARTIFICIALE",
        "desc": "Breakthroughs tecnici.",
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
        "desc": "Calcolo quantistico e fisica.",
        "urls": [
            "http://export.arxiv.org/api/query?search_query=cat:quant-ph&sortBy=submittedDate&sortOrder=descending&max_results=40",
            "https://www.nature.com/nphys.rss",
            "https://phys.org/rss-feed/physics-news/quantum-physics/",
            "https://scitechdaily.com/tag/quantum-physics/feed/",
            "https://www.quantamagazine.org/feed/"
        ]
    },
    "03_MATH_FRONTIER": {
        "name": "MATEMATICA",
        "desc": "Lista Custom Utente.",
        "urls": [
            "https://eprint.iacr.org/rss/rss.xml",
            "https://blog.cryptographyengineering.com/feed/",
            "https://news.mit.edu/rss/topic/mathematics",
            "https://sinews.siam.org/rss/sn_rss.aspx",
            "http://export.arxiv.org/api/query?search_query=cat:math.OC&sortBy=submittedDate&sortOrder=descending&max_results=20",
            "https://www.santafe.edu/news/rss"
        ]
    },
    "04_BIO_SYNTHETIC": {
        "name": "BIOLOGIA E BIOTECNOLOGIE",
        "desc": "Genomica, CRISPR.",
        "urls": [
            "https://connect.biorxiv.org/biorxiv_xml.php?subject=synthetic_biology",
            "https://www.nature.com/nbt.rss",
            "https://www.genengnews.com/feed/",
            "https://www.fiercebiotech.com/rss/xml"
        ]
    },
    "05_CYBER_WARFARE": {
        "name": "CYBER-WARFARE E INTELLIGENCE",
        "desc": "InfoSec, Zero-Day.",
        "urls": [
            "https://googleprojectzero.blogspot.com/feeds/posts/default",
            "https://krebsonsecurity.com/feed/",
            "https://unit42.paloaltonetworks.com/feed/",
            "https://www.cisa.gov/uscert/ncas/alerts.xml",
            "https://www.darkreading.com/rss.xml"
        ]
    },
    "06_CHIP_FAB": {
        "name": "SILICIO E FONDERIE",
        "desc": "TSMC, ASML.",
        "urls": [
            "https://semiengineering.com/feed/",
            "https://www.semiconductors.org/feed/",
            "https://www.digitimes.com/rss/daily.xml",
            "https://semianalysis.com/feed/"
        ]
    },
    "07_CHIP_DESIGN": {
        "name": "HARDWARE",
        "desc": "GPU Design, HPC.",
        "urls": [
            "https://www.anandtech.com/rss/",
            "https://www.tomshardware.com/feeds/all",
            "https://www.servethehome.com/feed/",
            "https://www.nextplatform.com/feed/"
        ]
    },
    "08_MATERIALS": {
        "name": "MATERIALI",
        "desc": "Batterie, Chimica.",
        "urls": [
            "https://www.nature.com/nmat.rss",
            "https://cen.acs.org/rss/materials.xml",
            "https://battery-news.com/feed/"
        ]
    },
    "09_SPACE_FRONTIER": {
        "name": "SPACE ECONOMY",
        "desc": "ESA, NASA.",
        "urls": [
            "https://spacenews.com/feed/",
            "https://spaceflightnow.com/feed/",
            "https://gsp.esa.int/documents/10180/0/rss"
        ]
    },
    "10_GEO_DEFENSE": {
        "name": "DIFESA",
        "desc": "Strategie militari.",
        "urls": [
            "https://rusi.org/rss.xml",
            "https://warontherocks.com/feed/",
            "https://www.defensenews.com/arc/outboundfeeds/rss/",
            "https://www.janes.com/feeds/news"
        ]
    },
    "11_GEO_STRATEGY": {
        "name": "GEOPOLITICA E DIPLOMAZIA",
        "desc": "Analisi globale.",
        "urls": [
            "https://www.foreignaffairs.com/rss.xml",
            "https://www.csis.org/rss/analysis",
            "https://thediplomat.com/feed/",
            "https://merics.org/en/rss.xml"
        ]
    },
    "12_CENTRAL_BANKS": {
        "name": "MACROECONOMIA",
        "desc": "Banche Centrali.",
        "urls": [
            "https://www.bis.org/doclist/research.rss",
            "https://www.nber.org/rss/new.xml",
            "https://www.imf.org/en/Publications/RSS?language=eng&series=IMF%20Working%20Papers",
            "https://www.project-syndicate.org/rss"
        ]
    },
    "13_GLOBAL_ENERGY": {
        "name": "ENERGIA E RISORSE",
        "desc": "Mercati energetici.",
        "urls": [
            "https://oilprice.com/rss/main",
            "https://iea.org/rss/news",
            "https://gcaptain.com/feed/"
        ]
    }
}

# --- ENGINE DI RACCOLTA (dalla versione di oggi con miglioramenti) ---
def fetch_feed(url):
    try:
        d = feedparser.parse(url, agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        items = []
        now = datetime.datetime.now(datetime.timezone.utc)
        cutoff = now - datetime.timedelta(hours=LOOKBACK_HOURS)
        
        for entry in d.entries:
            pub_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                pub_date = datetime.datetime(*entry.updated_parsed[:6], tzinfo=datetime.timezone.utc)
            
            if not pub_date or pub_date > cutoff:
                content = "No content"
                if hasattr(entry, 'summary'): content = entry.summary
                elif hasattr(entry, 'content'): content = entry.content[0].value
                elif hasattr(entry, 'description'): content = entry.description
                
                # Clean HTML
                try:
                    soup = BeautifulSoup(content, "html.parser")
                    content = soup.get_text(separator=" ", strip=True)[:1500]
                except Exception:
                    content = str(content).replace("<p>", "").replace("</p>", "").strip()[:1500]

                source = d.feed.get('title', 'Fonte')
                link = entry.link
                items.append(f"SRC: {source}\nLINK: {link}\nTITLE: {entry.title}\nTXT: {content}\n")
        return items
    except Exception as e:
        print(f"   ❌ ERRORE su {url}: {e}")
        return []

def get_cluster_data(urls):
    data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = executor.map(fetch_feed, urls)
        for res in results:
            data.extend(res)
    return data

# --- AGENTE ANALISTA (dal primo codice con prompt modificato) ---
def analyze_cluster(cluster_key, info, raw_text):
    if not raw_text: return ""
    
    print(f"  > Analisi {cluster_key} ({len(raw_text)} chars)...")
    
    system_prompt = f"""
    SEI: "Il Polimate", analista di intelligence.
    SETTORE: {info['name']}
    
    OBIETTIVO: Creare un report dettagliatissimo ed esteso.
    NON DEVI RIASSUMERE TUTTO IN UN PARAGRAFO.
    DEVI ANALIZZARE OGNI SINGOLA NOTIZIA RILEVANTE SEPARATAMENTE.
    
    INPUT: Lista di news/paper.
    
    OUTPUT RICHIESTO:
    - Scorri tutte le notizie fornite.
    - Se una notizia è tecnicamente rilevante, scrivi un paragrafo dedicato.
    - Se ci sono 10 notizie valide, voglio 10 paragrafi.
    - Se ci sono 20 notizie valide, voglio 20 paragrafi.
    
    FORMATO PER OGNI NOTIZIA (Usa Markdown):
    ### [Titolo in Italiano della notizia (sentence case)]
    [Analisi tecnica dettagliata di 2-3 righe. Spiega il 'cosa', il 'come' e il 'perché'. Usa termini tecnici.]
    
    Fonte: [LINK originale fornito] (DEVE ESSERE CLICCABILE, quindi usa il formato markdown [Testo](URL))
    
    STILE:
    - Densità informativa massima.
    - Italiano professionale (capitalizzazione italiana).
    - NESSUNA INTRODUZIONE, NESSUNA CONCLUSIONE. Solo la lista delle analisi.
    - Ogni notizia deve essere separata da una riga vuota.
    """
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"INPUT DATI:\n{raw_text[:MAX_SECTION_CONTEXT]}"}
            ],
            temperature=0.2,
            max_tokens=6000
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error {cluster_key}: {e}")
        return ""

# --- MAIN SEQUENCER ---
print("🚀 AVVIO POLIMATE (Versione Combinata)...")
start_time = time.time()
italian_date = get_italian_date()

# Timezone per nome file
try:
    tz = pytz.timezone("Europe/Rome")
    today_iso = datetime.datetime.now(tz).strftime("%Y-%m-%d")
except:
    today_iso = datetime.datetime.now().strftime("%Y-%m-%d")

# Costruzione del report
full_report = f"""# IL POLIMATE: Rassegna del {italian_date}
**Livello:** Deep Strategic Intelligence  
**Fonti:** 80+ Fonti Primarie

> Analisi granulare dei segnali rilevanti intercettati nelle ultime 24 ore.  
> Ogni sezione approfondisce multiple fonti con focus tecnico-operativo.

---

"""

total_news = 0

for key, info in CLUSTERS.items():
    print(f"\n--- Processando Cluster: {info['name']} ---")
    
    raw_data = get_cluster_data(info['urls'])
    
    if raw_data:
        raw_text = "\n---\n".join(raw_data)
        analysis = analyze_cluster(key, info, raw_text)
        
        if analysis and len(analysis) > 50:
            # Conta le notizie
            news_count = analysis.count("###")
            total_news += news_count
            
            # Aggiungi al report (senza hr finale)
            full_report += f"\n\n## {info['name']}\n\n{analysis}\n\n"
        else:
            print("  > Nessun output rilevante dall'AI.")
    else:
        print("  > Nessun dato grezzo trovato.")
    
    # Pausa per Rate Limit
    time.sleep(10)

# --- SALVATAGGIO ---
if not os.path.exists("_posts"):
    os.makedirs("_posts")

filename = f"_posts/{today_iso}-brief.md"

markdown_file = f"""---
title: "La rassegna del {italian_date}"
date: {today_iso}
layout: post
excerpt: "Intelligence strategica su {total_news} aggiornamenti globali."
---

{full_report}
"""

with open(filename, "w", encoding='utf-8') as f:
    f.write(markdown_file)

print(f"\n✅ SALVATO: {filename}")
print(f"📊 Totale notizie analizzate: {total_news}")
print(f"⏱️ Tempo totale: {time.time() - start_time:.1f} secondi")
