import os
import json
import datetime

# Setup
posts_dir = "_posts"
data_dir = "assets/data"
if not os.path.exists(posts_dir): os.makedirs(posts_dir)
if not os.path.exists(data_dir): os.makedirs(data_dir)

# 1. Mock Ticker Data
headlines = [
    "BCE: Lagarde segnala possibile taglio tassi a giugno",
    "Fusione nucleare: Nuovo record di stabilità al JET",
    "Tensioni Mar Rosso: Deviate il 40% delle rotte container",
    "AI Act: Approvato dal Parlamento Europeo il testo finale",
    "SpaceX: Successo parziale per il terzo test di Starship"
]
with open(os.path.join(data_dir, "headlines.json"), "w", encoding="utf-8") as f:
    json.dump(headlines, f, ensure_ascii=False, indent=2)

# 2. Mock Tensions Map Data
tensions = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [34.0, 31.0]},
            "properties": {
                "category": "CONFLICT",
                "title": "Escalation Confine Nord",
                "description": "Scambio di artiglieria pesante segnalato lungo la linea di demarcazione. Coinvolti sistemi di intercettazione.",
                "intensity": 8
            }
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [121.5, 25.0]},
            "properties": {
                "category": "BORDER_DISPUTE",
                "title": "Manovre Navali Stretto di Taiwan",
                "description": "Rilevato gruppo d'attacco portaerei in transito non programmato. Attivazione difese costiere.",
                "intensity": 6
            }
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [2.35, 48.85]},
            "properties": {
                "category": "PROTEST",
                "title": "Sciopero Generale Trasporti",
                "description": "Blocco totale degli hub logistici parigini. Stima 100k partecipanti.",
                "intensity": 4
            }
        }
    ]
}
with open(os.path.join(data_dir, "tensions.json"), "w", encoding="utf-8") as f:
    json.dump(tensions, f, ensure_ascii=False, indent=2)

# 3. Mock Daily Brief Post
today = datetime.datetime.now().strftime("%Y-%m-%d")
display_date = datetime.datetime.now().strftime("%d %B %Y")

post_content = f"""---
title: "La rassegna del giorno - {display_date}"
date: {today}
layout: post
categories: [brief]
---

<div class="mechanism-section">
    <h2 style="font-family: 'Playfair Display', serif; color: #000; border-bottom: 2px solid #000;">MECCANISMI</h2>
    <h3>L'Egemonia del Silicio: Oltre la Legge di Moore</h3>
    
    <p><strong>SINTESI SISTEMICA</strong></p>
    <p>La fine della scalatura planare dei transistor sta forzando un cambio di paradigma verso architetture 3D (Gate-All-Around) e packaging eterogeneo (Chiplets). Non è più una questione di fisica dei materiali, ma di architettura sistemica.</p>
    
    <p><strong>ARCHITETTURA CAUSALE</strong></p>
    <p>Il costo esponenziale delle fonderie a 2nm (causa) sta spingendo i designer verso l'integrazione verticale (effetto). Questo sposta il valore dalla litografia pura al design dell'interconnessione.</p>
</div>
<hr style="margin: 40px 0;">

## SCIENCE & FRONTIER COMPUTE

### Modelli Fluidodinamici per il Plasma Stellare
Un nuovo approccio ibrido (AI + Fisica) ha permesso di simulare il comportamento del plasma nei reattori Tokamak con una stabilità senza precedenti, superando i limiti delle equazioni di Navier-Stokes classiche.
**Fonte:** [Nature Physics](https://nature.com)

## GEOPOLITICS, DEFENSE & STRATEGY

### Riarmo Artico e Nuove Rotte Commerciali
La Russia ha riattivato tre basi sovietiche lungo la Northern Sea Route. La mossa segnala l'intenzione di controllare fisicamente la rotta commerciale che lo scioglimento dei ghiacci sta rendendo la più rapida tra Asia ed Europa.
**Fonte:** [CSIS Analysis](https://csis.org)
"""

with open(os.path.join(posts_dir, f"{today}-brief.md"), "w", encoding="utf-8") as f:
    f.write(post_content)

print("Dati simulati generati con successo.")
