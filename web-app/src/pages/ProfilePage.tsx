import { useEffect, useState } from 'react';
import { getProfile, logout } from '../api';

function ProfilePage() {
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadProfile();
  }, []);

  const loadProfile = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getProfile();
      setProfile(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load profile');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <main className="page-shell"><div className="loader">Loading profile…</div></main>;
  }

  if (error) {
    return <main className="page-shell"><div className="alert error">{error}</div></main>;
  }

  return (
    <main className="page-shell">
      <section className="card">
        <div className="page-title-row">
          <div>
            <h1>Profile</h1>
            <p>Review your account and verification status.</p>
          </div>
          <button className="ghost" onClick={() => { logout(); window.location.href = '/login'; }}>
            Logout
          </button>
        </div>
        <div className="profile-grid">
          <div className="profile-card">
            <h2>{profile.name}</h2>
            <p>{profile.college} · {profile.year} · {profile.branch}</p>
            <p>{profile.email}</p>
            <p>{profile.phone}</p>
          </div>
          <div className="profile-card">
            <h3>Vehicle</h3>
            <p>{profile.vehicle?.name || 'Not set'}</p>
            <p>Mileage: {profile.vehicle?.mileage_kmpl ?? 'N/A'} kmpl</p>
            <p>Fuel: {profile.vehicle?.fuel_type ?? 'N/A'}</p>
          </div>
          <div className="profile-card">
            <h3>Verification</h3>
            <p>Email: {profile.verification?.email_verified ? 'Verified' : 'Pending'}</p>
            <p>ID upload: {profile.verification?.id_uploaded ? 'Done' : 'Pending'}</p>
            <p>Face match: {profile.verification?.face_matched ? 'Done' : 'Pending'}</p>
          </div>
          <div className="profile-card">
            <h3>Stats</h3>
            <p>Rating: {profile.rating ?? '5.0'}</p>
            <p>Trust score: {profile.trust_score ?? 50}</p>
            <p>Total rides: {profile.total_rides ?? 0}</p>
          </div>
        </div>
      </section>
    </main>
  );
}

export default ProfilePage;
