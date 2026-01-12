---
layout: default
title: Edicola
---

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@400;500&display=swap" rel="stylesheet">

<div style="text-align: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 4px double #000;">
    
    <div style="font-family: 'Inter', sans-serif; font-size: 0.75em; letter-spacing: 3px; text-transform: uppercase; color: #666; margin-bottom: 5px;">
        EST. 2026 &mdash; STRATEGIC BRIEF
    </div>

    <h1 style="font-family: 'Playfair Display', serif; font-size: 4em; font-weight: 900; letter-spacing: -1.5px; margin: 0; line-height: 0.9; color: #111;">
        IL POLIMATE
    </h1>

    <div style="font-family: 'Playfair Display', serif; font-style: italic; font-size: 1.2em; color: #444; margin-top: 10px;">
        Intelligence per colazione.
    </div>

</div>
<div style="font-family: 'Inter', sans-serif;">
    <h3 style="border-left: 4px solid #000; padding-left: 10px; margin-bottom: 20px; text-transform: uppercase; font-size: 0.9em; letter-spacing: 1px;">
        Ultimi Dossier
    </h3>

    <ul class="post-list" style="list-style: none; padding: 0;">
      {% for post in site.posts %}
        <li style="margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #eee;">
          
            <span style="background-color: #111; color: #fff; padding: 4px 8px; font-size: 0.7em; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                {{ post.date | date: "%d %b %Y" }}
            </span>

            <a href="{{ post.url | relative_url }}" style="display: block; margin-top: 12px; font-family: 'Playfair Display', serif; font-size: 1.8em; font-weight: 700; color: #000; text-decoration: none; line-height: 1.1;">
                {{ post.title }}
            </a>

            <div style="margin-top: 8px; font-size: 1em; color: #555; line-height: 1.5;">
                Analisi profonda su Frontiera Scientifica, Hardware e Geopolitica.
                <span style="color: #000; text-decoration: underline; font-size: 0.9em;">Leggi il dossier &rarr;</span>
            </div>

        </li>
      {% endfor %}
    </ul>
</div>

<div style="text-align: center; margin-top: 50px; font-size: 0.8em; color: #999; border-top: 1px solid #eee; padding-top: 20px;">
    REDAZIONE ALGORITMICA &bull; HYDRA ENGINE &bull; <a href="https://github.com/marcorzzn" style="color: #999;">SOURCE</a>
</div>
