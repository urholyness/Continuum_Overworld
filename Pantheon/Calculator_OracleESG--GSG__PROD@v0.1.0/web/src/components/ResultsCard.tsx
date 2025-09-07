import React, { useState } from 'react';
import { calculationApi } from '@/api';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { useToast } from './ui/use-toast';
import { 
  Copy, 
  Download, 
  BarChart3, 
  Leaf, 
  Factory, 
  Zap, 
  Truck,
  Target,
  FileText
} from 'lucide-react';

interface ResultsCardProps {
  results: any;
  batchId: number | null;
}

export function ResultsCard({ results, batchId }: ResultsCardProps) {
  const { toast } = useToast();
  const [cbamSnippet, setCbamSnippet] = useState<string>('');
  const [loadingSnippet, setLoadingSnippet] = useState(false);

  const { iso14083, glec, ghg_protocol, intensity } = results;

  const handleCopySnippet = async () => {
    if (!batchId) return;
    
    try {
      setLoadingSnippet(true);
      const snippet = await calculationApi.getCbamSnippet(batchId);
      setCbamSnippet(snippet);
      
      await navigator.clipboard.writeText(snippet);
      toast({
        title: 'CBAM Snippet Copied',
        description: 'The embedded emissions snippet has been copied to clipboard',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to generate CBAM snippet',
        variant: 'destructive',
      });
    } finally {
      setLoadingSnippet(false);
    }
  };

  const formatEmissions = (value: number) => {
    if (value >= 1000) {
      return `${(value / 1000).toFixed(2)} tCO₂e`;
    }
    return `${value.toFixed(2)} kgCO₂e`;
  };

  const totalEmissions = iso14083?.totals?.total_kg || 0;
  const scopeTotal = ghg_protocol?.total_tco2e || 0;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Emissions</CardTitle>
            <Leaf className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {formatEmissions(totalEmissions)}
            </div>
            <p className="text-xs text-muted-foreground">
              ISO 14083 compliant
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Carbon Intensity</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {intensity?.toFixed(3) || '0.000'}
            </div>
            <p className="text-xs text-muted-foreground">
              kgCO₂e/kg product
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Transport Legs</CardTitle>
            <Truck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {iso14083?.legs?.length || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Multi-modal supply chain
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Hub Activities</CardTitle>
            <Factory className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {iso14083?.hubs?.length || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Energy consumption
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Results */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Detailed Results
          </CardTitle>
          <CardDescription>
            Comprehensive emission breakdown by methodology
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="iso" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="iso">ISO 14083</TabsTrigger>
              <TabsTrigger value="ghg">GHG Protocol</TabsTrigger>
              <TabsTrigger value="glec">GLEC Framework</TabsTrigger>
            </TabsList>

            <TabsContent value="iso" className="space-y-4">
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold mb-2">Transport Emissions</h4>
                  <div className="space-y-2">
                    {iso14083?.legs?.map((leg: any, idx: number) => (
                      <div key={idx} className="bg-gray-50 p-3 rounded-lg">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-medium">{leg.mode.toUpperCase()}: {leg.from} → {leg.to}</p>
                            <p className="text-sm text-gray-600">
                              {leg.distance_km} km • {leg.vehicle_class?.replace(/_/g, ' ')}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="font-medium">{formatEmissions(leg.total_kg)}</p>
                            <p className="text-xs text-gray-500">
                              TTW: {formatEmissions(leg.ttw_kg)} | WTW: {formatEmissions(leg.wtt_kg)}
                            </p>
                            {leg.rf_applied && (
                              <p className="text-xs bg-orange-100 text-orange-800 px-1 rounded">RF Applied</p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {iso14083?.hubs?.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2">Hub Emissions</h4>
                    <div className="space-y-2">
                      {iso14083.hubs.map((hub: any, idx: number) => (
                        <div key={idx} className="bg-blue-50 p-3 rounded-lg">
                          <div className="flex justify-between">
                            <div>
                              <p className="font-medium">{hub.type.replace('-', ' ').toUpperCase()}</p>
                              <p className="text-sm text-gray-600">
                                {hub.kwh} kWh • {hub.energy_source}
                              </p>
                            </div>
                            <p className="font-medium">{formatEmissions(hub.total_kg)}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="pt-4 border-t">
                  <div className="flex justify-between text-lg font-semibold">
                    <span>Total Emissions:</span>
                    <span className="text-green-600">{formatEmissions(totalEmissions)}</span>
                  </div>
                  <div className="flex justify-between text-sm text-gray-600">
                    <span>TTW (Tank-to-Wheel):</span>
                    <span>{formatEmissions(iso14083?.totals?.ttw_kg || 0)}</span>
                  </div>
                  <div className="flex justify-between text-sm text-gray-600">
                    <span>WTW (Well-to-Tank):</span>
                    <span>{formatEmissions(iso14083?.totals?.wtt_kg || 0)}</span>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="ghg" className="space-y-4">
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card className="bg-blue-50">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-lg flex items-center gap-2">
                        <Factory className="h-5 w-5" />
                        Scope 1
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-2xl font-bold text-blue-600">
                        {(ghg_protocol?.scope1?.emissions_tco2e || 0).toFixed(3)} tCO₂e
                      </p>
                      <p className="text-sm text-gray-600">Direct emissions</p>
                    </CardContent>
                  </Card>

                  <Card className="bg-yellow-50">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-lg flex items-center gap-2">
                        <Zap className="h-5 w-5" />
                        Scope 2
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-2xl font-bold text-yellow-600">
                        {(ghg_protocol?.scope2?.emissions_tco2e || 0).toFixed(3)} tCO₂e
                      </p>
                      <p className="text-sm text-gray-600">Purchased electricity</p>
                    </CardContent>
                  </Card>

                  <Card className="bg-green-50">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-lg flex items-center gap-2">
                        <Truck className="h-5 w-5" />
                        Scope 3
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-2xl font-bold text-green-600">
                        {(ghg_protocol?.scope3?.emissions_tco2e || 0).toFixed(3)} tCO₂e
                      </p>
                      <p className="text-sm text-gray-600">Value chain</p>
                    </CardContent>
                  </Card>
                </div>

                {ghg_protocol?.scope3?.categories && (
                  <div>
                    <h4 className="font-semibold mb-2">Scope 3 Categories</h4>
                    <div className="space-y-2">
                      {Object.entries(ghg_protocol.scope3.categories).map(([cat, data]: [string, any]) => (
                        <div key={cat} className="flex justify-between p-2 bg-gray-50 rounded">
                          <span>Category {cat}: {data.name}</span>
                          <span className="font-medium">{data.emissions_tco2e.toFixed(3)} tCO₂e</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="glec" className="space-y-4">
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold mb-2">Transport Mode Summary</h4>
                  <div className="space-y-2">
                    {glec?.modes && Object.entries(glec.modes).map(([mode, data]: [string, any]) => (
                      <div key={mode} className="bg-gray-50 p-3 rounded-lg">
                        <div className="flex justify-between">
                          <div>
                            <p className="font-medium capitalize">{mode} Transport</p>
                            <p className="text-sm text-gray-600">
                              {data.legs} legs • {data.total_distance_km} km • {data.total_payload_t.toFixed(2)}t
                            </p>
                            <p className="text-xs text-gray-500">
                              Avg load factor: {data.avg_load_factor.toFixed(0)}%
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="font-medium">{formatEmissions(data.total_emissions_kg)}</p>
                            {data.emissions_intensity_g_per_tkm && (
                              <p className="text-xs text-gray-500">
                                {data.emissions_intensity_g_per_tkm.toFixed(1)} g/t.km
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {glec?.hubs && (
                  <div>
                    <h4 className="font-semibold mb-2">Energy Summary</h4>
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-gray-600">Total Energy</p>
                          <p className="font-medium">{glec.hubs.total_kwh} kWh</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Renewable %</p>
                          <p className="font-medium">{glec.hubs.renewable_pct || 0}%</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* CBAM Export */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            CBAM Export
          </CardTitle>
          <CardDescription>
            Carbon Border Adjustment Mechanism compliant embedded emissions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Button 
              onClick={handleCopySnippet} 
              disabled={loadingSnippet}
              className="flex-1"
            >
              <Copy className="h-4 w-4 mr-2" />
              {loadingSnippet ? 'Generating...' : 'Copy CBAM Snippet'}
            </Button>
            
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export PDF
            </Button>
          </div>

          {cbamSnippet && (
            <div className="mt-4">
              <textarea
                readOnly
                value={cbamSnippet}
                className="w-full h-40 p-3 border rounded-md bg-gray-50 text-sm font-mono"
              />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}