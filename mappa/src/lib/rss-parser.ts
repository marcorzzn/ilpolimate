import { XMLParser } from 'fast-xml-parser';
import type { NewsItem, RSSSource, NewsCategory, SeverityLevel, GeoLocation } from '@/types';

// RSS Sources configuration
export const RSS_SOURCES: RSSSource[] = [
  // Tier 1 - Wire Services
  { id: 'reuters-world', name: 'Reuters World', url: 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best', category: 'general', region: 'global', tier: 1, active: true },
  { id: 'ap-news', name: 'AP News', url: 'https://news.google.com/rss/search?q=when:24h+allinurl:apnews.com&hl=en-US&gl=US&ceid=US:en', category: 'general', region: 'global', tier: 1, active: true },
  
  // Tier 2 - Major Outlets
  { id: 'bbc-world', name: 'BBC World', url: 'https://feeds.bbci.co.uk/news/world/rss.xml', category: 'general', region: 'global', tier: 2, active: true },
  { id: 'guardian-world', name: 'Guardian World', url: 'https://www.theguardian.com/world/rss', category: 'general', region: 'global', tier: 2, active: true },
  { id: 'aljazeera', name: 'Al Jazeera', url: 'https://www.aljazeera.com/xml/rss/all.xml', category: 'general', region: 'mena', tier: 2, active: true },
  { id: 'france24', name: 'France24', url: 'https://www.france24.com/en/rss', category: 'general', region: 'europe', tier: 2, active: true },
  { id: 'dw-news', name: 'Deutsche Welle', url: 'https://rss.dw.com/rdf/rss-en-all', category: 'general', region: 'europe', tier: 2, active: true },
  
  // Specialized
  { id: 'defense-one', name: 'Defense One', url: 'https://www.defenseone.com/rss/all/', category: 'military', region: 'global', tier: 3, active: true },
  { id: 'crisis-group', name: 'Crisis Group', url: 'https://www.crisisgroup.org/rss.xml', category: 'conflict', region: 'global', tier: 3, active: true },
];

// Keyword patterns for classification
const CLASSIFICATION_PATTERNS: Record<NewsCategory, RegExp[]> = {
  conflict: [/\b(war|conflict|invasion|offensive|battle|fighting|clashes|airstrike|bombardment|artillery|frontline)\b/i],
  protest: [/\b(protest|demonstration|riot|unrest|rally|march|strike|demonstrator)\b/i],
  disaster: [/\b(earthquake|flood|hurricane|typhoon|wildfire|tsunami|volcano|landslide|tornado|cyclone)\b/i],
  politics: [/\b(election|vote|parliament|congress|senate|president|minister|legislature|policy)\b/i],
  economy: [/\b(economy|market|trade|inflation|gdp|recession|stock|currency|tariff|sanction)\b/i],
  military: [/\b(military|army|navy|air force|troops|soldiers|defense|missile|drone|naval)\b/i],
  terrorism: [/\b(terrorist|terrorism|attack|bombing|explosion|isis|al-qaeda|extremist)\b/i],
  health: [/\b(pandemic|epidemic|virus|disease|outbreak|health|hospital|vaccine|who)\b/i],
  environment: [/\b(climate|environment|emission|carbon|pollution|deforestation|biodiversity)\b/i],
  diplomacy: [/\b(diplomat|treaty|negotiation|summit|talks|peace|agreement|accord|delegation)\b/i],
  general: [],
};

// Country name mappings for geocoding
const COUNTRY_PATTERNS: Record<string, { lat: number; lng: number; code: string; region: string }> = {
  // Major conflict zones
  'ukraine': { lat: 48.3794, lng: 31.1656, code: 'UA', region: 'Europe' },
  'russia': { lat: 61.5240, lng: 105.3188, code: 'RU', region: 'Europe/Asia' },
  'israel': { lat: 31.0461, lng: 34.8516, code: 'IL', region: 'Middle East' },
  'gaza': { lat: 31.3547, lng: 34.3088, code: 'PS', region: 'Middle East' },
  'palestine': { lat: 31.9522, lng: 35.2332, code: 'PS', region: 'Middle East' },
  'syria': { lat: 34.8021, lng: 38.9968, code: 'SY', region: 'Middle East' },
  'yemen': { lat: 15.5527, lng: 48.5164, code: 'YE', region: 'Middle East' },
  'iran': { lat: 32.4279, lng: 53.6880, code: 'IR', region: 'Middle East' },
  'afghanistan': { lat: 33.9391, lng: 67.7100, code: 'AF', region: 'Asia' },
  'sudan': { lat: 12.8628, lng: 30.2176, code: 'SD', region: 'Africa' },
  'myanmar': { lat: 21.9162, lng: 95.9560, code: 'MM', region: 'Asia' },
  'haiti': { lat: 18.9712, lng: -72.2852, code: 'HT', region: 'Americas' },
  'ethiopia': { lat: 9.1450, lng: 40.4897, code: 'ET', region: 'Africa' },
  'somalia': { lat: 5.1521, lng: 46.1996, code: 'SO', region: 'Africa' },
  'congo': { lat: -4.0383, lng: 21.7587, code: 'CD', region: 'Africa' },
  'drc': { lat: -4.0383, lng: 21.7587, code: 'CD', region: 'Africa' },
  'libya': { lat: 26.3351, lng: 17.2283, code: 'LY', region: 'Africa' },
  'mali': { lat: 17.5707, lng: -3.9962, code: 'ML', region: 'Africa' },
  'nigeria': { lat: 9.0820, lng: 8.6753, code: 'NG', region: 'Africa' },
  'taiwan': { lat: 23.6978, lng: 120.9605, code: 'TW', region: 'Asia' },
  'china': { lat: 35.8617, lng: 104.1954, code: 'CN', region: 'Asia' },
  'north korea': { lat: 40.3399, lng: 127.5101, code: 'KP', region: 'Asia' },
  'south korea': { lat: 35.9078, lng: 127.7669, code: 'KR', region: 'Asia' },
  'india': { lat: 20.5937, lng: 78.9629, code: 'IN', region: 'Asia' },
  'pakistan': { lat: 30.3753, lng: 69.3451, code: 'PK', region: 'Asia' },
  'iraq': { lat: 33.2232, lng: 43.6793, code: 'IQ', region: 'Middle East' },
  'lebanon': { lat: 33.8547, lng: 35.8623, code: 'LB', region: 'Middle East' },
  'venezuela': { lat: 6.4238, lng: -66.5897, code: 'VE', region: 'Americas' },
  'usa': { lat: 37.0902, lng: -95.7129, code: 'US', region: 'Americas' },
  'united states': { lat: 37.0902, lng: -95.7129, code: 'US', region: 'Americas' },
  'france': { lat: 46.2276, lng: 2.2137, code: 'FR', region: 'Europe' },
  'germany': { lat: 51.1657, lng: 10.4515, code: 'DE', region: 'Europe' },
  'uk': { lat: 55.3781, lng: -3.4360, code: 'GB', region: 'Europe' },
  'united kingdom': { lat: 55.3781, lng: -3.4360, code: 'GB', region: 'Europe' },
  'japan': { lat: 36.2048, lng: 138.2529, code: 'JP', region: 'Asia' },
  'turkey': { lat: 38.9637, lng: 35.2433, code: 'TR', region: 'Europe/Asia' },
  'turkiye': { lat: 38.9637, lng: 35.2433, code: 'TR', region: 'Europe/Asia' },
};

const parser = new XMLParser({
  ignoreAttributes: false,
  attributeNamePrefix: '@_',
});

// Classify news by category
export function classifyNews(title: string, description: string): NewsCategory {
  const text = `${title} ${description}`.toLowerCase();
  
  for (const [category, patterns] of Object.entries(CLASSIFICATION_PATTERNS)) {
    if (category === 'general') continue;
    for (const pattern of patterns) {
      if (pattern.test(text)) {
        return category as NewsCategory;
      }
    }
  }
  return 'general';
}

// Calculate severity based on content
export function calculateSeverity(title: string, description: string, category: NewsCategory): SeverityLevel {
  const text = `${title} ${description}`.toLowerCase();
  
  // Critical keywords
  if (/\b(killed|death toll|massacre|casualties|war|invasion|nuclear)\b/i.test(text)) return 5;
  if (/\b(explosion|bombing|attack|airstrike|missile|terrorist)\b/i.test(text)) return 4;
  if (/\b(clashes|fighting|protest|riot|earthquake|flood)\b/i.test(text)) return 3;
  if (/\b(tension|concern|warning|dispute|sanctions)\b/i.test(text)) return 2;
  
  // Category-based severity
  if (category === 'conflict' || category === 'terrorism') return 4;
  if (category === 'military' || category === 'disaster') return 3;
  if (category === 'protest') return 3;
  
  return 2;
}

// Extract location from text
export function extractLocation(title: string, description: string): GeoLocation | null {
  const text = `${title} ${description}`.toLowerCase();
  
  for (const [country, data] of Object.entries(COUNTRY_PATTERNS)) {
    const pattern = new RegExp(`\\b${country.replace(/\s+/g, '\\s+')}\\b`, 'i');
    if (pattern.test(text)) {
      return {
        lat: data.lat,
        lng: data.lng,
        country: country.charAt(0).toUpperCase() + country.slice(1),
        countryCode: data.code,
        region: data.region,
      };
    }
  }
  return null;
}

// Extract keywords from text
export function extractKeywords(title: string, description: string): string[] {
  const text = `${title} ${description}`;
  const keywords: string[] = [];
  
  // Extract named entities (simplified)
  const entityPatterns = [
    /\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b/g, // Capitalized words
    /\b(NATO|UN|EU|WHO|OSCE|ASEAN|G7|G20)\b/g, // Organizations
    /\b(Putin|Biden|Xi|Trump|Zelensky|Netanyahu|Khamenei|Kim Jong Un)\b/gi, // Leaders
  ];
  
  for (const pattern of entityPatterns) {
    const matches = text.match(pattern);
    if (matches) {
      keywords.push(...matches.slice(0, 5));
    }
  }
  
  return [...new Set(keywords)].slice(0, 10);
}

// Analyze sentiment
export function analyzeSentiment(title: string, description: string): 'positive' | 'negative' | 'neutral' {
  const text = `${title} ${description}`.toLowerCase();
  
  const negativeWords = ['war', 'death', 'kill', 'attack', 'crisis', 'collapse', 'threat', 'danger', 'conflict', 'violence', 'casualty', 'victim'];
  const positiveWords = ['peace', 'agreement', 'deal', 'progress', 'success', 'recovery', 'hope', 'relief', 'ceasefire', 'truce'];
  
  let negativeCount = 0;
  let positiveCount = 0;
  
  for (const word of negativeWords) {
    if (text.includes(word)) negativeCount++;
  }
  
  for (const word of positiveWords) {
    if (text.includes(word)) positiveCount++;
  }
  
  if (negativeCount > positiveCount + 1) return 'negative';
  if (positiveCount > negativeCount + 1) return 'positive';
  return 'neutral';
}

// Parse single RSS feed
export async function parseRSSFeed(source: RSSSource): Promise<NewsItem[]> {
  try {
    const response = await fetch(source.url, {
      headers: {
        'User-Agent': 'ConflictMap/1.0 News Aggregator',
        'Accept': 'application/rss+xml, application/xml, text/xml',
      },
      signal: AbortSignal.timeout(10000),
    });
    
    if (!response.ok) {
      console.error(`Failed to fetch ${source.name}: ${response.status}`);
      return [];
    }
    
    const xml = await response.text();
    const parsed = parser.parse(xml);
    
    const items: NewsItem[] = [];
    const rssItems = parsed.rss?.channel?.item || parsed.feed?.entry || [];
    const itemsArray = Array.isArray(rssItems) ? rssItems : [rssItems];
    
    for (const item of itemsArray.slice(0, 20)) {
      const title = item.title || '';
      const description = item.description || item.summary || '';
      const link = item.link || item.url || '';
      const pubDate = item.pubDate || item.published || item.updated || new Date().toISOString();
      
      if (!title) continue;
      
      const category = classifyNews(title, description);
      const severity = calculateSeverity(title, description, category);
      const location = extractLocation(title, description);
      const keywords = extractKeywords(title, description);
      const sentiment = analyzeSentiment(title, description);
      
      const publishedAt = new Date(pubDate);
      const isNew = Date.now() - publishedAt.getTime() < 3600000; // 1 hour
      
      items.push({
        id: Buffer.from(`${source.id}-${title}`).toString('base64').slice(0, 16),
        title: title.replace(/<[^>]*>/g, '').trim(),
        description: description.replace(/<[^>]*>/g, '').trim().slice(0, 300),
        link: typeof link === 'string' ? link : link?.href || '',
        source: source.name,
        publishedAt: publishedAt.toISOString(),
        category,
        severity,
        location,
        keywords,
        sentiment,
        isNew,
      });
    }
    
    return items;
  } catch (error) {
    console.error(`Error parsing ${source.name}:`, error);
    return [];
  }
}

// Fetch all RSS feeds
export async function fetchAllFeeds(sources: RSSSource[] = RSS_SOURCES.filter(s => s.active)): Promise<NewsItem[]> {
  const results = await Promise.allSettled(
    sources.map(source => parseRSSFeed(source))
  );
  
  const allItems = results
    .filter((r): r is PromiseFulfilledResult<NewsItem[]> => r.status === 'fulfilled')
    .flatMap(r => r.value);
  
  // Sort by publication date
  allItems.sort((a, b) => 
    new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()
  );
  
  // Deduplicate by title similarity
  const uniqueItems: NewsItem[] = [];
  for (const item of allItems) {
    const isDuplicate = uniqueItems.some(existing => {
      const similarity = calculateSimilarity(existing.title, item.title);
      return similarity > 0.7;
    });
    if (!isDuplicate) {
      uniqueItems.push(item);
    }
  }
  
  return uniqueItems;
}

// Calculate Jaccard similarity
function calculateSimilarity(a: string, b: string): number {
  const wordsA = new Set(a.toLowerCase().split(/\s+/));
  const wordsB = new Set(b.toLowerCase().split(/\s+/));
  
  const intersection = new Set([...wordsA].filter(x => wordsB.has(x)));
  const union = new Set([...wordsA, ...wordsB]);
  
  return intersection.size / union.size;
}
