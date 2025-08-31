export interface Task {
  id: number;
  title: string;
  description?: string;
  status: TaskStatus;
  created_at: string;
  updated_at: string;
}

export const TaskStatus = {
  OPEN: 'OPEN',
  IN_PROGRESS: 'IN_PROGRESS',
  DONE: 'DONE'
} as const;

export type TaskStatus = typeof TaskStatus[keyof typeof TaskStatus];

export const TaskTab = {
  ...TaskStatus,
  ALL: "ALL",
} as const;

export type TaskTab = typeof TaskTab[keyof typeof TaskTab];

export interface TaskListResponse {
  items: Task[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export type TaskStatusDistributionResponse = Record<TaskStatus | 'total', number>;

export interface CreateTaskRequest {
  title: string;
  description?: string;
  status?: TaskStatus;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  status?: TaskStatus;
}

export interface TaskFilters {
  status?: TaskStatus | 'ALL';
  page?: number;
  size?: number;
}