import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <main className="container mx-auto py-12">
      <div className="text-center space-y-6">
        <h1 className="text-4xl font-bold tracking-tighter">
          Welcome to Helios Console
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Enterprise Agricultural Data Platform - Monitor operations, trace activities, 
          manage farms, and coordinate agents in real-time.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-4xl mx-auto mt-12">
          <Link href="/ops">
            <div className="p-6 border rounded-lg hover:shadow-lg transition-shadow">
              <h3 className="text-lg font-semibold mb-2">Operations</h3>
              <p className="text-sm text-muted-foreground">
                Monitor real-time operational metrics and KPIs
              </p>
            </div>
          </Link>
          
          <Link href="/trace">
            <div className="p-6 border rounded-lg hover:shadow-lg transition-shadow">
              <h3 className="text-lg font-semibold mb-2">Traceability</h3>
              <p className="text-sm text-muted-foreground">
                Track events and audit trails across the platform
              </p>
            </div>
          </Link>
          
          <Link href="/agents">
            <div className="p-6 border rounded-lg hover:shadow-lg transition-shadow">
              <h3 className="text-lg font-semibold mb-2">Agents</h3>
              <p className="text-sm text-muted-foreground">
                Monitor agent status and performance metrics
              </p>
            </div>
          </Link>
          
          <Link href="/admin/farms">
            <div className="p-6 border rounded-lg hover:shadow-lg transition-shadow">
              <h3 className="text-lg font-semibold mb-2">Admin</h3>
              <p className="text-sm text-muted-foreground">
                Manage farms and administrative functions
              </p>
            </div>
          </Link>
        </div>
      </div>
    </main>
  );
}