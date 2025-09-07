'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';

interface TimelineEvent {
  id: string;
  type: 'ops' | 'ndvi' | 'weather' | 'alert';
  title: string;
  description: string;
  timestamp: string;
  icon?: string;
}

export default function Timeline({ farmId = '2BH' }) {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        // Fetch ops events
        const opsResponse = await axios.get(
          `${process.env.NEXT_PUBLIC_API_URL}/farms/${farmId}/ops?limit=10`
        );

        // Fetch recent readings for significant changes
        const since = new Date();
        since.setDate(since.getDate() - 7);
        const readingsResponse = await axios.get(
          `${process.env.NEXT_PUBLIC_API_URL}/farms/${farmId}/readings`,
          { params: { since: since.toISOString() } }
        );

        // Combine and sort events
        const combinedEvents: TimelineEvent[] = [];

        // Add ops events
        opsResponse.data.events?.forEach((event: any) => {
          combinedEvents.push({
            id: event.event_id,
            type: 'ops',
            title: event.type,
            description: event.note,
            timestamp: event.created_at,
            icon: '📋'
          });
        });

        // Add NDVI updates (only significant ones)
        const ndviReadings = readingsResponse.data.readings?.filter(
          (r: any) => r.sensors['sat.ndvi.mean']
        );
        
        if (ndviReadings && ndviReadings.length > 0) {
          const latestNdvi = ndviReadings[0];
          combinedEvents.push({
            id: `ndvi-${latestNdvi.timestamp}`,
            type: 'ndvi',
            title: 'NDVI Update',
            description: `Vegetation index: ${(latestNdvi.sensors['sat.ndvi.mean'].value * 100).toFixed(1)}%`,
            timestamp: latestNdvi.timestamp,
            icon: '🛰️'
          });
        }

        // Add weather alerts (heavy rain, extreme temps)
        const weatherReadings = readingsResponse.data.readings?.filter(
          (r: any) => r.sensors['weather.precip24h']?.value > 10
        );

        weatherReadings?.forEach((reading: any) => {
          combinedEvents.push({
            id: `weather-${reading.timestamp}`,
            type: 'weather',
            title: 'Heavy Rainfall',
            description: `${reading.sensors['weather.precip24h'].value}mm recorded`,
            timestamp: reading.timestamp,
            icon: '🌧️'
          });
        });

        // Sort by timestamp (newest first)
        combinedEvents.sort((a, b) => 
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        );

        setEvents(combinedEvents.slice(0, 15)); // Limit to 15 most recent
      } catch (error) {
        console.error('Error fetching timeline events:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, [farmId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-32">
        <div className="text-lg">Loading timeline...</div>
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        No recent events to display
      </div>
    );
  }

  const getEventColor = (type: string) => {
    switch (type) {
      case 'ops': return 'border-farm-green';
      case 'ndvi': return 'border-harvest-gold';
      case 'weather': return 'border-sky-blue';
      case 'alert': return 'border-red-500';
      default: return 'border-gray-400';
    }
  };

  return (
    <div className="relative">
      <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>
      
      {events.map((event, index) => (
        <div key={event.id} className="relative flex items-start mb-6">
          <div className={`absolute left-0 w-8 h-8 bg-white border-4 ${getEventColor(event.type)} rounded-full flex items-center justify-center text-sm`}>
            {event.icon || '•'}
          </div>
          
          <div className="ml-12 flex-1">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex justify-between items-start mb-2">
                <h4 className="font-semibold text-gray-900">{event.title}</h4>
                <span className="text-xs text-gray-500">
                  {new Date(event.timestamp).toLocaleString()}
                </span>
              </div>
              <p className="text-gray-700">{event.description}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}