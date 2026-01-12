import os
import datetime
import feedparser
from groq import Groq

# --- CONFIGURAZIONE ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("ERRORE: Manca la GROQ_API_KEY.")
    exit(1)

# --- 1. GATHERING (RSS PROTOCOL) ---
# Usiamo fonti dirette che NON bloccano i bot.
# Queste fonti coprono le 4 sezioni del Polymath Brief.
feeds_map = {
    "FRONTIERA_TECH": [
        "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=5", # AI Papers
        "http://export.arxiv.org/api/query?search_query=cat:physics&sortBy=submittedDate&sortOrder=descending&max_results=5" # Physics Papers
    ],
    "HARDWARE_CHIPS": [
        "https://www.tomshardware.com/feeds/all", # Hardware News
        "https://www.anandtech.com/rss/" # Deep Tech Analysis
    ],
    "GEOPOLITICA": [
        "https://oilprice.com/rss/main", # Energy & Geopolitics (Cruciale)
        "https://defence-blog.com/feed/" # Defense Tech
    ],
    "MACROECONOMIA": [
        "https://www.cnbc.com/id/10000003/device/rss/rss.html", # World Economy
        "https://cointelegraph.com/rss" # Crypto/Finance Frontier
    ]
}

print("Avvio protocollo RSS Gathering...")
raw_context = ""

for category, urls in feeds_map.items():
    print(f"\n--- SCANSIONE {category} ---")
    raw_context += f"\n\n=== CATEGORIA: {category} ===\n"
    
    for url in urls:
        try:
            print(f"Leggendo: {url}...")
            feed = feedparser.parse(url)
            # Prendiamo solo le prime 3 notizie per feed per non intasare l'AI
            for entry in feed.entries[:3]:
                title = entry.title
                # Pulizia sommaria del link e descrizione
                link = entry.link
                summary = entry.summary[:300] if hasattr(entry, 'summary') else "No summary"
                
                print(f"  -> Trovato: {title[:40]}...")
                raw_context += f"- TITOLO: {title}\n  LINK: {link}\n  SUMMARY: {summary}\n"
        except Exception as e:
            print(f"Errore lettura feed {url}: {e}")

if len(raw_context) < 100:
    raw_context = "ERRORE CRITICO: Nessun feed RSS è stato caricato. Genera un report di emergenza."

# --- 2. ANALYSIS (GROQ) ---
today = datetime.datetime.now().strftime("%Y-%m-%d")
print(f"\nGenerazione Report con AI (Input size: {len(raw_context)} chars)...")

system_prompt = """
SEI: "The Polymath", analista di intelligence strategica.
OBIETTIVO: Scrivere "THE POLYMATH BRIEF" del {date}.

INPUT: Una lista di notizie grezze divise per categorie (RSS Feeds).

REGOLE DI SCRITTURA:
1. SELEZIONA SOLO IL MEGLIO: Hai molte notizie, scegline SOLO 1 per ogni sezione (le 4 sezioni standard). Scarta le banalità.
2. STILE: Asettico, denso, alta competenza tecnica. Italiano professionale.
3. FORMATO OBBLIGATORIO PER OGNI SEZIONE:
   ## [NOME SEZIONE]
   **Il Segnale:** [Titolo breve]
   * **I Fatti:** [Cosa è successo]
   * **Il Meccanismo:** [Analisi tecnica del PERCHÉ è importante]
   * **Fonti:** [Inserisci il LINK originale fornito nel feed]

LE 4 SEZIONI SONO:
1. FRONTIERA HARD-TECH (Dagli Arxiv/Physics)
2. HARDWARE & MACCHINE (Da Tom's Hardware/Anandtech)
3. GEOPOLITICA & ENERGIA (Da OilPrice/Defence)
4. RADAR SOCIALE & MACRO (Da CNBC/Cointelegraph)

Se una sezione non ha notizie valide, scrivi "NESSUN SEGNALE RILEVATO".
"""

try:
    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt.format(date=today)},
            {"role": "user", "content": f"DATI RSS:\n{raw_context}"}
        ],
        temperature=0.3
    )
    report_content = completion.choices[0].message.content
except Exception as e:
    report_content = f"ERRORE AI: {str(e)}"

# --- 3. PUBLISHING ---
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

print("Brief completato.")
