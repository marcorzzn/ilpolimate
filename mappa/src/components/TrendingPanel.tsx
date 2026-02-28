'use client';

import type { TrendingTopic, CountryInstabilityIndex } from '@/types';

interface TrendingPanelProps {
  topics: TrendingTopic[];
  countries: CountryInstabilityIndex[];
  loading: boolean;
}

export default function TrendingPanel({ topics, countries, loading }: TrendingPanelProps) {
  return (
    <div className="bg-gray-900 text-white p-4 rounded-lg h-full overflow-hidden flex flex-col">
      {/* Trending Topics */}
      <div className="mb-4">
        <h3 className="text-sm font-bold mb-2 flex items-center gap-2">
          <span>🔥</span> Argomenti Trending
        </h3>
        <div className="flex flex-wrap gap-1.5">
          {loading ? (
            <div className="flex gap-2">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-6 w-20 bg-gray-700 rounded animate-pulse" />
              ))}
            </div>
          ) : (
            topics.slice(0, 8).map((topic) => (
              <div
                key={topic.keyword}
                className="flex items-center gap-1 px-2 py-1 bg-gray-800 rounded-full text-xs"
              >
                <span>{topic.keyword}</span>
                <span className="text-gray-400">({topic.count})</span>
                {topic.trend === 'rising' && <span className="text-green-400">↑</span>}
                {topic.trend === 'falling' && <span className="text-red-400">↓</span>}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Country Instability Index */}
      <div className="flex-1 overflow-hidden">
        <h3 className="text-sm font-bold mb-2 flex items-center gap-2">
          <span>🌍</span> Indice Instabilità (CII)
        </h3>
        <div className="overflow-y-auto h-[calc(100%-2rem)] space-y-1.5 pr-1">
          {loading ? (
            <div className="space-y-2">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-12 bg-gray-800 rounded animate-pulse" />
              ))}
            </div>
          ) : (
            countries.slice(0, 10).map((country) => (
              <div
                key={country.countryCode}
                className="flex items-center gap-3 p-2 bg-gray-800/50 rounded hover:bg-gray-800 transition-colors"
              >
                {/* CII Score Gauge */}
                <div className="relative w-10 h-10 flex-shrink-0">
                  <svg className="w-10 h-10 -rotate-90">
                    <circle
                      cx="20"
                      cy="20"
                      r="16"
                      fill="none"
                      stroke="#374151"
                      strokeWidth="4"
                    />
                    <circle
                      cx="20"
                      cy="20"
                      r="16"
                      fill="none"
                      stroke={getScoreColor(country.score)}
                      strokeWidth="4"
                      strokeDasharray={`${(country.score / 100) * 100.53} 100.53`}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center text-xs font-bold">
                    {country.score}
                  </div>
                </div>

                {/* Country info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium truncate">{country.countryName}</span>
                    <span
                      className={`text-[10px] ${
                        country.trend === 'worsening'
                          ? 'text-red-400'
                          : country.trend === 'improving'
                          ? 'text-green-400'
                          : 'text-gray-400'
                      }`}
                    >
                      {country.trend === 'worsening' && '⚠️'}
                      {country.trend === 'improving' && '↓'}
                      {country.trend === 'stable' && '→'}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-[10px] text-gray-400">
                    {country.conflictCount > 0 && (
                      <span className="flex items-center gap-1">
                        <span className="w-1.5 h-1.5 bg-red-500 rounded-full" />
                        {country.conflictCount} conflitto
                      </span>
                    )}
                    {country.protestCount > 0 && (
                      <span className="flex items-center gap-1">
                        <span className="w-1.5 h-1.5 bg-orange-500 rounded-full" />
                        {country.protestCount} proteste
                      </span>
                    )}
                    <span>📰 {country.newsVolume}</span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function getScoreColor(score: number): string {
  if (score >= 80) return '#ef4444'; // red
  if (score >= 60) return '#f97316'; // orange
  if (score >= 40) return '#eab308'; // yellow
  if (score >= 20) return '#84cc16'; // lime
  return '#22c55e'; // green
}
