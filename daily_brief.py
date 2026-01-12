import os
import datetime
import time
import feedparser
import concurrent.futures
from groq import Groq

# --- CONFIGURAZIONE ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MAX_WORKERS = 30
LOOKBACK_HOURS = 28  # Finestra ampia per non perdere nulla
MAX_SECTION_CONTEXT = 30000 

if not GROQ_API_KEY:
    print("ERRORE: Manca GROQ_API_KEY.")
    exit(1)

# --- 1. DEFINIZIONE DEI CLUSTER (GRANULARITÀ MASSIMA) ---
# Dividiamo il mondo in 12 micro-settori per massimizzare la "Deep Intelligence"
CLUSTERS = {
    "01_AI_RESEARCH": {
        "name": "INTELLIGENZA ARTIFICIALE (RICERCA)",
        "desc": "Paper Arxiv, Nuove architetture, LLM Theory.",
        "urls": [
            "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=20",
            "http://export.arxiv.org/api/query?search_query=cat:cs.LG&sortBy=submittedDate&sortOrder=descending&max_results=20",
            "https://bair.berkeley.edu/blog/feed.xml"
        ]
    },
    "02_QUANTUM_PHYSICS": {
        "name": "FISICA QUANTISTICA & COMPUTING",
        "desc": "Qubits, Error Correction, Nuovi stati della materia.",
        "urls": [
            "http://export.arxiv.org/api/query?search_query=cat:quant-ph&sortBy=submittedDate&sortOrder=descending&max_results=15",
            "https://www.nature.com/nphys.rss",
            "https://phys.org/rss-feed/physics-news/quantum-physics/"
        ]
    },
    "03_CRYPTO_MATH": {
        "name": "CRITTOGRAFIA & MATEMATICA",
        "desc": "Post-Quantum Crypto, Zero-Knowledge Proofs, Sicurezza matematica.",
        "urls": [
            "https://eprint.iacr.org/rss/rss.xml",
            "https://blog.cryptographyengineering.com/feed/"
        ]
    },
    "04_BIO_SYNTHETIC": {
        "name": "BIOLOGIA SINTETICA & GENOMICA",
        "desc": "CRISPR, Gene Editing, Bio-Computing.",
        "urls": [
            "https://connect.biorxiv.org/biorxiv_xml.php?subject=synthetic_biology",
            "https://connect.biorxiv.org/biorxiv_xml.php?subject=genomics",
            "https://www.nature.com/nbt.rss"
        ]
    },
    "05_CYBER_OFFENSIVE": {
        "name": "CYBER-WARFARE & EXPLOIT",
        "desc": "0-days, APT Groups, Vulnerabilità critiche.",
        "urls": [
            "https://googleprojectzero.blogspot.com/feeds/posts/default",
            "https://www.usenix.org/rss/conference/all-proceedings",
            "https://threatpost.com/feed/",
            "https://krebsonsecurity.com/feed/"
        ]
    },
    "06_CHIP_MANUFACTURING": {
        "name": "HARDWARE: FABBRICAZIONE & LITOGRAFIA",
        "desc": "TSMC, ASML, High-NA EUV, Packaging avanzato.",
        "urls": [
            "https://semiengineering.com/feed/",
            "https://www.imec-int.com/en/rss",
            "https://www.semiconductors.org/feed/"
        ]
    },
    "07_CHIP_DESIGN": {
        "name": "HARDWARE: ARCHITETTURE & DISPOSITIVI",
        "desc": "GPU Design, Neuromorphic Chips, Photonics.",
        "urls": [
            "https://spectrum.ieee.org/feeds/topic/semiconductors/rss",
            "https://www.anandtech.com/rss/",
            "https://www.tomshardware.com/feeds/all"
        ]
    },
    "08_MATERIALS": {
        "name": "SCIENZA DEI MATERIALI & ENERGIA",
        "desc": "Batterie stato solido, Perovskite, Superconduttori.",
        "urls": [
            "https://chemrxiv.org/engage/chemrxiv/rss",
            "https://www.anl.gov/rss/research-news/feed",
            "https://www.nature.com/nmat.rss"
        ]
    },
    "09_GEO_DEFENSE": {
        "name": "GEOPOLITICA: DIFESA & CONFLITTI",
        "desc": "Movimenti truppe, Nuovi armamenti, Dottrina.",
        "urls": [
            "https://rusi.org/rss.xml",
            "https://warontherocks.com/feed/",
            "https://www.defensenews.com/arc/outboundfeeds/rss/",
            "https://news.usni.org/feed"
        ]
    },
    "10_GEO_STRATEGY": {
        "name": "GEOPOLITICA: STRATEGIA & PACIFICO",
        "desc": "Cina, Taiwan, Cavi sottomarini, Spazio.",
        "urls": [
            "https://www.aspistrategist.org.au/feed/",
            "https://jamestown.org/feed/",
            "https://www.csis.org/rss/analysis",
            "https://thediplomat.com/feed/"
        ]
    },
    "11_CENTRAL_BANKS": {
        "name": "MACRO: BANCHE CENTRALI",
        "desc": "Policy, Research Papers, Repo Market.",
        "urls": [
            "https://www.bis.org/doclist/research.rss",
            "https://www.federalreserve.gov/feeds/feds_rss.xml",
            "https://libertystreeteconomics.newyorkfed.org/feed/",
            "https://www.ecb.europa.eu/rss/wppub.xml"
        ]
    },
    "12_GLOBAL_ECONOMY": {
        "name": "MACRO: ENERGIA & COMMERCIO",
        "desc": "Petrolio, Gas, Supply Chain logistica.",
        "urls": [
            "https://oilprice.com/rss/main",
            "https://www.imf.org/en/Publications/RSS?language=eng&series=IMF%20Working%20Papers",
            "https://www.oxfordenergy.org/feed/"
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
            
            # Accettiamo tutto ciò che è recente O che non ha data (per sicurezza)
            if not pub_date or pub_date > cutoff:
                content = "No content"
                if hasattr(entry, 'summary'): content = entry.summary
                elif hasattr(entry, 'content'): content = entry.content[0].value
                elif hasattr(entry, 'description'): content = entry.description
                
                content = content.replace("<p>", "").replace("</p>", "").replace("<div>", "").strip()[:1500]
                source = d.feed.get('title', 'Unknown Source')
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

# --- 3. AGENTE ANALISTA (PROMPT MASSIVO) ---
def analyze_cluster(cluster_key, info, raw_text):
    if not raw_text: return ""
    
    print(f"  > Analisi {cluster_key} ({len(raw_text)} chars)...")
    
    # Prompt modificato per generare TANTI contenuti con link
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
    ### [Titolo in Italiano della notizia]
    [Analisi tecnica dettagliata di 4-5 righe. Spiega il 'cosa', il 'come' e il 'perché'. Usa termini tecnici.]
    **Fonte:** [Inserisci il LINK originale fornito] (DEVE ESSERE CLICCABILE)
    
    STILE:
    - Densità informativa massima.
    - Italiano professionale.
    - NESSUNA INTRODUZIONE, NESSUNA CONCLUSIONE. Solo la lista delle analisi.
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
            max_tokens=6000 # Massimo spazio per scrivere tantissimo
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error {cluster_key}: {e}")
        return ""

# --- 4. SEQUENCER ---
print("Avvio MOTORE EPOCHALE...")
today = datetime.datetime.now().strftime("%Y-%m-%d")
display_date = datetime.datetime.now().strftime("%d %B %Y")

full_report = f"""# IL POLIMATE: Edizione Estesa del {display_date}
**Livello:** Deep Strategic Intelligence
**Fonti:** 75+ Tier-0 Sources

> Questo documento contiene un'analisi granulare di tutti i segnali rilevanti intercettati nelle ultime 24 ore. Ogni sezione approfondisce decine di paper, report e comunicati.

---
"""

for key, info in CLUSTERS.items():
    print(f"\n--- Processando Cluster: {info['name']} ---")
    
    raw_data = get_cluster_data(info['urls'])
    
    if raw_data:
        raw_text = "\n---\n".join(raw_data)
        analysis = analyze_cluster(key, info, raw_text)
        
        if analysis and len(analysis) > 50:
            full_report += f"\n\n## {info['name']}\n\n{analysis}\n\n<br><hr><br>\n"
        else:
            print("  > Nessun output rilevante dall'AI.")
    else:
        print("  > Nessun dato grezzo trovato.")
    
    # Pausa per Rate Limit (fondamentale quando si fanno 12 chiamate pesanti)
    time.sleep(10)

# --- 5. SALVATAGGIO ---
if not os.path.exists("_posts"): os.makedirs("_posts")
filename = f"_posts/{today}-brief.md"

markdown_file = f"""---
title: "Dossier Esteso: {today}"
date: {today}
layout: post
excerpt: "Edizione Monumentale. Analisi granulare di oltre 12 settori strategici con centinaia di fonti primarie."
---

{full_report}
"""

with open(filename, "w", encoding='utf-8') as f:
    f.write(markdown_file)

print("Dossier Epochale Generato.")
