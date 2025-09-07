'use client';

import { useEffect } from 'react';
import L from 'leaflet';
import { MapContainer, TileLayer, Polygon, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in Next.js
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

interface MapProps {
  farmPolygon?: any;
}

export default function Map({ farmPolygon }: MapProps) {
  const defaultCenter: [number, number] = [-0.5143, 35.2698];
  const defaultPolygon = [
    [35.2648, -0.5193],
    [35.2748, -0.5193],
    [35.2748, -0.5093],
    [35.2648, -0.5093],
    [35.2648, -0.5193]
  ];

  const polygonCoords = farmPolygon?.geometry?.coordinates?.[0] || defaultPolygon;
  // Leaflet expects [lat, lng] but GeoJSON is [lng, lat]
  const leafletCoords = polygonCoords.map((coord: number[]) => [coord[1], coord[0]] as [number, number]);

  return (
    <MapContainer
      center={defaultCenter}
      zoom={14}
      style={{ height: '100%', width: '100%' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Polygon
        positions={leafletCoords}
        pathOptions={{
          color: '#2F7D32',
          weight: 3,
          opacity: 0.8,
          fillColor: '#4CAF50',
          fillOpacity: 0.3
        }}
      />
      <Marker position={defaultCenter}>
        <Popup>
          Two Butterflies Homestead<br />
          Eldoret, Kenya
        </Popup>
      </Marker>
    </MapContainer>
  );
}