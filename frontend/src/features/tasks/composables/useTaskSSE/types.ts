import type { Task } from '@/features/tasks/types';

export const SSE_TASK_EVENT_TYPES = ['task_created', 'task_updated', 'task_deleted'] as const;

export interface SSETaskEvent {
  event: (typeof SSE_TASK_EVENT_TYPES)[number]
  data: {
    task?: Task
  }
}

export const isTaskEvent = (event: unknown): event is SSETaskEvent => {
  return (
    event != null &&
    typeof event === 'object' &&
    'event' in event &&
    typeof event.event === 'string' &&
    SSE_TASK_EVENT_TYPES.includes(event.event as typeof SSE_TASK_EVENT_TYPES[number]) &&
    'data' in event &&
    event.data != null &&
    typeof event.data === 'object' &&
    'task' in event.data &&
    typeof event.data.task === 'object'
  )
}