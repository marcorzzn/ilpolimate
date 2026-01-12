import os
import datetime
import time
import feedparser
import concurrent.futures
from groq import Groq

# --- CONFIGURAZIONE ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MAX_WORKERS = 30
LOOKBACK_HOURS = 26 

if not GROQ_API_KEY:
    print("ERRORE: Manca la GROQ_API_KEY.")
    exit(1)

# --- 1. DEFINIZIONE DEI DOMINI E DELLE FONTI ---
# Organizziamo le fonti per "Cluster" tematici. Ogni cluster avrà il suo Agente AI dedicato.

DOMAINS = {
    "1_FRONTIERA_SCIENZA": {
        "title": "FRONTIERA SCIENTIFICA & BIO-CODICE",
        "description": "Focus su Crittografia Post-Quantum, Biologia Sintetica, Nuovi Teoremi, AI Architectures.",
        "urls": [
            "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=15",
            "http://export.arxiv.org/api/query?search_query=cat:quant-ph&sortBy=submittedDate&sortOrder=descending&max_results=10",
            "https://eprint.iacr.org/rss/rss.xml",
            "https://connect.biorxiv.org/biorxiv_xml.php?subject=synthetic_biology",
            "https://connect.biorxiv.org/biorxiv_xml.php?subject=genomics",
            "https://www.nature.com/nphys.rss",
            "https://www.usenix.org/rss/conference/all-proceedings",
            "https://googleprojectzero.blogspot.com/feeds/posts/default"
        ]
    },
    "2_HARDWARE_ATOMS": {
        "title": "HARDWARE, SUPPLY CHAIN & FISICA DELLA MATERIA",
        "description": "Focus su Litografia, Semiconduttori, Chimica delle Batterie, Materiali Rari.",
        "urls": [
            "https://semiengineering.com/feed/",
            "https://spectrum.ieee.org/feeds/topic/semiconductors/rss",
            "https://www.semiconductors.org/feed/",
            "https://chemrxiv.org/engage/chemrxiv/rss",
            "https://www.anl.gov/rss/research-news/feed",
            "https://www.nist.gov/news-events/news/rss.xml",
            "https://www.imec-int.com/en/rss"
        ]
    },
    "3_GEOPOLITICA_POWER": {
        "title": "GEOPOLITICA, DIFESA & DOTTRINA",
        "description": "Focus su Movimenti Militari, Cavi Sottomarini, Alleanze Strategiche, Intelligence.",
        "urls": [
            "https://rusi.org/rss.xml",
            "https://www.csis.org/rss/analysis",
            "https://jamestown.org/feed/",
            "https://www.aspistrategist.org.au/feed/",
            "https://warontherocks.com/feed/",
            "https://www.defensenews.com/arc/outboundfeeds/rss/",
            "https://carnegieendowment.org/rss/solr/get/all-content"
        ]
    },
    "4_MACRO_MONEY": {
        "title": "MACROECONOMIA STRUTTURALE & RISCHIO",
        "description": "Focus su Banche Centrali, Liquidità, Shadow Banking, Commodities Energetiche.",
        "urls": [
            "https://www.bis.org/doclist/research.rss",
            "https://www.federalreserve.gov/feeds/feds_rss.xml",
            "https://libertystreeteconomics.newyorkfed.org/feed/",
            "https://www.imf.org/en/Publications/RSS?language=eng&series=IMF%20Working%20Papers",
            "https://oilprice.com/rss/main",
            "https://www.oxfordenergy.org/feed/"
        ]
    }
}

