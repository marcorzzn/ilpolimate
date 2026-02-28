import { NextResponse } from 'next/server';
import type { TrendingTopic, CountryInstabilityIndex } from '@/types';

// Simulated trending topics based on current geopolitical situation
const TRENDING_TOPICS: TrendingTopic[] = [
  { keyword: 'Ucraina', count: 245, trend: 'stable', relatedCategories: ['conflict', 'military'], lastMention: new Date().toISOString() },
  { keyword: 'Gaza', count: 312, trend: 'rising', relatedCategories: ['conflict', 'diplomacy'], lastMention: new Date().toISOString() },
  { keyword: 'Houthi', count: 89, trend: 'rising', relatedCategories: ['military', 'conflict'], lastMention: new Date().toISOString() },
  { keyword: 'Sudan', count: 67, trend: 'stable', relatedCategories: ['conflict'], lastMention: new Date().toISOString() },
  { keyword: 'Mar Rosso', count: 156, trend: 'rising', relatedCategories: ['military', 'economy'], lastMention: new Date().toISOString() },
  { keyword: 'Haiti', count: 45, trend: 'falling', relatedCategories: ['conflict'], lastMention: new Date().toISOString() },
  { keyword: 'NATO', count: 78, trend: 'stable', relatedCategories: ['military', 'diplomacy'], lastMention: new Date().toISOString() },
  { keyword: 'Iran', count: 134, trend: 'rising', relatedCategories: ['conflict', 'diplomacy'], lastMention: new Date().toISOString() },
  { keyword: 'Russia', count: 267, trend: 'stable', relatedCategories: ['conflict', 'military'], lastMention: new Date().toISOString() },
  { keyword: 'Cina', count: 56, trend: 'stable', relatedCategories: ['diplomacy', 'economy'], lastMention: new Date().toISOString() },
];

// Country Instability Index data
const CII_DATA: CountryInstabilityIndex[] = [
  { countryCode: 'UA', countryName: 'Ucraina', score: 95, trend: 'stable', conflictCount: 1, protestCount: 12, newsVolume: 245, lastUpdate: new Date().toISOString() },
  { countryCode: 'PS', countryName: 'Palestina', score: 98, trend: 'stable', conflictCount: 1, protestCount: 5, newsVolume: 312, lastUpdate: new Date().toISOString() },
  { countryCode: 'SD', countryName: 'Sudan', score: 92, trend: 'worsening', conflictCount: 1, protestCount: 3, newsVolume: 67, lastUpdate: new Date().toISOString() },
  { countryCode: 'YE', countryName: 'Yemen', score: 88, trend: 'stable', conflictCount: 2, protestCount: 2, newsVolume: 125, lastUpdate: new Date().toISOString() },
  { countryCode: 'MM', countryName: 'Myanmar', score: 85, trend: 'worsening', conflictCount: 1, protestCount: 45, newsVolume: 25, lastUpdate: new Date().toISOString() },
  { countryCode: 'HT', countryName: 'Haiti', score: 82, trend: 'worsening', conflictCount: 1, protestCount: 8, newsVolume: 55, lastUpdate: new Date().toISOString() },
  { countryCode: 'CD', countryName: 'RDC', score: 78, trend: 'worsening', conflictCount: 1, protestCount: 15, newsVolume: 40, lastUpdate: new Date().toISOString() },
  { countryCode: 'SY', countryName: 'Siria', score: 75, trend: 'improving', conflictCount: 1, protestCount: 2, newsVolume: 30, lastUpdate: new Date().toISOString() },
  { countryCode: 'AF', countryName: 'Afghanistan', score: 72, trend: 'stable', conflictCount: 1, protestCount: 5, newsVolume: 20, lastUpdate: new Date().toISOString() },
  { countryCode: 'ML', countryName: 'Mali', score: 70, trend: 'stable', conflictCount: 1, protestCount: 8, newsVolume: 35, lastUpdate: new Date().toISOString() },
  { countryCode: 'IR', countryName: 'Iran', score: 65, trend: 'stable', conflictCount: 0, protestCount: 25, newsVolume: 134, lastUpdate: new Date().toISOString() },
  { countryCode: 'SO', countryName: 'Somalia', score: 68, trend: 'improving', conflictCount: 1, protestCount: 3, newsVolume: 15, lastUpdate: new Date().toISOString() },
  { countryCode: 'NG', countryName: 'Nigeria', score: 55, trend: 'stable', conflictCount: 1, protestCount: 20, newsVolume: 18, lastUpdate: new Date().toISOString() },
  { countryCode: 'ET', countryName: 'Etiopia', score: 60, trend: 'improving', conflictCount: 1, protestCount: 10, newsVolume: 12, lastUpdate: new Date().toISOString() },
];

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const type = searchParams.get('type') || 'all';
  
  if (type === 'topics') {
    return NextResponse.json({
      topics: TRENDING_TOPICS.sort((a, b) => b.count - a.count),
      lastUpdate: new Date().toISOString(),
    });
  }
  
  if (type === 'cii') {
    return NextResponse.json({
      countries: CII_DATA.sort((a, b) => b.score - a.score),
      lastUpdate: new Date().toISOString(),
    });
  }
  
  return NextResponse.json({
    topics: TRENDING_TOPICS.sort((a, b) => b.count - a.count),
    countries: CII_DATA.sort((a, b) => b.score - a.score),
    lastUpdate: new Date().toISOString(),
  });
}
