import { Link } from 'react-router-dom';
import { getCurrentUser, logout } from '../api';
import ActiveRidesPanel from '../components/ActiveRidesPanel';
import RequestsPanel from '../components/RequestsPanel';

function HomePage() {
  const user = getCurrentUser();

  return (
    <main className="page-shell animate-fade-in">
      <section className="card hero-card">
        <div className="hero-content">
          <div>
            <h1>Welcome back, {user?.name ?? 'CampusPool user'}!</h1>
            <p>Plan smarter, connect with fellow commuters, and make every campus ride more social.</p>
            <div className="hero-actions">
              <Link className="button-link" to="/find">Find a ride</Link>
              <Link className="button-link secondary" to="/connect">Connect</Link>
            </div>
          </div>
          <div className="hero-badge">
            <span>New</span>
            <p>Messages and community chat now live inside CampusPool.</p>
          </div>
        </div>
      </section>

      <section className="grid-panel">
        <Link className="panel-card pulse-card" to="/find">
          <h2>Find a ride</h2>
          <p>Browse nearby ride offers and request a seat quickly.</p>
        </Link>
        <Link className="panel-card pulse-card" to="/post">
          <h2>Post a ride</h2>
          <p>Share your route and invite passengers to join.</p>
        </Link>
        <Link className="panel-card pulse-card" to="/connect">
          <h2>Connect</h2>
          <p>Match with other riders and start a chat.</p>
        </Link>
        <Link className="panel-card pulse-card" to="/messages">
          <h2>Messages</h2>
          <p>Keep all conversations and ride plans in one place.</p>
        </Link>
      </section>
      <section className="card stats-card">
        <div className="stat-block">
          <strong>92%</strong>
          <p>Ride acceptance rate</p>
        </div>
        <div className="stat-block">
          <strong>4.8</strong>
          <p>Average driver rating</p>
        </div>
        <div className="stat-block">
          <strong>3 mins</strong>
          <p>Average response time</p>
        </div>
      </section>

      <section className="card">
        <ActiveRidesPanel />
      </section>

      <section className="card">
        <RequestsPanel />
      </section>
    </main>
  );
}

export default HomePage;
