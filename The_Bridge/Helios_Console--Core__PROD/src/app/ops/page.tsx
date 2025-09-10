import { getOpsMetrics } from "@/lib/api/composer";
import { Suspense } from "react";

export const revalidate = 60; // Revalidate every 60 seconds

async function OpsMetrics() {
  const metrics = await getOpsMetrics();
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {metrics.map((metric, index) => (
        <div key={`${metric.kpi}-${metric.ts}-${index}`} className="rounded-2xl border p-4">
          <div className="text-sm text-muted-foreground">{metric.kpi}</div>
          <div className="text-3xl font-bold">
            {metric.value} 
            <span className="text-base font-normal"> {metric.unit}</span>
          </div>
          <div className="text-xs opacity-70">
            {new Date(metric.ts).toLocaleString()}
          </div>
        </div>
      ))}
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="rounded-2xl border p-4">
          <div className="h-4 bg-muted rounded animate-pulse mb-2"></div>
          <div className="h-8 bg-muted rounded animate-pulse mb-2"></div>
          <div className="h-3 bg-muted rounded animate-pulse w-1/2"></div>
        </div>
      ))}
    </div>
  );
}

export default function OpsPage() {
  return (
    <main className="container mx-auto py-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Operations</h1>
        <div className="text-sm text-muted-foreground">
          Real-time operational metrics
        </div>
      </div>
      
      <Suspense fallback={<LoadingSkeleton />}>
        <OpsMetrics />
      </Suspense>
    </main>
  );
}