'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import type { NewsItem } from '@/types';
import { CATEGORY_COLORS, SEVERITY_COLORS } from '@/types';

interface NewsSidebarProps {
  news: NewsItem[];
  loading: boolean;
  onSearch: (query: string) => void;
  onCategoryFilter: (category: string) => void;
  onTimeFilter: (range: string) => void;
  selectedCategory: string;
  selectedTimeRange: string;
  totalCount: number;
}

export default function NewsSidebar({
  news,
  loading,
  onSearch,
  onCategoryFilter,
  onTimeFilter,
  selectedCategory,
  selectedTimeRange,
  totalCount,
}: NewsSidebarProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [visibleCount, setVisibleCount] = useState(30);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement>(null);

  // Virtual scrolling - load more on scroll
  useEffect(() => {
    observerRef.current = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !loading) {
          setVisibleCount(prev => Math.min(prev + 20, news.length));
        }
      },
      { threshold: 0.1 }
    );

    if (loadMoreRef.current) {
      observerRef.current.observe(loadMoreRef.current);
    }

    return () => observerRef.current?.disconnect();
  }, [loading, news.length]);

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
    onSearch(query);
  }, [onSearch]);

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Ora';
    if (diffMins < 60) return `${diffMins}m fa`;
    if (diffHours < 24) return `${diffHours}h fa`;
    if (diffDays < 7) return `${diffDays}g fa`;
    return date.toLocaleDateString('it-IT');
  };

  const categories = ['all', 'conflict', 'protest', 'disaster', 'military', 'terrorism', 'politics', 'economy', 'diplomacy'];

  return (
    <div className="flex flex-col h-full bg-gray-900 text-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-lg font-bold mb-3">📰 Notizie in Tempo Reale</h2>
        
        {/* Search */}
        <div className="relative">
          <input
            type="text"
            placeholder="Cerca notizie..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="w-full px-4 py-2 pl-10 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
          />
          <svg className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      {/* Filters */}
      <div className="p-3 border-b border-gray-700 space-y-2">
        {/* Time filter */}
        <div className="flex gap-1 flex-wrap">
          {['1h', '6h', '24h', '7d'].map((range) => (
            <button
              key={range}
              onClick={() => onTimeFilter(range)}
              className={`px-3 py-1 text-xs rounded-full transition-colors ${
                selectedTimeRange === range
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {range}
            </button>
          ))}
        </div>

        {/* Category filter */}
        <div className="flex gap-1 flex-wrap">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => onCategoryFilter(cat)}
              className={`px-2 py-1 text-xs rounded transition-colors ${
                selectedCategory === cat
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {cat === 'all' ? 'Tutti' : cat.charAt(0).toUpperCase() + cat.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div className="px-4 py-2 bg-gray-800/50 text-xs text-gray-400">
        {totalCount} notizie • Aggiornamento automatico ogni 5 min
      </div>

      {/* News list */}
      <div className="flex-1 overflow-y-auto">
        {loading && news.length === 0 ? (
          <div className="flex items-center justify-center h-32">
            <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <>
            {news.slice(0, visibleCount).map((item, index) => (
              <NewsCard key={item.id} item={item} formatTimeAgo={formatTimeAgo} />
            ))}
            
            {/* Load more trigger */}
            <div ref={loadMoreRef} className="h-8 flex items-center justify-center">
              {loading && visibleCount < news.length && (
                <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
              )}
            </div>
          </>
        )}

        {news.length === 0 && !loading && (
          <div className="p-8 text-center text-gray-500">
            Nessuna notizia trovata
          </div>
        )}
      </div>
    </div>
  );
}

// Individual news card component
function NewsCard({ item, formatTimeAgo }: { item: NewsItem; formatTimeAgo: (d: string) => string }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className={`p-3 border-b border-gray-800 hover:bg-gray-800/50 cursor-pointer transition-colors ${
        item.isNew ? 'bg-blue-900/20' : ''
      }`}
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex items-start gap-2">
        {/* Category indicator */}
        <div
          className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0"
          style={{ background: CATEGORY_COLORS[item.category] }}
        />
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span
              className="px-1.5 py-0.5 text-[10px] rounded uppercase font-medium"
              style={{ background: CATEGORY_COLORS[item.category], color: 'white' }}
            >
              {item.category}
            </span>
            {item.isNew && (
              <span className="px-1.5 py-0.5 text-[10px] rounded bg-red-500 text-white animate-pulse">
                LIVE
              </span>
            )}
            {/* Severity indicator */}
            <div className="flex gap-0.5">
              {[1, 2, 3, 4, 5].map((level) => (
                <div
                  key={level}
                  className="w-1.5 h-1.5 rounded-full"
                  style={{
                    background: level <= item.severity 
                      ? SEVERITY_COLORS[item.severity]
                      : '#374151',
                  }}
                />
              ))}
            </div>
          </div>
          
          <h3 className="text-sm font-medium leading-tight mb-1 line-clamp-2">
            {item.title}
          </h3>
          
          {expanded && item.description && (
            <p className="text-xs text-gray-400 mb-2 leading-relaxed">
              {item.description}
            </p>
          )}
          
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span className="font-medium">{item.source}</span>
            <span>•</span>
            <span>{formatTimeAgo(item.publishedAt)}</span>
            {item.location && (
              <>
                <span>•</span>
                <span>📍 {item.location.country}</span>
              </>
            )}
          </div>
          
          {expanded && (
            <a
              href={item.link}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block mt-2 text-xs text-blue-400 hover:text-blue-300"
              onClick={(e) => e.stopPropagation()}
            >
              Leggi di più →
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
