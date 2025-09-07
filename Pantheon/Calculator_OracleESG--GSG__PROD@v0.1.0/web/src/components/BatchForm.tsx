import React, { useState } from 'react';
import { batchApi, legApi, hubApi, calculationApi, Batch, Leg, Hub } from '@/api';
import { LegRepeater } from './LegRepeater';
import { HubForm } from './HubForm';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { useToast } from './ui/use-toast';
import { Calculator, Package, Truck } from 'lucide-react';

interface BatchFormProps {
  onCalculate: (results: any, batchId: number) => void;
}

export function BatchForm({ onCalculate }: BatchFormProps) {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  
  // Default French beans example
  const [batch, setBatch] = useState<Batch>({
    project_tag: 'GSG-FB-2025-W34',
    commodity: 'French beans',
    net_mass_kg: 1000,
    packaging_mass_kg: 80,
    harvest_week: '2025-W34',
    ownership: '3PL',
  });

  const [legs, setLegs] = useState<Leg[]>([
    {
      mode: 'truck',
      from_loc: 'Eldoret',
      to_loc: 'NBO',
      distance_km: 320,
      payload_t: 1.08,
      load_factor_pct: 70,
      backhaul: false,
      vehicle_class: 'Rigid_7.5-12t_Euro6',
      energy_type: 'diesel_l',
      date: '2025-08-28',
      data_quality: 'default',
    },
    {
      mode: 'air',
      from_loc: 'NBO',
      to_loc: 'FRA',
      distance_km: 6200,
      payload_t: 1.08,
      vehicle_class: 'Widebody_Freighter',
      rf_apply: true,
      date: '2025-08-29',
      data_quality: 'default',
    },
    {
      mode: 'rail',
      from_loc: 'FRA',
      to_loc: 'Hamburg',
      distance_km: 500,
      payload_t: 1.08,
      vehicle_class: 'EU_Freight_Rail_Avg',
      date: '2025-08-30',
      data_quality: 'default',
    },
  ]);

  const [hubs, setHubs] = useState<Hub[]>([
    {
      type: 'packhouse',
      kwh: 120,
      energy_source: 'solar',
      hours: 24,
      location: 'Eldoret',
    },
  ]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Create batch
      const createdBatch = await batchApi.create(batch);
      const batchId = createdBatch.id;

      // Add legs
      if (legs.length > 0) {
        await legApi.create(batchId, legs);
      }

      // Add hubs
      if (hubs.length > 0) {
        await hubApi.create(batchId, hubs);
      }

      // Calculate emissions
      const results = await calculationApi.calculate(batchId);
      
      toast({
        title: 'Calculation Complete',
        description: `Batch ${batch.project_tag} calculated successfully`,
      });

      onCalculate(results, batchId);
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to calculate emissions',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="h-5 w-5" />
            Batch Information
          </CardTitle>
          <CardDescription>
            Enter shipment batch details for emission calculation
          </CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="project_tag">Project Tag</Label>
            <Input
              id="project_tag"
              value={batch.project_tag}
              onChange={(e) => setBatch({ ...batch, project_tag: e.target.value })}
              placeholder="GSG-FB-2025-W34"
              required
            />
          </div>
          
          <div>
            <Label htmlFor="commodity">Commodity</Label>
            <Input
              id="commodity"
              value={batch.commodity}
              onChange={(e) => setBatch({ ...batch, commodity: e.target.value })}
              placeholder="French beans"
              required
            />
          </div>
          
          <div>
            <Label htmlFor="net_mass">Net Mass (kg)</Label>
            <Input
              id="net_mass"
              type="number"
              value={batch.net_mass_kg}
              onChange={(e) => setBatch({ ...batch, net_mass_kg: parseFloat(e.target.value) })}
              required
            />
          </div>
          
          <div>
            <Label htmlFor="pkg_mass">Packaging Mass (kg)</Label>
            <Input
              id="pkg_mass"
              type="number"
              value={batch.packaging_mass_kg}
              onChange={(e) => setBatch({ ...batch, packaging_mass_kg: parseFloat(e.target.value) })}
              required
            />
          </div>
          
          <div>
            <Label htmlFor="harvest_week">Harvest Week</Label>
            <Input
              id="harvest_week"
              value={batch.harvest_week || ''}
              onChange={(e) => setBatch({ ...batch, harvest_week: e.target.value })}
              placeholder="2025-W34"
            />
          </div>
          
          <div>
            <Label htmlFor="ownership">Ownership</Label>
            <Select
              value={batch.ownership}
              onValueChange={(value) => setBatch({ ...batch, ownership: value })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="own">Own Fleet</SelectItem>
                <SelectItem value="3PL">Third Party Logistics</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Truck className="h-5 w-5" />
            Transport Legs
          </CardTitle>
          <CardDescription>
            Define each transport segment in the supply chain
          </CardDescription>
        </CardHeader>
        <CardContent>
          <LegRepeater legs={legs} setLegs={setLegs} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Hub Activities</CardTitle>
          <CardDescription>
            Add packhouse, cold storage, and cross-dock energy usage
          </CardDescription>
        </CardHeader>
        <CardContent>
          <HubForm hubs={hubs} setHubs={setHubs} />
        </CardContent>
      </Card>

      <div className="flex justify-end gap-4">
        <Button
          type="button"
          variant="outline"
          onClick={() => {
            setBatch({
              project_tag: 'GSG-FB-2025-W34',
              commodity: 'French beans',
              net_mass_kg: 1000,
              packaging_mass_kg: 80,
              harvest_week: '2025-W34',
              ownership: '3PL',
            });
          }}
        >
          Reset to Example
        </Button>
        
        <Button type="submit" disabled={loading}>
          <Calculator className="h-4 w-4 mr-2" />
          {loading ? 'Calculating...' : 'Calculate Emissions'}
        </Button>
      </div>
    </form>
  );
}