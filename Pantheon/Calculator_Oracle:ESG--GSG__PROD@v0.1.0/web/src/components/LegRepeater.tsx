import React from 'react';
import { Leg } from '@/api';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Plus, Minus, Truck, Plane, Ship, Train } from 'lucide-react';

interface LegRepeaterProps {
  legs: Leg[];
  setLegs: React.Dispatch<React.SetStateAction<Leg[]>>;
}

const transportModes = [
  { value: 'truck', label: 'Truck', icon: Truck },
  { value: 'air', label: 'Air Freight', icon: Plane },
  { value: 'rail', label: 'Rail', icon: Train },
  { value: 'ship', label: 'Sea Freight', icon: Ship },
];

const vehicleClasses = {
  truck: [
    'Rigid_3.5-7.5t_Euro6',
    'Rigid_7.5-12t_Euro6',
    'Rigid_12-14t_Euro6',
    'Articulated_14-20t_Euro6',
    'Articulated_20-26t_Euro6',
    'Articulated_26-28t_Euro6',
    'Articulated_28-34t_Euro6',
    'Articulated_>34t_Euro6',
  ],
  air: [
    'Narrowbody_Freighter',
    'Widebody_Freighter',
    'Passenger_Belly_Narrowbody',
    'Passenger_Belly_Widebody',
  ],
  rail: [
    'EU_Freight_Rail_Avg',
    'UK_Freight_Rail',
    'Electric_Rail',
    'Diesel_Rail',
  ],
  ship: [
    'Container_Ship_Small',
    'Container_Ship_Large',
    'Bulk_Carrier',
    'RoRo_Ferry',
    'General_Cargo',
  ],
};

export function LegRepeater({ legs, setLegs }: LegRepeaterProps) {
  const addLeg = () => {
    const newLeg: Leg = {
      mode: 'truck',
      from_loc: '',
      to_loc: '',
      distance_km: 0,
      payload_t: 1.0,
      load_factor_pct: 80,
      backhaul: false,
      vehicle_class: 'Rigid_7.5-12t_Euro6',
      data_quality: 'default',
    };
    setLegs([...legs, newLeg]);
  };

  const removeLeg = (index: number) => {
    setLegs(legs.filter((_, i) => i !== index));
  };

  const updateLeg = (index: number, field: keyof Leg, value: any) => {
    const updatedLegs = legs.map((leg, i) => {
      if (i === index) {
        const updated = { ...leg, [field]: value };
        // Auto-update vehicle class when mode changes
        if (field === 'mode') {
          updated.vehicle_class = vehicleClasses[value as keyof typeof vehicleClasses][0];
          updated.rf_apply = value === 'air';
        }
        return updated;
      }
      return leg;
    });
    setLegs(updatedLegs);
  };

  return (
    <div className="space-y-4">
      {legs.map((leg, index) => {
        const ModeIcon = transportModes.find(m => m.value === leg.mode)?.icon || Truck;
        
        return (
          <Card key={index} className="relative">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center gap-2">
                  <ModeIcon className="h-5 w-5" />
                  Leg {index + 1} - {transportModes.find(m => m.value === leg.mode)?.label}
                </CardTitle>
                {legs.length > 1 && (
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => removeLeg(index)}
                  >
                    <Minus className="h-4 w-4" />
                  </Button>
                )}
              </div>
              <CardDescription>
                {leg.from_loc || 'Origin'} → {leg.to_loc || 'Destination'} 
                {leg.distance_km ? ` (${leg.distance_km} km)` : ''}
              </CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor={`mode-${index}`}>Transport Mode</Label>
                  <Select
                    value={leg.mode}
                    onValueChange={(value) => updateLeg(index, 'mode', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {transportModes.map((mode) => (
                        <SelectItem key={mode.value} value={mode.value}>
                          {mode.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor={`vehicle-${index}`}>Vehicle Class</Label>
                  <Select
                    value={leg.vehicle_class}
                    onValueChange={(value) => updateLeg(index, 'vehicle_class', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {vehicleClasses[leg.mode as keyof typeof vehicleClasses]?.map((cls) => (
                        <SelectItem key={cls} value={cls}>
                          {cls.replace(/_/g, ' ')}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor={`from-${index}`}>From</Label>
                  <Input
                    id={`from-${index}`}
                    value={leg.from_loc}
                    onChange={(e) => updateLeg(index, 'from_loc', e.target.value)}
                    placeholder="Origin location"
                  />
                </div>
                
                <div>
                  <Label htmlFor={`to-${index}`}>To</Label>
                  <Input
                    id={`to-${index}`}
                    value={leg.to_loc}
                    onChange={(e) => updateLeg(index, 'to_loc', e.target.value)}
                    placeholder="Destination location"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label htmlFor={`distance-${index}`}>Distance (km)</Label>
                  <Input
                    id={`distance-${index}`}
                    type="number"
                    step="0.1"
                    value={leg.distance_km || ''}
                    onChange={(e) => updateLeg(index, 'distance_km', parseFloat(e.target.value))}
                    placeholder="0"
                  />
                </div>
                
                <div>
                  <Label htmlFor={`payload-${index}`}>Payload (tonnes)</Label>
                  <Input
                    id={`payload-${index}`}
                    type="number"
                    step="0.01"
                    value={leg.payload_t}
                    onChange={(e) => updateLeg(index, 'payload_t', parseFloat(e.target.value))}
                  />
                </div>
                
                <div>
                  <Label htmlFor={`load-factor-${index}`}>Load Factor (%)</Label>
                  <Input
                    id={`load-factor-${index}`}
                    type="number"
                    min="1"
                    max="100"
                    value={leg.load_factor_pct || 100}
                    onChange={(e) => updateLeg(index, 'load_factor_pct', parseFloat(e.target.value))}
                  />
                </div>
              </div>

              <div className="flex gap-4">
                {leg.mode === 'air' && (
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id={`rf-${index}`}
                      checked={leg.rf_apply || false}
                      onChange={(e) => updateLeg(index, 'rf_apply', e.target.checked)}
                      className="rounded border-gray-300"
                    />
                    <Label htmlFor={`rf-${index}`}>Apply Radiative Forcing</Label>
                  </div>
                )}
                
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id={`backhaul-${index}`}
                    checked={leg.backhaul || false}
                    onChange={(e) => updateLeg(index, 'backhaul', e.target.checked)}
                    className="rounded border-gray-300"
                  />
                  <Label htmlFor={`backhaul-${index}`}>Backhaul</Label>
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
      
      <Button
        type="button"
        variant="outline"
        onClick={addLeg}
        className="w-full"
      >
        <Plus className="h-4 w-4 mr-2" />
        Add Transport Leg
      </Button>
    </div>
  );
}