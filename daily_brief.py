import os
import datetime
import time
from duckduckgo_search import DDGS
from groq import Groq

# --- CONFIGURAZIONE ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("ERRORE: Manca la GROQ_API_KEY.")
    exit(1)

# --- 1. GATHERING (STEALTH MODE) ---
print("Inizializzazione DuckDuckGo Stealth...")
ddgs = DDGS()
today = datetime.datetime.now().strftime("%Y-%m-%d")

# Query semplificate per massimizzare i risultati
queries = [
    "physics breakthrough arxiv nature science", # Tolto "last 24h" per testare se trova qualcosa
    "semiconductor technology news tsmc intel",
    "submarine cables geopolitics internet",
    "central bank digital currency news"
]

raw_context = ""

for query in queries:
    print(f"--- Cercando: {query} ---")
    try:
        # backend="html" è più lento ma spesso aggira i blocchi anti-bot
        # togliamo time_range per ora per assicurarci di trovare ALMENO qualcosa
        results = ddgs.text(query, max_results=4, backend="html")
        
        found_for_query = False
        if results:
            for r in results:
                print(f"Trovato: {r['title'][:30]}...") # Log per capire cosa trova
                raw_context += f"\nTITOLO: {r['title']}\nSNIPPET: {r['body']}\nURL: {r['href']}\n"
                found_for_query = True
        
        if not found_for_query:
            print("Nessun risultato per questa query.")

        time.sleep(2) # Pausa più lunga per non sembrare un bot aggressivo

    except Exception as e:
        print(f"ERRORE RICERCA '{query}': {e}")

# Se ancora vuoto, usiamo dati finti per testare almeno la generazione del sito
if not raw_context or len(raw_context) < 50:
    print("ATTENZIONE: Ricerca fallita o bloccata. Uso dati di fallback.")
    raw_context = "NESSUNA NOTIZIA TROVATA DAL MOTORE DI RICERCA. IL SISTEMA DI GATHERING È STATO BLOCCATO."

# --- 2. ANALYSIS (GROQ) ---
print(f"Input per AI (lungh: {len(raw_context)} chars). Generazione report...")

system_prompt = """
SEI: "The Polymath".
OBIETTIVO: Scrivere "THE POLYMATH BRIEF".
DATA: {date}

REGOLE:
1. Basati sul testo fornito ("NOTIZIE GREZZE").
2. Se il testo dice che non ci sono notizie, scrivi un report sarcastico che si lamenta della mancanza di segnale.
3. Se ci sono notizie, usa il formato standard: 4 sezioni, Titolo, Fatti, Meccanismo.
"""

try:
    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt.format(date=today)},
            {"role": "user", "content": f"NOTIZIE GREZZE:\n{raw_context}"}
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

print("Script completato.")
