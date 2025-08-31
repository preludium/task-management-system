<template>
  <div
    v-if="isVisible"
    class="flex flex-col h-[121px] gap-2 p-4 bg-white border border-gray-200 border-t-4 rounded-lg shadow-sm fade-in"
    :class="
      cn({
        'border-t-green-400': task.status === TaskStatus.DONE,
        'border-t-blue-400': task.status === TaskStatus.IN_PROGRESS,
        'border-t-gray-400': task.status === TaskStatus.OPEN,
      })
    "
  >
    <div class="flex justify-between items-start">
      <TaskStatusBadgeDropdown :task="task" />
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" class="size-6">
            <MoreVertical class="w-3 h-3" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent class="flex flex-col p-2 gap-2" align="end">
          <DropdownMenuItem
            @click="$emit('edit', task)"
            :disabled="isLoading"
            :aria-label="`Edit task: ${task.title}`"
          >
            <SquarePen class="w-4 h-4 sm:mr-2" aria-hidden="true" />
            <span>Edit</span>
          </DropdownMenuItem>
          <DropdownMenuItem
            variant="destructive"
            @click="$emit('delete', task)"
            :disabled="isLoading"
            aria-label="Delete task"
          >
            <Trash2 class="w-4 h-4 sm:mr-2" aria-hidden="true" />
            <span>Delete</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
    <h3 class="font-medium text-gray-800 m-0 truncate" :title="task.title">
      {{ task.title }}
    </h3>
    <div class="text-sm text-gray-500 truncate" :title="task.description">
      {{ task.description }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { TaskStatus, type Task } from "@/features/tasks/types";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import TaskStatusBadgeDropdown from "./TaskStatusBadgeDropdown.vue";
import { Trash2, SquarePen, MoreVertical } from "lucide-vue-next";
import { cn } from "@/components/ui/utils";
import { onMounted, ref } from "vue";

interface Props {
  task: Task;
  isLoading?: boolean;
}

withDefaults(defineProps<Props>(), {
  isLoading: false,
});

defineEmits<{
  edit: [task: Task];
  delete: [task: Task];
}>();

const isVisible = ref(false);

onMounted(() => {
  isVisible.value = true;
});
</script>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.5s ease-out forwards;
}
</style>
