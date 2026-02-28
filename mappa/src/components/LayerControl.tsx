'use client';

import { useState } from 'react';

interface LayerControlProps {
  activeLayers: string[];
  onToggle: (layer: string) => void;
}

const LAYERS = [
  { id: 'conflicts', name: 'Conflitti', icon: '⚔️', color: '#ef4444' },
  { id: 'news', name: 'Notizie', icon: '📰', color: '#3b82f6' },
  { id: 'protests', name: 'Proteste', icon: '✊', color: '#f97316' },
  { id: 'disasters', name: 'Disastri', icon: '🌊', color: '#eab308' },
  { id: 'military', name: 'Militari', icon: '🎖️', color: '#8b5cf6' },
];

export default function LayerControl({ activeLayers, onToggle }: LayerControlProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="absolute top-4 right-16 z-10">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-gray-900/90 backdrop-blur border border-gray-700 rounded-lg text-white text-sm hover:bg-gray-800 transition-colors"
      >
        <span>📚</span>
        <span>Layer</span>
        <svg
          className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute top-12 right-0 bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg p-3 min-w-[180px] shadow-xl">
          <div className="text-xs text-gray-400 mb-2 uppercase tracking-wider">
            Livelli Mappa
          </div>
          <div className="space-y-1">
            {LAYERS.map((layer) => {
              const isActive = activeLayers.includes(layer.id);
              return (
                <button
                  key={layer.id}
                  onClick={() => onToggle(layer.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded transition-colors ${
                    isActive ? 'bg-blue-600/30 text-white' : 'text-gray-400 hover:bg-gray-800'
                  }`}
                >
                  <span className="text-lg">{layer.icon}</span>
                  <span className="flex-1 text-left text-sm">{layer.name}</span>
                  <div
                    className={`w-4 h-4 rounded-full border-2 flex items-center justify-center transition-colors ${
                      isActive ? 'border-blue-500 bg-blue-500' : 'border-gray-600'
                    }`}
                  >
                    {isActive && (
                      <svg className="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    )}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Quick actions */}
          <div className="mt-3 pt-3 border-t border-gray-700 flex gap-2">
            <button
              onClick={() => LAYERS.forEach(l => !activeLayers.includes(l.id) && onToggle(l.id))}
              className="flex-1 text-xs py-1.5 bg-gray-800 hover:bg-gray-700 rounded text-gray-300"
            >
              Tutti
            </button>
            <button
              onClick={() => {
                // Toggle all off
                activeLayers.forEach(l => onToggle(l));
              }}
              className="flex-1 text-xs py-1.5 bg-gray-800 hover:bg-gray-700 rounded text-gray-300"
            >
              Nessuno
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
