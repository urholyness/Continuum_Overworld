'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import FreshnessBadge from '@/components/FreshnessBadge';
import axios from 'axios';

const Map = dynamic(() => import('@/components/Map'), {
  ssr: false,
  loading: () => <p>Loading map...</p>
});

interface FarmSummary {
  id: string;
  name: string;
  location: string;
  coords: any;
  last_ndvi: { value: number; timestamp: string; unit: string } | null;
  last_weather: { temperature: { value: number; timestamp: string; unit: string } | null };
  next_harvest_eta: string;
  last_ops_event: { type: string; note: string; timestamp: string } | null;
  freshness: {
    weather_ts: string | null;
    sat_ts: string | null;
    ops_ts: string | null;
  };
}

export default function FarmPublicPage() {
  const [summary, setSummary] = useState<FarmSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await axios.get(
          `${process.env.NEXT_PUBLIC_API_URL}/farms/2BH/summary`
        );
        setSummary(response.data);
      } catch (error) {
        console.error('Error fetching farm summary:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
    const interval = setInterval(fetchSummary, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-2xl">Loading farm data...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-farm-green to-sky-blue text-white py-16">
        <div className="container mx-auto px-4">
          <h1 className="text-5xl font-bold mb-4">Two Butterflies Homestead</h1>
          <p className="text-2xl">Eldoret, Kenya</p>
        </div>
      </div>

      {/* Freshness Badges */}
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold mb-4">Live Data Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center justify-between">
              <span className="font-medium">Weather Data:</span>
              <FreshnessBadge ts={summary?.freshness.weather_ts} />
            </div>
            <div className="flex items-center justify-between">
              <span className="font-medium">Satellite Data:</span>
              <FreshnessBadge ts={summary?.freshness.sat_ts} />
            </div>
            <div className="flex items-center justify-between">
              <span className="font-medium">Operations Log:</span>
              <FreshnessBadge ts={summary?.freshness.ops_ts} />
            </div>
          </div>
        </div>
      </div>

      {/* Map Section */}
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold mb-4">Farm Location</h2>
          <div className="h-96">
            <Map farmPolygon={summary?.coords} />
          </div>
        </div>
      </div>

      {/* NDVI and Weather Section */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-4">Vegetation Health (NDVI)</h2>
            {summary?.last_ndvi ? (
              <>
                <div className="text-4xl font-bold text-farm-green mb-2">
                  {(summary.last_ndvi.value * 100).toFixed(1)}%
                </div>
                <p className="text-gray-600">
                  Last updated: {new Date(summary.last_ndvi.timestamp).toLocaleString()}
                </p>
                <div className="mt-4">
                  <img
                    src={`${process.env.NEXT_PUBLIC_S3_URL}/sat/2BH/${new Date().toISOString().split('T')[0]}/ndvi.png`}
                    alt="NDVI Thumbnail"
                    className="w-full rounded"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                    }}
                  />
                </div>
              </>
            ) : (
              <p className="text-gray-500">No NDVI data available</p>
            )}
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-4">Current Weather</h2>
            {summary?.last_weather.temperature ? (
              <>
                <div className="text-4xl font-bold text-sky-blue mb-2">
                  {summary.last_weather.temperature.value}°C
                </div>
                <p className="text-gray-600">
                  Last updated: {new Date(summary.last_weather.temperature.timestamp).toLocaleString()}
                </p>
              </>
            ) : (
              <p className="text-gray-500">No weather data available</p>
            )}
          </div>
        </div>
      </div>

      {/* Today at the Farm */}
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold mb-4">Today at the Farm</h2>
          {summary?.last_ops_event ? (
            <div className="border-l-4 border-farm-green pl-4">
              <h3 className="font-semibold text-lg capitalize">{summary.last_ops_event.type}</h3>
              <p className="text-gray-700 mt-2">{summary.last_ops_event.note}</p>
              <p className="text-gray-500 text-sm mt-2">
                {new Date(summary.last_ops_event.timestamp).toLocaleString()}
              </p>
            </div>
          ) : (
            <p className="text-gray-500">No recent operations logged</p>
          )}
        </div>
      </div>

      {/* Next Harvest */}
      <div className="container mx-auto px-4 py-8 pb-16">
        <div className="bg-gradient-to-r from-harvest-gold to-farm-green text-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold mb-2">Next Harvest Expected</h2>
          <p className="text-3xl font-bold">
            {summary ? new Date(summary.next_harvest_eta).toLocaleDateString() : 'TBD'}
          </p>
        </div>
      </div>
    </div>
  );
}