import os
import datetime
import json
import markdown

class ReportGenerator:
    def __init__(self, output_dir="_posts", site_data_dir="assets/data"):
        self.output_dir = output_dir
        self.site_data_dir = site_data_dir
        
        if not os.path.exists(self.output_dir): os.makedirs(self.output_dir)
        if not os.path.exists(self.site_data_dir): os.makedirs(self.site_data_dir)

    def save_daily_brief(self, date_obj, clusters_content, mechanism_content):
        """Saves the main unified post."""
        date_str = date_obj.strftime("%Y-%m-%d")
        mesi = ["", "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
        display_date = f"{date_obj.day} {mesi[date_obj.month]} {date_obj.year}"
        
        # Frontmatter
        md = f"""---
title: "La rassegna del {display_date}"
date: {date_str}
layout: post
categories: [brief]
---
"""
        # 1. Meccanismi Section (Top)
        if mechanism_content:
            try:
                # Convert Markdown Editorial to HTML
                mechanism_html = markdown.markdown(mechanism_content)
            except Exception as e:
                print(f"HTML Generation Error: {e}")
                mechanism_html = mechanism_content

            md += f"""
<div class="mechanism-section">
    <h2 class="section-title">L'EDITORIALE</h2>
    <div class="editorial-text">
{mechanism_html}
    </div>
</div>
"""

        # 2. Clusters (The Feed)
        md_parts = [md, '\n<div class="feed-section">\n<div class="feed-grid">\n']
        for cluster_name, content in clusters_content.items():
            if content:
                # Wrap each cluster in a card
                md_parts.append(f"\n<div class=\"feed-cluster\">\n<div class=\"cluster-header\">{cluster_name}</div>\n\n{content}\n</div>\n")
        md_parts.append('\n</div>\n</div>\n')

        md = "".join(md_parts)
        md = "".join(md_parts)
        final_md = "".join(md_parts)

        filename = os.path.join(self.output_dir, f"{date_str}-brief.md")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(final_md)
        return filename

    def save_ticker_data(self, headlines):
        """Saves headlines.json for the frontend ticker."""
        path = os.path.join(self.site_data_dir, "headlines.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(headlines, f, ensure_ascii=False)
    
    def save_tensions_map(self, geojson_data, date_obj=None):
        """Saves tensions.json for the map with history."""
        if date_obj is None:
            date_obj = datetime.datetime.now()
            
        path = os.path.join(self.site_data_dir, "tensions.json")
        date_str = date_obj.strftime("%Y-%m-%d")
        
        history = {}
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    history = json.load(f)
                    
                    if "type" in history and history["type"] == "FeatureCollection":
                        # Convert old format to new format using today's date
                        history = {date_str: history}
            except Exception:
                pass
                
        history[date_str] = geojson_data
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False)