# --- 2. ENGINE DI RACCOLTA (HYDRA) ---
def fetch_feed_data(urls):
    """Scarica le notizie per un singolo dominio in parallelo"""
    collected_data = []
    
    def load_url(url):
        try:
            d = feedparser.parse(url, agent="Mozilla/5.0 (PolymathBot)")
            items = []
            now = datetime.datetime.now(datetime.timezone.utc)
            cutoff = now - datetime.timedelta(hours=LOOKBACK_HOURS)
            
            for entry in d.entries:
                # Gestione Data
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime.datetime(*entry.updated_parsed[:6], tzinfo=datetime.timezone.utc)
                
                # Filtro temporale rigoroso
                if pub_date and pub_date > cutoff:
                    content = "No content"
                    if hasattr(entry, 'summary'): content = entry.summary
                    elif hasattr(entry, 'description'): content = entry.description
                    elif hasattr(entry, 'content'): content = entry.content[0].value
                    
                    # Pulizia testo
                    content = content.replace("<p>", "").replace("</p>", "").replace("<div>", "")[:1500] # AUMENTATO A 1500 CARATTERI
                    items.append(f"SOURCE: {d.feed.get('title', 'Unknown')}\nTITLE: {entry.title}\nTXT: {content}\nLINK: {entry.link}\n")
            return items
        except:
            return []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(load_url, urls)
        for res in results:
            collected_data.extend(res)
            
    return collected_data

# --- 3. IL GENERATORE DI CAPITOLI (L'AGENTE AI) ---
def generate_chapter(domain_key, domain_info, raw_data):
    """Genera un capitolo massivo per un singolo dominio"""
    
    if not raw_data:
        return f"## {domain_info['title']}\n\n*Nessun segnale rilevante intercettato nelle ultime 24 ore in questo settore.*\n\n---\n"

    # Uniamo i dati (fino a 40.000 caratteri per dominio per non saturare troppo)
    context_text = "\n---\n".join(raw_data)[:40000]
    
    print(f"Generazione capitolo: {domain_info['title']} (Input: {len(context_text)} chars)...")

    system_prompt = f"""
    SEI: "The Polymath", analista senior di intelligence.
    SETTORE DI ANALISI: {domain_info['title']} ({domain_info['description']})
    
    OBIETTIVO:
    Scrivere un CAPITOLO ESTESO E DETTAGLIATO per il Daily Dossier.
    Non devi fare un elenco puntato veloce. Devi scrivere come se fosse un articolo di fondo di "The Economist" o un report di "Stratfor".
    
    ISTRUZIONI RIGIDE:
    1. Seleziona le 3 notizie/paper più critici dal dataset fornito.
    2. Per OGNUNA delle 3 notizie, scrivi un'analisi approfondita strutturata così:
       - **TITOLO:** Chiaro e tecnico.
       - **EXECUTIVE SUMMARY:** Cosa è successo (2-3 frasi).
       - **DEEP DIVE TECNICO:** Spiega il "come" e il "perché" in dettaglio (almeno 150 parole). Usa terminologia specifica.
       - **IMPATTO A CATENA:** Conseguenze di secondo e terzo ordine (es. se manca il Gallio -> impatto sui radar AESA -> impatto sulla dottrina navale).
       - **FONTE:** Link.
    
    3. GLOSSARIO DI SETTORE (Obbligatorio alla fine del capitolo):
       Definisci 3 termini tecnici complessi emersi in questo specifico capitolo.
       
    TONO: Asettico, densità informativa massima, professionale.
    """

    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"DATI GREZZI SETTORE:\n{context_text}"}
        ],
        temperature=0.2,
        max_tokens=5000 # Max output per capitolo
    )
    return completion.choices[0].message.content

# --- 4. MAIN SEQUENCER ---
print("Avvio POLYMATH LONG-FORM ENGINE...")
full_dossier = ""
today = datetime.datetime.now().strftime("%Y-%m-%d")

# Header del Dossier
full_dossier += f"# POLYMATH DEEP-DIVE DOSSIER\n"
full_dossier += f"**Data:** {today}\n"
full_dossier += f"**Classification:** EYES ONLY / STRATEGIC ANALYSIS\n\n"
full_dossier += f"> Questo dossier è generato da un'architettura multi-agente che analizza fonti primarie (Tier-0). Ogni sezione rappresenta un'analisi verticale approfondita.\n\n---\n\n"

# Ciclo sequenziale sui domini
for key, info in DOMAINS.items():
    print(f"\n--- Elaborazione Dominio: {key} ---")
    
    # 1. Raccolta Dati
    domain_data = fetch_feed_data(info['urls'])
    print(f"Segnali trovati: {len(
