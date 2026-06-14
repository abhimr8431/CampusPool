import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getActiveRequests } from '../api';

export default function ActiveRidesPanel() {
  const [activeRides, setActiveRides] = useState<any[]>([]);
  const [expandedRequest, setExpandedRequest] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadActiveRides = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getActiveRequests();
      setActiveRides(res.active_requests || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load active rides');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadActiveRides();
  }, []);

  const toggleDetails = (requestId: string) => {
    setExpandedRequest((current) => (current === requestId ? null : requestId));
  };

  const renderLocationLink = (lat?: number, lon?: number) => {
    if (!lat || !lon) return null;
    const href = `https://www.google.com/maps/search/?api=1&query=${lat},${lon}`;
    return (
      <a className="button-link ghost" href={href} target="_blank" rel="noreferrer">
        Open location
      </a>
    );
  };

  const renderRoleCopy = (item: any) => {
    if (item.role === 'passenger') {
      return `You are confirmed as a rider with ${item.rider?.name || 'the driver'}`;
    }
    return `You are driving a confirmed passenger: ${item.passenger?.name || 'the rider'}`;
  };

  return (
    <div className="active-rides-panel">
      <div className="page-title-row">
        <div>
          <h2>Active accepted rides</h2>
          <p>Quickly review confirmed rides and pickup location details.</p>
        </div>
        <button className="ghost" onClick={loadActiveRides} disabled={loading}>
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="loader">Loading active rides…</div>
      ) : error ? (
        <div className="alert error">{error}</div>
      ) : activeRides.length === 0 ? (
        <div className="empty-state">No active accepted rides yet.</div>
      ) : (
        <div className="list-grid">
          {activeRides.map((ride) => (
            <article key={ride.request_id} className="ride-card">
              <div className="ride-head">
                <div>
                  <strong>{ride.role === 'passenger' ? ride.rider?.name : ride.passenger?.name}</strong>
                  <p className="small-text">
                    {ride.role === 'passenger'
                      ? `Pickup: ${ride.ride?.origin?.name ?? 'Unknown location'}`
                      : `Passenger pickup near ${ride.ride?.origin?.name ?? 'ride origin'}`}
                  </p>
                </div>
                <span className={`tag ${ride.status === 'accepted' ? 'success' : ''}`}>{ride.status}</span>
              </div>

              <p>{renderRoleCopy(ride)}</p>
              <p>Departure: {ride.ride?.departure_time ?? 'TBD'}</p>
              <p className="small-text">Vehicle: {ride.ride?.vehicle_name ?? 'N/A'}</p>

              <div className="action-row">
                <button type="button" onClick={() => toggleDetails(ride.request_id)}>
                  {expandedRequest === ride.request_id ? 'Hide details' : 'Show details'}
                </button>
                {renderLocationLink(ride.pickup?.lat, ride.pickup?.lon)}
              </div>

              {expandedRequest === ride.request_id && (
                <div className="request-details">
                  <p><strong>Pickup coordinates:</strong> {ride.pickup?.lat?.toFixed(5) ?? 'N/A'}, {ride.pickup?.lon?.toFixed(5) ?? 'N/A'}</p>
                  <p><strong>Ride origin:</strong> {ride.ride?.origin?.name ?? 'Unknown'}</p>
                  <p><strong>Vehicle:</strong> {ride.ride?.vehicle_name ?? 'N/A'}</p>
                  {ride.role === 'passenger' ? (
                    <p><strong>Driver:</strong> {ride.rider?.name ?? 'Unknown'} • {ride.rider?.year ?? ''} {ride.rider?.branch ?? ''}</p>
                  ) : (
                    <p><strong>Passenger:</strong> {ride.passenger?.name ?? 'Unknown'} • {ride.passenger?.year ?? ''} {ride.passenger?.branch ?? ''}</p>
                  )}
                  <p className="small-text">Confirmed seat count remaining: {ride.ride?.seats_left ?? 'N/A'}</p>
                  <Link className="button-link secondary" to="/connect">
                    Open chat
                  </Link>
                </div>
              )}
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
