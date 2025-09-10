// File: The_Bridge/Helios_Console--Core__PROD/src/app/admin/oracle-status/page.tsx
// Task 2: Oracle Status Dashboard Page

import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Oracle Services Status',
  description: 'Monitor oracle services health and costs',
};

// Card components (would be imported from shadcn/ui in real implementation)
interface CardProps {
  children: React.ReactNode;
  className?: string;
}

function Card({ children, className = '' }: CardProps) {
  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
      {children}
    </div>
  );
}

function CardHeader({ children }: { children: React.ReactNode }) {
  return <div className="px-6 py-4 border-b border-gray-200">{children}</div>;
}

function CardTitle({ children }: { children: React.ReactNode }) {
  return <h3 className="text-lg font-semibold text-gray-900">{children}</h3>;
}

function CardContent({ children }: { children: React.ReactNode }) {
  return <div className="px-6 py-4">{children}</div>;
}

// Get JWT token (simplified - would use proper auth in production)
async function getJWT(): Promise<string> {
  // In production, this would fetch from auth service or session
  return process.env.ADMIN_JWT_TOKEN || '';
}

interface OracleStatus {
  satellite: {
    lastHourCount: number;
    estimatedCost: number;
    status: 'online' | 'offline' | 'degraded';
    lastUpdate?: string;
  };
  weather: {
    last24HourCount: number;
    estimatedCost: number;
    status: 'online' | 'offline' | 'degraded';
    lastUpdate?: string;
  };
  blockchain: {
    lastHourCount: number;
    gasUsed: number;
    estimatedCost: number;
    status: 'online' | 'offline' | 'degraded';
  };
  totalDailyCost: number;
  timestamp: string;
}

async function getOracleStatus(): Promise<OracleStatus> {
  const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://cn-api.greenstemglobal.com';
  
  try {
    const res = await fetch(`${apiUrl}/admin/oracle-status`, {
      headers: { 
        Authorization: `Bearer ${await getJWT()}`,
        'Content-Type': 'application/json'
      },
      next: { revalidate: 60 } // Cache for 1 minute
    });
    
    if (!res.ok) {
      throw new Error(`Failed to fetch oracle status: ${res.status}`);
    }
    
    return await res.json();
  } catch (error) {
    console.error('Oracle status fetch failed:', error);
    // Return default status on error
    return {
      satellite: { lastHourCount: 0, estimatedCost: 0, status: 'offline' },
      weather: { last24HourCount: 0, estimatedCost: 0, status: 'offline' },
      blockchain: { lastHourCount: 0, gasUsed: 0, estimatedCost: 0, status: 'offline' },
      totalDailyCost: 0,
      timestamp: new Date().toISOString()
    };
  }
}

function StatusBadge({ status }: { status: 'online' | 'offline' | 'degraded' }) {
  const colors = {
    online: 'bg-green-100 text-green-800',
    offline: 'bg-red-100 text-red-800',
    degraded: 'bg-yellow-100 text-yellow-800'
  };
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[status]}`}>
      {status.toUpperCase()}
    </span>
  );
}

export default async function OracleStatusPage() {
  const status = await getOracleStatus();
  
  return (
    <main className="p-6 space-y-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Oracle Services Status</h1>
          <p className="text-sm text-gray-500 mt-1">
            Last updated: {new Date(status.timestamp).toLocaleString()}
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-6">
          {/* Satellite Oracle Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Satellite Oracle</CardTitle>
                <StatusBadge status={status.satellite.status} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Status</span>
                  <span className={`font-medium ${
                    status.satellite.status === 'online' ? 'text-green-600' : 
                    status.satellite.status === 'degraded' ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {status.satellite.status}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Last Hour</span>
                  <span className="font-medium">{status.satellite.lastHourCount} images</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Cost</span>
                  <span className="font-medium">${status.satellite.estimatedCost.toFixed(2)}</span>
                </div>
                {status.satellite.lastUpdate && (
                  <div className="pt-2 border-t">
                    <span className="text-xs text-gray-500">
                      Last update: {new Date(status.satellite.lastUpdate).toLocaleTimeString()}
                    </span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
          
          {/* Weather Oracle Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Weather Oracle</CardTitle>
                <StatusBadge status={status.weather.status} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Status</span>
                  <span className={`font-medium ${
                    status.weather.status === 'online' ? 'text-green-600' : 
                    status.weather.status === 'degraded' ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {status.weather.status}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Last 24 Hours</span>
                  <span className="font-medium">{status.weather.last24HourCount} calls</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Cost</span>
                  <span className="font-medium">${status.weather.estimatedCost.toFixed(2)}</span>
                </div>
                {status.weather.lastUpdate && (
                  <div className="pt-2 border-t">
                    <span className="text-xs text-gray-500">
                      Last update: {new Date(status.weather.lastUpdate).toLocaleTimeString()}
                    </span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Blockchain Oracle Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Blockchain Oracle</CardTitle>
                <StatusBadge status={status.blockchain.status} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Status</span>
                  <span className={`font-medium ${
                    status.blockchain.status === 'online' ? 'text-green-600' : 
                    status.blockchain.status === 'degraded' ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {status.blockchain.status}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Last Hour</span>
                  <span className="font-medium">{status.blockchain.lastHourCount} txs</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Gas Used</span>
                  <span className="font-medium">{status.blockchain.gasUsed.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Cost</span>
                  <span className="font-medium">${status.blockchain.estimatedCost.toFixed(2)}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Total Cost Summary */}
        <Card className="mt-6">
          <CardContent>
            <div className="text-center py-4">
              <p className="text-sm text-gray-600 mb-2">Estimated Daily Cost</p>
              <p className="text-4xl font-bold text-gray-900">
                ${status.totalDailyCost.toFixed(2)}
              </p>
              <p className="text-xs text-gray-500 mt-2">
                Based on current usage patterns
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Cost Breakdown Chart (placeholder) */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Cost Breakdown (Last 7 Days)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
              <p className="text-gray-500 text-sm">
                Chart visualization would be rendered here using recharts or similar library
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
