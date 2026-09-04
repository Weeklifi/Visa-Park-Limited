import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function HomePage() {
  const { user } = useAuth();

  return (
    <div className="page">
      <h1>Welcome to Visa Park</h1>
      <p>An invite-only travel and vendor marketplace platform.</p>
      <div className="home-links">
        <Link to="/tours" className="home-card">
          <h2>Tours & Travel Packages</h2>
          <p>Curated corporate travel offerings.</p>
        </Link>
        <Link to="/vendor-products" className="home-card">
          <h2>Vendor's Product</h2>
          <p>Peer-submitted marketplace products with commission sharing.</p>
        </Link>
      </div>
      {!user && (
        <p className="hint">
          <Link to="/register">Register</Link> with an invite code, or <Link to="/login">log in</Link>.
        </p>
      )}
    </div>
  );
}
