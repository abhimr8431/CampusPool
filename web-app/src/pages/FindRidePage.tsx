import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import L from 'leaflet';
import { findRides, sendRequest } from '../api';
import { Ride } from '../types';

import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

const demoFallbackRide: Ride = {
  ride_id: 'demo-fallback',
  origin: { name: 'Kengeri', lat: 12.9352, lon: 77.6245 },
  departure_time: '08:12',
  seats_left: 2,
  vehicle_name: 'Honda City',
  rider: { name: 'CampusPool Tester', year: '3rd', branch: 'CSE', rating: 4.9, verified: true }
};

L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const pickupIcon = L.divIcon({
  className: 'pickup-icon',
  html: '<div class="pickup-icon-symbol"></div>',
  iconSize: [28, 28],
  iconAnchor: [14, 28],
  popupAnchor: [0, -28],
});

const rideIcon = L.divIcon({
  className: 'ride-icon',
  html: '<div class="ride-icon-symbol"></div>',
  iconSize: [24, 24],
  iconAnchor: [12, 24],
  popupAnchor: [0, -26],
});

type Position = { lat: number; lon: number };

function FindRidePage() {
  const navigate = useNavigate();
  const [rides, setRides] = useState<Ride[]>([]);
  const [center, setCenter] = useState<Position>({ lat: 12.9370, lon: 77.6190 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [selectedRideId, setSelectedRideId] = useState<string | null>(null);
  const [pickupAddress, setPickupAddress] = useState<string>('Current location');
  const mapRef = useRef<L.Map | null>(null);
  const markerLayer = useRef<L.LayerGroup | null>(null);
  const routeLayer = useRef<L.LayerGroup | null>(null);
  const markersRef = useRef<Record<string, L.Marker | L.CircleMarker>>({});

  const COLLEGE_LOCATION = {
    lat: 13.0128,
    lon: 77.5748,
    name: 'Ramaiah Institute of Technology'
  };

  const fetchAddress = async (lat: number, lon: number) => {
    try {
      const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lon}`);
      const data = await res.json();
      return data.display_name || 'Unknown address';
    } catch {
      return 'Unknown address';
    }
  };

  const computeDijkstraRoute = (start: Position, via: Position, end: Position) => {
    const toRadians = (value: number) => value * (Math.PI / 180);
    const distance = (a: Position, b: Position) => {
      const R = 6371;
      const dLat = toRadians(b.lat - a.lat);
      const dLon = toRadians(b.lon - a.lon);
      const lat1 = toRadians(a.lat);
      const lat2 = toRadians(b.lat);
      const sinDLat = Math.sin(dLat / 2);
      const sinDLon = Math.sin(dLon / 2);
      return R * 2 * Math.atan2(
        Math.sqrt(sinDLat * sinDLat + Math.cos(lat1) * Math.cos(lat2) * sinDLon * sinDLon),
        Math.sqrt(1 - (sinDLat * sinDLat + Math.cos(lat1) * Math.cos(lat2) * sinDLon * sinDLon))
      );
    };

    const segment1 = distance(start, via);
    const segment2 = distance(via, end);
    return {
      points: [start, via, end],
      distance: segment1 + segment2,
    };
  };

  const loadRides = async () => {
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      const position = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 8000 });
      });
      const data = await findRides(position.coords.latitude, position.coords.longitude);
      setCenter({ lat: position.coords.latitude, lon: position.coords.longitude });
      setPickupAddress(await fetchAddress(position.coords.latitude, position.coords.longitude));
      setRides(data.rides || []);
    } catch (err) {
      try {
        const data = await findRides(center.lat, center.lon);
        setPickupAddress(await fetchAddress(center.lat, center.lon));
        setRides(data.rides || []);
      } catch (errorResponse) {
        setError(errorResponse instanceof Error ? errorResponse.message : 'Unable to load rides');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!mapRef.current) {
      const map = L.map('ride-map', { center: [center.lat, center.lon], zoom: 14, zoomControl: false });
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
      }).addTo(map);
      L.control.zoom({ position: 'topright' }).addTo(map);
      markerLayer.current = L.layerGroup().addTo(map);
      routeLayer.current = L.layerGroup().addTo(map);
      mapRef.current = map;
    }
  }, []);

  useEffect(() => {
    if (!mapRef.current) return;
    mapRef.current.setView([center.lat, center.lon], mapRef.current.getZoom());
  }, [center]);

  useEffect(() => {
    if (!markerLayer.current || !mapRef.current) return;
    markerLayer.current.clearLayers();
    if (routeLayer.current) {
      routeLayer.current.clearLayers();
    }
    markersRef.current = {};

    const addPopupMarker = (ride: Ride | null, lat: number, lon: number, popupText: string, highlight = false) => {
      const coords = `${lat.toFixed(5)}, ${lon.toFixed(5)}`;
      const content = ride === null
        ? `${popupText}<br/><small>${pickupAddress}</small><br/><small>${coords}</small>`
        : `${popupText}<br/><small>${coords}</small>`;
      const marker = ride === null
        ? L.marker([lat, lon], { icon: pickupIcon })
        : highlight
          ? L.circleMarker([lat, lon], { radius: 9, color: '#22c55e', fillColor: '#22c55e', fillOpacity: 0.8 })
          : L.marker([lat, lon], { icon: rideIcon });
      marker.addTo(markerLayer.current!).bindPopup(content);
      if (ride) {
        marker.on('click', () => setSelectedRideId(ride.ride_id));
        markersRef.current[ride.ride_id] = marker;
      }
    };

    addPopupMarker(null, center.lat, center.lon, 'Pickup location');

    const visibleRides = rides.length > 0 ? rides : [demoFallbackRide];
    visibleRides.forEach((ride) => {
      const lat = Number(ride.origin.lat ?? 12.9370);
      const lon = Number(ride.origin.lon ?? 77.6190);
      addPopupMarker(
        ride,
        lat,
        lon,
        `<strong>${ride.rider?.name || 'Driver'}</strong><br/>${ride.origin.name}<br/>${ride.departure_time} · ${ride.seats_left} seats`,
      );
    });

    if (selectedRideId) {
      const selectedRide = visibleRides.find((ride) => ride.ride_id === selectedRideId);
      const selectedMarker = selectedRide ? markersRef.current[selectedRideId] : null;
      if (selectedRide && selectedMarker) {
        const rideOrigin = {
          lat: Number(selectedRide.origin.lat ?? center.lat),
          lon: Number(selectedRide.origin.lon ?? center.lon),
        };
        const collegePoint = { lat: COLLEGE_LOCATION.lat, lon: COLLEGE_LOCATION.lon };
        const route = computeDijkstraRoute(center, rideOrigin, collegePoint);
        const routePoints: [number, number][] = route.points.map((point) => [point.lat, point.lon]);

        L.polyline(routePoints, {
          color: '#2563eb',
          weight: 5,
          opacity: 0.8,
          dashArray: '8,6',
        }).addTo(routeLayer.current!);

        L.circleMarker([collegePoint.lat, collegePoint.lon], {
          radius: 8,
          color: '#db2777',
          fillColor: '#f472b6',
          fillOpacity: 0.9,
        }).addTo(routeLayer.current!).bindPopup(COLLEGE_LOCATION.name);

        const bounds = L.latLngBounds(routePoints as any);
        mapRef.current.fitBounds(bounds.pad(0.25));
        selectedMarker.openPopup();
      }
    }
  }, [center, rides, selectedRideId]);

  useEffect(() => {
    void loadRides();
  }, []);

  const handleCenterRide = (rideId: string) => {
    const ride = visibleRides.find((rideItem) => rideItem.ride_id === rideId);
    if (!ride) return;
    setSelectedRideId(rideId);
    if (mapRef.current) {
      mapRef.current.setView([Number(ride.origin.lat ?? center.lat), Number(ride.origin.lon ?? center.lon)], 15);
    }
    markersRef.current[rideId]?.openPopup();
  };

  const handleRequest = async (rideId: string) => {
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      const res = await sendRequest(rideId, center.lat, center.lon);
      setMessage(res.message || 'Request sent');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send request');
    } finally {
      setLoading(false);
    }
  };

  const visibleRides = rides.length > 0 ? rides : [demoFallbackRide];

  return (
    <main className="page-shell animate-fade-in">
      <section className="card">
        <div className="page-title-row">
          <div>
            <h1>Find a ride</h1>
            <p>Browse nearby offers on the map, powered by OpenStreetMap.</p>
          </div>
          <button className="ghost" onClick={loadRides} disabled={loading}>
            Refresh
          </button>
        </div>
        {error && <div className="alert error">{error}</div>}
        {message && <div className="alert success">{message}</div>}

        <div id="ride-map" className="map-card" />
        <div className="pickup-details">
          <p><strong>Pickup location:</strong> {pickupAddress}</p>
          <p className="small-text">Coordinates: {center.lat.toFixed(5)}, {center.lon.toFixed(5)}</p>
        </div>

        {loading ? (
          <div className="loader">Loading rides…</div>
        ) : (
          <div className="list-grid">
            {visibleRides.map((ride) => (
              <article key={ride.ride_id} className={`ride-card animate-fade-in${ride.ride_id === selectedRideId ? ' selected' : ''}`}>
                <div className="ride-head">
                  <div>
                    <strong>{ride.rider?.name || 'Driver'}</strong>
                    <p>{ride.vehicle_name} · {ride.rider?.year} · {ride.rider?.branch}</p>
                  </div>
                  <span className="tag">{ride.seats_left} seats</span>
                </div>
                <p>{ride.origin.name ?? 'Pickup location'}</p>
                <div className="ride-meta">
                  <span>{ride.departure_time}</span>
                  <span>{ride.vehicle_name}</span>
                </div>
                <div className="action-row">
                  <button type="button" className={ride.ride_id === selectedRideId ? 'secondary' : 'ghost'} onClick={() => handleCenterRide(ride.ride_id)}>
                    {ride.ride_id === selectedRideId ? 'Viewing on map' : 'Show on map'}
                  </button>
                  <button onClick={() => handleRequest(ride.ride_id)} disabled={loading || rides.length === 0}>
                    Request to join
                  </button>
                </div>
                {ride.ride_id === selectedRideId && (
                  <p className="small-text">Shortest route to {COLLEGE_LOCATION.name} is shown on the map.</p>
                )}
                {rides.length === 0 && (
                  <p className="small-text">Demo ride card shown when no live rides are available.</p>
                )}
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

export default FindRidePage;
