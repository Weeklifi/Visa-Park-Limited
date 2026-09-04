export interface UserProfile {
  id: string;
  full_name: string;
  email: string;
  referral_code: string;
  layer_level: number;
  node_path: string;
  child_count: number;
  is_active: boolean;
}

export type ProductCategory = "TRAVEL_PACKAGE" | "VENDOR_PRODUCT";

export interface Product {
  id: string;
  vendor_id: string;
  title: string;
  description: string | null;
  category: ProductCategory;
  base_price: string;
  retail_price: string;
  stock_quantity: number;
  is_active: boolean;
}

export type OrderStatus = "PENDING" | "PAID" | "COMPLETED" | "CANCELLED" | "REFUNDED";

export interface Order {
  id: string;
  buyer_id: string;
  product_id: string;
  vendor_id: string;
  unit_base_price: string;
  unit_retail_price: string;
  quantity: number;
  total_amount: string;
  status: OrderStatus;
}

export interface CommissionPayoutResult {
  order_id: string;
  vendor_id: string;
  vendor_total_payout: string;
  upward_ancestors_count: number;
  per_ancestor_payout: string;
  root_remainder_credit: string;
  status: string;
}
