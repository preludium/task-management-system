<template>
  <EmptyTaskTab v-if="tasks.length === 0" />

  <div
    v-else
    class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
    role="grid"
    :aria-label="`${tasks.length} tasks displayed`"
    data-testid="task-list"
  >
    <TaskCardSkeleton
      v-if="loading"
      v-for="i in 9"
      :key="i"
      role="status"
      aria-live="polite"
      aria-label="Loading tasks"
    />

    <TaskCard
      v-else
      v-for="task in tasks"
      :key="task.id"
      :task="task"
      :is-loading="false"
      @edit="handleEditTask"
      @delete="handleDeleteTask"
      class="transition-all duration-200"
      role="gridcell"
    />
  </div>

  <TaskForm
    mode="modal"
    :is-open="showEditModal"
    @update:is-open="showEditModal = $event"
    :task="editingTask"
    :is-loading="isUpdating.value"
    @submit="handleUpdateTask"
    @cancel="handleCancelEdit"
  />

  <ConfirmDialog
    :is-open="showDeleteModal"
    @update:is-open="showDeleteModal = $event"
    title="Delete Task"
    :message="`Are you sure you want to delete &quot;${deletingTask?.title}&quot;? This action cannot be undone.`"
    :is-loading="isDeleting.value"
    @confirm="handleConfirmDelete"
    @cancel="handleCancelDelete"
    confirmButtonTestId="confirm-delete-button"
  />
</template>

<script setup lang="ts">
import { ref } from "vue";
import {
  type Task,
  type UpdateTaskRequest,
  TaskTab,
} from "@/features/tasks/types";
import ConfirmDialog from "@/components/ConfirmDialog.vue";
import TaskCardSkeleton from "./TaskCardSkeleton.vue";
import { useTaskMutation } from "../composables/useTaskMutation";
import TaskCard from "./TaskCard.vue";
import { TaskForm } from "./TaskForm";
import EmptyTaskTab from "./EmptyTaskTab.vue";

interface Props {
  tab: TaskTab;
  tasks: Task[];
  loading?: boolean;
}

withDefaults(defineProps<Props>(), {
  tab: TaskTab.ALL,
  loading: false,
  tasks: () => [],
});

const { deleteTask, updateTask, isDeleting, isUpdating } = useTaskMutation();

const showEditModal = ref(false);
const showDeleteModal = ref(false);

const editingTask = ref<Task | null>(null);
const deletingTask = ref<Task | null>(null);

const handleEditTask = (task: Task) => {
  editingTask.value = task;
  showEditModal.value = true;
};

const handleUpdateTask = (data: UpdateTaskRequest) => {
  if (editingTask.value) {
    updateTask(editingTask.value.id, data);
    showEditModal.value = false;
  }
};

const handleCancelEdit = () => {
  editingTask.value = null;
  showEditModal.value = false;
};

const handleDeleteTask = (task: Task) => {
  deletingTask.value = task;
  showDeleteModal.value = true;
};

const handleConfirmDelete = () => {
  if (deletingTask.value) {
    deleteTask(deletingTask.value.id);
    showDeleteModal.value = false;
  }
};

const handleCancelDelete = () => {
  deletingTask.value = null;
  showDeleteModal.value = false;
};
</script>
