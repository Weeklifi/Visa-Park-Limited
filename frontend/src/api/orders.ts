import { apiRequest } from "./client";
import type { CommissionPayoutResult, Order } from "./types";

export function listMyOrders() {
  return apiRequest<Order[]>("/orders");
}

export function createOrder(product_id: string, quantity: number) {
  return apiRequest<Order>("/orders", { method: "POST", body: { product_id, quantity } });
}

export function markOrderPaid(orderId: string) {
  return apiRequest<Order>(`/orders/${orderId}/mark-paid`, { method: "POST" });
}

export function processPayout(orderId: string) {
  return apiRequest<CommissionPayoutResult>(`/orders/${orderId}/process-payout`, { method: "POST" });
}
