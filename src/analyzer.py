import os
import time
from openai import OpenAI
import yfinance as yf
import json

class ContentAnalyzer:
    def __init__(self):
        # Setup Groq and x.ai (Grok)
        self.groq_key = os.environ.get("GROQ_API_KEY")
        
        self.groq_client = OpenAI(api_key=self.groq_key, base_url="https://api.groq.com/openai/v1") if self.groq_key else None

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
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq Error on {cluster_name}: {e}")
            return None

    def analyze_mechanism_daily(self, all_items_context):
        """Generates the 'Meccanismi' daily editorial."""
        if not self.groq_client: return None
        
        context_sample = all_items_context[:30000] # Cap safely within groq limits
        
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
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"GLOBAL CONTEXT:\n{context_sample}"}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq Mechanism Error: {e}")
            return None

    def generate_ticker_headlines(self, items):
        """Uses yfinance for fast, free market data generation."""
        # We don't need 'items' anymore for the ticker, we fetch market data instead.
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
                # Fetch history for last 2 days to calculate % change
                hist = ticker.history(period="2d")
                if len(hist) >= 2:
                    last_close = hist['Close'].iloc[-2]
                    current = hist['Close'].iloc[-1]
                    change = ((current - last_close) / last_close) * 100
                    sign = "+" if change > 0 else ""
                    headline = f"{name}: {current:.2f} ({sign}{change:.2f}%)"
                    market_headlines.append(headline)
                elif len(hist) == 1:
                    current = hist['Close'].iloc[-1]
                    headline = f"{name}: {current:.2f}"
                    market_headlines.append(headline)
                    
            if not market_headlines:
                return ["Mercati chiusi o dati temporaneamente non disponibili."]
            return market_headlines
            
        except Exception as e:
            print(f"yfinance Ticker Error: {e}")
            return ["Dati mercati finanziari momentaneamente non disponibili."]

    def analyze_tensions_map(self, all_items_context):
        """Generates GeoJSON data for the Map of Tensions using Groq."""
        if not self.groq_client: return {"type": "FeatureCollection", "features": []}
        
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
            # We specifically request JSON output
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"NEWS DATA:\n{all_items_context[:30000]}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            raw_text = response.choices[0].message.content.strip()
            # Safety checks in case output contains markdown blocks
            if raw_text.startswith("```json"):
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            return json.loads(raw_text)
        except Exception as e:
            print(f"Groq Map Error: {e}")
            return {"type": "FeatureCollection", "features": []}
