<template>
  <div
    class="text-center py-12 border border-dashed"
    role="status"
    aria-live="polite"
  >
    <div class="max-w-md mx-auto">
      <div
        class="flex items-center justify-center w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full"
        aria-hidden="true"
      >
        <ClipboardList class="w-8 h-8 text-gray-400" />
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2" id="empty-title">
        No tasks here
      </h3>
      <p class="text-gray-600 mb-6" id="empty-description">
        This tab is empty. Check the others!
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ClipboardList } from "lucide-vue-next";
</script>
