'use client';

import { useState, useEffect } from 'react';

interface StatusBarProps {
  lastUpdate: string;
  itemCount: number;
  isLoading: boolean;
  onRefresh: () => void;
}

export default function StatusBar({ lastUpdate, itemCount, isLoading, onRefresh }: StatusBarProps) {
  const [timeSinceUpdate, setTimeSinceUpdate] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const diff = Date.now() - new Date(lastUpdate).getTime();
      const mins = Math.floor(diff / 60000);
      if (mins < 1) setTimeSinceUpdate('Adesso');
      else if (mins < 60) setTimeSinceUpdate(`${mins} min fa`);
      else {
        const hours = Math.floor(mins / 60);
        setTimeSinceUpdate(`${hours}h fa`);
      }
    };

    updateTime();
    const interval = setInterval(updateTime, 60000);
    return () => clearInterval(interval);
  }, [lastUpdate]);

  return (
    <div className="flex items-center gap-4 px-4 py-2 bg-gray-800/50 border-b border-gray-700 text-sm">
      {/* Status indicator */}
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${isLoading ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'}`} />
        <span className="text-gray-400">
          {isLoading ? 'Aggiornamento...' : 'Live'}
        </span>
      </div>

      {/* Item count */}
      <div className="text-gray-400">
        <span className="text-white font-medium">{itemCount}</span> notizie
      </div>

      {/* Last update */}
      <div className="text-gray-500">
        Ultimo agg: <span className="text-gray-400">{timeSinceUpdate}</span>
      </div>

      {/* Refresh button */}
      <button
        onClick={onRefresh}
        disabled={isLoading}
        className="ml-auto flex items-center gap-2 px-3 py-1 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded text-white text-sm transition-colors"
      >
        <svg
          className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
        Aggiorna
      </button>

      {/* Auto-refresh indicator */}
      <div className="flex items-center gap-1 text-gray-500 text-xs">
        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
            clipRule="evenodd"
          />
        </svg>
        Auto: 5 min
      </div>
    </div>
  );
}
