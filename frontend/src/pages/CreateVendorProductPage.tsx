import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { createProduct } from "../api/products";
import { ApiError } from "../api/client";
import ErrorBanner from "../components/ErrorBanner";

export default function CreateVendorProductPage() {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [basePrice, setBasePrice] = useState("");
  const [stock, setStock] = useState("1");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const parsedBase = Number(basePrice);
  const retailPreview = Number.isFinite(parsedBase) && parsedBase > 0 ? (parsedBase * 1.8).toFixed(2) : null;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await createProduct({
        title,
        description: description || undefined,
        category: "VENDOR_PRODUCT",
        base_price: parsedBase,
        stock_quantity: Number(stock),
      });
      navigate("/vendor-products");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create product");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page">
      <h1>List a Vendor Product</h1>
      <p className="hint">
        You set the base price. The platform automatically computes the retail price at
        180% of base and handles commission distribution up your referral chain when it sells.
      </p>
      <ErrorBanner message={error} />
      <form onSubmit={handleSubmit} className="form">
        <label>
          Title
          <input value={title} onChange={(e) => setTitle(e.target.value)} required minLength={2} />
        </label>
        <label>
          Description
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={3} />
        </label>
        <label>
          Base price ($)
          <input
            type="number"
            min="0.01"
            step="0.01"
            value={basePrice}
            onChange={(e) => setBasePrice(e.target.value)}
            required
          />
        </label>
        <label>
          Stock quantity
          <input
            type="number"
            min="0"
            step="1"
            value={stock}
            onChange={(e) => setStock(e.target.value)}
            required
          />
        </label>
        {retailPreview && (
          <p className="hint">
            Retail price will be <strong>${retailPreview}</strong>
          </p>
        )}
        <button type="submit" disabled={submitting}>
          {submitting ? "Listing…" : "List product"}
        </button>
      </form>
    </div>
  );
}
