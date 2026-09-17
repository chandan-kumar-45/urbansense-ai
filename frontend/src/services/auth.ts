import { apiRequest } from "./api";
import type { AuthToken, User } from "@/types";

export function login(email: string, password: string) {
  return apiRequest<AuthToken>("/api/auth/login", {
    method: "POST",
    body: { email, password },
    auth: false,
  });
}

export function register(name: string, email: string, password: string, role: string) {
  return apiRequest<AuthToken>("/api/auth/register", {
    method: "POST",
    body: { name, email, password, role },
    auth: false,
  });
}

export function me() {
  return apiRequest<User>("/api/auth/me");
}

export function forgotPassword(email: string) {
  return apiRequest<{ message: string }>("/api/auth/forgot-password", {
    method: "POST",
    body: { email },
    auth: false,
  });
}
