---
layout: default
title: Home
---

# IL POLIMATE
### Intelligence a colazione

---

## EDIZIONI RECENTI

<ul class="post-list">
  {% for post in site.posts %}
    <li style="margin-bottom: 25px; border-bottom: 1px solid #eee; padding-bottom: 15px;">
      <span style="font-family: 'Helvetica', sans-serif; font-weight: bold; font-size: 0.8em; color: #d00;">
        {{ post.date | date: "%d GENNAIO %Y" }}
      </span>
      <br>
      <a href="{{ post.url | relative_url }}" style="font-size: 1.4em; font-family: 'Georgia', serif; font-weight: bold; text-decoration: none; color: #111; line-height: 1.2; display: block; margin-top: 5px;">
        {{ post.title }}
      </a>
      <div style="font-size: 1em; color: #444; margin-top: 8px; font-family: sans-serif;">
        <em>Un dossier su Scienza, Atomi e Potere.</em>
      </div>
    </li>
  {% endfor %}
</ul>

---
<center>
<small style="color: #bbb;">Redazione Algoritmica | <a href="https://github.com/marcorzzn" style="color: #bbb;">Codice Sorgente</a></small>
</center>
