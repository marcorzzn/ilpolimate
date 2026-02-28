import { NextResponse } from 'next/server';
import { fetchAllFeeds, RSS_SOURCES } from '@/lib/rss-parser';
import type { FeedResponse } from '@/types';

// Cache configuration
let cachedData: FeedResponse | null = null;
let lastFetchTime = 0;
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const timeRange = searchParams.get('timeRange') || '24h';
  const category = searchParams.get('category');
  const search = searchParams.get('search');
  const forceRefresh = searchParams.get('refresh') === 'true';
  
  // Check cache
  const now = Date.now();
  if (!forceRefresh && cachedData && now - lastFetchTime < CACHE_TTL) {
    let items = cachedData.items;
    
    // Apply filters
    if (category && category !== 'all') {
      items = items.filter(item => item.category === category);
    }
    
    if (search) {
      const searchLower = search.toLowerCase();
      items = items.filter(item => 
        item.title.toLowerCase().includes(searchLower) ||
        item.description.toLowerCase().includes(searchLower)
      );
    }
    
    // Filter by time range
    const hoursAgo = parseInt(timeRange.replace('h', '').replace('d', '')) * (timeRange.includes('d') ? 24 : 1);
    const cutoff = now - hoursAgo * 60 * 60 * 1000;
    items = items.filter(item => new Date(item.publishedAt).getTime() > cutoff);
    
    return NextResponse.json({
      ...cachedData,
      items,
      totalCount: items.length,
      cached: true,
    });
  }
  
  // Fetch fresh data
  try {
    const items = await fetchAllFeeds();
    
    cachedData = {
      items,
      sources: RSS_SOURCES.filter(s => s.active),
      lastUpdate: new Date().toISOString(),
      totalCount: items.length,
      cached: false,
    };
    lastFetchTime = now;
    
    // Apply filters to fresh data too
    let filteredItems = items;
    
    if (category && category !== 'all') {
      filteredItems = filteredItems.filter(item => item.category === category);
    }
    
    if (search) {
      const searchLower = search.toLowerCase();
      filteredItems = filteredItems.filter(item => 
        item.title.toLowerCase().includes(searchLower) ||
        item.description.toLowerCase().includes(searchLower)
      );
    }
    
    // Filter by time range
    const hoursAgo = parseInt(timeRange.replace('h', '').replace('d', '')) * (timeRange.includes('d') ? 24 : 1);
    const cutoff = now - hoursAgo * 60 * 60 * 1000;
    filteredItems = filteredItems.filter(item => new Date(item.publishedAt).getTime() > cutoff);
    
    return NextResponse.json({
      ...cachedData,
      items: filteredItems,
      totalCount: filteredItems.length,
    });
  } catch (error) {
    console.error('Error fetching news:', error);
    
    // Return cached data if available, even if stale
    if (cachedData) {
      return NextResponse.json({
        ...cachedData,
        cached: true,
        error: 'Using cached data due to fetch error',
      });
    }
    
    return NextResponse.json(
      { error: 'Failed to fetch news', items: [], sources: [], lastUpdate: new Date().toISOString(), totalCount: 0, cached: false },
      { status: 500 }
    );
  }
}
