import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useApi } from '../../../composables/useApi'
import type {
  TaskStatusDistributionResponse,
} from '../types'

export const useTaskCount = () => {
  const api = useApi()

  const {
    data: tasksResponse,
    isLoading,
    error
  } = useQuery({
    queryKey: ['tasks-counts'],
    queryFn: () => api.get<TaskStatusDistributionResponse>('/tasks/counts'),
    retry: 3,
    staleTime: 30_000,
  })

  const all = computed(() => tasksResponse.value?.total ?? 0)
  const open = computed(() => tasksResponse.value?.OPEN ?? 0)
  const inProgress = computed(() => tasksResponse.value?.IN_PROGRESS ?? 0)
  const done = computed(() => tasksResponse.value?.DONE ?? 0)

  return {
    all,
    open,
    inProgress,
    done,
    isLoading,
    error
  }
}