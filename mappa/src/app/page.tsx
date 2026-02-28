'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import dynamic from 'next/dynamic';
import useSWR from 'swr';
import NewsSidebar from '@/components/NewsSidebar';
import LayerControl from '@/components/LayerControl';
import TrendingPanel from '@/components/TrendingPanel';
import StatusBar from '@/components/StatusBar';
import type { NewsItem, ConflictZone, MapMarker } from '@/types';

// Dynamic import for Map to avoid SSR issues
const Map = dynamic(() => import('@/components/Map'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-gray-900">
      <div className="text-center text-white">
        <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-gray-400">Caricamento mappa...</p>
      </div>
    </div>
  ),
});

// Fetcher for SWR
const fetcher = (url: string) => fetch(url).then((res) => res.json());

// Default active layers
const DEFAULT_LAYERS = ['conflicts', 'news'];

export default function Dashboard() {
  // State
  const [activeLayers, setActiveLayers] = useState<string[]>(DEFAULT_LAYERS);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h');
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);

  // Data fetching with SWR
  const { data: newsData, mutate: mutateNews, isLoading: newsLoading } = useSWR(
    `/api/news?timeRange=${selectedTimeRange}&category=${selectedCategory}&search=${encodeURIComponent(searchQuery)}&refresh=${refreshKey > 0}`,
    fetcher,
    { 
      refreshInterval: 300000, // 5 minutes auto-refresh
      revalidateOnFocus: false,
    }
  );

  const { data: conflictsData, isLoading: conflictsLoading } = useSWR(
    '/api/conflicts',
    fetcher,
    { refreshInterval: 300000 }
  );

  const { data: trendsData, isLoading: trendsLoading } = useSWR(
    '/api/trends',
    fetcher,
    { refreshInterval: 300000 }
  );

  // Derived data
  const news: NewsItem[] = useMemo(() => newsData?.items || [], [newsData]);
  const conflicts: ConflictZone[] = useMemo(() => conflictsData?.conflicts || [], [conflictsData]);

  // Calculate stats
  const stats = useMemo(() => {
    const liveCount = news.filter(n => n.isNew).length;
    const activeConflicts = conflicts.filter(c => c.status === 'active' || c.status === 'escalating').length;
    const highSeverity = news.filter(n => n.severity >= 4).length;
    return { liveCount, activeConflicts, highSeverity, totalNews: news.length };
  }, [news, conflicts]);

  // Handlers
  const handleLayerToggle = useCallback((layer: string) => {
    setActiveLayers(prev => 
      prev.includes(layer) 
        ? prev.filter(l => l !== layer) 
        : [...prev, layer]
    );
  }, []);

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  const handleCategoryFilter = useCallback((category: string) => {
    setSelectedCategory(category);
  }, []);

  const handleTimeFilter = useCallback((range: string) => {
    setSelectedTimeRange(range);
  }, []);

  const handleMarkerClick = useCallback((marker: MapMarker) => {
    console.log('Marker clicked:', marker);
    // Could open a detail modal here
  }, []);

  const handleRefresh = useCallback(() => {
    setRefreshKey(prev => prev + 1);
    mutateNews();
  }, [mutateNews]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      
      switch (e.key.toLowerCase()) {
        case 'r':
          e.preventDefault();
          handleRefresh();
          break;
        case '1':
          e.preventDefault();
          handleTimeFilter('1h');
          break;
        case '2':
          e.preventDefault();
          handleTimeFilter('6h');
          break;
        case '3':
          e.preventDefault();
          handleTimeFilter('24h');
          break;
        case '4':
          e.preventDefault();
          handleTimeFilter('7d');
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleRefresh, handleTimeFilter]);

  return (
    <div className="h-screen flex flex-col bg-gray-950 text-white overflow-hidden">
      {/* Header */}
      <header className="h-14 border-b border-gray-800 px-4 flex items-center justify-between bg-gray-900/95 backdrop-blur-sm flex-shrink-0 z-50">
        <div className="flex items-center gap-3">
          <div className="text-2xl">🌍</div>
          <div>
            <h1 className="text-lg font-bold">Conflict Map</h1>
            <p className="text-xs text-gray-500 hidden sm:block">Real-time Global Intelligence</p>
          </div>
          <div className="flex items-center gap-1.5 ml-4">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-xs text-gray-400">LIVE</span>
          </div>
        </div>

        {/* Stats */}
        <div className="hidden lg:flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            <span className="text-gray-400">Conflitti attivi:</span>
            <span className="font-bold text-red-400">{stats.activeConflicts}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-blue-500 rounded-full" />
            <span className="text-gray-400">Notizie:</span>
            <span className="font-bold">{stats.totalNews}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-yellow-500 rounded-full" />
            <span className="text-gray-400">Alta severità:</span>
            <span className="font-bold text-yellow-400">{stats.highSeverity}</span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleRefresh}
            disabled={newsLoading}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded text-sm transition-colors flex items-center gap-2"
          >
            <svg className={`w-4 h-4 ${newsLoading ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span className="hidden sm:inline">Aggiorna</span>
          </button>
        </div>
      </header>

      {/* Status bar */}
      <StatusBar
        lastUpdate={newsData?.lastUpdate || new Date().toISOString()}
        itemCount={stats.totalNews}
        isLoading={newsLoading}
        onRefresh={handleRefresh}
      />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <aside className="w-80 lg:w-96 border-r border-gray-800 flex-shrink-0 overflow-hidden">
          <NewsSidebar
            news={news}
            loading={newsLoading}
            onSearch={handleSearch}
            onCategoryFilter={handleCategoryFilter}
            onTimeFilter={handleTimeFilter}
            selectedCategory={selectedCategory}
            selectedTimeRange={selectedTimeRange}
            totalCount={newsData?.totalCount || 0}
          />
        </aside>

        {/* Map Area */}
        <main className="flex-1 relative overflow-hidden">
          <Map
            news={news}
            conflicts={conflicts}
            activeLayers={activeLayers}
            onMarkerClick={handleMarkerClick}
          />

          {/* Layer Control */}
          <LayerControl
            activeLayers={activeLayers}
            onToggle={handleLayerToggle}
          />

          {/* Trending Panel */}
          <div className="absolute top-4 left-4 w-72 z-10">
            <TrendingPanel
              topics={trendsData?.topics || []}
              countries={trendsData?.countries || []}
              loading={trendsLoading}
            />
          </div>
        </main>
      </div>

      {/* Keyboard shortcuts hint */}
      <div className="fixed bottom-4 right-4 text-xs text-gray-500 bg-gray-900/80 px-3 py-2 rounded-lg backdrop-blur">
        <span className="hidden sm:inline">Tasti rapidi: </span>
        <span className="text-gray-400">R</span> aggiorna • 
        <span className="text-gray-400"> 1-4</span> filtro tempo
      </div>
    </div>
  );
}
