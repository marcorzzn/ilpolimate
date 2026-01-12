import os
import datetime
import time
from duckduckgo_search import DDGS
from groq import Groq

# --- CONFIGURAZIONE ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("Manca la GROQ_API_KEY nei Secrets!")

# Inizializza il client Groq
client = Groq(api_key=GROQ_API_KEY)
# Inizializza DuckDuckGo (senza chiave)
ddgs = DDGS()

today = datetime.datetime.now().strftime("%Y-%m-%d")

# --- 1. GATHERING (DUCKDUCKGO) ---
queries = [
    "arxiv physics breakthrough new discovery last 24 hours",
    "semiconductor advanced packaging news tsmc intel last 24 hours",
    "undersea internet cables geopolitics news last 24 hours",
    "central bank digital currency cbdc latest pilot news last 24 hours"
]

print(f"Scansione gratuita avviata per il {today}...")
raw_context = ""

for query in queries:
    print(f"Cercando su DDG: {query}")
    try:
        # Cerca massimo 3 risultati per query per essere veloci
        results = ddgs.text(query, max_results=3)
        if results:
            for r in results:
                raw_context += f"\nTITOLO: {r['title']}\nSNIPPET: {r['body']}\nURL: {r['href']}\n"
        time.sleep(1) # Pausa di cortesia per non essere bloccati
    except Exception as e:
        print(f"Errore ricerca '{query}': {e}")

if not raw_context:
    raw_context = "Nessuna notizia trovata. Genera un report vuoto segnalando l'assenza di dati."

# --- 2. ANALYSIS (GROQ + LLAMA 3) ---
system_prompt = """
SEI: "The Polymath", analista di intelligence.
OBIETTIVO: Scrivere "THE POLYMATH BRIEF".
DATA: {date}

REGOLE:
1. Fonte dati: Usa SOLO il testo fornito.
2. Stile: Asettico, tecnico, italiano.
3. Formato: 4 Sezioni (Frontiera Tech, Hardware, Geopolitica, Macro).
   Per ogni notizia:
   - **Il Segnale:** [Titolo]
   - **I Fatti:** [Dettagli]
   - **Il Meccanismo:** [Perché tecnico]
   - **Fonti:** https://www.fornino.com/

Se non ci sono notizie valide per una sezione, scrivi "NESSUN SEGNALE RILEVATO".
"""

print("Generazione report con Groq (Llama 3)...")
try:
    completion = client.chat.completions.create(
        model="llama3-70b-8192", # Modello potente e gratuito
        messages=[
            {"role": "system", "content": system_prompt.format(date=today)},
            {"role": "user", "content": f"NOTIZIE GREZZE:\n{raw_context}"}
        ],
        temperature=0.3
    )
    
    report_content = completion.choices[0].message.content

except Exception as e:
    print(f"Errore Groq: {e}")
    report_content = "Errore nella generazione del report."

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

print("Fatto.")
