import { apiRequest } from "./client";
import type { Product, ProductCategory } from "./types";

export interface ProductCreatePayload {
  title: string;
  description?: string;
  category: ProductCategory;
  base_price: number;
  stock_quantity: number;
}

export function listProducts(category?: ProductCategory) {
  const query = category ? `?category=${category}` : "";
  return apiRequest<Product[]>(`/products${query}`, { auth: false });
}

export function createProduct(payload: ProductCreatePayload) {
  return apiRequest<Product>("/products", { method: "POST", body: payload });
}

export function deactivateProduct(id: string) {
  return apiRequest<void>(`/products/${id}`, { method: "DELETE" });
}
