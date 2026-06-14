import { Navigate, NavLink, Route, Routes, useLocation } from 'react-router-dom';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import ProfilePage from './pages/ProfilePage';
import RegisterPage from './pages/RegisterPage';
import FindRidePage from './pages/FindRidePage';
import PostRidePage from './pages/PostRidePage';
import RequestsPage from './pages/RequestsPage';
import ConnectPage from './pages/ConnectPage';
import MessagesPage from './pages/MessagesPage';
import RequireAuth from './components/RequireAuth';
import NavBar from './components/NavBar';

function App() {
  const location = useLocation();
  const showNav = !['/login', '/register'].includes(location.pathname);

  return (
    <div className="app-shell">
      {showNav && <NavBar />}
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/" element={<Navigate to="/home" replace />} />
        <Route path="/" element={<RequireAuth />}>
          <Route path="home" element={<HomePage />} />
          <Route path="find" element={<FindRidePage />} />
          <Route path="post" element={<PostRidePage />} />
          <Route path="requests" element={<RequestsPage />} />
          <Route path="connect" element={<ConnectPage />} />
          <Route path="messages" element={<MessagesPage />} />
          <Route path="profile" element={<ProfilePage />} />
        </Route>
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
      <footer className="app-footer">CampusPool Web rebuild · React + Vite</footer>
    </div>
  );
}

export default App;
