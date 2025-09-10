// File: Agora/Site--GreenStemGlobal__PROD@v1.0.0/src/app/trace/page.tsx
// Task 1: Updated trace highlights page with real API connection

import Hero from '@/components/Hero';
import Link from 'next/link';
import { MapPin, Package, Truck, Clock, AlertCircle } from 'lucide-react';

interface TraceHighlight {
  id: string;
  timestamp: string;
  type: 'harvest' | 'processing' | 'transport' | 'delivery';
  location: string;
  description: string;
  product?: string;
  quantity?: string;
  lotNumber?: string;
}

async function getHighlights(): Promise<TraceHighlight[]> {
  const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://cn-api.greenstemglobal.com';
  
  try {
    const res = await fetch(`${apiUrl}/public/trace/highlights`, {
      next: { revalidate: 60 }, // Cache for 1 minute
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!res.ok) {
      console.error(`Highlights API returned ${res.status}`);
      return [];
    }
    
    const data = await res.json();
    return data.items || data.events || [];
  } catch (error) {
    console.error('Failed to fetch highlights:', error);
    return [];
  }
}

function getEventIcon(type: string) {
  switch (type) {
    case 'harvest':
      return <MapPin className="h-5 w-5" />;
    case 'processing':
      return <Package className="h-5 w-5" />;
    case 'transport':
      return <Truck className="h-5 w-5" />;
    case 'delivery':
      return <MapPin className="h-5 w-5" />;
    default:
      return <Clock className="h-5 w-5" />;
  }
}

function formatTimestamp(timestamp: string) {
  const date = new Date(timestamp);
  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short'
  }).format(date);
}

export default async function TracePage() {
  const highlights = await getHighlights();

  return (
    <>
      <Hero
        title="Supply Chain Traceability"
        subtitle="View real-time events from our verified supply chain network."
      />

      <section className="py-20 bg-white">
        <div className="container">
          <div className="max-w-4xl mx-auto">
            {/* Info Banner */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
              <div className="flex items-start">
                <AlertCircle className="h-5 w-5 text-blue-600 mr-2 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-blue-800">
                  <p>
                    Public trace data is delayed 24-48 hours for security. 
                    Buyers with active contracts have access to real-time tracking.
                  </p>
                </div>
              </div>
            </div>

            {/* Events Timeline */}
            {highlights.length > 0 ? (
              <>
                <h2 className="text-2xl font-display font-bold mb-8">Recent Supply Chain Events</h2>
                <div className="space-y-6">
                  {highlights.map((event, index) => (
                    <div key={event.id || index} className="flex items-start">
                      <div className="flex-shrink-0 w-10 h-10 bg-leaf/10 rounded-full flex items-center justify-center text-leaf">
                        {getEventIcon(event.type)}
                      </div>
                      <div className="ml-4 flex-grow">
                        <div className="flex items-start justify-between">
                          <div>
                            <h3 className="font-semibold capitalize">{event.type}</h3>
                            <p className="text-gray-600 mt-1">{event.description}</p>
                            {event.product && (
                              <p className="text-sm text-gray-500 mt-1">
                                Product: {event.product}
                                {event.quantity && ` • Quantity: ${event.quantity}`}
                              </p>
                            )}
                            <p className="text-sm text-gray-500 mt-1">
                              Location: {event.location}
                            </p>
                            {event.lotNumber && (
                              <Link 
                                href={`/trace/${event.lotNumber}`}
                                className="text-sm text-leaf hover:underline mt-1 inline-block"
                              >
                                View Full Trace → {event.lotNumber}
                              </Link>
                            )}
                          </div>
                          <span className="text-sm text-gray-500 ml-4">
                            {formatTimestamp(event.timestamp)}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Load More Button (if API supports pagination) */}
                <div className="mt-8 text-center">
                  <p className="text-sm text-gray-500">
                    Showing last {highlights.length} events
                  </p>
                </div>
              </>
            ) : (
              <div className="text-center py-12">
                <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Clock className="h-10 w-10 text-gray-400" />
                </div>
                <p className="text-gray-600 text-lg mb-2">No trace events available</p>
                <p className="text-sm text-gray-500">
                  Check back later for supply chain updates, or contact us for real-time access.
                </p>
              </div>
            )}

            {/* CTA for Buyers */}
            <div className="mt-12 p-6 bg-light rounded-lg text-center">
              <h3 className="text-lg font-semibold mb-2">Need Real-Time Access?</h3>
              <p className="text-gray-600 mb-4">
                Active buyers get immediate access to shipment tracking and quality data.
              </p>
              <Link href="/contact" className="btn-primary inline-block">
                Become a Buyer
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
