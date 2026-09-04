import { apiRequest } from "./client";
import type { UserProfile } from "./types";

export interface RegisterPayload {
  full_name: string;
  email: string;
  password: string;
  parent_referral_code?: string;
}

export interface RegisterResponse {
  id: string;
  full_name: string;
  email: string;
  referral_code: string;
  layer_level: number;
  node_path: string;
}

export function register(payload: RegisterPayload) {
  return apiRequest<RegisterResponse>("/auth/register", { method: "POST", body: payload, auth: false });
}

export async function login(email: string, password: string) {
  const res = await apiRequest<{ access_token: string; token_type: string }>("/auth/login", {
    method: "POST",
    body: { email, password },
    auth: false,
  });
  localStorage.setItem("access_token", res.access_token);
  return res;
}

export function logout() {
  localStorage.removeItem("access_token");
}

export function getMyProfile() {
  return apiRequest<UserProfile>("/users/me");
}
