import os
import time
from openai import OpenAI
import yfinance as yf
import json
from bs4 import BeautifulSoup

class ContentAnalyzer:
    def __init__(self):
        # Setup Groq and x.ai (Grok)
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.xai_key = os.environ.get("XAI_API_KEY")
        
        self.groq_client = OpenAI(api_key=self.groq_key, base_url="https://api.groq.com/openai/v1") if self.groq_key else None
        self.xai_client = OpenAI(api_key=self.xai_key, base_url="https://api.x.ai/v1") if self.xai_key else None

    def analyze_cluster_groq(self, cluster_name, items):
        """Uses Groq for massive context analysis of a cluster."""
        if not items: return None
        if not self.groq_client: return None
        
        # Prepare context
        context_text = ""
        for item in items:
            context_text += f"SOURCE: {item['source']}\nTITLE: {item['title']}\nLINK: {item['link']}\nCONTENT: {item['content']}\n\n---\n\n"
        
        prompt = f"""
        ACT AS: Senior Tech Intelligence Analyst for 'Il Polimate'.
        SECTOR: {cluster_name}
        
        OBJECTIVE: Analyze the provided news items and generate a High-Density Intelligence Report.
        
        INPUT DATA: {len(items)} source items.
        
        INSTRUCTIONS:
        1. Scan ALL items.
        2. Identify the top 2-3 most significant technical or strategic developments.
        3. For each development, write a structured HTML block (NO MARKDOWN).
        
        BLOCK FORMAT (Strict HTML):
        <div class="news-item">
            <h3>[Italian Title, Elegante & Impattante]</h3>
            <p>[Body: 3-4 sentences in elegant, astute, cultured Italian. Focus on the core mechanism and implication. Not too verbose.]</p>
            <p class="source-link"><a href="Current_Link_From_Input" target="_blank">Fonte: Source Name</a></p>
        </div>
        
        CRITICAL RULES:
        - Strict Italian Language.
        - TONE: Elegant, astute, cultured, analytical. Not overly verbose.
        - Merge duplicate stories.
        - Output ONLY HTML, without markdown code fences like ```html.
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
            
            # Sanitize and fix broken HTML tags using BeautifulSoup
            soup = BeautifulSoup(raw_html, "html.parser")
            return str(soup)
            
        except Exception as e:
            print(f"Groq Error on {cluster_name}: {e}")
            return None

    def analyze_mechanism_daily(self, all_items_context):
        """Generates the 'Meccanismi' daily editorial."""
        # Use xAI (Grok) if available to handle the massive context window (128k)
        client = self.xai_client if self.xai_client else self.groq_client
        model_name = "grok-beta" if self.xai_client else "llama-3.1-8b-instant"
        
        if not client: return None
        
        # If falling back to Groq, cap tightly to avoid rate limits. xAI can take more.
        limit = 80000 if self.xai_client else 15000 
        context_sample = all_items_context[:limit]
        
        prompt = """
        ACT AS: Systemic Editor for 'Il Polimate'.
        TASK: Seleziona la notizia o il macro-trend più importante in assoluto a livello globale tra quelli forniti, e scrivi l'editoriale da prima pagina 'Meccanismi'.
        
        PHILOSOPHY: L'analisi deve essere acuta, scaltra, colta ed erudita, ma mai inutilmente verbosa. Spiega i legami profondi tra geopolitica, tecnologia ed economia.
        
        STRUCTURE:
        TITOLO: [Titolo Elegante e d'Impatto] - [Sottotitolo]
        
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
                    # We store symbol ID inside the text to extract it in JS for Google Finance link
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
        client = self.xai_client if self.xai_client else self.groq_client
        model_name = "grok-beta" if self.xai_client else "llama-3.1-8b-instant"
        
        if not client: return {"type": "FeatureCollection", "features": []}
        
        limit = 80000 if self.xai_client else 15000 
        
        prompt = """
        TASK: Extract "Tension Events" for a Geopolitical Map.
        
        CATEGORIES:
        - CONFLICT (Red)
        - PROTEST (Orange)
        - INFRASTRUCTURE_CRITICAL (Purple)
        - BORDER_DISPUTE (Grey)
        
        OUTPUT: JSON Object with a 'features' list (GeoJSON style).
        Each feature must have:
        - type: "Feature"
        - geometry: {type: "Point", coordinates: [lon, lat]}
        - properties: {
            category: "CONFLICT",
            title: "Brief Title",
            description: "Technical description",
            intensity: 1-10
          }
        
        EXTRACT FROM DATA PROVIDED. IF NO LOCATION, SKIP.
        """
        
        try:
            # Note: grok-beta may not officially support response_format={"type": "json_object"} in the same way,
            # but usually formatting the prompt strictly works. We'll try it.
            kwargs = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"NEWS DATA:\n{all_items_context[:limit]}"}
                ],
                "temperature": 0.1
            }
            if not self.xai_client:
                kwargs["response_format"] = {"type": "json_object"}
                
            response = client.chat.completions.create(**kwargs)
            raw_text = response.choices[0].message.content.strip()
            
            if raw_text.startswith("```json"):
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            elif raw_text.startswith("```"):
                raw_text = raw_text.replace("```", "").strip()
                
            return json.loads(raw_text)
        except Exception as e:
            print(f"Map Generation Error ({model_name}): {e}")
            return {"type": "FeatureCollection", "features": []}
