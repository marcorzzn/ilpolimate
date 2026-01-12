---
layout: default
title: Home
---

# THE POLYMATH BRIEF
### Intelligence Strategica Quotidiana

---

## Archivio Report

<ul>
  {% for post in site.posts %}
    <li>
      <span style="color: gray; font-family: monospace;">[{{ post.date | date: "%Y-%m-%d" }}]</span>
      <a href="{{ post.url }}">{{ post.title }}</a>
    </li>
  {% endfor %}
</ul>
