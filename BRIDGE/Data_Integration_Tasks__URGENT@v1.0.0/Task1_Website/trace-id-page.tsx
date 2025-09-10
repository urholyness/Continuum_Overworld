// File: Agora/Site--GreenStemGlobal__PROD@v1.0.0/src/app/trace/[id]/page.tsx
// Task 1: Real Data Connection for Individual Trace Page

import { notFound } from 'next/navigation';

interface TraceData {
  traceId: string;
  lotNumber: string;
  farm: string;
  product: string;
  harvestDate: string;
  ndvi: number | null;
  temperature: number | null;
  blockchain: string | null;
  events: Array<{
    type: string;
    timestamp: string;
    location?: string;
    details?: any;
  }>;
  certifications: string[];
}

async function getTraceData(id: string): Promise<TraceData | null> {
  const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://cn-api.greenstemglobal.com';
  
  try {
    const res = await fetch(`${apiUrl}/public/trace/${id}`, {
      next: { revalidate: 300 }, // Cache for 5 minutes
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!res.ok) {
      console.error(`Trace API returned ${res.status} for ID: ${id}`);
      return null;
    }
    
    const data = await res.json();
    
    // Transform API response to component format
    return {
      traceId: data.id || id,
      lotNumber: data.lotNumber || id,
      farm: data.farmName || 'Unknown Farm',
      product: data.product || 'Unknown Product',
      harvestDate: data.harvestDate || new Date().toISOString(),
      ndvi: data.satelliteData?.ndvi || null,
      temperature: data.weatherData?.temp || null,
      blockchain: data.blockchainTx || null,
      events: data.timeline || [],
      certifications: data.certifications || []
    };
  } catch (error) {
    console.error('Trace fetch failed:', error);
    return null;
  }
}

export default async function TracePage({ params }: { params: { id: string } }) {
  const trace = await getTraceData(params.id);
  
  if (!trace) {
    notFound();
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-light to-white">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-soil mb-2">Trace Details</h1>
          <p className="text-gray-600">Lot Number: {trace.lotNumber}</p>
        </div>

        {/* Main Info Card */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h2 className="text-xl font-semibold mb-4">Product Information</h2>
              <dl className="space-y-2">
                <div className="flex justify-between">
                  <dt className="text-gray-600">Product:</dt>
                  <dd className="font-medium">{trace.product}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-600">Farm:</dt>
                  <dd className="font-medium">{trace.farm}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-600">Harvest Date:</dt>
                  <dd className="font-medium">
                    {new Date(trace.harvestDate).toLocaleDateString()}
                  </dd>
                </div>
              </dl>
            </div>

            <div>
              <h2 className="text-xl font-semibold mb-4">Environmental Data</h2>
              <dl className="space-y-2">
                {trace.ndvi !== null && (
                  <div className="flex justify-between">
                    <dt className="text-gray-600">NDVI Index:</dt>
                    <dd className="font-medium">{trace.ndvi.toFixed(2)}</dd>
                  </div>
                )}
                {trace.temperature !== null && (
                  <div className="flex justify-between">
                    <dt className="text-gray-600">Temperature:</dt>
                    <dd className="font-medium">{trace.temperature}°C</dd>
                  </div>
                )}
                {trace.blockchain && (
                  <div className="flex justify-between">
                    <dt className="text-gray-600">Blockchain TX:</dt>
                    <dd className="font-mono text-xs truncate max-w-[200px]">
                      {trace.blockchain}
                    </dd>
                  </div>
                )}
              </dl>
            </div>
          </div>
        </div>

        {/* Certifications */}
        {trace.certifications.length > 0 && (
          <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
            <h2 className="text-xl font-semibold mb-4">Certifications</h2>
            <div className="flex flex-wrap gap-2">
              {trace.certifications.map((cert, index) => (
                <span 
                  key={index} 
                  className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm"
                >
                  {cert}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Timeline */}
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h2 className="text-xl font-semibold mb-6">Supply Chain Timeline</h2>
          <div className="space-y-4">
            {trace.events.map((event, index) => (
              <div key={index} className="flex items-start">
                <div className="flex-shrink-0 w-10 h-10 bg-leaf rounded-full flex items-center justify-center text-white">
                  <span className="text-sm font-bold">{index + 1}</span>
                </div>
                <div className="ml-4 flex-grow">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold capitalize">
                        {event.type.replace(/_/g, ' ')}
                      </h3>
                      {event.location && (
                        <p className="text-sm text-gray-600 mt-1">
                          Location: {event.location}
                        </p>
                      )}
                      {event.details && (
                        <p className="text-sm text-gray-600 mt-1">
                          {JSON.stringify(event.details)}
                        </p>
                      )}
                    </div>
                    <span className="text-sm text-gray-500">
                      {new Date(event.timestamp).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
