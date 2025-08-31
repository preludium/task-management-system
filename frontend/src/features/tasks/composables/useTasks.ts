import { computed, ref, type Ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useApi } from '@/composables/useApi'
import type {
  TaskListResponse,
  TaskTab,
} from '../types'
import { useTaskSSE } from './useTaskSSE'

export interface TaskFilters {
  tab?: TaskTab
  page?: number
  size?: number
}

export const useTasks = (filters: Ref<TaskFilters> = ref({})) => {
  useTaskSSE(filters);
  const api = useApi()

  const getTasksQueryKey = (filters: TaskFilters) => [
    'tasks',
    {
      status: filters.tab === 'ALL' ? undefined : filters.tab,
      page: filters.page || 1,
      size: filters.size || 12
    }
  ]

  const {
    data: tasksResponse,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: computed(() => getTasksQueryKey(filters.value)),
    queryFn: async () => {
      const params = new URLSearchParams()

      if (filters.value.tab && filters.value.tab !== 'ALL') {
        params.append('status', filters.value.tab)
      }

      if (filters.value.page) {
        params.append('page', filters.value.page.toString())
      }

      if (filters.value.size) {
        params.append('size', filters.value.size.toString())
      }

      const queryString = params.toString()
      const url = queryString ? `/tasks?${queryString}` : '/tasks'

      return api.get<TaskListResponse>(url)
    },
    retry: 3,
    staleTime: 30_000,
  })

  const tasks = computed(() => tasksResponse.value?.items || [])
  const totalTasks = computed(() => tasksResponse.value?.total || 0)
  const currentPage = computed(() => tasksResponse.value?.page || 1)
  const pageSize = computed(() => tasksResponse.value?.size || 10)
  const totalPages = computed(() => tasksResponse.value?.pages || 1)

  const setFilter = (newFilters: Partial<TaskFilters>) => {
    filters.value = { ...filters.value, ...newFilters }
  }

  const setPage = (page: number) => {
    setFilter({ page })
  }

  const setPageSize = (size: number) => {
    setFilter({ size, page: 1 })
  }

  const setStatusFilter = (tab: TaskTab) => {
    setFilter({ tab, page: 1 })
  }

  return {
    tasks,
    tasksResponse,
    totalTasks,
    currentPage,
    pageSize,
    totalPages,

    isLoading,

    error,

    refetch,

    setFilter,
    setPage,
    setPageSize,
    setStatusFilter,

    filters: computed(() => filters.value)
  }
}