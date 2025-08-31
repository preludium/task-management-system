<template>
  <Modal
    :open="isOpen"
    @update:open="$emit('update:isOpen', $event)"
    :title="title"
    :description="message"
    :close-on-backdrop="!isLoading"
    role="alertdialog"
    aria-modal="true"
  >
    <div
      class="flex flex-col sm:flex-row gap-3 sm:justify-end pt-4"
      @keydown="handleKeydown"
    >
      <Button
        ref="cancelButtonRef"
        type="button"
        variant="outline"
        @click="handleCancel"
        :disabled="isLoading"
        class="order-2 sm:order-1"
        :aria-label="`Cancel ${actionType || 'action'}`"
      >
        Cancel
      </Button>
      <Button
        ref="confirmButtonRef"
        type="button"
        variant="destructive"
        @click="handleConfirm"
        :disabled="isLoading"
        class="order-1 sm:order-2"
        :aria-label="`${confirmText} ${actionType || 'action'}`"
        :aria-describedby="isLoading ? 'loading-description' : undefined"
        :data-testid="confirmButtonTestId"
      >
        <LoadingSpinner v-if="isLoading" class="w-4 h-4 mr-2" />
        {{ isLoading ? loadingText : confirmText }}
        <span v-if="isLoading" id="loading-description" class="sr-only">
          Operation in progress, please wait
        </span>
      </Button>
    </div>
  </Modal>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from "vue";
import Modal from "@/components/ui/Modal.vue";
import { Button } from "@/components/ui/button";

interface Props {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  loadingText?: string;
  actionType?: string;
  isLoading?: boolean;
  confirmButtonTestId?: string;
}

const props = withDefaults(defineProps<Props>(), {
  confirmText: "Confirm",
  loadingText: "Processing...",
  isLoading: false,
});

const emit = defineEmits<{
  "update:isOpen": [value: boolean];
  confirm: [];
  cancel: [];
}>();

const cancelButtonRef = ref<InstanceType<typeof Button>>();
const confirmButtonRef = ref<InstanceType<typeof Button>>();

const handleConfirm = () => {
  emit("confirm");
};

const handleCancel = () => {
  emit("update:isOpen", false);
  emit("cancel");
};

const handleKeydown = (event: KeyboardEvent) => {
  // Handle Enter key to confirm
  if (event.key === "Enter" && !props.isLoading) {
    event.preventDefault();
    handleConfirm();
  }

  // Handle Escape key to cancel (if not loading)
  if (event.key === "Escape" && !props.isLoading) {
    event.preventDefault();
    handleCancel();
  }
};

// Focus management - focus the confirm button when dialog opens
watch(
  () => props.isOpen,
  async (isOpen) => {
    if (isOpen) {
      await nextTick();
      // Focus the confirm button by default for destructive actions
      confirmButtonRef.value?.$el?.focus();
    }
  }
);

// Simple loading spinner component
const LoadingSpinner = {
  template: `
    <svg 
      class="animate-spin" 
      viewBox="0 0 24 24" 
      fill="none"
      role="img"
      aria-label="Loading"
    >
      <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25"></circle>
      <path fill="currentColor" class="opacity-75" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
  `,
};
</script>
