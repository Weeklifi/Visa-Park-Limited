import { useEffect, useState } from "react";
import { listMyOrders, markOrderPaid, processPayout } from "../api/orders";
import type { Order } from "../api/types";
import { useAuth } from "../context/AuthContext";
import { ApiError } from "../api/client";
import ErrorBanner from "../components/ErrorBanner";

export default function OrdersPage() {
  const { user } = useAuth();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  async function refresh() {
    setLoading(true);
    try {
      const data = await listMyOrders();
      setOrders(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load orders");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleMarkPaid(id: string) {
    setError(null);
    setBusyId(id);
    try {
      await markOrderPaid(id);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to mark order paid");
    } finally {
      setBusyId(null);
    }
  }

  async function handleProcessPayout(id: string) {
    setError(null);
    setBusyId(id);
    try {
      await processPayout(id);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to process payout");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="page">
      <h1>My Orders</h1>
      <ErrorBanner message={error} />
      {loading && <p>Loading…</p>}
      {!loading && orders.length === 0 && <p>No orders yet.</p>}

      <table className="orders-table">
        <thead>
          <tr>
            <th>Order</th>
            <th>Role</th>
            <th>Qty</th>
            <th>Total</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((o) => {
            const isBuyer = o.buyer_id === user?.id;
            return (
              <tr key={o.id}>
                <td>
                  <code>{o.id.slice(0, 8)}</code>
                </td>
                <td>{isBuyer ? "Buyer" : "Vendor"}</td>
                <td>{o.quantity}</td>
                <td>${o.total_amount}</td>
                <td>{o.status}</td>
                <td>
                  {isBuyer && o.status === "PENDING" && (
                    <button disabled={busyId === o.id} onClick={() => handleMarkPaid(o.id)}>
                      {busyId === o.id ? "Confirming…" : "Confirm payment"}
                    </button>
                  )}
                  {o.status === "PAID" && (
                    <button disabled={busyId === o.id} onClick={() => handleProcessPayout(o.id)}>
                      {busyId === o.id ? "Processing…" : "Process payout"}
                    </button>
                  )}
                  {o.status === "COMPLETED" && <span>Commission distributed</span>}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
