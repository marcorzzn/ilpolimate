import os
import datetime
import json
import markdown

class ReportGenerator:
    def __init__(self, output_dir="_posts", site_data_dir="assets/data", audio_dir="assets/audio"):
        self.output_dir = output_dir
        self.site_data_dir = site_data_dir
        self.audio_dir = audio_dir
        
        if not os.path.exists(self.output_dir): os.makedirs(self.output_dir)
        if not os.path.exists(self.site_data_dir): os.makedirs(self.site_data_dir)
        if not os.path.exists(self.audio_dir): os.makedirs(self.audio_dir)

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
            # Generate Audio
            try:
                # Convert Markdown Editorial to HTML
                mechanism_html = markdown.markdown(mechanism_content)
                
                audio_html = f'''
                <div style="margin-top: 15px; margin-bottom: 25px; text-align: center; width: 100%;">
                    <button id="edPlayBtn" style="font-family: 'Inter', sans-serif; font-weight: 600; padding: 10px 20px; border: 1px solid #111; border-radius: 30px; cursor: pointer; background: #111; color: #fff; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; transition: all 0.2s;">
                        <i class="fas fa-play" style="margin-right: 8px;"></i> Ascolta l'Editoriale
                    </button>
                    <button id="edStopBtn" style="display: none; font-family: 'Inter', sans-serif; font-weight: 600; padding: 10px 20px; border: 1px solid #d00; border-radius: 30px; cursor: pointer; background: #fff; color: #d00; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; transition: all 0.2s; margin-left:10px;">
                        <i class="fas fa-stop"></i> Ferma
                    </button>
                </div>
                '''
            except Exception as e:
                print(f"HTML Generation Error: {e}")
                audio_html = ""

            md += f"""
<div class="mechanism-section">
    <h2 class="section-title">L'EDITORIALE</h2>
    {audio_html}
    <div class="editorial-text">
{mechanism_html}
    </div>
</div>
"""

        # 2. Clusters (The Feed)
        md += '\n<div class="feed-section">\n<div class="feed-grid">\n'
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
