import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function NavBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">Visa Park</Link>
      </div>
      <div className="navbar-links">
        <Link to="/tours">Tours & Travel Packages</Link>
        <Link to="/vendor-products">Vendor's Product</Link>
        {user && <Link to="/orders">My Orders</Link>}
        {user && <Link to="/dashboard">Dashboard</Link>}
      </div>
      <div className="navbar-auth">
        {user ? (
          <>
            <span className="navbar-user">
              {user.full_name} (L{user.layer_level})
            </span>
            <button onClick={handleLogout}>Log out</button>
          </>
        ) : (
          <>
            <Link to="/login">Log in</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}
