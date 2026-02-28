'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import type { MapMarker, NewsItem, ConflictZone, MapState } from '@/types';
import { CATEGORY_COLORS, SEVERITY_COLORS } from '@/types';

interface MapProps {
  news: NewsItem[];
  conflicts: ConflictZone[];
  activeLayers: string[];
  onMarkerClick?: (marker: MapMarker) => void;
  onMapStateChange?: (state: MapState) => void;
}

export default function Map({ news, conflicts, activeLayers, onMarkerClick, onMapStateChange }: MapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);
  const [mapLoaded, setMapLoaded] = useState(false);

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: 'https://demotiles.maplibre.org/style.json',
      center: [15, 30],
      zoom: 2,
      maxZoom: 18,
      minZoom: 1,
    });

    map.current.addControl(new maplibregl.NavigationControl(), 'top-right');
    map.current.addControl(new maplibregl.ScaleControl(), 'bottom-left');

    map.current.on('load', () => {
      setMapLoaded(true);
    });

    map.current.on('moveend', () => {
      if (map.current && onMapStateChange) {
        const center = map.current.getCenter();
        onMapStateChange({
          center: [center.lng, center.lat],
          zoom: map.current.getZoom(),
          activeLayers,
          timeRange: '24h',
          searchQuery: '',
        });
      }
    });

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, [activeLayers, onMapStateChange]);

  // Update markers when data changes
  const updateMarkers = useCallback(() => {
    if (!map.current || !mapLoaded) return;

    // Clear existing markers
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];

    // Add conflict markers
    if (activeLayers.includes('conflicts')) {
      conflicts.forEach(conflict => {
        if (!map.current) return;

        const el = document.createElement('div');
        el.className = 'conflict-marker';
        el.style.cssText = `
          width: ${8 + conflict.intensity * 4}px;
          height: ${8 + conflict.intensity * 4}px;
          background: ${SEVERITY_COLORS[conflict.intensity as keyof typeof SEVERITY_COLORS]};
          border: 2px solid white;
          border-radius: 50%;
          cursor: pointer;
          box-shadow: 0 0 10px ${SEVERITY_COLORS[conflict.intensity as keyof typeof SEVERITY_COLORS]};
        `;

        const popup = new maplibregl.Popup({ offset: 25 }).setHTML(`
          <div style="min-width: 200px; padding: 8px;">
            <h3 style="margin: 0 0 8px; font-size: 14px; font-weight: bold;">${conflict.name}</h3>
            <p style="margin: 0 0 4px; font-size: 12px; color: #666;">${conflict.country}</p>
            <div style="display: flex; gap: 8px; margin-top: 8px;">
              <span style="padding: 2px 6px; background: ${SEVERITY_COLORS[conflict.intensity as keyof typeof SEVERITY_COLORS]}; color: white; border-radius: 4px; font-size: 10px;">
                Intensità: ${conflict.intensity}/5
              </span>
              <span style="padding: 2px 6px; background: #333; color: white; border-radius: 4px; font-size: 10px;">
                ${conflict.status.toUpperCase()}
              </span>
            </div>
            <p style="margin: 8px 0 0; font-size: 11px; line-height: 1.4;">${conflict.description}</p>
          </div>
        `);

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([conflict.lng, conflict.lat])
          .setPopup(popup)
          .addTo(map.current);

        marker.getElement().addEventListener('click', () => {
          if (onMarkerClick) {
            onMarkerClick({
              id: conflict.id,
              type: 'conflict',
              lat: conflict.lat,
              lng: conflict.lng,
              title: conflict.name,
              severity: conflict.intensity as 1 | 2 | 3 | 4 | 5,
              timestamp: conflict.lastUpdate,
              metadata: { ...conflict },
            });
          }
        });

        markersRef.current.push(marker);
      });
    }

    // Add news markers
    if (activeLayers.includes('news')) {
      news.forEach(item => {
        if (!map.current || !item.location) return;

        const el = document.createElement('div');
        el.className = 'news-marker';
        el.style.cssText = `
          width: ${8 + item.severity * 2}px;
          height: ${8 + item.severity * 2}px;
          background: ${CATEGORY_COLORS[item.category]};
          border: 2px solid white;
          border-radius: 50%;
          cursor: pointer;
          opacity: 0.9;
        `;

        const popup = new maplibregl.Popup({ offset: 25 }).setHTML(`
          <div style="min-width: 220px; padding: 8px;">
            <span style="padding: 2px 6px; background: ${CATEGORY_COLORS[item.category]}; color: white; border-radius: 4px; font-size: 10px; text-transform: uppercase;">
              ${item.category}
            </span>
            <h3 style="margin: 8px 0 4px; font-size: 13px; line-height: 1.3;">${item.title}</h3>
            <p style="margin: 0 0 4px; font-size: 11px; color: #888;">${item.source} • ${new Date(item.publishedAt).toLocaleDateString('it-IT')}</p>
          </div>
        `);

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([item.location.lng, item.location.lat])
          .setPopup(popup)
          .addTo(map.current);

        marker.getElement().addEventListener('click', () => {
          if (onMarkerClick) {
            onMarkerClick({
              id: item.id,
              type: 'news',
              lat: item.location!.lat,
              lng: item.location!.lng,
              title: item.title,
              severity: item.severity,
              timestamp: item.publishedAt,
              metadata: { ...item },
            });
          }
        });

        markersRef.current.push(marker);
      });
    }
  }, [mapLoaded, conflicts, news, activeLayers, onMarkerClick]);

  useEffect(() => {
    updateMarkers();
  }, [updateMarkers]);

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainer} className="w-full h-full rounded-lg" />
      
      {/* Loading overlay */}
      {!mapLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900/50 rounded-lg">
          <div className="flex flex-col items-center gap-3">
            <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-white text-sm">Caricamento mappa...</span>
          </div>
        </div>
      )}
      
      {/* Map legend */}
      <div className="absolute bottom-12 left-4 bg-gray-900/90 backdrop-blur p-3 rounded-lg text-xs">
        <div className="text-gray-400 font-semibold mb-2">Legenda</div>
        <div className="flex flex-col gap-1.5">
          {Object.entries(CATEGORY_COLORS).map(([cat, color]) => (
            <div key={cat} className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ background: color }} />
              <span className="text-gray-300 capitalize">{cat}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
