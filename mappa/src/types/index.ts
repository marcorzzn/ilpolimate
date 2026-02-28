// Types for the Conflict Map Dashboard

export interface NewsItem {
  id: string;
  title: string;
  description: string;
  link: string;
  source: string;
  publishedAt: string;
  category: NewsCategory;
  severity: SeverityLevel;
  location: GeoLocation | null;
  keywords: string[];
  sentiment: 'positive' | 'negative' | 'neutral';
  isNew: boolean;
}

export interface GeoLocation {
  lat: number;
  lng: number;
  country: string;
  countryCode: string;
  region: string;
}

export type NewsCategory = 
  | 'conflict'
  | 'protest'
  | 'disaster'
  | 'politics'
  | 'economy'
  | 'military'
  | 'terrorism'
  | 'health'
  | 'environment'
  | 'diplomacy'
  | 'general';

export type SeverityLevel = 1 | 2 | 3 | 4 | 5;

export interface ConflictZone {
  id: string;
  name: string;
  country: string;
  countryCode: string;
  lat: number;
  lng: number;
  type: 'war' | 'insurgency' | 'territorial' | 'civil' | 'international';
  status: 'active' | 'frozen' | 'escalating' | 'de_escalating';
  intensity: SeverityLevel;
  casualties: number | null;
  startDate: string;
  lastUpdate: string;
  description: string;
  involvedParties: string[];
  newsCount: number;
}

export interface MapMarker {
  id: string;
  type: 'conflict' | 'protest' | 'disaster' | 'military' | 'news';
  lat: number;
  lng: number;
  title: string;
  severity: SeverityLevel;
  timestamp: string;
  metadata: Record<string, unknown>;
}

export interface ClusterProperties {
  cluster: boolean;
  point_count: number;
  point_count_abbreviated: string;
  severity: SeverityLevel;
  types: string[];
}

export interface TrendingTopic {
  keyword: string;
  count: number;
  trend: 'rising' | 'falling' | 'stable';
  relatedCategories: NewsCategory[];
  lastMention: string;
}

export interface CountryInstabilityIndex {
  countryCode: string;
  countryName: string;
  score: number; // 0-100
  trend: 'improving' | 'stable' | 'worsening';
  conflictCount: number;
  protestCount: number;
  newsVolume: number;
  lastUpdate: string;
}

export interface RSSSource {
  id: string;
  name: string;
  url: string;
  category: NewsCategory;
  region: string;
  tier: 1 | 2 | 3 | 4;
  active: boolean;
}

export interface TimeRange {
  value: number;
  label: string;
  param: string;
}

export const TIME_RANGES: TimeRange[] = [
  { value: 1, label: '1 ora', param: '1h' },
  { value: 6, label: '6 ore', param: '6h' },
  { value: 24, label: '24 ore', param: '24h' },
  { value: 168, label: '7 giorni', param: '7d' },
];

export const CATEGORY_COLORS: Record<NewsCategory, string> = {
  conflict: '#ef4444',
  protest: '#f97316',
  disaster: '#eab308',
  politics: '#3b82f6',
  economy: '#22c55e',
  military: '#8b5cf6',
  terrorism: '#dc2626',
  health: '#06b6d4',
  environment: '#10b981',
  diplomacy: '#6366f1',
  general: '#64748b',
};

export const SEVERITY_COLORS: Record<SeverityLevel, string> = {
  1: '#22c55e', // green - low
  2: '#84cc16', // lime - minor
  3: '#eab308', // yellow - moderate
  4: '#f97316', // orange - high
  5: '#ef4444', // red - critical
};

export interface MapState {
  center: [number, number];
  zoom: number;
  activeLayers: string[];
  timeRange: string;
  searchQuery: string;
}

export interface FeedResponse {
  items: NewsItem[];
  sources: RSSSource[];
  lastUpdate: string;
  totalCount: number;
  cached: boolean;
}
