import os
import time
from openai import OpenAI
import yfinance as yf
import json
import re
from bs4 import BeautifulSoup

class ContentAnalyzer:
    def __init__(self):
        # Setup Groq and Z.ai (ZhipuAI)
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.zai_key = os.environ.get("XAI_API_KEY") # User saved Z.ai key in XAI_API_KEY
        
        self.groq_client = OpenAI(api_key=self.groq_key, base_url="https://api.groq.com/openai/v1") if self.groq_key else None
        self.zai_client = OpenAI(api_key=self.zai_key, base_url="https://open.bigmodel.cn/api/paas/v4/") if self.zai_key else None

    def analyze_cluster_groq(self, cluster_name, items):
        """Uses Groq for massive context analysis of a cluster."""
        if not items: return None
        if not self.groq_client: return None
        
        # Prepare context (Optimized string concatenation)
        context_parts = []
        for item in items:
            context_parts.append(f"SOURCE: {item['source']}\nTITLE: {item['title']}\nLINK: {item['link']}\nCONTENT: {item['content']}\n\n---\n\n")
        context_text = "".join(context_parts)
        
        prompt = f"""
        ACT AS: Senior Tech Intelligence Analyst for 'Il Polimate'.
        SECTOR: {cluster_name}
        
        OBJECTIVE: Analyze the provided news items and generate a High-Density Intelligence Report, strictly prioritizing tier-0, -1, and -2 sources and true breakthroughs.
        
        INPUT DATA: {len(items)} source items.
        
        INSTRUCTIONS:
        1. Scan ALL items and rigorously discard noise.
        2. Identify the top 3-4 most significant technical or strategic developments that represent real steps forward compared to traditional news.
        3. For each development, write a structured HTML block (NO MARKDOWN).
        
        BLOCK FORMAT (Strict HTML):
        <div class="news-item">
            <h3>[Italian Title, Elegante & Impattante]</h3>
            <p>[Body: 3-4 sentences in elegant, astute, cultured Italian. Focus on the core mechanism and strategic implication. Not too verbose.]</p>
            <p class="source-link"><a href="Current_Link_From_Input" target="_blank">Fonte: Source Name</a></p>
        </div>
        
        CRITICAL RULES:
        - MANDA IN OUTPUT SOLO LINGUA ITALIANA. TUTTO IL TESTO, I TITOLI E LE DESCRIZIONI DEVONO ESSERE IN ITALIANO PERFETTO.
        - Output ONLY pure HTML. Do NOT include <a </div> typo. Ensure all tags are correctly closed.
        """

        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"DATA:\n{context_text}"}
                ],
                temperature=0.2,
                max_tokens=3000
            )
            raw_html = response.choices[0].message.content
            
            # 1. Regex Fix for Groq hallucinated unclosed A tag typos 
            raw_html = re.sub(r'<\s*a\s*</div\s*>', '</a></div>', raw_html)
            raw_html = raw_html.replace("<a </div>", "</a></div>")
            
            # 2. Sanitize and fix broken HTML tags using BeautifulSoup
            soup = BeautifulSoup(raw_html, "html.parser")
            
            # For each news-item, ensure it's not nested inside another news-item due to missing closing divs
            clean_html_parts = []
            for item in soup.find_all('div', class_='news-item', recursive=False):
                clean_html_parts.append(str(item) + "\n")
            clean_html = "".join(clean_html_parts)
                
            # If the above fails to find top-level news-items, fallback to full soup
            if not clean_html.strip():
                clean_html = str(soup)
                
            return clean_html
            
        except Exception as e:
            print(f"Groq Error on {cluster_name}: {e}")
            return None

    def analyze_mechanism_daily(self, all_items_context):
        """Generates the 'Meccanismi' daily editorial."""
        # Use Z.ai (ZhipuAI) if available to handle the massive context window (128k)
        client = self.zai_client if self.zai_client else self.groq_client
        model_name = "glm-4-flash" if self.zai_client else "llama-3.1-8b-instant"
        
        if not client: return None
        
        # If falling back to Groq, cap tightly to avoid rate limits. Z.ai can take more.
        limit = 80000 if self.zai_client else 15000 
        context_sample = all_items_context[:limit]
        
        prompt = """
        ACT AS: Systemic Editor for 'Il Polimate'.
        TASK: Tra TUTTI i dati forniti, individua l'UNICA notizia o il singolo macro-trend più scottante, dirompente e importante in assoluto a livello globale (priorità a breakthrough da fonti tier 0, -1, -2).
        Scrivi l'editoriale quotidiano da prima pagina 'Meccanismi' basandoti ESCLUSIVAMENTE su questo singolo tema centrale.
        
        PHILOSOPHY: L'analisi deve essere acuta, scaltra, colta ed erudita, ma mai inutilmente verbosa. Spiega i legami profondi tra geopolitica, tecnologia, economia e l'impatto di questa notizia.
        
        STRUCTURE:
        Scrivi il Titolo Elegante e d'Impatto in grassetto o come Header Markdown, seguito dal Sottotitolo.
        ASSOLUTAMENTE VIETATO scrivere testualmente le parole "TITOLO:" o "Sottotitolo:". Inizia direttamente con il vero titolo testuale.
        
        Scrivi 3-4 paragrafi fluidi (senza bullet points).
        
        OUTPUT: Markdown formatted per il testo (paragrafi semplici, grassetti dove serve). Stile giornalistico d'alto livello. Italiano.
        """
        
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"GLOBAL CONTEXT:\n{context_sample}"}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Mechanism Editor Error ({model_name}): {e}")
            return None

    def translate_ultima_ora(self, items):
        """Translates both titles and contents of the breaking news items to Italian."""
        client = self.zai_client if self.zai_client else self.groq_client
        model_name = "glm-4-flash" if self.zai_client else "llama-3.1-8b-instant"
        
        if not client or not items: return items
        
        # Batch translation to avoid token limits per request
        batch_size = 20  # Reduced batch size since we're translating more content
        for i in range(0, len(items), batch_size):
            batch = items[i:i+batch_size]
            payload_dict = {
                str(idx): {"title": item.get('title', ''), "content": item.get('content', '')[:1000]} # Cap content length
                for idx, item in enumerate(batch)
            }
            
            prompt = """
            Traduci tutti i campi 'title' e 'content' dei seguenti oggetti JSON dall'inglese (o altra lingua) all'Italiano perfetto, giornalistico e conciso.
            Restituisci ESATTAMENTE E SOLO lo stesso dizionario JSON, mantenendo le stesse chiavi numeriche, e dove i valori 'title' e 'content' sono tradotti in italiano in modo eccellente.
            Non aggiungere commenti o backtick code blocks come ```json, solo l'oggetto JSON puro. Assicurati che le virgolette interne siano encodate correttamente (escaped) per non rompere il JSON.
            """
            
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": json.dumps(payload_dict)}
                    ],
                    temperature=0.1
                )
                raw_text = response.choices[0].message.content.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text.replace("```json", "", 1).replace("```", "").strip()
                elif raw_text.startswith("```"):
                    raw_text = raw_text.replace("```", "", 1).replace("```", "").strip()
                    
                translated_dict = json.loads(raw_text)
                for key, translated_obj in translated_dict.items():
                    idx = int(key)
                    if 0 <= idx < len(batch) and isinstance(translated_obj, dict):
                        if 'title' in translated_obj:
                            batch[idx]['title'] = translated_obj['title']
                        if 'content' in translated_obj:
                            batch[idx]['content'] = translated_obj['content']
            except Exception as e:
                print(f"Translation Error ({model_name}): {e}")
                
        return items

    def generate_ticker_headlines(self, items):
        """Uses yfinance for fast, free market data generation."""
        symbols = {
            "S&P 500": "^GSPC",
            "Nasdaq": "^IXIC",
            "Oro": "GC=F",
            "Petrolio WTI": "CL=F",
            "EUR/USD": "EURUSD=X",
            "Bitcoin": "BTC-USD"
        }
        
        market_headlines = []
        try:
            for name, symbol in symbols.items():
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                if len(hist) >= 2:
                    last_close = hist['Close'].iloc[-2]
                    current = hist['Close'].iloc[-1]
                    change = ((current - last_close) / last_close) * 100
                    sign = "+" if change > 0 else ""
                    headline = f"{name} ({symbol}): {current:.2f} ({sign}{change:.2f}%)"
                    market_headlines.append(headline)
                elif len(hist) == 1:
                    current = hist['Close'].iloc[-1]
                    headline = f"{name} ({symbol}): {current:.2f}"
                    market_headlines.append(headline)
                    
            if not market_headlines:
                return ["Mercati chiusi o dati temporaneamente non disponibili."]
            return market_headlines
            
        except Exception as e:
            print(f"yfinance Ticker Error: {e}")
            return ["Dati mercati finanziari momentaneamente non disponibili."]

    def analyze_tensions_map(self, all_items_context):
        """Generates GeoJSON data for the Map of Tensions."""
        client = self.zai_client if self.zai_client else self.groq_client
        model_name = "glm-4-flash" if self.zai_client else "llama-3.1-8b-instant"
        
        if not client: return {"type": "FeatureCollection", "features": []}
        
        limit = 80000 if self.zai_client else 15000 
        
        prompt = """
        TASK: Extract "Tension Events" for a Geopolitical Map.
        
        CATEGORIES:
        - CONFLICT (Red)
        - PROTEST (Orange)
        - INFRASTRUCTURE_CRITICAL (Purple)
        - BORDER_DISPUTE (Grey)
        - DISASTER_NATURAL (Yellow)
        
        OUTPUT: JSON Object with a 'features' list. Note: WE WILL ADD GEOJSON GEOMETRY LATER.
        Each feature must have:
        - type: "Feature"
        - properties: {
            category: "CONFLICT",
            title: "Brief Title",
            description: "Technical description",
            intensity: 1-10,
            location_name: "Exact City, Country"
          }
        
        EXTREME CRITICAL INSTRUCTIONS: 
        1. Extract ALL distinct tension events (conflicts, protests, natural disasters, infrastructural issues) from the provided text. BE HYPER LOCAL AND GRANULAR. Do NOT invent events that are not in the text.
        2. DO NOT GROUP EVENTS. A protest in Paris and a protest in Lyon are TWO separate events. An earthquake in Tokyo and one in Kyoto are TWO events.
        3. Search for EVERY military incident, EVERY protest, EVERY hack, EVERY diplomatic friction, EVERY infrastructure issue, EVERY natural disaster (earthquakes, floods, etc).
        4. Extract the EXACT location name (e.g. "Kyiv, Ukraine", "Paris, France"). Do not invent coordinates. Put it in `location_name`.
        5. DO NOT REPEAT THE SAME EVENT MULTIPLE TIMES. Each feature must be a distinct physical event.
        """
        
        try:
            kwargs = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"NEWS DATA:\n{all_items_context[:limit]}"}
                ],
                "temperature": 0.1
            }
            if not self.zai_client:
                kwargs["response_format"] = {"type": "json_object"}
                
            response = client.chat.completions.create(**kwargs)
            raw_text = response.choices[0].message.content.strip()
            
            if raw_text.startswith("```json"):
                raw_text = raw_text.replace("```json", "", 1)
            if raw_text.endswith("```"):
                raw_text = raw_text[:raw_text.rfind("```")]
            raw_text = raw_text.strip()
                
            data = json.loads(raw_text)

            # Geocode the locations
            from geopy.geocoders import Nominatim
            from geopy.exc import GeocoderTimedOut
            import time as geopy_time

            geolocator = Nominatim(user_agent="ilpolimate_map_updater")

            if "features" in data:
                valid_features = []
                for f in data["features"]:
                    loc_name = f.get("properties", {}).get("location_name")
                    if loc_name:
                        try:
                            geopy_time.sleep(1) # Respect Nominatim rate limit
                            location = geolocator.geocode(loc_name)
                            if location:
                                f["geometry"] = {
                                    "type": "Point",
                                    "coordinates": [location.longitude, location.latitude]
                                }
                                valid_features.append(f)
                            else:
                                print(f"Could not geocode location: {loc_name}")
                        except Exception as geo_e:
                            print(f"Geocoding error for {loc_name}: {geo_e}")
                data["features"] = valid_features

            return data

        except Exception as e:
            print(f"Map Generation Error ({model_name}): {e}")
            return {"type": "FeatureCollection", "features": []}
