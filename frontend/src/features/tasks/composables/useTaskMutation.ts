import { computed } from 'vue'
import { useMutation, useQueryClient } from '@tanstack/vue-query'
import { useApi } from '../../../composables/useApi'
import type {
  Task,
  CreateTaskRequest,
  UpdateTaskRequest,
} from '../types'
import { toast } from 'vue-sonner'

export const useTaskMutation = () => {
  const api = useApi()
  const queryClient = useQueryClient()

  const createTaskMutation = useMutation({
    mutationFn: (data: CreateTaskRequest) => api.post<Task>('/tasks', data),
    onSuccess: (task) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      queryClient.invalidateQueries({ queryKey: ['tasks-counts'] })
      toast.success(`Task "${task.title}" created successfully`)
    },
    onError: (_, { title }) => {
      toast.error(`Failed to create task "${title}"`)
    }
  })

  const updateTaskMutation = useMutation({
    mutationFn: ({ id, data }: { id: Task['id']; data: UpdateTaskRequest }) =>
      api.put<Task>(`/tasks/${id}`, data),
    onSuccess: (task) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      queryClient.invalidateQueries({ queryKey: ['tasks-counts'] })
      toast.success(`Task "${task.title}" updated successfully`)
    },
    onError: (_, { data }) => {
      toast.error(`Failed to update task "${data.title}"`)
    }
  })

  const deleteTaskMutation = useMutation({
    mutationFn: (id: Task['id']) => api.delete(`/tasks/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      queryClient.invalidateQueries({ queryKey: ['tasks-counts'] })
      toast.success('Task deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete a task')
    }
  })

  return {
    isCreating: computed(() => createTaskMutation.isPending),
    isUpdating: computed(() => updateTaskMutation.isPending),
    isDeleting: computed(() => deleteTaskMutation.isPending),

    createTask: createTaskMutation.mutate,
    updateTask: (id: Task['id'], data: UpdateTaskRequest) => updateTaskMutation.mutate({ id, data }),
    deleteTask: deleteTaskMutation.mutate,
  }
}