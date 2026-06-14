import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { acceptRequest, declineRequest, getIncomingRequests, getMyRequests } from '../api';

function RequestsPage() {
  const [tab, setTab] = useState<'my' | 'incoming'>('my');
  const [myRequests, setMyRequests] = useState<any[]>([]);
  const [incoming, setIncoming] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [my, inc] = await Promise.all([getMyRequests(), getIncomingRequests()]);
      setMyRequests(my.requests || []);
      setIncoming(inc.requests || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load requests');
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (reqId: string) => {
    setLoading(true);
    setError(null);
    try {
      await acceptRequest(reqId);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to accept request');
    } finally {
      setLoading(false);
    }
  };

  const handleDecline = async (reqId: string) => {
    setLoading(true);
    setError(null);
    try {
      await declineRequest(reqId);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to decline request');
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to refresh request status');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page-shell">
      <section className="card">
        <div className="page-title-row">
          <div>
            <h1>Requests</h1>
            <p>Track your own requests and manage incoming ride requests.</p>
          </div>
        </div>
        <div className="tab-bar">
          <button className={tab === 'my' ? 'active' : ''} onClick={() => setTab('my')}>
            My Requests
          </button>
          <button className={tab === 'incoming' ? 'active' : ''} onClick={() => setTab('incoming')}>
            Incoming Requests
          </button>
        </div>
        {error && <div className="alert error">{error}</div>}
        {loading ? (
          <div className="loader">Loading requests…</div>
        ) : tab === 'my' ? (
          myRequests.length === 0 ? (
            <div className="empty-state">No ride requests sent yet.</div>
          ) : (
            <div className="list-grid">
              {myRequests.map((req) => (
                <article key={req.request_id} className="ride-card">
                  <div className="ride-head">
                    <div>
                      <strong>{req.ride?.rider?.name || 'Driver'}</strong>
                      <p className="small-text">{req.ride?.origin?.name ?? 'Pickup location'}</p>
                    </div>
                    <span className={`tag ${req.status === 'accepted' ? 'success' : ''}`}>{req.status}</span>
                  </div>
                  <p>Departure: {req.ride?.departure_time}</p>
                  <p className="small-text">Vehicle: {req.rider?.vehicle || req.ride?.vehicle_name || 'N/A'}</p>
                  {req.status === 'accepted' && (
                    <div className="action-row">
                      <button onClick={handleRefreshStatus} disabled={loading}>
                        Refresh status
                      </button>
                      <Link className="button-link secondary" to="/connect">
                        Connect
                      </Link>
                    </div>
                  )}
                </article>
              ))}
            </div>
          )
        ) : incoming.length === 0 ? (
          <div className="empty-state">No incoming requests at the moment.</div>
        ) : (
          <div className="list-grid">
            {incoming.map((req) => (
              <article key={req.request_id} className="ride-card">
                <div className="ride-head">
                  <div>
                    <strong>{req.passenger?.name || 'Passenger'}</strong>
                    <p>{req.passenger?.year} · {req.passenger?.branch}</p>
                  </div>
                  <span className={`tag ${req.status === 'accepted' ? 'success' : ''}`}>{req.status}</span>
                </div>
                <p>Pickup: {req.ride?.origin?.name ?? 'Location'}</p>
                <p>Departure: {req.ride?.departure_time}</p>
                <p className="small-text">Pickup confirmed from your selected location.</p>
                {req.status === 'pending' ? (
                  <div className="action-row">
                    <button onClick={() => handleAccept(req.request_id)} disabled={loading}>
                      Accept
                    </button>
                    <button className="secondary" onClick={() => handleDecline(req.request_id)} disabled={loading}>
                      Decline
                    </button>
                  </div>
                ) : (
                  <div className="action-row">
                    <button onClick={handleRefreshStatus} disabled={loading}>
                      Refresh status
                    </button>
                    <Link className="button-link secondary" to="/connect">
                      Connect
                    </Link>
                  </div>
                )}
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

export default RequestsPage;
