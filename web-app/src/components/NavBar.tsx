import { NavLink } from 'react-router-dom';

const NavBar = () => {
  return (
    <header className="app-nav">
      <div className="brand">CampusPool</div>
      <nav>
        <NavLink to="/home" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Home</NavLink>
        <NavLink to="/find" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Find</NavLink>
        <NavLink to="/post" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Post</NavLink>
        <NavLink to="/connect" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Connect</NavLink>
        <NavLink to="/messages" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Messages</NavLink>
        <NavLink to="/profile" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Profile</NavLink>
      </nav>
    </header>
  );
};

export default NavBar;
