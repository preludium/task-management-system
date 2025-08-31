import { z } from 'zod'
import { TaskStatus } from '@/features/tasks/types'

export const taskStatusSchema = z.enum(Object.values(TaskStatus) as [string, ...string[]])

export const taskSchema = z.object({
  title: z
    .string()
    .min(1, 'Title is required')
    .max(200, 'Title must be less than 200 characters')
    .regex(/^[^<>"']*$/, 'Title contains invalid characters')
    .refine(
      (value) => !/<[^>]*>/g.test(value),
      'Title cannot contain HTML tags'
    ),

  description: z
    .string()
    .max(1000, 'Description must be less than 1000 characters')
    .refine(
      (value) => !/<[^>]*>/g.test(value),
      'Description cannot contain HTML tags'
    )
    .optional()
    .or(z.literal('')),

  status: taskStatusSchema
})

export const createTaskSchema = taskSchema.extend({
  status: taskStatusSchema.default('OPEN')
})

export const updateTaskSchema = taskSchema.partial()

export const taskFormSchema = z.object({
  title: z
    .string()
    .min(1, 'Title is required')
    .max(200, 'Title must be less than 200 characters'),
  description: z
    .string()
    .max(1000, 'Description must be less than 1000 characters')
    .optional()
    .or(z.literal('')),
  status: taskStatusSchema
})

export type TaskFormData = z.infer<typeof taskFormSchema>
export type CreateTaskData = z.infer<typeof createTaskSchema>
export type UpdateTaskData = z.infer<typeof updateTaskSchema>
export type TaskStatusType = z.infer<typeof taskStatusSchema>