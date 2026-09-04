import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listProducts } from "../api/products";
import { createOrder } from "../api/orders";
import type { Product, ProductCategory } from "../api/types";
import { useAuth } from "../context/AuthContext";
import { ApiError } from "../api/client";
import ErrorBanner from "../components/ErrorBanner";

interface Props {
  category: ProductCategory;
  title: string;
}

export default function ProductListPage({ category, title }: Props) {
  const { user } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [buyingId, setBuyingId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    listProducts(category)
      .then(setProducts)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load products"))
      .finally(() => setLoading(false));
  }, [category]);

  async function handleBuy(productId: string) {
    setError(null);
    setMessage(null);
    setBuyingId(productId);
    try {
      const order = await createOrder(productId, 1);
      setMessage(`Order placed (status: ${order.status}). View it in My Orders to complete payment.`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to place order");
    } finally {
      setBuyingId(null);
    }
  }

  return (
    <div className="page">
      <h1>{title}</h1>
      {category === "VENDOR_PRODUCT" && user && (
        <p className="hint">
          Selling something? <Link to="/vendor-products/new">List a product</Link>
        </p>
      )}
      <ErrorBanner message={error} />
      {message && <div className="success-banner">{message}</div>}

      {loading && <p>Loading…</p>}
      {!loading && products.length === 0 && <p>No products available yet.</p>}

      <div className="product-grid">
        {products.map((p) => (
          <div className="product-card" key={p.id}>
            <h3>{p.title}</h3>
            {p.description && <p>{p.description}</p>}
            <p className="price">${p.retail_price}</p>
            <p className="stock">{p.stock_quantity} in stock</p>
            <button
              disabled={!user || buyingId === p.id || p.stock_quantity < 1}
              onClick={() => handleBuy(p.id)}
            >
              {buyingId === p.id ? "Placing order…" : user ? "Buy" : "Log in to buy"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
