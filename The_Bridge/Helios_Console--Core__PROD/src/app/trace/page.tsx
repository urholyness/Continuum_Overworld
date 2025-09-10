import { getTraceEvents } from "@/lib/api/composer";
import { Suspense } from "react";

interface TracePageProps {
  searchParams: { 
    from?: string; 
    to?: string; 
    cursor?: string;
    limit?: string;
  };
}

async function TraceEvents({ searchParams }: TracePageProps) {
  const events = await getTraceEvents({
    from: searchParams.from,
    to: searchParams.to,
    cursor: searchParams.cursor,
    limit: searchParams.limit ? parseInt(searchParams.limit) : undefined,
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          {events.items.length} events
          {events.nextCursor && (
            <span className="ml-2">
              (<a 
                href={`?${new URLSearchParams({ ...searchParams, cursor: events.nextCursor }).toString()}`}
                className="text-blue-600 hover:underline"
              >
                Load more
              </a>)
            </span>
          )}
        </div>
      </div>
      
      {events.items.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No trace events found for the specified time range.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {events.items.map((event, index) => (
            <div key={`${event.id}-${index}`} className="rounded-2xl border p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">{event.type}</span>
                <span className="text-xs text-muted-foreground">
                  {new Date(event.ts).toLocaleString()}
                </span>
              </div>
              
              {event.actor && (
                <div className="text-xs text-muted-foreground mb-2">
                  Actor: {event.actor}
                </div>
              )}
              
              <pre className="text-xs bg-muted p-2 rounded overflow-x-auto">
                {JSON.stringify(event.payload, null, 2)}
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-2">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="rounded-2xl border p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="h-4 bg-muted rounded animate-pulse w-1/4"></div>
            <div className="h-3 bg-muted rounded animate-pulse w-1/6"></div>
          </div>
          <div className="h-20 bg-muted rounded animate-pulse"></div>
        </div>
      ))}
    </div>
  );
}

export default function TracePage({ searchParams }: TracePageProps) {
  return (
    <main className="container mx-auto py-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold">Traceability</h1>
        <div className="text-sm text-muted-foreground">
          Event audit trail
        </div>
      </div>
      
      <Suspense fallback={<LoadingSkeleton />}>
        <TraceEvents searchParams={searchParams} />
      </Suspense>
    </main>
  );
}