<template>
  <DropdownMenu>
    <DropdownMenuTrigger asChild>
      <Button
        variant="ghost"
        class="p-0 h-auto rounded-full group"
        testId="task-card-dropdown-menu"
      >
        <TaskStatusBadge
          :status="task.status"
          :class="
            cn({
              'group-hover:bg-green-200': task.status === TaskStatus.DONE,
              'group-hover:bg-blue-200': task.status === TaskStatus.IN_PROGRESS,
              'group-hover:bg-gray-300': task.status === TaskStatus.OPEN,
            })
          "
        />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent class="flex flex-col p-2 gap-2" align="start">
      <DropdownMenuItem
        v-for="status in availableStatuses"
        @click="updateTask(task.id, { status })"
        class="hover:!bg-gray-50 hover:cursor-pointer"
      >
        <TaskStatusBadge :status="status" />
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>

<script setup lang="ts">
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import TaskStatusBadge from "./TaskStatusBadge.vue";
import { TaskStatus, type Task } from "../types";
import { cn } from "@/components/ui/utils";
import { useTaskMutation } from "../composables/useTaskMutation";
import { computed } from "vue";

interface Props {
  task: Pick<Task, "id" | "status">;
}

interface Emits {
  edit: [id: Task["id"], status: Task["status"]];
}

const props = defineProps<Props>();
defineEmits<Emits>();

const availableStatuses = computed(() => {
  const { [props.task.status]: _, ...rest } = TaskStatus;
  return rest;
});

const { updateTask } = useTaskMutation();
</script>
