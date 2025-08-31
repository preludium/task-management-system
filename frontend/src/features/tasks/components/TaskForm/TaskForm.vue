<template>
  <div>
    <!-- Modal Mode -->
    <Modal
      v-if="mode === 'modal'"
      :open="isOpen"
      @update:open="handleModalClose"
      :title="isEditing ? 'Edit Task' : 'Create New Task'"
      :description="
        isEditing
          ? 'Update the task details below.'
          : 'Fill in the details to create a new task.'
      "
    >
      <TaskFormContent
        ref="taskFormRef"
        :task="task"
        :is-loading="isLoading"
        @submit="handleSubmit"
        @cancel="handleCancel"
      />
    </Modal>

    <!-- Inline Mode -->
    <div v-else-if="mode === 'inline'" class="bg-gray-50 rounded-lg p-4 border">
      <TaskFormContent
        ref="taskFormRef"
        :task="task"
        :is-loading="isLoading"
        @submit="handleSubmit"
        @cancel="handleCancel"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import type {
  Task,
  CreateTaskRequest,
  UpdateTaskRequest,
} from "@/features/tasks/types";
import Modal from "@/components/ui/Modal.vue";
import TaskFormContent from "./TaskFormContent.vue";

interface Props {
  mode: "modal" | "inline";
  isOpen?: boolean;
  task?: Task | null;
  isLoading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  isOpen: false,
  task: null,
  isLoading: false,
});

const emit = defineEmits<{
  "update:isOpen": [value: boolean];
  submit: [data: CreateTaskRequest | UpdateTaskRequest];
  cancel: [];
  validationError: [error: any];
}>();

const isEditing = computed(() => props.task !== null);
const taskFormRef = ref<InstanceType<typeof TaskFormContent> | null>(null);

const handleSubmit = (data: CreateTaskRequest | UpdateTaskRequest) => {
  emit("submit", data);
};

const handleCancel = () => {
  if (props.mode === "modal") {
    emit("update:isOpen", false);
  }
  emit("cancel");
};

const handleModalClose = (isOpen: boolean) => {
  emit("update:isOpen", isOpen);
  if (!isOpen) {
    handleCancel();
  }
};

const handleServerError = (error: any) => {
  if (taskFormRef.value?.handleServerErrors) {
    const handled = taskFormRef.value.handleServerErrors(error);
    if (!handled) {
      emit("validationError", error);
    }
  } else {
    emit("validationError", error);
  }
};

defineExpose({
  handleServerError,
});
</script>
