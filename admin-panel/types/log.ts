export interface AdminLog {
  id: number;
  admin_id: number;
  admin_username: string;
  action: string;
  target_type: string | null;
  target_id: number | null;
  details: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

export interface LogsListResponse {
  logs: AdminLog[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface LogsListParams {
  page?: number;
  per_page?: number;
  admin_id?: number;
  action?: string;
  target_type?: string;
}
