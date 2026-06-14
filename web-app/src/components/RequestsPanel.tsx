import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getIncomingRequests, acceptRequest, declineRequest } from '../api';

export default function RequestsPanel() {
  const [incoming, setIncoming] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getIncomingRequests();
      setIncoming(res.requests || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load requests');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const handleAccept = async (id: string) => {
    setLoading(true);
    try {
      await acceptRequest(id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to accept');
    } finally {
      setLoading(false);
    }
  };

  const handleDecline = async (id: string) => {
    setLoading(true);
    try {
      await declineRequest(id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to decline');
    } finally {
      setLoading(false);
    }
  };

  if (loading && incoming.length === 0) return <div className="loader">Loading requests…</div>;
  if (error) return <div className="alert error">{error}</div>;

  return (
    <div className="requests-panel">
      <h3>Incoming requests</h3>
      {incoming.length === 0 ? (
        <div className="small-text">No incoming requests right now.</div>
      ) : (
        <div className="list-grid">
          {incoming.map((r) => (
            <article key={r.request_id} className="ride-card">
              <div className="ride-head">
                <div>
                  <strong>{r.passenger?.name}</strong>
                  <p className="small-text">{r.passenger?.year} · {r.passenger?.branch}</p>
                </div>
                <span className="tag">{r.status}</span>
              </div>
              <p>Pickup: {r.ride?.origin?.name}</p>
              <div className="action-row">
                {r.status === 'pending' ? (
                  <>
                    <button onClick={() => handleAccept(r.request_id)} disabled={loading}>Accept</button>
                    <button className="secondary" onClick={() => handleDecline(r.request_id)} disabled={loading}>Decline</button>
                  </>
                ) : (
                  <>
                    <button onClick={load} disabled={loading}>Refresh status</button>
                    <Link className="button-link secondary" to="/connect">Connect</Link>
                  </>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
