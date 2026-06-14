import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '../api';

const years = ['1st', '2nd', '3rd', '4th'];
const branches = ['CSE', 'ECE', 'MECH', 'CIVIL', 'EEE', 'ISE', 'AIML'];
const fuels = ['petrol', 'diesel'];

function RegisterPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    phone: '',
    roll_number: '',
    year: '1st',
    branch: 'CSE',
    vehicle_name: '',
    mileage_kmpl: '',
    fuel_type: 'petrol',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const handleChange = (key: string, value: string) => {
    setForm({ ...form, [key]: value });
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setMessage(null);
    setLoading(true);
    try {
      const payload = {
        name: form.name.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
        phone: form.phone.trim(),
        roll_number: form.roll_number.trim(),
        college: 'RVCE',
        year: form.year,
        branch: form.branch,
        vehicle: {
          name: form.vehicle_name.trim(),
          fuel_type: form.fuel_type,
          mileage_kmpl: Number(form.mileage_kmpl) || 40,
          reg_number: '',
        },
      };
      await register(payload);
      setMessage('Registered successfully. You can now sign in.');
      setTimeout(() => navigate('/login'), 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page-shell">
      <section className="card form-card wide-card">
        <h1>Create account</h1>
        <p>Use your college email to register.</p>
        {error ? <div className="alert error">{error}</div> : null}
        {message ? <div className="alert success">{message}</div> : null}
        <form onSubmit={handleSubmit}>
          <label>
            Full name
            <input
              value={form.name}
              onChange={(e) => handleChange('name', e.target.value)}
              required
            />
          </label>
          <label>
            College email
            <input
              type="email"
              value={form.email}
              onChange={(e) => handleChange('email', e.target.value)}
              required
              placeholder="yourname@rvce.edu.in"
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={form.password}
              onChange={(e) => handleChange('password', e.target.value)}
              required
            />
          </label>
          <label>
            Phone number
            <input
              value={form.phone}
              onChange={(e) => handleChange('phone', e.target.value)}
            />
          </label>
          <label>
            Roll number
            <input
              value={form.roll_number}
              onChange={(e) => handleChange('roll_number', e.target.value)}
            />
          </label>
          <div className="form-row">
            <label>
              Year
              <select
                value={form.year}
                onChange={(e) => handleChange('year', e.target.value)}
              >
                {years.map((year) => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Branch
              <select
                value={form.branch}
                onChange={(e) => handleChange('branch', e.target.value)}
              >
                {branches.map((branch) => (
                  <option key={branch} value={branch}>
                    {branch}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <label>
            Vehicle name
            <input
              value={form.vehicle_name}
              onChange={(e) => handleChange('vehicle_name', e.target.value)}
              required
            />
          </label>
          <div className="form-row">
            <label>
              Mileage (kmpl)
              <input
                type="number"
                min="1"
                value={form.mileage_kmpl}
                onChange={(e) => handleChange('mileage_kmpl', e.target.value)}
                required
              />
            </label>
            <label>
              Fuel type
              <select
                value={form.fuel_type}
                onChange={(e) => handleChange('fuel_type', e.target.value)}
              >
                {fuels.map((fuel) => (
                  <option key={fuel} value={fuel}>
                    {fuel}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <button type="submit" disabled={loading}>
            {loading ? 'Registering…' : 'Register'}
          </button>
        </form>
        <p className="text-center">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </section>
    </main>
  );
}

export default RegisterPage;
