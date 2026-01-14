# 🏛️ IL POLIMATE
> **Automated Strategic Intelligence Engine**

[![Daily Brief](https://github.com/marcorzzn/ilpolimate/actions/workflows/daily.yml/badge.svg)](https://github.com/marcorzzn/ilpolimate/actions/workflows/daily.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Il Polimate** è un sistema completamente automatizzato di aggregazione e analisi notizie ("Open Source Intelligence" - OSINT). Ogni mattina, il sistema scansiona centinaia di feed RSS da fonti accademiche, governative e industriali, utilizza un LLM (Large Language Model) per estrarre solo le informazioni ad alto valore strategico e pubblica un dossier sintetico sul web.

🔗 **Leggi la Rassegna:** [https://marcorzzn.github.io/ilpolimate/](https://marcorzzn.github.io/ilpolimate/)

---

## ⚙️ Come Funziona

Il sistema opera su un ciclo di 24 ore gestito interamente da **GitHub Actions**:

1.  **Harvesting (Raccolta):** Alle 08:00 (CET), lo script Python si attiva e scarica gli ultimi paper e articoli da fonti come *ArXiv, Nature, MIT News, Foreign Affairs, DARPA, ecc.*
2.  **AI Analysis (Analisi):** I contenuti grezzi vengono puliti e inviati via API a **Groq (Llama-3-70b)**. L'AI agisce come un analista esperto, filtrando il rumore e scrivendo riassunti in italiano focalizzati sull'impatto tecnico/strategico.
3.  **Publishing (Pubblicazione):** Il report viene formattato in Markdown, committato automaticamente nella repository e pubblicato via **Jekyll** come post statico.

## Settori Monitorati

Il "Radar" del Polimate copre 13 cluster strategici:

* 🤖 **Intelligenza Artificiale** (LLM, Agenti, Computer Vision)
* ⚛️ **Fisica di Frontiera** (Quantum Computing, Ottica)
* 🧮 **Matematica Avanzata** (Crittografia, Teoria dei Giochi)
* 🧬 **Biologia Sintetica** (Genomica, CRISPR)
* 🛡️ **Cyber-Warfare** (InfoSec, Zero-Day, Threat Intel)
* 💾 **Silicio & Chip Design** (Semiconduttori, Architetture HPC)
* 🚀 **Space Economy** (Lanci, Satelliti, Esplorazione)
* 🧪 **Scienza dei Materiali** (Batterie, Superconduttori)
* ⚔️ **Difesa & Strategia** (Tecnologia militare, Dottrina)
* 🌍 **Geopolitica** (Analisi globale, Diplomazia)
* 📉 **Macroeconomia** (Banche Centrali, Policy)
* ⚡ **Energia** (Rinnovabili, Nucleare, Mercati)

## Stack Tecnologico

* **Core:** Python 3.9
* **Feed Parsing:** `feedparser`, `beautifulsoup4`
* **AI Inference:** Groq API (Model: `llama-3.3-70b-versatile`)
* **Automation:** GitHub Actions (Cron Job)
* **Frontend:** Jekyll (GitHub Pages) con tema custom "Polymath Minimal".

## Struttura dei File

* `daily_brief.py`: Il "cervello" del sistema. Contiene la logica di raccolta, i prompt per l'AI e la generazione del file Markdown.
* `.github/workflows/daily.yml`: Il file di configurazione che ordina a GitHub di eseguire lo script ogni mattina.
* `_layouts/`: Contiene i template HTML per la visualizzazione grafica del sito.
* `_config.yml`: Configurazione principale di Jekyll.
