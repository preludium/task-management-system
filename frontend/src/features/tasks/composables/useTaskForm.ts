import { computed } from 'vue'
import { useFormValidation } from '@/composables/useFormValidation'
import { taskFormSchema, type TaskFormData } from '@/features/tasks/schemas/task'
import type { Task, CreateTaskRequest, UpdateTaskRequest } from '../types'
import { TaskStatus } from '../types'

export interface UseTaskFormOptions {
  task?: Task | null
  mode?: 'create' | 'edit'
}

export const useTaskForm = ({ task = null, mode = 'create' }: UseTaskFormOptions = {}) => {
  const initialValues: TaskFormData = {
    title: task?.title || '',
    description: task?.description || '',
    status: task?.status || TaskStatus.OPEN
  }

  const form = useFormValidation<TaskFormData>({
    initialValues,
    validationSchema: taskFormSchema,
    validateOnMount: false
  })

  const isEditing = computed(() => mode === 'edit' || task !== null)

  const createSubmitHandler = (onSubmit: (data: CreateTaskRequest | UpdateTaskRequest) => Promise<void> | void) => {
    return form.handleSubmit(async (values: TaskFormData) => {
      try {
        const submitData: CreateTaskRequest | UpdateTaskRequest = {
          title: values.title.trim(),
          description: values.description?.trim() || undefined,
          status: values.status as TaskStatus
        }

        await onSubmit(submitData)
      } catch (error) {
        if (!form.handleServerErrors(error)) {
          throw error
        }
      }
    })
  }

  const resetForm = (newTask?: Task | null) => {
    const resetValues: TaskFormData = {
      title: newTask?.title || '',
      description: newTask?.description || '',
      status: newTask?.status || TaskStatus.OPEN
    }
    form.reset(resetValues)
  }

  const titleCharCount = computed(() => form.values.title?.length || 0)
  const descriptionCharCount = computed(() => form.values.description?.length || 0)

  const canSubmit = computed(() => {
    return form.isValid.value &&
      form.values.title?.trim().length > 0 &&
      !form.isSubmitting.value
  })

  return {
    ...form,

    isEditing,
    canSubmit,
    titleCharCount,
    descriptionCharCount,

    handleSubmit: createSubmitHandler,
    resetForm,
  }
}