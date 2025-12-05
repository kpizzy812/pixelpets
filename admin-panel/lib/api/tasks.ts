import { apiClient } from "./client";
import {
  TasksListResponse,
  Task,
  CreateTaskRequest,
  UpdateTaskRequest,
  DeleteTaskResponse,
} from "@/types";

export async function getTasks(includeInactive = true): Promise<TasksListResponse> {
  const response = await apiClient.get<TasksListResponse>("/admin/tasks", {
    params: { include_inactive: includeInactive },
  });
  return response.data;
}

export async function createTask(data: CreateTaskRequest): Promise<Task> {
  const response = await apiClient.post<Task>("/admin/tasks", data);
  return response.data;
}

export async function updateTask(
  taskId: number,
  data: UpdateTaskRequest
): Promise<Task> {
  const response = await apiClient.patch<Task>(`/admin/tasks/${taskId}`, data);
  return response.data;
}

export async function deleteTask(
  taskId: number,
  hardDelete = false
): Promise<DeleteTaskResponse> {
  const response = await apiClient.delete<DeleteTaskResponse>(
    `/admin/tasks/${taskId}`,
    { params: { hard_delete: hardDelete } }
  );
  return response.data;
}
