import { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { useNavigate } from 'react-router-dom';
import { postRide } from '../api';

import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const pickupIcon = L.divIcon({
  className: 'pickup-icon',
  html: '<div class="pickup-icon-symbol">📍</div>',
  iconSize: [28, 28],
  iconAnchor: [14, 28],
  popupAnchor: [0, -28],
});

type PlaceResult = {
  display_name: string;
  lat: string;
  lon: string;
};

type Position = {
  lat: number;
  lon: number;
};

function PostRidePage() {
  const navigate = useNavigate();
  const [origin, setOrigin] = useState('');
  const [departureTime, setDepartureTime] = useState('08:30');
  const [seats, setSeats] = useState(1);
  const [position, setPosition] = useState<Position>({ lat: 12.9370, lon: 77.6190 });
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<PlaceResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const markerRef = useRef<L.Marker | null>(null);

  const initializeMap = () => {
    if (!mapRef.current) {
      const map = L.map('post-map', { center: [position.lat, position.lon], zoom: 13, zoomControl: false });
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
      }).addTo(map);
      L.control.zoom({ position: 'topright' }).addTo(map);
      markerRef.current = L.marker([position.lat, position.lon], { icon: pickupIcon }).addTo(map).bindPopup('Pickup location');
      map.on('click', (event) => {
        const lat = event.latlng.lat;
        const lon = event.latlng.lng;
        setPosition({ lat, lon });
        setOrigin(`Picked location ${lat.toFixed(4)}, ${lon.toFixed(4)}`);
      });
      mapRef.current = map;
    }
  };

  useEffect(() => {
    initializeMap();
  }, []);

  useEffect(() => {
    if (!mapRef.current) return;
    mapRef.current.setView([position.lat, position.lon], mapRef.current.getZoom());
    markerRef.current?.setLatLng([position.lat, position.lon]);
  }, [position]);

  const searchLocation = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a location to search.');
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery.trim())}&limit=5`
      );
      const data = await response.json();
      setSearchResults((data as PlaceResult[]) || []);
    } catch (err) {
      setError('Unable to search location. Try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectResult = (place: PlaceResult) => {
    const lat = Number(place.lat);
    const lon = Number(place.lon);
    setPosition({ lat, lon });
    setOrigin(place.display_name);
    setSearchResults([]);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setMessage(null);
    if (!origin || !departureTime) {
      setError('Please provide pickup location and departure time.');
      return;
    }
    setLoading(true);
    try {
      const res = await postRide({
        origin_lat: position.lat,
        origin_lon: position.lon,
        origin_name: origin,
        departure_time: departureTime,
        seats,
      });
      setMessage(`Ride posted successfully. Estimated fare: ₹${res.estimated_fare}`);
      setTimeout(() => navigate('/find'), 1600);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to post ride.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page-shell animate-fade-in">
      <section className="card form-card">
        <h1>Post a ride</h1>
        <p>Search or tap a pickup location on the map using OpenStreetMap.</p>

        {error && <div className="alert error">{error}</div>}
        {message && <div className="alert success">{message} Redirecting…</div>}

        <div className="map-search-row">
          <div className="map-search-panel">
            <label>
              Search pickup location
              <input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search e.g. Kengeri, Banashankari"
              />
            </label>
            <button type="button" className="secondary" onClick={searchLocation} disabled={loading}>
              {loading ? 'Searching…' : 'Search map'}
            </button>
            {searchResults.length > 0 && (
              <div className="search-results">
                {searchResults.map((place, index) => (
                  <button key={`${place.lat}-${place.lon}-${index}`} type="button" className="ghost" onClick={() => handleSelectResult(place)}>
                    {place.display_name}
                  </button>
                ))}
              </div>
            )}
          </div>
          <div className="map-preview">
            <div id="post-map" style={{ height: '320px', width: '100%' }} />
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <label>
            Pickup name
            <input value={origin} onChange={(e) => setOrigin(e.target.value)} placeholder="e.g. Kengeri Bus Stop" required />
          </label>

          <label>
            Departure time
            <input type="time" value={departureTime} onChange={(e) => setDepartureTime(e.target.value)} required />
          </label>

          <label>
            Available seats
            <input type="number" min="1" max="5" value={seats} onChange={(e) => setSeats(Number(e.target.value))} />
          </label>

          <button type="submit" disabled={loading}>
            {loading ? 'Posting…' : 'Post Ride'}
          </button>
        </form>
      </section>
    </main>
  );
}

export default PostRidePage;
