import { listAgents } from "@/lib/api/admin";
import { Suspense } from "react";

async function AgentsList() {
  const agents = await listAgents();

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'bg-green-100 text-green-800';
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800';
      case 'offline':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-4">
      <div className="text-sm text-muted-foreground">
        {agents.length} agents
      </div>
      
      {agents.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No agents found.</p>
        </div>
      ) : (
        <ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <li key={agent.id} className="border rounded-2xl p-4 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="font-medium text-lg">{agent.name}</h3>
                <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                  getStatusColor(agent.status)
                }`}>
                  {agent.status}
                </span>
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Role:</span>
                  <span>{agent.role}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Tier:</span>
                  <span>{agent.tier}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">ID:</span>
                  <span className="text-xs font-mono">{agent.id}</span>
                </div>
              </div>
              
              <div className="pt-2 border-t">
                <div className="flex space-x-2">
                  <button className="text-xs text-blue-600 hover:underline">
                    View Details
                  </button>
                  <button className="text-xs text-blue-600 hover:underline">
                    Logs
                  </button>
                  <button className="text-xs text-blue-600 hover:underline">
                    Metrics
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-4">
      <div className="h-4 bg-muted rounded animate-pulse w-1/4"></div>
      
      <ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <li key={i} className="border rounded-2xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="h-5 bg-muted rounded animate-pulse w-1/2"></div>
              <div className="h-5 bg-muted rounded-full animate-pulse w-16"></div>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between">
                <div className="h-4 bg-muted rounded animate-pulse w-1/4"></div>
                <div className="h-4 bg-muted rounded animate-pulse w-1/3"></div>
              </div>
              <div className="flex justify-between">
                <div className="h-4 bg-muted rounded animate-pulse w-1/4"></div>
                <div className="h-4 bg-muted rounded animate-pulse w-1/4"></div>
              </div>
              <div className="flex justify-between">
                <div className="h-4 bg-muted rounded animate-pulse w-1/6"></div>
                <div className="h-4 bg-muted rounded animate-pulse w-1/2"></div>
              </div>
            </div>
            
            <div className="pt-2 border-t">
              <div className="flex space-x-2">
                <div className="h-3 bg-muted rounded animate-pulse w-16"></div>
                <div className="h-3 bg-muted rounded animate-pulse w-12"></div>
                <div className="h-3 bg-muted rounded animate-pulse w-16"></div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function AgentsPage() {
  return (
    <main className="container mx-auto py-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold">Agents</h1>
        <div className="text-sm text-muted-foreground">
          Monitor agent status and performance
        </div>
      </div>
      
      <Suspense fallback={<LoadingSkeleton />}>
        <AgentsList />
      </Suspense>
    </main>
  );
}