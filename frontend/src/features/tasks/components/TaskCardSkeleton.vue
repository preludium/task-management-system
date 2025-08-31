<template>
  <div
    class="flex flex-col h-[121px] gap-2 p-4 bg-white border border-gray-200 border-t-4 rounded-lg shadow-sm animate-pulse"
  >
    <div class="flex justify-between items-start">
      <!-- Status badge and dropdown placeholder -->
      <div class="flex items-center gap-2">
        <Skeleton class="h-6 w-16 bg-gray-200 rounded-full" />
      </div>
      <!-- MoreVertical icon placeholder -->
      <Skeleton class="h-6 w-6 bg-gray-200 rounded-full" />
    </div>
    <!-- Title placeholder -->
    <Skeleton class="h-4 w-3/4 bg-gray-200 rounded-md" />
    <!-- Description placeholder -->
    <Skeleton class="h-4 w-full bg-gray-200 rounded-md" />
  </div>
</template>

<style scoped>
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
