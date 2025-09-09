'use client'

import { useState, useEffect } from 'react'
import Hero from '@/components/Hero'
import { MapPin, Package, Truck, Clock, AlertCircle } from 'lucide-react'

interface TraceEvent {
  id: string
  timestamp: string
  type: 'harvest' | 'processing' | 'transport' | 'delivery'
  location: string
  description: string
  product?: string
  quantity?: string
}

export default function TracePage() {
  const [events, setEvents] = useState<TraceEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchTraceData()
  }, [])

  const fetchTraceData = async () => {
    try {
      // Try to fetch from the public trace endpoint
      const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || ''
      const response = await fetch(`${apiUrl}/public/trace/highlights`)
      
      if (response.ok) {
        const data = await response.json()
        setEvents(data.events || [])
      } else {
        // If endpoint is not available, show message instead of dummy data
        setEvents([])
      }
    } catch (err) {
      console.error('Failed to fetch trace data:', err)
      setError('Trace data endpoint not yet configured')
      setEvents([])
    } finally {
      setLoading(false)
    }
  }

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'harvest':
        return <MapPin className="h-5 w-5" />
      case 'processing':
        return <Package className="h-5 w-5" />
      case 'transport':
        return <Truck className="h-5 w-5" />
      case 'delivery':
        return <MapPin className="h-5 w-5" />
      default:
        return <Clock className="h-5 w-5" />
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return new Intl.DateTimeFormat('en-US', {
      dateStyle: 'medium',
      timeStyle: 'short'
    }).format(date)
  }

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
            {loading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-leaf"></div>
                <p className="mt-4 text-gray-600">Loading trace events...</p>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <p className="text-gray-600">{error}</p>
                <p className="mt-2 text-sm text-gray-500">
                  Trace functionality will be available once the backend is deployed.
                </p>
              </div>
            ) : events.length > 0 ? (
              <>
                <h2 className="text-2xl font-display font-bold mb-8">Recent Supply Chain Events</h2>
                <div className="space-y-6">
                  {events.map((event, index) => (
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
                          </div>
                          <span className="text-sm text-gray-500 ml-4">
                            {formatTimestamp(event.timestamp)}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="text-center py-12">
                <p className="text-gray-600">No trace events available at this time.</p>
                <p className="mt-2 text-sm text-gray-500">
                  Check back later for supply chain updates.
                </p>
              </div>
            )}

            {/* CTA for Buyers */}
            <div className="mt-12 p-6 bg-light rounded-lg text-center">
              <h3 className="text-lg font-semibold mb-2">Need Real-Time Access?</h3>
              <p className="text-gray-600 mb-4">
                Active buyers get immediate access to shipment tracking and quality data.
              </p>
              <a href="/contact" className="btn-primary inline-block">
                Become a Buyer
              </a>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
