import React from 'react';
import { Hub } from '@/api';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Plus, Minus, Zap, Building, Snowflake } from 'lucide-react';

interface HubFormProps {
  hubs: Hub[];
  setHubs: React.Dispatch<React.SetStateAction<Hub[]>>;
}

const hubTypes = [
  { value: 'packhouse', label: 'Pack House', icon: Building },
  { value: 'x-dock', label: 'Cross Dock', icon: Building },
  { value: 'cold-storage', label: 'Cold Storage', icon: Snowflake },
];

const energySources = [
  { value: 'grid', label: 'Grid Electricity' },
  { value: 'solar', label: 'Solar PV' },
  { value: 'wind', label: 'Wind' },
  { value: 'diesel', label: 'Diesel Generator' },
];

export function HubForm({ hubs, setHubs }: HubFormProps) {
  const addHub = () => {
    const newHub: Hub = {
      type: 'packhouse',
      kwh: 0,
      energy_source: 'grid',
      hours: 24,
      location: '',
    };
    setHubs([...hubs, newHub]);
  };

  const removeHub = (index: number) => {
    setHubs(hubs.filter((_, i) => i !== index));
  };

  const updateHub = (index: number, field: keyof Hub, value: any) => {
    const updatedHubs = hubs.map((hub, i) => {
      if (i === index) {
        return { ...hub, [field]: value };
      }
      return hub;
    });
    setHubs(updatedHubs);
  };

  return (
    <div className="space-y-4">
      {hubs.map((hub, index) => {
        const HubIcon = hubTypes.find(t => t.value === hub.type)?.icon || Building;
        
        return (
          <Card key={index} className="relative">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center gap-2">
                  <HubIcon className="h-5 w-5" />
                  {hubTypes.find(t => t.value === hub.type)?.label} {index + 1}
                </CardTitle>
                {hubs.length > 1 && (
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => removeHub(index)}
                  >
                    <Minus className="h-4 w-4" />
                  </Button>
                )}
              </div>
              <CardDescription>
                {hub.kwh > 0 ? `${hub.kwh} kWh` : 'No energy usage'} 
                {hub.location && ` • ${hub.location}`}
              </CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor={`hub-type-${index}`}>Hub Type</Label>
                  <Select
                    value={hub.type}
                    onValueChange={(value) => updateHub(index, 'type', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {hubTypes.map((type) => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor={`energy-source-${index}`}>Energy Source</Label>
                  <Select
                    value={hub.energy_source}
                    onValueChange={(value) => updateHub(index, 'energy_source', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {energySources.map((source) => (
                        <SelectItem key={source.value} value={source.value}>
                          {source.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor={`kwh-${index}`}>Energy Usage (kWh)</Label>
                  <Input
                    id={`kwh-${index}`}
                    type="number"
                    step="0.1"
                    value={hub.kwh}
                    onChange={(e) => updateHub(index, 'kwh', parseFloat(e.target.value) || 0)}
                    placeholder="0"
                  />
                </div>
                
                <div>
                  <Label htmlFor={`hours-${index}`}>Operating Hours</Label>
                  <Input
                    id={`hours-${index}`}
                    type="number"
                    step="0.5"
                    value={hub.hours || ''}
                    onChange={(e) => updateHub(index, 'hours', parseFloat(e.target.value))}
                    placeholder="24"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor={`location-${index}`}>Location</Label>
                <Input
                  id={`location-${index}`}
                  value={hub.location || ''}
                  onChange={(e) => updateHub(index, 'location', e.target.value)}
                  placeholder="Hub location"
                />
              </div>
            </CardContent>
          </Card>
        );
      })}
      
      <Button
        type="button"
        variant="outline"
        onClick={addHub}
        className="w-full"
      >
        <Plus className="h-4 w-4 mr-2" />
        Add Hub Activity
      </Button>
    </div>
  );
}