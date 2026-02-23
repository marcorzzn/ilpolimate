import os
import datetime
import json

class ReportGenerator:
    def __init__(self, output_dir="_posts", site_data_dir="assets/data"):
        self.output_dir = output_dir
        self.site_data_dir = site_data_dir
        
        if not os.path.exists(self.output_dir): os.makedirs(self.output_dir)
        if not os.path.exists(self.site_data_dir): os.makedirs(self.site_data_dir)

    def save_daily_brief(self, date_obj, clusters_content, mechanism_content):
        """Saves the main unified post."""
        date_str = date_obj.strftime("%Y-%m-%d")
        display_date = date_obj.strftime("%d %B %Y")
        
        # Frontmatter
        md = f"""---
title: "Analisi: {display_date}"
date: {date_str}
layout: post
categories: [brief]
---
"""
        # 1. Meccanismi Section (Top)
        if mechanism_content:
            md += f"""
<div class="mechanism-section">
    <h2 class="section-title">L'EDITORIALE</h2>
    <div class="editorial-text">
{mechanism_content}
    </div>
</div>
"""

        # 2. Clusters (The Feed)
        md += '\n<div class="feed-section">\n<h2 class="section-title">IL FEED STRATEGICO</h2>\n<div class="feed-grid">\n'
        for cluster_name, content in clusters_content.items():
            if content:
                # Wrap each cluster in a card
                md += f"\n<div class=\"feed-cluster\">\n<div class=\"cluster-header\">{cluster_name}</div>\n\n{content}\n</div>\n"
        md += '\n</div>\n</div>\n'

        filename = os.path.join(self.output_dir, f"{date_str}-brief.md")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(md)
        return filename

    def save_ticker_data(self, headlines):
        """Saves headlines.json for the frontend ticker."""
        path = os.path.join(self.site_data_dir, "headlines.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(headlines, f, ensure_ascii=False)
    
    def save_tensions_map(self, geojson_data):
        """Saves tensions.json for the map."""
        path = os.path.join(self.site_data_dir, "tensions.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(geojson_data, f, ensure_ascii=False)
