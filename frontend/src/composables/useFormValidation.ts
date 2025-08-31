import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'
import type { ZodSchema, ZodError } from 'zod'
import { computed } from 'vue'

export interface UseFormValidationOptions {
  initialValues?: Record<string, unknown>
  validationSchema: ZodSchema
  validateOnMount?: boolean
}

export const useFormValidation = <T extends Record<string, unknown>>({
  initialValues = {},
  validationSchema,
  validateOnMount = false
}: UseFormValidationOptions) => {

  const typedSchema = toTypedSchema(validationSchema)

  const {
    handleSubmit,
    resetForm,
    setFieldError,
    setErrors,
    setFieldValue,
    setFieldTouched,
    values,
    errors,
    isSubmitting,
    submitCount,
    meta
  } = useForm({
    validationSchema: typedSchema,
    initialValues,
    validateOnMount
  })

  const isValid = computed(() => meta.value.valid)
  const hasErrors = computed(() => Object.keys(errors.value).length > 0)
  const isDirty = computed(() => meta.value.dirty)
  const isTouched = computed(() => meta.value.touched)

  const handleServerErrors = (error: any) => {
    if (error?.status === 422 && error?.data?.detail) {
      const serverErrors: Record<string, string> = {}

      if (Array.isArray(error.data.detail)) {
        // Pydantic validation errors
        error.data.detail.forEach((err: any) => {
          const field = err.loc?.[err.loc.length - 1]
          if (field && err.msg) {
            serverErrors[field] = err.msg
          }
        })
      } else if (typeof error.data.detail === 'object') {
        // Custom validation errors
        Object.entries(error.data.detail).forEach(([field, message]) => {
          serverErrors[field] = message as string
        })
      }

      if (Object.keys(serverErrors).length > 0) {
        setErrors(serverErrors)
        return true
      }
    }

    // Zod validation errors
    if (error?.name === 'ZodError') {
      const zodError = error as ZodError
      const zodErrors: Record<string, string> = {}

      zodError.issues.forEach((err: any) => {
        const field = err.path.join('.')
        zodErrors[field] = err.message
      })

      setErrors(zodErrors)
      return true
    }

    return false
  }

  const reset = (newValues?: Partial<T>) => {
    resetForm({
      values: newValues ? { ...initialValues, ...newValues } : initialValues
    })
  }

  return {
    // Form state
    values: values as T,
    errors,
    isValid,
    hasErrors,
    isDirty,
    isTouched,
    isSubmitting,
    submitCount,
    meta,

    handleSubmit,
    reset,
    setErrors,
    handleServerErrors,

    setFieldValue,
    setFieldTouched,
    setFieldError,
    resetForm
  }
}