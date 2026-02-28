import os
import datetime
import json
import re
from gtts import gTTS

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
        display_date = date_obj.strftime("%d %B %Y")
        
        # Frontmatter
        md = f"""---
title: "La rassegna del giorno - {display_date}"
date: {date_str}
layout: post
categories: [brief]
---
"""
        # 1. Meccanismi Section (Top)
        if mechanism_content:
            # Generate Audio
            audio_filename = f"{date_str}-audio.mp3"
            audio_path = os.path.join(self.audio_dir, audio_filename)
            try:
                # Clean text for TTS
                clean_text = re.sub('<[^<]+?>', '', mechanism_content) # Remove HTML
                clean_text = re.sub(r'[*#_]', '', clean_text) # Remove common Markdown
                
                tts = gTTS(text=clean_text, lang='it', slow=False)
                tts.save(audio_path)
                
                audio_html = f'''
                <div style="margin-top: 20px; text-align: center; border: 1px solid #eaeaea; padding: 15px; border-radius: 8px; background: #fff;">
                    <div style="font-family: 'Inter', sans-serif; font-size: 0.85rem; text-transform: uppercase; color: #555; margin-bottom: 10px; letter-spacing: 1px;">
                        <i class="fas fa-headphones" style="margin-right: 5px;"></i> Ascolta l'Editoriale
                    </div>
                    <audio controls style="width: 100%; max-width: 400px;">
                        <source src="/assets/audio/{audio_filename}" type="audio/mpeg">
                        Il tuo browser non supporta l'elemento audio.
                    </audio>
                </div>
                '''
            except Exception as e:
                print(f"Audio Generation Error: {e}")
                audio_html = ""

            md += f"""
<div class="mechanism-section">
    <h2 class="section-title">L'EDITORIALE</h2>
    <div class="editorial-text">
{mechanism_content}
    </div>
    {audio_html}
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
