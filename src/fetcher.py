import feedparser
import concurrent.futures
import datetime

class FeedFetcher:
    def __init__(self, lookback_hours=24, max_workers=20):
        self.lookback_hours = lookback_hours
        self.max_workers = max_workers
        self.user_agent = "Mozilla/5.0 (PolimateBot/4.0; +http://ilpolimate.com)"

    def fetch_feed(self, url):
        try:
            d = feedparser.parse(url, agent=self.user_agent)
            items = []
            now = datetime.datetime.now(datetime.timezone.utc)
            cutoff = now - datetime.timedelta(hours=self.lookback_hours)
            
            source_name = d.feed.get('title', 'Unknown Source')

            for entry in d.entries:
                # 1. Date Parsing Strategy
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime.datetime(*entry.updated_parsed[:6], tzinfo=datetime.timezone.utc)
                
                # 2. Filtering
                if not pub_date or pub_date > cutoff:
                    # Content Extraction
                    content = "No content"
                    if hasattr(entry, 'summary'): content = entry.summary
                    elif hasattr(entry, 'content'): content = entry.content[0].value
                    elif hasattr(entry, 'description'): content = entry.description
                    
                    # Cleanup
                    content = self._clean_html(content)
                    
                    items.append({
                        "source": source_name,
                        "title": entry.title,
                        "link": entry.link,
                        "published": pub_date,
                        "content": content[:3000] # Cap content per item
                    })
            return items
        except Exception as e:
            # print(f"Error fetching {url}: {e}") # Silent fail to avoid log spam
            return []

    def _clean_html(self, text):
        # Basic cleanup, can be improved with BeautifulSoup if heavy HTML
        text = text.replace("<p>", "").replace("</p>", "\n")
        text = text.replace("<div>", "").replace("</div>", "")
        text = text.replace("<br>", "\n").replace("<br/>", "\n")
        # Remove massive whitespace
        return "\n".join([line.strip() for line in text.splitlines() if line.strip()])

    def get_cluster_data(self, urls):
        all_items = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self.fetch_feed, url): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                data = future.result()
                all_items.extend(data)
        
        # Deduplication by link
        unique_items = {item['link']: item for item in all_items}.values()
        return list(unique_items)
