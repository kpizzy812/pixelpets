import { apiClient } from "./client";
import {
  Admin,
  LoginRequest,
  LoginResponse,
  CreateAdminRequest,
  UpdateAdminRequest,
} from "@/types";

export async function login(data: LoginRequest): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>("/admin/login", data);
  return response.data;
}

export async function getCurrentAdmin(): Promise<Admin> {
  const response = await apiClient.get<Admin>("/admin/me");
  return response.data;
}

export async function createAdmin(data: CreateAdminRequest): Promise<Admin> {
  const response = await apiClient.post<Admin>("/admin/admins", data);
  return response.data;
}

export async function updateAdmin(
  adminId: number,
  data: UpdateAdminRequest
): Promise<Admin> {
  const response = await apiClient.patch<Admin>(`/admin/admins/${adminId}`, data);
  return response.data;
}
