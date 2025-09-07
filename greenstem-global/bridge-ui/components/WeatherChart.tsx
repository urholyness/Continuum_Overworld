'use client';

import { useEffect, useState } from 'react';
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import axios from 'axios';

interface WeatherReading {
  timestamp: string;
  sensors: {
    'weather.temp'?: { value: number; unit: string };
    'weather.humidity'?: { value: number; unit: string };
    'weather.precip24h'?: { value: number; unit: string };
  };
}

interface ChartData {
  date: string;
  temperature: number;
  humidity: number;
  precipitation: number;
}

export default function WeatherChart({ farmId = '2BH', days = 7 }) {
  const [data, setData] = useState<ChartData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWeatherData = async () => {
      try {
        const since = new Date();
        since.setDate(since.getDate() - days);
        
        const response = await axios.get(
          `${process.env.NEXT_PUBLIC_API_URL}/farms/${farmId}/readings`,
          {
            params: {
              since: since.toISOString()
            }
          }
        );

        const readings: WeatherReading[] = response.data.readings;
        
        // Process and aggregate data by day
        const dailyData = new Map<string, ChartData>();
        
        readings.forEach(reading => {
          const date = new Date(reading.timestamp).toLocaleDateString();
          
          if (!dailyData.has(date)) {
            dailyData.set(date, {
              date,
              temperature: 0,
              humidity: 0,
              precipitation: 0
            });
          }
          
          const dayData = dailyData.get(date)!;
          
          if (reading.sensors['weather.temp']) {
            dayData.temperature = reading.sensors['weather.temp'].value;
          }
          if (reading.sensors['weather.humidity']) {
            dayData.humidity = reading.sensors['weather.humidity'].value;
          }
          if (reading.sensors['weather.precip24h']) {
            dayData.precipitation = Math.max(
              dayData.precipitation,
              reading.sensors['weather.precip24h'].value
            );
          }
        });
        
        const sortedData = Array.from(dailyData.values())
          .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
        
        setData(sortedData);
      } catch (error) {
        console.error('Error fetching weather data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchWeatherData();
  }, [farmId, days]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading weather data...</div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-500">No weather data available</div>
      </div>
    );
  }

  return (
    <div className="w-full">
      <h3 className="text-xl font-semibold mb-4">Weather Trends ({days} days)</h3>
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis
            yAxisId="temp"
            orientation="left"
            label={{ value: 'Temperature (°C)', angle: -90, position: 'insideLeft' }}
            domain={['auto', 'auto']}
          />
          <YAxis
            yAxisId="precip"
            orientation="right"
            label={{ value: 'Precipitation (mm)', angle: 90, position: 'insideRight' }}
            domain={[0, 'auto']}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #ccc',
              borderRadius: '4px'
            }}
            formatter={(value: any, name: string) => {
              if (name === 'Temperature') return [`${value}°C`, name];
              if (name === 'Precipitation') return [`${value}mm`, name];
              if (name === 'Humidity') return [`${value}%`, name];
              return [value, name];
            }}
          />
          <Legend />
          <Bar
            yAxisId="precip"
            dataKey="precipitation"
            fill="#0288D1"
            name="Precipitation"
            barSize={30}
          />
          <Line
            yAxisId="temp"
            type="monotone"
            dataKey="temperature"
            stroke="#FF6B35"
            strokeWidth={3}
            name="Temperature"
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
          <Line
            yAxisId="temp"
            type="monotone"
            dataKey="humidity"
            stroke="#4CAF50"
            strokeWidth={2}
            name="Humidity"
            strokeDasharray="5 5"
            dot={{ r: 3 }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}