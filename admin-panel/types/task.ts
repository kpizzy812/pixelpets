export type TaskType =
  | "TELEGRAM_CHANNEL"
  | "TELEGRAM_CHAT"
  | "TWITTER"
  | "DISCORD"
  | "WEBSITE"
  | "OTHER"
  | "INVITE_FRIEND"
  | "INVITE_ACTIVE_FRIEND"
  | "BUY_PET";

// Task types that require a required_count in verification_data
export const PROGRESS_TASK_TYPES: TaskType[] = [
  "INVITE_FRIEND",
  "INVITE_ACTIVE_FRIEND",
  "BUY_PET",
];

export interface Task {
  id: number;
  title: string;
  description: string | null;
  reward_xpet: string;
  link: string | null;
  task_type: TaskType;
  verification_data: Record<string, unknown> | null;
  is_active: boolean;
  order: number;
  created_at: string;
  updated_at: string;
  completions_count: number;
}

export interface TasksListResponse {
  tasks: Task[];
  total: number;
}

export interface CreateTaskRequest {
  title: string;
  description?: string | null;
  reward_xpet: number;
  link?: string | null;
  task_type?: TaskType;
  verification_data?: Record<string, unknown> | null;
  is_active?: boolean;
  order?: number;
}

export interface UpdateTaskRequest {
  title?: string | null;
  description?: string | null;
  reward_xpet?: number | null;
  link?: string | null;
  task_type?: TaskType | null;
  verification_data?: Record<string, unknown> | null;
  is_active?: boolean | null;
  order?: number | null;
}

export interface DeleteTaskResponse {
  status: string;
  deleted: number;
}
