export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  size: number;
}
export interface ApiError {
  message: string;
  code: string;
  status: number;
}
