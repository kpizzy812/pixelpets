export * from "./admin";
export * from "./user";
export * from "./deposit";
export * from "./withdrawal";
export * from "./pet-type";
export * from "./task";
export * from "./config";
export * from "./stats";
export * from "./log";

export interface PaginatedResponse<T> {
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  items: T[];
}

export interface ApiError {
  detail: string;
}
