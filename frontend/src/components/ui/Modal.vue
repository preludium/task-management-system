<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent
      :class="
        cn('sm:max-w-md [&>*]:flex [&>*]:flex-col [&>*]:gap-8', contentClass)
      "
      :close-on-backdrop="closeOnBackdrop"
      :role="role"
      :aria-modal="ariaModal"
    >
      <DialogHeader v-if="title || description">
        <DialogTitle v-if="title">{{ title }}</DialogTitle>
        <DialogDescription v-if="description">{{
          description
        }}</DialogDescription>
      </DialogHeader>

      <slot />

      <DialogFooter v-if="$slots.footer">
        <slot name="footer" />
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { cn } from "@/components/ui/utils";

interface Props {
  open: boolean;
  title?: string;
  description?: string;
  contentClass?: string;
  closeOnBackdrop?: boolean;
  role?: string;
  ariaModal?: string;
}

withDefaults(defineProps<Props>(), {
  closeOnBackdrop: true,
  role: "dialog",
  ariaModal: "true",
});

defineEmits<{
  "update:open": [value: boolean];
}>();
</script>
