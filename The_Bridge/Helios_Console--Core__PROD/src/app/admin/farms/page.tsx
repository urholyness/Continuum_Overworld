import { listFarms } from "@/lib/api/admin";
import { Suspense } from "react";
import { Button } from "@/components/ui/button";

async function FarmsTable() {
  const farms = await listFarms();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          {farms.length} farms
        </div>
        <Button size="sm">Add Farm</Button>
      </div>
      
      {farms.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No farms found.</p>
        </div>
      ) : (
        <div className="border rounded-2xl overflow-hidden">
          <table className="w-full">
            <thead className="border-b bg-muted/50">
              <tr>
                <th className="p-3 text-left text-sm font-medium">Name</th>
                <th className="p-3 text-left text-sm font-medium">Region</th>
                <th className="p-3 text-left text-sm font-medium">Hectares</th>
                <th className="p-3 text-left text-sm font-medium">Status</th>
                <th className="p-3 text-left text-sm font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {farms.map((farm, index) => (
                <tr key={farm.id} className={index > 0 ? "border-t" : ""}>
                  <td className="p-3 font-medium">{farm.name}</td>
                  <td className="p-3 text-muted-foreground">{farm.region}</td>
                  <td className="p-3 text-muted-foreground">{farm.hectares}</td>
                  <td className="p-3">
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                      farm.status === 'active' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {farm.status}
                    </span>
                  </td>
                  <td className="p-3">
                    <div className="flex space-x-2">
                      <Button variant="outline" size="sm">Edit</Button>
                      <Button variant="outline" size="sm">View</Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="h-4 bg-muted rounded animate-pulse w-1/4"></div>
        <div className="h-8 bg-muted rounded animate-pulse w-20"></div>
      </div>
      
      <div className="border rounded-2xl overflow-hidden">
        <div className="border-b bg-muted/50 p-3">
          <div className="flex space-x-4">
            {['Name', 'Region', 'Hectares', 'Status', 'Actions'].map((header, i) => (
              <div key={i} className="h-4 bg-muted rounded animate-pulse flex-1"></div>
            ))}
          </div>
        </div>
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="p-3 border-t">
            <div className="flex space-x-4">
              <div className="h-4 bg-muted rounded animate-pulse flex-1"></div>
              <div className="h-4 bg-muted rounded animate-pulse flex-1"></div>
              <div className="h-4 bg-muted rounded animate-pulse flex-1"></div>
              <div className="h-4 bg-muted rounded animate-pulse flex-1"></div>
              <div className="h-4 bg-muted rounded animate-pulse flex-1"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function FarmsAdminPage() {
  return (
    <main className="container mx-auto py-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Farms Administration</h1>
        <div className="text-sm text-muted-foreground">
          Manage farm registrations and configurations
        </div>
      </div>
      
      <Suspense fallback={<LoadingSkeleton />}>
        <FarmsTable />
      </Suspense>
    </main>
  );
}