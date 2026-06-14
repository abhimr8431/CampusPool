import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { login, logout, saveSession } from '../api';

function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('testuser@rvce.edu.in');
  const [password, setPassword] = useState('TestPass123!');

  useEffect(() => {
    logout();
  }, []);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDemoLogin = async () => {
    setError(null);
    setLoading(true);
    try {
      const data = await login('testuser@rvce.edu.in', 'TestPass123!');
      if (data.token) {
        saveSession(data.token, data.user);
        navigate('/home');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Demo login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoRiderLogin = async () => {
    setError(null);
    setLoading(true);
    try {
      const data = await login('demorider@rvce.edu.in', 'DemoPass123!');
      if (data.token) {
        saveSession(data.token, data.user);
        navigate('/home');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Demo rider login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const data = await login(email.trim(), password);
      if (data.token) {
        saveSession(data.token, data.user);
        navigate('/home');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page-shell">
      <section className="card form-card">
        <h1>CampusPool</h1>
        <p>Sign in with your college email.</p>
        {error ? <div className="alert error">{error}</div> : null}
        <form onSubmit={handleSubmit}>
          <label>
            College email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="yourname@rvce.edu.in"
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
            />
          </label>
          <button type="submit" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
          <button
            type="button"
            className="secondary-button"
            onClick={handleDemoLogin}
            disabled={loading}
          >
            {loading ? 'Signing in…' : 'Login as Demo User'}
          </button>
          <button
            type="button"
            className="secondary-button"
            onClick={handleDemoRiderLogin}
            disabled={loading}
            style={{ marginLeft: 8 }}
          >
            {loading ? 'Signing in…' : 'Login as Demo Rider'}
          </button>
        </form>
        <p className="text-center demo-note">
          Demo credentials pre-filled: <strong>testuser@rvce.edu.in</strong> / <strong>TestPass123!</strong>
        </p>
        <p className="text-center">
          Don’t have an account? <Link to="/register">Register</Link>
        </p>
      </section>
    </main>
  );
}

export default LoginPage;
