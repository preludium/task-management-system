<template>
  <form @submit.prevent="onSubmit" class="flex flex-col gap-6 px-1">
    <FormField name="title" v-slot="{ componentField }">
      <FormItem>
        <FormLabel>Title<span className="text-destructive">*</span></FormLabel>
        <FormControl>
          <Input
            placeholder="Enter task title"
            v-bind="componentField"
            required
          />
        </FormControl>
        <FormMessage />
      </FormItem>
    </FormField>

    <FormField name="description" v-slot="{ componentField }">
      <FormItem>
        <FormLabel>Description</FormLabel>
        <FormControl>
          <Textarea
            placeholder="Optional: Enter task description"
            v-bind="componentField"
          />
        </FormControl>
        <FormMessage />
      </FormItem>
    </FormField>

    <FormField name="status" v-slot="{ componentField }">
      <FormItem>
        <FormLabel>Status<span className="text-destructive">*</span></FormLabel>
        <Select v-bind="componentField">
          <SelectTrigger class="w-full">
            <SelectValue placeholder="Select a status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem :value="TaskStatus.OPEN">Open</SelectItem>
            <SelectItem :value="TaskStatus.IN_PROGRESS">In Progress</SelectItem>
            <SelectItem :value="TaskStatus.DONE">Done</SelectItem>
          </SelectContent>
        </Select>
        <FormMessage />
      </FormItem>
    </FormField>

    <div class="flex flex-col sm:flex-row gap-3 sm:justify-end">
      <Button
        type="button"
        variant="outline"
        @click="$emit('cancel')"
        :disabled="isLoading"
        class="order-2 sm:order-1 touch-target w-full sm:w-auto"
        size="lg"
      >
        Cancel
      </Button>
      <Button
        type="submit"
        :disabled="isLoading || !canSubmit"
        class="order-1 sm:order-2 touch-target w-full sm:w-auto"
        size="lg"
      >
        <LoadingSpinner v-if="isLoading" class="w-4 h-4 mr-2" />
        {{ isLoading ? "Saving..." : "Save Task" }}
      </Button>
    </div>
  </form>
</template>

<script setup lang="ts">
import {
  type Task,
  type CreateTaskRequest,
  type UpdateTaskRequest,
  TaskStatus,
} from "../../types";
import { useTaskForm } from "@/features/tasks/composables/useTaskForm";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormControl,
} from "@/components/ui/form";

interface Props {
  task?: Task | null;
  isLoading: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  task: null,
  isLoading: false,
});

const emit = defineEmits<{
  submit: [data: CreateTaskRequest | UpdateTaskRequest];
  cancel: [];
}>();

const {
  canSubmit,
  handleSubmit: createSubmitHandler,
  handleServerErrors,
} = useTaskForm({
  task: props.task,
  mode: props.task ? "edit" : "create",
});

const onSubmit = createSubmitHandler(async (data) => {
  emit("submit", data);
});

defineExpose({
  handleServerErrors,
});
</script>
