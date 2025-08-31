import { ref, onMounted, onUnmounted, type Ref } from 'vue'
import { useQueryClient } from '@tanstack/vue-query'
import { useSSE } from '@/composables'
import type { Task, TaskListResponse, TaskStatusDistributionResponse } from '../../types'
import type { TaskFilters } from '../useTasks'
import { isTaskEvent, SSE_TASK_EVENT_TYPES } from './types'


export const useTaskSSE = (filters: Ref<TaskFilters> = ref({})) => {
  const queryClient = useQueryClient()
  const sse = useSSE('/api/sse/tasks', [...SSE_TASK_EVENT_TYPES])

  const handleSSETaskEvent = (eventData: unknown) => {
    if (!isTaskEvent(eventData)) return

    switch (eventData.event) {
      case 'task_created':
        handleTaskCreated(eventData.data.task)
        break
      case 'task_updated':
        handleTaskUpdated(eventData.data.task)
        break
      case 'task_deleted':
        handleTaskDeleted(eventData.data.task)
        break
    }
  }

  const handleTaskCreated = (task?: Task) => {
    if (!task) return

    const currentFilters = filters.value
    const shouldShowInCurrentView =
      !currentFilters.tab ||
      currentFilters.tab === 'ALL' ||
      currentFilters.tab === task.status

    queryClient.setQueryData(['tasks-counts'], (oldData: TaskStatusDistributionResponse) => {
      if (!oldData) return oldData

      return {
        ...oldData,
        total: Math.max(0, oldData.total + 1),
        [task.status]: Math.max(0, oldData[task.status] + 1),
      }
    })

    if (shouldShowInCurrentView) {
      queryClient.setQueryData(
        ['tasks', {
          status: currentFilters.tab === 'ALL' ? undefined : currentFilters.tab,
          page: currentFilters.page || 1,
          size: currentFilters.size || 12
        }],
        (oldData: TaskListResponse) => {
          if (!oldData) return oldData

          const existingTask = oldData.items.find((item: Task) => item.id === task.id)
          if (existingTask) return oldData

          return {
            ...oldData,
            items: [task, ...oldData.items],
            total: oldData.total + 1
          }
        }
      )
    }
  }

  const handleTaskUpdated = (task?: Task) => {
    if (!task) return

    queryClient.setQueryData(
      ['tasks', {
        status: filters.value.tab === 'ALL' ? undefined : filters.value.tab,
        page: filters.value.page || 1,
        size: filters.value.size || 12
      }],
      (oldData: TaskListResponse) => {
        if (!oldData) return oldData

        const updatedItems = oldData.items.map((item: Task) =>
          item.id === task.id ? { ...item, ...task } : item
        )

        return {
          ...oldData,
          items: updatedItems
        }
      }
    )
  }

  const handleTaskDeleted = (task?: Task) => {
    if (!task) return

    queryClient.setQueryData(
      ['tasks', {
        status: filters.value.tab === 'ALL' ? undefined : filters.value.tab,
        page: filters.value.page || 1,
        size: filters.value.size || 12
      }],
      (oldData: TaskListResponse) => {
        if (!oldData) return oldData

        const filteredItems = oldData.items.filter((item: Task) => item.id !== task.id)

        return {
          ...oldData,
          items: filteredItems,
          total: Math.max(0, oldData.total - 1)
        }
      }
    )

    queryClient.setQueryData(['tasks-counts'], (oldData: TaskStatusDistributionResponse) => {
      if (!oldData) return oldData

      return {
        ...oldData,
        total: Math.max(0, oldData.total - 1),
        [task.status]: Math.max(0, oldData[task.status] - 1),
      }
    })
  }

  const connectSSE = () => {
    sse.connect()
  }

  const disconnectSSE = () => {
    sse.disconnect()
  }

  const reconnectSSE = () => {
    sse.forceReconnect()
  }

  onMounted(() => {
    sse.addEventHandler(handleSSETaskEvent)
    connectSSE()
  })

  onUnmounted(() => {
    sse.removeEventHandler(handleSSETaskEvent)
    disconnectSSE()
  })

  return {
    sse: {
      isConnected: sse.isConnected,
      isConnecting: sse.isConnecting,
      isReconnecting: sse.isReconnecting,
      hasFailedPermanently: sse.hasFailedPermanently,
      canRetry: sse.canRetry,
      connectionState: sse.connectionState,
      lastError: sse.lastError,
      retryCount: sse.retryCount,
      nextRetryIn: sse.nextRetryIn,
    },

    connectSSE,
    disconnectSSE,
    reconnectSSE,
    forceReconnect: sse.forceReconnect,
  }
}