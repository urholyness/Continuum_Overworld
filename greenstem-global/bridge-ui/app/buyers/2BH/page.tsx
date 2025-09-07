'use client';

import { useEffect, useState } from 'react';
import { Amplify } from 'aws-amplify';
import { Authenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import WeatherChart from '@/components/WeatherChart';
import Timeline from '@/components/Timeline';
import axios from 'axios';

// Configure Amplify
if (process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID && process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID) {
  Amplify.configure({
    Auth: {
      region: process.env.NEXT_PUBLIC_COGNITO_REGION,
      userPoolId: process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID,
      userPoolWebClientId: process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID,
    }
  });
}

interface FarmSummary {
  id: string;
  name: string;
  location: string;
  last_ndvi: { value: number; timestamp: string } | null;
  next_harvest_eta: string;
}

export default function BuyerDashboard() {
  const [summary, setSummary] = useState<FarmSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(
          `${process.env.NEXT_PUBLIC_API_URL}/farms/2BH/summary`
        );
        setSummary(response.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <Authenticator>
      {({ signOut, user }) => (
        <div className="min-h-screen bg-gray-50">
          {/* Header */}
          <div className="bg-gradient-to-r from-farm-green to-sky-blue text-white py-8">
            <div className="container mx-auto px-4 flex justify-between items-center">
              <div>
                <h1 className="text-3xl font-bold">Buyer Dashboard</h1>
                <p className="text-lg mt-2">Two Butterflies Homestead - Eldoret, Kenya</p>
              </div>
              <div className="text-right">
                <p className="text-sm mb-2">Welcome, {user?.username}</p>
                <button
                  onClick={signOut}
                  className="bg-white text-farm-green px-4 py-2 rounded hover:bg-gray-100"
                >
                  Sign Out
                </button>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="container mx-auto px-4 py-8">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Current NDVI</h3>
                <p className="text-3xl font-bold text-farm-green">
                  {summary?.last_ndvi ? `${(summary.last_ndvi.value * 100).toFixed(1)}%` : 'N/A'}
                </p>
                <p className="text-xs text-gray-400 mt-2">Vegetation Health Index</p>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Next Harvest</h3>
                <p className="text-3xl font-bold text-harvest-gold">
                  {summary ? new Date(summary.next_harvest_eta).toLocaleDateString() : 'TBD'}
                </p>
                <p className="text-xs text-gray-400 mt-2">Estimated Date</p>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Quality Score</h3>
                <p className="text-3xl font-bold text-sky-blue">A+</p>
                <p className="text-xs text-gray-400 mt-2">Based on latest inspection</p>
              </div>
            </div>

            {/* Timeline */}
            <div className="bg-white rounded-lg shadow p-6 mb-8">
              <h2 className="text-2xl font-semibold mb-4">Farm Activity Timeline</h2>
              <Timeline farmId="2BH" />
            </div>

            {/* Weather Chart */}
            <div className="bg-white rounded-lg shadow p-6 mb-8">
              <WeatherChart farmId="2BH" days={30} />
            </div>

            {/* Lot Preview */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-2xl font-semibold mb-4">Upcoming Lot Preview</h2>
              <div className="border-l-4 border-harvest-gold pl-4">
                <h3 className="font-semibold text-lg">Premium Green Beans - Lot #2BH-2025-Q1</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                  <div>
                    <p className="text-sm text-gray-500">Variety</p>
                    <p className="font-medium">French Beans</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Expected Volume</p>
                    <p className="font-medium">5,000 kg</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Certification</p>
                    <p className="font-medium">GlobalGAP</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Packaging</p>
                    <p className="font-medium">200g punnets</p>
                  </div>
                </div>
                <p className="text-gray-600 mt-4">
                  This premium lot features hand-picked French beans grown using sustainable 
                  farming practices. Perfect for export markets requiring consistent quality 
                  and traceability.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </Authenticator>
  );
}