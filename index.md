---
layout: default
title: Home
---

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">

<style>
    /* 1. PULIZIA TOTALE DEGLI ELEMENTI DI DEFAULT DEL TEMA */
    header, .site-header, .site-title, .site-description, .wrapper > header { 
        display: none !important; 
        height: 0 !important;
        visibility: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* RESET DEL CONTAINER PRINCIPALE */
    .wrapper { 
        max-width: 900px !important; 
        margin: 0 auto !important; 
        padding-top: 20px !important;
    }

    /* 2. STILI DEL SITO */
    body {
        font-family: 'Inter', sans-serif;
        background-color: #fdfdfd;
        color: #111;
        transition: background 0.3s, color 0.3s;
    }

    /* PULSANTI FLOTTANTI FISSI (FUNZIONANO SEMPRE) */
    .floating-controls {
        position: fixed;
        top: 20px;
        right: 20px;
        display: flex;
        gap: 10px;
        z-index: 9999;
        background: rgba(255,255,255,0.8);
        padding: 5px;
        border-radius: 8px;
        backdrop-filter: blur(5px);
    }

    .ctrl-btn {
        background: #fff;
        border: 1px solid #ccc;
        color: #333;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2em;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .ctrl-btn:hover { transform: scale(1.1); border-color: #000; }

    /* HEADER GIORNALE */
    .masthead {
        text-align: center;
        border-bottom: 4px double #000;
        padding-bottom: 30px;
        margin-bottom: 50px;
        margin-top: 40px;
    }
    .masthead-top {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #555;
        margin-bottom: 10px;
    }
    .masthead-title {
        font-family: 'Playfair Display', serif;
        font-size: 5rem;
        font-weight: 900;
        letter-spacing: -2px;
        margin: 0;
        line-height: 0.9;
    }
    .masthead-sub {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 1.4rem;
        color: #444;
        margin-top: 10px;
    }

    /* ARTICOLO IN EVIDENZA (OGGI) */
    .feature-article {
        margin-bottom: 60px;
    }
    .date-label {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 2px solid #000;
        display: inline-block;
        margin-bottom: 15px;
    }
    .feature-title {
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        font-weight: 700;
        line-height: 1.1;
        margin-bottom: 15px;
        color: #000;
        text-decoration: none;
        display: block;
    }
    .feature-title:hover { text-decoration: underline; }
    
    .feature-snippet {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #333;
        margin-bottom: 20px;
    }

    .read-btn {
        display: inline-block;
        background: #000;
        color: #fff;
        padding: 10px 20px;
        font-weight: 600;
        text-decoration: none;
        font-size: 0.9rem;
        border-radius: 4px;
        transition: background 0.2s;
    }
    .read-btn:hover { background: #333; }

    /* ARCHIVIO */
    .archive-section {
        border-top: 1px solid #ddd;
        padding-top: 40px;
    }
    .archive-header {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 30px;
        font-size: 0.9rem;
        color: #666;
    }
    .archive-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 30px;
    }
    .archive-item a {
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        font-size: 1.2rem;
        color: #000;
        text-decoration: none;
        line-height: 1.3;
    }
    .archive-item a:hover { color: #555; }
    .archive-date {
        font-size: 0.8rem;
        color: #888;
        display: block;
        margin-bottom: 5px;
    }

    /* DARK MODE */
    body.dark-mode { background: #121212; color: #e0e0e0; }
    body.dark-mode .floating-controls { background: rgba(0,0,0,0.8); }
    body.dark-mode .ctrl-btn { background: #222; border-color: #444; color: #fff; }
    body.dark-mode .masthead { border-bottom-color: #fff; }
    body.dark-mode .masthead-title, body.dark-mode .feature-title, body.dark-mode .archive-item a { color: #fff; }
    body.dark-mode .masthead-sub, body.dark-mode .feature-snippet { color: #aaa; }
    body.dark-mode .date-label { border-bottom-color: #fff; }
    body.dark-mode .read-btn { background: #fff; color: #000; }
    body.dark-mode .read-btn:hover { background: #ccc; }

    /* Translate Override */
    .goog-te-banner-frame { display: none !important; }
    body { top: 0px !important; }
</style>

<div class="floating-controls">
    <button class="ctrl-btn" onclick="toggleDark()" title="Dark Mode"><i class="fas fa-moon"></i></button>
    <div id="google_translate_element" style="opacity: 0; width: 1px; height: 1px; overflow: hidden;"></div>
    <button class="ctrl-btn" onclick="triggerTranslate()" title="Translate"><i class="fas fa-language"></i></button>
</div>

<div class="masthead">
    <div class="masthead-top">Est. 2026 &mdash; Daily Strategic Intelligence</div>
    <h1 class="masthead-title">IL POLIMATE</h1>
    <div class="masthead-sub">L'essenziale strategico, ogni mattina.</div>
</div>

{% assign latest = site.posts.first %}
<div class="feature-article">
    <div class="date-label">{{ latest.date | date: "%d %B %Y" }}</div>
    <a href="{{ latest.url | relative_url }}" class="feature-title">{{ latest.title }}</a>
    <div class="feature-snippet">
        {{ latest.excerpt | strip_html | truncatewords: 30 }}
    </div>
    <a href="{{ latest.url | relative_url }}" class="read-btn">LEGGI IL DOSSIER COMPLETO &rarr;</a>
</div>

<div class="archive-section">
    <div class="archive-header">Archivio Edizioni</div>
    <div class="archive-grid">
        {% for post in site.posts offset:1 %}
        <div class="archive-item">
            <span class="archive-date">{{ post.date | date: "%d/%m/%Y" }}</span>
            <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
        </div>
        {% endfor %}
    </div>
</div>

<script>
    // Dark Mode
    function toggleDark() {
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('theme', document.body.classList.contains('dark-mode') ? 'dark' : 'light');
    }
    if(localStorage.getItem('theme') === 'dark') document.body.classList.add('dark-mode');

    // Translate Logic
    function triggerTranslate() {
        var select = document.querySelector(".goog-te-combo");
        if(select) {
            select.value = select.value === 'it' ? 'en' : 'it'; // Toggle veloce IT/EN o apre menu
            select.dispatchEvent(new Event('change'));
        } else {
            alert("Il modulo traduzione si sta caricando...");
        }
    }
    function googleTranslateElementInit() {
        new google.translate.TranslateElement({pageLanguage: 'it', layout: google.translate.TranslateElement.InlineLayout.SIMPLE}, 'google_translate_element');
    }
</script>
<script type="text/javascript" src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
