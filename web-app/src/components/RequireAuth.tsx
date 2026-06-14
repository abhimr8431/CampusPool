import { Navigate, Outlet, useLocation } from 'react-router-dom';

const RequireAuth = () => {
  const token = localStorage.getItem('campuspool_token');
  const location = useLocation();
  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return <Outlet />;
};

export default RequireAuth;
