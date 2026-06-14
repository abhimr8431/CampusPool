const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:5000/api';

const getToken = () => localStorage.getItem('campuspool_token');

const authHeaders = () => {
  const token = getToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

async function request(path: string, options: RequestInit = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...authHeaders(),
      ...options.headers,
    },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    if (res.status === 401 || res.status === 403) {
      logout();
      window.location.href = '/login';
    }
    throw new Error(body.error || 'Request failed');
  }
  return body;
}

export async function login(email: string, password: string) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function register(data: Record<string, unknown>) {
  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function logout() {
  localStorage.removeItem('campuspool_token');
  localStorage.removeItem('campuspool_user');
}

export function saveSession(token: string, user: unknown) {
  localStorage.setItem('campuspool_token', token);
  localStorage.setItem('campuspool_user', JSON.stringify(user));
}

export function getCurrentUser() {
  const raw = localStorage.getItem('campuspool_user');
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export async function getProfile() {
  return request('/profile/me');
}

export async function postRide(payload: { origin_lat: number; origin_lon: number; origin_name: string; departure_time: string; seats: number; }) {
  return request('/rides/post', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function findRides(lat: number, lon: number) {
  return request(`/rides/find?lat=${lat}&lon=${lon}`);
}

export async function sendRequest(rideId: string, passengerLat: number, passengerLon: number) {
  return request('/requests/send', {
    method: 'POST',
    body: JSON.stringify({ ride_id: rideId, passenger_lat: passengerLat, passenger_lon: passengerLon }),
  });
}

export async function getMyRequests() {
  return request('/requests/my-requests');
}

export async function getActiveRequests() {
  return request('/requests/active');
}

export async function getIncomingRequests() {
  return request('/requests/incoming');
}

export async function acceptRequest(reqId: string) {
  return request(`/requests/${reqId}/accept`, { method: 'PATCH' });
}

export async function declineRequest(reqId: string) {
  return request(`/requests/${reqId}/decline`, { method: 'PATCH' });
}
