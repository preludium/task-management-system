<template>
  <Toaster position="top-right" richColors />
  <AppLayout>
    <div class="flex justify-between items-center">
      <div class="flex items-center gap-6">
        <Rocket class="w-16 h-16" />
        <div class="flex flex-col">
          <h1
            class="text-2xl sm:text-3xl font-bold text-gray-900 mb-2 break-words"
          >
            Task Management
          </h1>
          <p class="text-sm sm:text-base text-gray-600">
            Manage your tasks efficiently with real-time updates
          </p>
        </div>
      </div>
    </div>

    <TaskManager />

    <Button
      @click="showCreateModal = true"
      class="fixed right-10 bottom-10 h-14 w-14 rounded-full justify-center items-center"
      aria-label="Create a new task"
    >
      <Plus class="!w-6 !h-6" />
    </Button>

    <TaskForm
      mode="modal"
      :is-open="showCreateModal"
      :is-loading="isCreating.value"
      @submit="handleTaskCreate"
      @cancel="showCreateModal = false"
    />
  </AppLayout>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Plus, Rocket } from "lucide-vue-next";
import AppLayout from "@/components/layout/AppLayout.vue";
import { Toaster } from "@/components/ui/sonner";
import {
  type CreateTaskRequest,
  type UpdateTaskRequest,
} from "./features/tasks/types";
import { TaskForm, TaskManager } from "@/features/tasks/components";
import { useTaskMutation } from "@/features/tasks/composables/useTaskMutation";
import { Button } from "@/components/ui/button";
import "vue-sonner/style.css";

const showCreateModal = ref(false);
const { createTask, isCreating } = useTaskMutation();

const handleTaskCreate = (data: CreateTaskRequest | UpdateTaskRequest) => {
  createTask(data as CreateTaskRequest);
  showCreateModal.value = false;
};
</script>
