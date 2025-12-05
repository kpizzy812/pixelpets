export type AdminRole = "super_admin" | "admin" | "moderator";

export interface Admin {
  id: number;
  username: string;
  email: string | null;
  role: AdminRole;
  is_active: boolean;
  last_login_at: string | null;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  admin: Admin;
}

export interface CreateAdminRequest {
  username: string;
  password: string;
  email?: string | null;
  role?: AdminRole;
}

export interface UpdateAdminRequest {
  email?: string | null;
  role?: AdminRole | null;
  is_active?: boolean | null;
  password?: string | null;
}
