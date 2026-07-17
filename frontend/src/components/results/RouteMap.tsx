import { useEffect } from 'react'
import { MapContainer, Marker, Polyline, TileLayer, Tooltip, useMap } from 'react-leaflet'
import L from 'leaflet'
import type { LatLngBoundsExpression, LatLngExpression } from 'leaflet'
import type { Stop } from '../../types/trip'

type RouteMapProps = {
  routePositions: [number, number][]
  stops: Stop[]
}

const stopLabels: Record<string, string> = {
  start: 'S',
  pickup: 'P',
  dropoff: 'D',
  fuel: 'F',
  break: 'B',
  daily_rest: 'R',
  restart: '34',
}

export function RouteMap({ routePositions, stops }: RouteMapProps) {
  const mapCenter = routePositions[0] ?? [39.5, -98.35]

  return (
    <MapContainer center={mapCenter} zoom={5} scrollWheelZoom className="route-map">
      <TileLayer attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <Polyline positions={routePositions} pathOptions={{ color: '#27d4c4', weight: 6, opacity: 0.9 }} />
      {stops.map((stop, index) => (
        <Marker key={`${stop.type}-${index}`} position={stop.coordinate} icon={markerIcon(stop.type)}>
          <Tooltip direction="top">
            <strong>{stop.title}</strong><br />{stop.location}<br />{stop.mile !== null ? `${stop.mile} mi` : ''}
          </Tooltip>
        </Marker>
      ))}
      <FitBounds positions={routePositions} />
    </MapContainer>
  )
}

function FitBounds({ positions }: { positions: LatLngExpression[] }) {
  const map = useMap()

  useEffect(() => {
    if (positions.length > 1) {
      map.fitBounds(positions as LatLngBoundsExpression, { padding: [28, 28] })
    }
  }, [map, positions])

  return null
}

function markerIcon(type: string) {
  return L.divIcon({
    className: `stop-marker stop-marker-${type}`,
    html: `<span>${stopLabels[type] ?? '.'}</span>`,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
  })
}